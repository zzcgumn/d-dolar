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


def test_player_defended_boards_excludes_declaring_and_opponent_rows() -> None:
    from d_dolar.reports.partnership_d_dolar import player_defended_boards

    joined = load_joined_boards(FIXTURES)
    result = player_defended_boards(joined, "HEGYI ANDRAS")
    assert _board_uids(result) == {583742, 408320, 512007, 283292}


def test_player_defended_boards_can_exclude_a_named_partner() -> None:
    from d_dolar.reports.partnership_d_dolar import player_defended_boards

    joined = load_joined_boards(FIXTURES)
    result = player_defended_boards(joined, "HEGYI ANDRAS", exclude_partner="LEVAI FERENC")
    assert _board_uids(result) == {512007, 283292}


def test_player_d_dolar_summary_excludes_the_named_partner() -> None:
    from d_dolar.reports.partnership_d_dolar import player_d_dolar_summary

    joined = load_joined_boards(FIXTURES)
    summary = player_d_dolar_summary(joined, "HEGYI ANDRAS", exclude_partner="LEVAI FERENC")
    assert summary == {
        "boards_defended": 2,
        "boards_judged": 2,
        "boards_optimal": 1,
        "boards_suboptimal": 1,
        "d_dolar_rate": 0.5,
    }


def test_player_d_dolar_summary_for_levai_excludes_hegyi() -> None:
    from d_dolar.reports.partnership_d_dolar import player_d_dolar_summary

    joined = load_joined_boards(FIXTURES)
    summary = player_d_dolar_summary(joined, "LEVAI FERENC", exclude_partner="HEGYI ANDRAS")
    assert summary == {
        "boards_defended": 2,
        "boards_judged": 2,
        "boards_optimal": 1,
        "boards_suboptimal": 1,
        "d_dolar_rate": 0.5,
    }


def test_player_d_dolar_summary_without_exclusion_includes_everyone() -> None:
    from d_dolar.reports.partnership_d_dolar import player_d_dolar_summary

    joined = load_joined_boards(FIXTURES)
    summary = player_d_dolar_summary(joined, "HEGYI ANDRAS")
    assert summary["boards_defended"] == 4


def test_two_player_d_dolar_report_combines_all_three_summaries() -> None:
    from d_dolar.reports.partnership_d_dolar import (
        partnership_d_dolar_summary,
        player_d_dolar_summary,
        two_player_d_dolar_report,
    )

    joined = load_joined_boards(FIXTURES)
    report = two_player_d_dolar_report(joined, "HEGYI ANDRAS", "LEVAI FERENC")
    assert report == {
        "partnership": partnership_d_dolar_summary(joined, "HEGYI ANDRAS", "LEVAI FERENC"),
        "player_a_other_partners": player_d_dolar_summary(
            joined, "HEGYI ANDRAS", exclude_partner="LEVAI FERENC"
        ),
        "player_b_other_partners": player_d_dolar_summary(
            joined, "LEVAI FERENC", exclude_partner="HEGYI ANDRAS"
        ),
    }
