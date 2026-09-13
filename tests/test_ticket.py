from rhchain.ticket import Ticket


def test_ticket_normalizes_and_computes_notional() -> None:
    t = Ticket(symbol=" hood ", side="buy", qty=10, limit=42.5, tif="ioc")
    assert t.symbol == "HOOD"
    assert t.notional == 425.0
    assert t.as_dict()["submit"] is False


def test_ticket_rejects_bad_qty() -> None:
    try:
        Ticket(symbol="HOOD", side="buy", qty=0, limit=1)
    except ValueError as exc:
        assert "qty" in str(exc)
    else:
        raise AssertionError("expected ValueError")
