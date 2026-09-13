# Architecture

Vectorix Robinhood Chain Desk is a small Python package with four layers. Each layer is independently testable so the same desk pattern can move to another EVM L2 or a CEX ticket adapter.

```
CLI (rhchain)
  ├── rpc     read-only JSON-RPC against Robinhood Chain
  ├── tape    decode Uniswap-style Swap logs from hex
  ├── ticket  Robinhood-style order intent (no submit)
  ├── risk    hard gates before any fill is accepted
  └── paper   simulated book + execution loop
```

## Why paper first

Live bots fail in the same three places: bad tickets, missing risk, and silent inventory. The paper loop forces those to be explicit. A later live adapter would replace only the fill source — tickets and risk stay the same objects.

## Ticket

A ticket is an intent, not a send:

- `symbol`, `side` (`buy` | `sell`)
- `qty` (shares / token units)
- `limit` (price)
- `tif` (`day` | `ioc` | `fok`)
- `notional` = qty × limit

The CLI prints a copy-ready ticket. Nothing is signed.

## Risk

Gates trip before a fill is booked:

| Gate | Default |
| --- | --- |
| Max notional per ticket | 25_000 |
| Max absolute inventory per symbol | 500 |
| Max gross notional | 100_000 |
| Kill switch | off until drawn down or set by operator |

## Paper book

Each tick draws a mid from a random walk, builds a one-tick bid/ask, and the bot posts inside the spread. Fills occur when noise crosses the ticket. PnL is marked to mid.

## RPC

`RpcClient` speaks `eth_chainId`, `eth_blockNumber`, and `eth_gasPrice`. Health fails if the remote chain id is not `4663` unless you override `RHCHAIN_CHAIN_ID`.
