from pathlib import Path

import polars as pl

from d_dolar.rawdb.loader import load_joined_boards

FIXTURES = Path(__file__).parent / "fixtures"


def _board_uids(frame: pl.LazyFrame) -> set[int]:
    return set(frame.collect()["BoardUID"].to_list())


def test_player_as_other_defender_boards_excludes_boards_the_player_led() -> None:
    from d_dolar.reports.pairings import player_as_other_defender_boards

    joined = load_joined_boards(FIXTURES)
    result = player_as_other_defender_boards(joined, "HEGYI ANDRAS", exclude_partner="LEVAI FERENC")
    assert _board_uids(result) == {512007}


def test_player_as_leader_boards_excludes_a_malformed_declarer_instead_of_assuming_west() -> None:
    from d_dolar.reports.pairings import player_as_leader_boards

    # A real RawDB defect (specs/rawdb-import.md): 3 boards.csv rows have
    # Declarer == "s" (lowercase), outside N/E/S/W. Such a row must be
    # excluded, not silently treated as Declarer == "W" (which would
    # wrongly compare the queried player against North, the seat that
    # would lead against a real West declarer).
    joined = pl.DataFrame(
        {
            "BoardUID": [1],
            "North": ["ALICE"],
            "East": ["BOB"],
            "South": ["CAROL"],
            "West": ["DAVE"],
            "Declarer": ["s"],
        }
    ).lazy()
    result = player_as_leader_boards(joined, "ALICE")
    assert _board_uids(result) == set()
