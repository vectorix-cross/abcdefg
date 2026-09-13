"""Vectorix desk for Robinhood Chain: tickets, tape, risk, paper bots."""

from rhchain.chain import NETWORK
from rhchain.ticket import Ticket

__all__ = ["NETWORK", "Ticket", "__version__"]
__version__ = "0.1.0"
