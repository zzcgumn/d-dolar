from pathlib import Path

import polars as pl

from d_dolar.rawdb.loader import load_joined_boards

FIXTURES = Path(__file__).parents[1] / "reports" / "fixtures"

_EXPECTED = {
    ("hegyi andras", "kirschner jozsef"): 3,
    ("hegyi andras", "levai ferenc"): 3,
    ("balogh timea", "murkl mate"): 1,
    ("buratti andrea", "failla giuseppe"): 1,
    ("czimer csaba", "szalka tamas"): 1,
    ("dornyei zsolt", "levai ferenc"): 1,
    ("gira tiborne", "kiss sandor"): 1,
    ("hansen jorgen cilleborg", "schou steen"): 1,
    ("harris judy", "smith julie"): 1,
    ("hasegawa", "inami"): 1,
    ("hegyi andras", "marjan gyorgy"): 1,
    ("kisgyorgy lajos", "liska tibor"): 1,
    ("kovacs gyorgy", "novottny erno"): 1,
    ("kovacs gyorgy dr", "novottny erno"): 1,
    ("levai ferenc", "murkl mate"): 1,
    ("piscitelli francesca", "saccavini ilaria"): 1,
    ("welker jacint", "welker katalin"): 1,
    ("xiao", "yue"): 1,
}


def test_enumerate_partnerships_matches_the_confirmed_fixture_table() -> None:
    from d_dolar.analysis.partnerships import enumerate_partnerships

    joined = load_joined_boards(FIXTURES)
    result = enumerate_partnerships(joined)

    assert set(result.columns) >= {"player_a", "player_b", "boards_together"}
    by_pair = {
        (row["player_a"], row["player_b"]): row["boards_together"]
        for row in result.iter_rows(named=True)
    }
    assert by_pair == _EXPECTED


def test_min_boards_filters_to_the_two_three_board_partnerships() -> None:
    from d_dolar.analysis.partnerships import enumerate_partnerships

    joined = load_joined_boards(FIXTURES)
    result = enumerate_partnerships(joined, min_boards=2)

    by_pair = {
        (row["player_a"], row["player_b"]): row["boards_together"]
        for row in result.iter_rows(named=True)
    }
    assert by_pair == {
        ("hegyi andras", "kirschner jozsef"): 3,
        ("hegyi andras", "levai ferenc"): 3,
    }


def test_aliases_merge_the_kovacs_gyorgy_variants() -> None:
    from d_dolar.analysis.partnerships import enumerate_partnerships

    joined = load_joined_boards(FIXTURES)
    result = enumerate_partnerships(joined, aliases={"KOVACS GYORGY DR": "KOVACS GYORGY"})

    by_pair = {
        (row["player_a"], row["player_b"]): row["boards_together"]
        for row in result.iter_rows(named=True)
    }
    assert by_pair["kovacs gyorgy", "novottny erno"] == 2
    assert ("kovacs gyorgy dr", "novottny erno") not in by_pair


def test_normalize_true_merges_case_and_whitespace_variants() -> None:
    # No pure case/whitespace duplicate exists in the real fixtures
    # (confirmed this session: all 30 distinct names there are
    # already case-distinct) -- a synthetic frame exercises this.
    from d_dolar.analysis.partnerships import enumerate_partnerships

    joined = pl.LazyFrame(
        {
            "North": ["Jane Smith", "JANE SMITH "],
            "South": ["Bob Jones", "Bob Jones"],
            "East": [None, None],
            "West": [None, None],
        }
    )
    result = enumerate_partnerships(joined, normalize=True)
    assert result.height == 1
    assert result.row(0, named=True)["boards_together"] == 2


def test_normalize_false_keeps_case_variants_separate() -> None:
    from d_dolar.analysis.partnerships import enumerate_partnerships

    joined = pl.LazyFrame(
        {
            "North": ["Jane Smith", "JANE SMITH "],
            "South": ["Bob Jones", "Bob Jones"],
            "East": [None, None],
            "West": [None, None],
        }
    )
    result = enumerate_partnerships(joined, normalize=False)
    assert result.height == 2


def test_null_seat_name_is_dropped_not_paired() -> None:
    from d_dolar.analysis.partnerships import enumerate_partnerships

    joined = pl.LazyFrame(
        {
            "North": ["Jane Smith"],
            "South": [None],
            "East": [None],
            "West": [None],
        }
    )
    result = enumerate_partnerships(joined)
    assert result.height == 0
