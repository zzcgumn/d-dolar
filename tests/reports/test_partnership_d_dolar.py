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


def test_partnership_d_dolar_summary_aggregates_optimal_and_suboptimal() -> None:
    from d_dolar.reports.partnership_d_dolar import partnership_d_dolar_summary

    joined = load_joined_boards(FIXTURES)
    summary = partnership_d_dolar_summary(joined, "HEGYI ANDRAS", "LEVAI FERENC")
    assert summary == {
        "boards_defended": 2,
        "boards_judged": 2,
        "boards_optimal": 1,
        "boards_suboptimal": 1,
        "d_dolar_rate": 0.5,
    }


def test_partnership_d_dolar_summary_counts_unrecorded_lead_as_defended_not_judged() -> None:
    from d_dolar.reports.partnership_d_dolar import partnership_d_dolar_summary

    joined = load_joined_boards(FIXTURES)
    summary = partnership_d_dolar_summary(joined, "XIAO", "YUE")
    assert summary == {
        "boards_defended": 1,
        "boards_judged": 0,
        "boards_optimal": 0,
        "boards_suboptimal": 0,
        "d_dolar_rate": None,
    }


def test_partnership_d_dolar_summary_is_all_zero_for_an_unknown_pair() -> None:
    from d_dolar.reports.partnership_d_dolar import partnership_d_dolar_summary

    joined = load_joined_boards(FIXTURES)
    summary = partnership_d_dolar_summary(joined, "NOBODY ONE", "NOBODY TWO")
    assert summary == {
        "boards_defended": 0,
        "boards_judged": 0,
        "boards_optimal": 0,
        "boards_suboptimal": 0,
        "d_dolar_rate": None,
    }
