"""Read-only JSON-RPC client for Robinhood Chain."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from rhchain.chain import NETWORK


@dataclass(frozen=True)
class Health:
    ok: bool
    chain_id: int | None
    block_number: int | None
    gas_price_wei: int | None
    error: str | None = None


class RpcClient:
    def __init__(self, url: str | None = None, timeout: float = 8.0) -> None:
        self.url = url or NETWORK.rpc_url
        self.timeout = timeout
        self._req_id = 0

    def call(self, method: str, params: list[Any] | None = None) -> Any:
        self._req_id += 1
        payload = json.dumps(
            {
                "jsonrpc": "2.0",
                "id": self._req_id,
                "method": method,
                "params": params or [],
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            self.url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        if "error" in body:
            raise RuntimeError(body["error"])
        return body["result"]

    def chain_id(self) -> int:
        return int(self.call("eth_chainId"), 16)

    def block_number(self) -> int:
        return int(self.call("eth_blockNumber"), 16)

    def gas_price(self) -> int:
        return int(self.call("eth_gasPrice"), 16)

    def health(self) -> Health:
        try:
            cid = self.chain_id()
            head = self.block_number()
            gas = self.gas_price()
        except (urllib.error.URLError, TimeoutError, RuntimeError, ValueError, OSError) as exc:
            return Health(False, None, None, None, str(exc))
        ok = cid == NETWORK.chain_id
        err = None if ok else f"chain id {cid} != expected {NETWORK.chain_id}"
        return Health(ok, cid, head, gas, err)
