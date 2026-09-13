from rhchain.paper_bot import PaperBot
from rhchain.tape import UNISWAP_V2_SWAP_TOPIC, decode_v2_swap


def test_paper_run_is_deterministic() -> None:
    a = PaperBot(seed=7).run(80)
    b = PaperBot(seed=7).run(80)
    assert [(r.mid, r.filled, r.pnl) for r in a] == [(r.mid, r.filled, r.pnl) for r in b]
    assert any(r.filled for r in a)


def test_decode_v2_swap() -> None:
    data = "0x" + "".join(
        [
            f"{1:064x}",
            f"{0:064x}",
            f"{0:064x}",
            f"{2:064x}",
        ]
    )
    topics = [
        UNISWAP_V2_SWAP_TOPIC,
        "0x" + "0" * 24 + "aa" * 20,
        "0x" + "0" * 24 + "bb" * 20,
    ]
    swap = decode_v2_swap(topics, data)
    assert swap.amount0_in == 1
    assert swap.amount1_out == 2
    assert swap.side == "sell_token0"
