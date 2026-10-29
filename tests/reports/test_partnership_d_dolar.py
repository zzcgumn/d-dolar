from pathlib import Path

import polars as pl

from d_dolar.rawdb.loader import load_joined_boards

FIXTURES = Path(__file__).parent / "fixtures"


def _board_uids(frame: pl.LazyFrame) -> set[int]:
    return set(frame.collect()["BoardUID"].to_list())


def test_partnership_defended_boards_finds_the_defended_pair() -> None:
    from d_dolar.reports.partnership_d_dolar import partnership_defended_boards

    joined = load_joined_boards(FIXTURES)
    result = partnership_defended_boards(joined, "HEGYI ANDRAS", "LEVAI FERENC")
    assert _board_uids(result) == {583742, 408320}


def test_partnership_defended_boards_argument_order_does_not_matter() -> None:
    from d_dolar.reports.partnership_d_dolar import partnership_defended_boards

    joined = load_joined_boards(FIXTURES)
    result = partnership_defended_boards(joined, "LEVAI FERENC", "HEGYI ANDRAS")
    assert _board_uids(result) == {583742, 408320}


def test_partnership_defended_boards_empty_for_an_unknown_pair() -> None:
    from d_dolar.reports.partnership_d_dolar import partnership_defended_boards

    joined = load_joined_boards(FIXTURES)
    result = partnership_defended_boards(joined, "NOBODY ONE", "NOBODY TWO")
    assert _board_uids(result) == set()
