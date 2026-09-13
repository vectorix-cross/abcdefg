"""Paper execution loop: synthetic book, tickets, risk, fills, mark."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from rhchain.risk import Book, RiskEngine
from rhchain.ticket import Ticket


@dataclass
class TickResult:
    tick: int
    mid: float
    ticket: Ticket | None
    filled: bool
    fill_price: float | None
    reject: str | None
    inventory: float
    pnl: float


@dataclass
class PaperBot:
    symbol: str = "HOOD"
    start_mid: float = 42.0
    spread_bps: float = 8.0
    qty: float = 5.0
    seed: int = 7
    book: Book = field(default_factory=Book)
    risk: RiskEngine = field(default_factory=RiskEngine)
    mid: float = field(init=False)
    history: list[TickResult] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.mid = self.start_mid
        self._rng = random.Random(self.seed)

    def _next_mid(self) -> float:
        shock = self._rng.gauss(0.0, 0.12)
        self.mid = max(0.50, self.mid * (1.0 + shock / self.mid))
        return self.mid

    def _quote(self) -> Ticket:
        half = self.mid * (self.spread_bps / 10_000.0) / 2.0
        inv = self.book.qty(self.symbol)
        # lean against inventory: long -> sell, short -> buy
        side = "sell" if inv >= 0 else "buy"
        limit = self.mid + half if side == "sell" else self.mid - half
        return Ticket(symbol=self.symbol, side=side, qty=self.qty, limit=round(limit, 4), tif="ioc")

    def _maybe_fill(self, ticket: Ticket) -> float | None:
        noise = self._rng.gauss(0.0, 0.08)
        print_px = self.mid + noise
        if ticket.side == "buy" and print_px <= ticket.limit:
            return round(print_px, 4)
        if ticket.side == "sell" and print_px >= ticket.limit:
            return round(print_px, 4)
        return None

    def step(self, tick: int) -> TickResult:
        self._next_mid()
        self.book.marks[self.symbol] = self.mid
        ticket = self._quote()
        reject = self.risk.check_ticket(ticket, self.book)
        fill_px = None
        filled = False
        if reject is None:
            fill_px = self._maybe_fill(ticket)
            if fill_px is not None:
                self.book.apply_fill(ticket, fill_px, ticket.qty)
                filled = True
                if abs(self.book.unrealized()) > 5_000:
                    self.risk.trip()
                    reject = "kill switch after drawdown"
        result = TickResult(
            tick=tick,
            mid=round(self.mid, 4),
            ticket=ticket,
            filled=filled,
            fill_price=fill_px,
            reject=reject,
            inventory=round(self.book.qty(self.symbol), 4),
            pnl=round(self.book.unrealized(), 4),
        )
        self.history.append(result)
        return result

    def run(self, ticks: int) -> list[TickResult]:
        return [self.step(i + 1) for i in range(ticks)]
