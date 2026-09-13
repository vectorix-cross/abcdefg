"""Hard gates that must pass before a paper fill is booked."""

from __future__ import annotations

from dataclasses import dataclass, field

from rhchain.ticket import Ticket


@dataclass
class RiskLimits:
    max_ticket_notional: float = 25_000.0
    max_abs_inventory: float = 500.0
    max_gross_notional: float = 100_000.0
    kill_switch: bool = False


@dataclass
class Book:
    """Inventory and cash after paper fills."""

    cash: float = 0.0
    inventory: dict[str, float] = field(default_factory=dict)
    marks: dict[str, float] = field(default_factory=dict)

    def qty(self, symbol: str) -> float:
        return self.inventory.get(symbol, 0.0)

    def apply_fill(self, ticket: Ticket, fill_price: float, fill_qty: float) -> None:
        signed = fill_qty if ticket.side == "buy" else -fill_qty
        self.inventory[ticket.symbol] = self.qty(ticket.symbol) + signed
        self.cash -= signed * fill_price
        self.marks[ticket.symbol] = fill_price

    def unrealized(self) -> float:
        pnl = 0.0
        for symbol, qty in self.inventory.items():
            mid = self.marks.get(symbol)
            if mid is None:
                continue
            # cash already includes -qty * fill; mark leftover vs last mid
            pnl += qty * mid
        return self.cash + pnl

    def gross_notional(self) -> float:
        total = 0.0
        for symbol, qty in self.inventory.items():
            mid = self.marks.get(symbol, 0.0)
            total += abs(qty * mid)
        return total


class RiskEngine:
    def __init__(self, limits: RiskLimits | None = None) -> None:
        self.limits = limits or RiskLimits()

    def check_ticket(self, ticket: Ticket, book: Book) -> str | None:
        if self.limits.kill_switch:
            return "kill switch is on"
        if ticket.notional > self.limits.max_ticket_notional:
            return (
                f"ticket notional {ticket.notional:.2f} "
                f"> {self.limits.max_ticket_notional:.2f}"
            )
        projected = book.qty(ticket.symbol)
        projected += ticket.qty if ticket.side == "buy" else -ticket.qty
        if abs(projected) > self.limits.max_abs_inventory:
            return f"inventory {projected:.4f} would exceed {self.limits.max_abs_inventory}"
        projected_gross = book.gross_notional() + ticket.notional
        if projected_gross > self.limits.max_gross_notional:
            return (
                f"gross notional {projected_gross:.2f} "
                f"> {self.limits.max_gross_notional:.2f}"
            )
        return None

    def trip(self) -> None:
        self.limits.kill_switch = True
