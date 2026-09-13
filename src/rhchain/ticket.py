"""Robinhood-style order tickets. Intent only — nothing is submitted."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

Side = Literal["buy", "sell"]
Tif = Literal["day", "ioc", "fok"]


@dataclass(frozen=True)
class Ticket:
    symbol: str
    side: Side
    qty: float
    limit: float
    tif: Tif = "day"
    ticket_id: str = field(default_factory=lambda: uuid4().hex[:12])
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def __post_init__(self) -> None:
        if self.side not in ("buy", "sell"):
            raise ValueError("side must be buy or sell")
        if self.tif not in ("day", "ioc", "fok"):
            raise ValueError("tif must be day, ioc, or fok")
        if self.qty <= 0:
            raise ValueError("qty must be positive")
        if self.limit <= 0:
            raise ValueError("limit must be positive")
        object.__setattr__(self, "symbol", self.symbol.strip().upper())

    @property
    def notional(self) -> float:
        return self.qty * self.limit

    def as_dict(self) -> dict[str, object]:
        return {
            "ticket_id": self.ticket_id,
            "symbol": self.symbol,
            "side": self.side,
            "qty": self.qty,
            "limit": self.limit,
            "tif": self.tif,
            "notional": round(self.notional, 6),
            "created_at": self.created_at,
            "submit": False,
        }

    def render(self) -> str:
        rows = [
            f"TICKET  {self.ticket_id}",
            f"SYMBOL  {self.symbol}",
            f"SIDE    {self.side.upper()}",
            f"QTY     {self.qty}",
            f"LIMIT   {self.limit}",
            f"TIF     {self.tif.upper()}",
            f"NOTIONAL {self.notional:.2f}",
            "STATUS  INTENT ONLY - not submitted",
        ]
        return "\n".join(rows)
