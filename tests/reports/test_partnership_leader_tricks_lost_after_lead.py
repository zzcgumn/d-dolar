import sys
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


def test_two_player_leader_tricks_lost_after_lead_report_combines_all_three_summaries() -> None:
    from d_dolar.reports.partnership_leader_tricks_lost_after_lead import (
        partnership_leader_tricks_lost_after_lead_summary,
        player_leader_tricks_lost_after_lead_summary,
        two_player_leader_tricks_lost_after_lead_report,
    )

    joined = load_joined_boards(FIXTURES)
    report = two_player_leader_tricks_lost_after_lead_report(joined, "HEGYI ANDRAS", "LEVAI FERENC")
    assert report == {
        "partnership": partnership_leader_tricks_lost_after_lead_summary(
            joined, "HEGYI ANDRAS", "LEVAI FERENC"
        ),
        "player_a_other_partners": player_leader_tricks_lost_after_lead_summary(
            joined, "HEGYI ANDRAS", exclude_partner="LEVAI FERENC"
        ),
        "player_b_other_partners": player_leader_tricks_lost_after_lead_summary(
            joined, "LEVAI FERENC", exclude_partner="HEGYI ANDRAS"
        ),
    }


def test_main_prints_all_three_sections(capsys) -> None:
    from d_dolar.reports.partnership_leader_tricks_lost_after_lead import main

    old_argv = sys.argv
    sys.argv = ["prog", "--rawdb-dir", str(FIXTURES), "HEGYI ANDRAS", "LEVAI FERENC"]
    try:
        main()
    finally:
        sys.argv = old_argv

    out = capsys.readouterr().out
    assert "Partnership" in out
    assert "HEGYI ANDRAS (other partners)" in out
    assert "LEVAI FERENC (other partners)" in out
    assert "boards_defended: 2" in out
    assert "average_tricks_lost: 1.0" in out
