<div align="center">

# Vectorix · Robinhood Chain Desk

**Operator toolkit for Robinhood Chain — tickets, tape, risk, and paper bots.**  
Maintained by **Vectorix** (`vectorix-cross`) · [vanjasretenovic4@gmail.com](mailto:vanjasretenovic4@gmail.com) · Telegram [@vectoris_corss](https://t.me/vectoris_corss) · [Portfolio](https://portfolio.vanjasretenovic4.workers.dev/)

Robinhood Chain is a public, EVM-compatible Layer 2 built for tokenized markets, stablecoins, and on-chain rails. This repo is an independent desk: connect to the network, watch blocks and DEX flow, write Robinhood-style tickets, and run a paper execution bot with hard risk gates.

[![GitHub](https://img.shields.io/badge/github-vectorix--cross-181717?style=for-the-badge&logo=github)](https://github.com/vectorix-cross/robinhood-chain-desk)
[![License: MIT](https://img.shields.io/badge/license-MIT-22c55e?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](#stack)
[![Chain](https://img.shields.io/badge/chain-Robinhood%20L2%204663-000000?style=for-the-badge)](#network)

[Portfolio](https://portfolio.vanjasretenovic4.workers.dev/) · [Architecture](docs/ARCHITECTURE.md) · [Disclaimer](docs/DISCLAIMER.md) · [Quick start](#quick-start)

</div>

This project is **not affiliated with, endorsed by, or part of Robinhood Markets, Inc.** It uses only public chain parameters and public RPC. Default mode is paper. No custody, no private keys in the repo, no live order router.

## What this shows

| Skill | Where it lives |
| --- | --- |
| Chain ops (RPC health, chain id, gas, head) | `rhchain health` · `src/rhchain/rpc.py` |
| Robinhood-style tickets (side, qty, limit, TIF) | `rhchain ticket` · `src/rhchain/ticket.py` |
| Risk gates (notional, inventory, kill switch) | `src/rhchain/risk.py` |
| Paper execution bot (spread capture, fills, PnL) | `rhchain paper-run` · `src/rhchain/paper_bot.py` |
| Tape / log decode for Uniswap-style swaps | `src/rhchain/tape.py` |
| Operator CLI | `src/rhchain/cli.py` |

## Network

Public Robinhood Chain parameters (verify against [official docs](https://docs.robinhood.com/chain/) before any live work):

| Field | Value |
| --- | --- |
| Network | Robinhood Chain |
| Chain ID | `4663` |
| RPC | `https://rpc.mainnet.chain.robinhood.com` |
| Currency | ETH (gas) |
| Explorer | [robinhoodchain.blockscout.com](https://robinhoodchain.blockscout.com) |
| Compatibility | EVM · Arbitrum stack · standard JSON-RPC |

Override RPC with `RHCHAIN_RPC` if you use Alchemy or another provider.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Unix:    source .venv/bin/activate
pip install -e ".[dev]"
rhchain health
rhchain ticket --symbol HOOD --side buy --qty 10 --limit 42.50
rhchain paper-run --ticks 200 --seed 7
pytest
```

`health` talks to the public RPC (read-only). `ticket` and `paper-run` stay local unless you later wire a signed live adapter — this cut does not ship one.

## Paper bot

The paper loop is how the desk trains and how reviewers see the bot craft:

1. Build a synthetic book for a tokenized symbol.
2. Quote a spread, size from risk, emit a ticket.
3. Simulate fills against mid + noise.
4. Mark inventory, realized / unrealized PnL, and halt if a gate trips.

This is the same skeleton used on other Vectorix desks (Polymarket, crypto tape): **intent → risk → fill → mark**. Live keys stay off the machine until you add them.

```
RPC head --> tape events --> signal --> ticket (limit / TIF) --> risk gates
                                                              |
                                              paper fill <----+---- optional live adapter (not shipped)
                                                              |
                                                              v
                                                        inventory + PnL
```

## Stack

- Python 3.11+
- `urllib` JSON-RPC client (no heavy framework)
- pytest for ticket / risk / paper invariants
- GitHub Actions CI

## Related work

- [My-Polymarket-trading-bot-python](https://github.com/vectorix-cross/My-Polymarket-trading-bot-python) — prediction-market bot
- [CrossYield](https://github.com/vectorix-cross/CrossYield) — cross-chain RWA yield
- [My-web3-projects](https://github.com/vectorix-cross/My-web3-projects) — catalog
- [portfolio](https://github.com/vectorix-cross/portfolio) — public gallery

## License

MIT. See [docs/DISCLAIMER.md](docs/DISCLAIMER.md) before you treat any output as a trade.
