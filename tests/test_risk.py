from rhchain.risk import Book, RiskEngine, RiskLimits
from rhchain.ticket import Ticket


def test_blocks_oversize_ticket() -> None:
    risk = RiskEngine(RiskLimits(max_ticket_notional=100))
    ticket = Ticket(symbol="HOOD", side="buy", qty=10, limit=50)
    assert risk.check_ticket(ticket, Book()) is not None


def test_blocks_inventory_and_kill_switch() -> None:
    book = Book()
    ticket = Ticket(symbol="HOOD", side="buy", qty=10, limit=40)
    book.apply_fill(ticket, 40, 10)
    risk = RiskEngine(RiskLimits(max_abs_inventory=12))
    next_buy = Ticket(symbol="HOOD", side="buy", qty=10, limit=40)
    assert "inventory" in (risk.check_ticket(next_buy, book) or "")
    risk.trip()
    assert risk.check_ticket(Ticket(symbol="HOOD", side="sell", qty=1, limit=40), book)
