from pathlib import Path

from d_dolar.rawdb.loader import load_joined_boards

FIXTURES = Path(__file__).parent / "fixtures"


def test_partnership_second_defender_summary_aggregates_tricks_lost() -> None:
    from d_dolar.reports.partnership_second_defender_tricks_lost import (
        partnership_second_defender_summary,
    )

    joined = load_joined_boards(FIXTURES)
    summary = partnership_second_defender_summary(joined, "HEGYI ANDRAS", "LEVAI FERENC")
    assert summary == {
        "boards_defended": 2,
        "boards_judged": 2,
        "total_tricks_lost": 1,
        "average_tricks_lost": 0.5,
    }


def test_partnership_second_defender_summary_is_all_zero_for_an_unknown_pair() -> None:
    from d_dolar.reports.partnership_second_defender_tricks_lost import (
        partnership_second_defender_summary,
    )

    joined = load_joined_boards(FIXTURES)
    summary = partnership_second_defender_summary(joined, "NOBODY ONE", "NOBODY TWO")
    assert summary == {
        "boards_defended": 0,
        "boards_judged": 0,
        "total_tricks_lost": 0,
        "average_tricks_lost": None,
    }


def test_player_second_defender_summary_excludes_the_named_partner() -> None:
    from d_dolar.reports.partnership_second_defender_tricks_lost import (
        player_second_defender_summary,
    )

    joined = load_joined_boards(FIXTURES)
    summary = player_second_defender_summary(joined, "HEGYI ANDRAS", exclude_partner="LEVAI FERENC")
    assert summary == {
        "boards_defended": 1,
        "boards_judged": 1,
        "total_tricks_lost": 2,
        "average_tricks_lost": 2.0,
    }


def test_player_second_defender_summary_for_levai_excludes_hegyi() -> None:
    from d_dolar.reports.partnership_second_defender_tricks_lost import (
        player_second_defender_summary,
    )

    joined = load_joined_boards(FIXTURES)
    summary = player_second_defender_summary(joined, "LEVAI FERENC", exclude_partner="HEGYI ANDRAS")
    assert summary == {
        "boards_defended": 1,
        "boards_judged": 1,
        "total_tricks_lost": 0,
        "average_tricks_lost": 0.0,
    }


def test_two_player_second_defender_report_combines_all_three_summaries() -> None:
    from d_dolar.reports.partnership_second_defender_tricks_lost import (
        partnership_second_defender_summary,
        player_second_defender_summary,
        two_player_second_defender_report,
    )

    joined = load_joined_boards(FIXTURES)
    report = two_player_second_defender_report(joined, "HEGYI ANDRAS", "LEVAI FERENC")
    assert report == {
        "partnership": partnership_second_defender_summary(joined, "HEGYI ANDRAS", "LEVAI FERENC"),
        "player_a_other_partners": player_second_defender_summary(
            joined, "HEGYI ANDRAS", exclude_partner="LEVAI FERENC"
        ),
        "player_b_other_partners": player_second_defender_summary(
            joined, "LEVAI FERENC", exclude_partner="HEGYI ANDRAS"
        ),
    }
