"""Decode Uniswap V2-style Swap logs from hex (no RPC required for unit tests)."""

from __future__ import annotations

from dataclasses import dataclass

# keccak256("Swap(address,uint256,uint256,uint256,uint256,address)")
UNISWAP_V2_SWAP_TOPIC = (
    "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
)


def _u256(word: str) -> int:
    return int(word, 16)


@dataclass(frozen=True)
class SwapPrint:
    sender: str
    to: str
    amount0_in: int
    amount1_in: int
    amount0_out: int
    amount1_out: int

    @property
    def side(self) -> str:
        if self.amount0_in > 0 and self.amount1_out > 0:
            return "sell_token0"
        if self.amount1_in > 0 and self.amount0_out > 0:
            return "buy_token0"
        return "unknown"


def decode_v2_swap(topics: list[str], data: str) -> SwapPrint:
    if not topics or topics[0].lower() != UNISWAP_V2_SWAP_TOPIC:
        raise ValueError("not a Uniswap V2 Swap topic0")
    raw = data[2:] if data.startswith("0x") else data
    if len(raw) < 256:
        raise ValueError("swap data too short")
    words = [raw[i : i + 64] for i in range(0, 256, 64)]
    sender = "0x" + topics[1][-40:] if len(topics) > 1 else "0x" + words[0][-40:]
    to = "0x" + topics[2][-40:] if len(topics) > 2 else "0x" + "0" * 40
    return SwapPrint(
        sender=sender,
        to=to,
        amount0_in=_u256(words[0]),
        amount1_in=_u256(words[1]),
        amount0_out=_u256(words[2]),
        amount1_out=_u256(words[3]),
    )
