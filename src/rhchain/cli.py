"""Operator CLI: health, ticket, paper-run."""

from __future__ import annotations

import argparse
import json
import sys

from rhchain.chain import NETWORK
from rhchain.paper_bot import PaperBot
from rhchain.rpc import RpcClient
from rhchain.ticket import Ticket


def cmd_health(_: argparse.Namespace) -> int:
    print(f"network  {NETWORK.name}")
    print(f"chain    {NETWORK.chain_id}")
    print(f"rpc      {NETWORK.rpc_url}")
    print(f"explorer {NETWORK.explorer}")
    health = RpcClient().health()
    if health.ok:
        print(f"head     {health.block_number}")
        print(f"gas_wei  {health.gas_price_wei}")
        print("status   ok")
        return 0
    print(f"status   fail: {health.error}")
    return 1


def cmd_ticket(args: argparse.Namespace) -> int:
    ticket = Ticket(
        symbol=args.symbol,
        side=args.side,
        qty=args.qty,
        limit=args.limit,
        tif=args.tif,
    )
    print(ticket.render())
    return 0


def cmd_paper(args: argparse.Namespace) -> int:
    bot = PaperBot(symbol=args.symbol, seed=args.seed, qty=args.qty)
    rows = bot.run(args.ticks)
    fills = sum(1 for r in rows if r.filled)
    last = rows[-1] if rows else None
    print(f"symbol     {bot.symbol}")
    print(f"ticks      {len(rows)}")
    print(f"fills      {fills}")
    if last:
        print(f"last_mid   {last.mid}")
        print(f"inventory  {last.inventory}")
        print(f"pnl        {last.pnl}")
        print(f"kill       {bot.risk.limits.kill_switch}")
    if args.json:
        payload = [
            {
                "tick": r.tick,
                "mid": r.mid,
                "filled": r.filled,
                "fill_price": r.fill_price,
                "reject": r.reject,
                "inventory": r.inventory,
                "pnl": r.pnl,
                "ticket": None if r.ticket is None else r.ticket.as_dict(),
            }
            for r in rows
        ]
        print(json.dumps(payload, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="rhchain",
        description="Vectorix desk for Robinhood Chain (paper by default).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    h = sub.add_parser("health", help="Ping public RPC and verify chain id 4663")
    h.set_defaults(func=cmd_health)

    t = sub.add_parser("ticket", help="Print a Robinhood-style intent ticket")
    t.add_argument("--symbol", default="HOOD")
    t.add_argument("--side", choices=("buy", "sell"), required=True)
    t.add_argument("--qty", type=float, required=True)
    t.add_argument("--limit", type=float, required=True)
    t.add_argument("--tif", choices=("day", "ioc", "fok"), default="day")
    t.set_defaults(func=cmd_ticket)

    r = sub.add_parser("paper-run", help="Run the paper execution bot")
    r.add_argument("--symbol", default="HOOD")
    r.add_argument("--ticks", type=int, default=200)
    r.add_argument("--seed", type=int, default=7)
    r.add_argument("--qty", type=float, default=5.0)
    r.add_argument("--json", action="store_true")
    r.set_defaults(func=cmd_paper)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
