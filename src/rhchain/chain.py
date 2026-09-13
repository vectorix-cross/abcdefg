"""Public Robinhood Chain parameters.

Values follow published network docs. Confirm before live work:
https://docs.robinhood.com/chain/
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Network:
    name: str
    chain_id: int
    rpc_url: str
    explorer: str
    native_symbol: str


NETWORK = Network(
    name="Robinhood Chain",
    chain_id=int(os.environ.get("RHCHAIN_CHAIN_ID", "4663")),
    rpc_url=os.environ.get(
        "RHCHAIN_RPC", "https://rpc.mainnet.chain.robinhood.com"
    ),
    explorer="https://robinhoodchain.blockscout.com",
    native_symbol="ETH",
)
