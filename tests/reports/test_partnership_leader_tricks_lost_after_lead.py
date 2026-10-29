from pathlib import Path

from d_dolar.rawdb.loader import load_joined_boards

FIXTURES = Path(__file__).parent / "fixtures"


def test_partnership_leader_tricks_lost_after_lead_summary_aggregates_tricks_lost() -> None:
    from d_dolar.reports.partnership_leader_tricks_lost_after_lead import (
        partnership_leader_tricks_lost_after_lead_summary,
    )

    joined = load_joined_boards(FIXTURES)
    summary = partnership_leader_tricks_lost_after_lead_summary(
        joined, "HEGYI ANDRAS", "LEVAI FERENC"
    )
    assert summary == {
        "boards_defended": 2,
        "boards_judged": 2,
        "total_tricks_lost": 2,
        "average_tricks_lost": 1.0,
    }


def test_partnership_leader_tricks_lost_after_lead_summary_is_all_zero_for_an_unknown_pair() -> None:
    from d_dolar.reports.partnership_leader_tricks_lost_after_lead import (
        partnership_leader_tricks_lost_after_lead_summary,
    )

    joined = load_joined_boards(FIXTURES)
    summary = partnership_leader_tricks_lost_after_lead_summary(joined, "NOBODY ONE", "NOBODY TWO")
    assert summary == {
        "boards_defended": 0,
        "boards_judged": 0,
        "total_tricks_lost": 0,
        "average_tricks_lost": None,
    }


def test_player_leader_tricks_lost_after_lead_summary_excludes_the_named_partner() -> None:
    from d_dolar.reports.partnership_leader_tricks_lost_after_lead import (
        player_leader_tricks_lost_after_lead_summary,
    )

    joined = load_joined_boards(FIXTURES)
    summary = player_leader_tricks_lost_after_lead_summary(
        joined, "HEGYI ANDRAS", exclude_partner="LEVAI FERENC"
    )
    assert summary == {
        "boards_defended": 1,
        "boards_judged": 1,
        "total_tricks_lost": 0,
        "average_tricks_lost": 0.0,
    }


def test_player_leader_tricks_lost_after_lead_summary_for_levai_excludes_hegyi() -> None:
    from d_dolar.reports.partnership_leader_tricks_lost_after_lead import (
        player_leader_tricks_lost_after_lead_summary,
    )

    joined = load_joined_boards(FIXTURES)
    summary = player_leader_tricks_lost_after_lead_summary(
        joined, "LEVAI FERENC", exclude_partner="HEGYI ANDRAS"
    )
    assert summary == {
        "boards_defended": 1,
        "boards_judged": 1,
        "total_tricks_lost": 0,
        "average_tricks_lost": 0.0,
    }
