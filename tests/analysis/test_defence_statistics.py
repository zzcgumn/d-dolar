from pathlib import Path

import polars as pl

from d_dolar.rawdb.loader import load_joined_boards

FIXTURES = Path(__file__).parents[1] / "reports" / "fixtures"

_EXPECTED = {
    583742: (1, 2, 0),
    408320: (0, 0, 1),
    102648: (1, 0, 0),
    142234: (1, 0, 0),
    512007: (1, 1, 2),
    283292: (0, 0, 0),
    1313031: (1, 0, 0),
    1109355: (0, 0, 0),
    946801: (None, 0, 2),
    1499299: (1, None, None),
    1117730: (None, None, None),
}


def test_with_defence_statistics_adds_three_columns_matching_each_statistic() -> None:
    from d_dolar.analysis.defence_statistics import with_defence_statistics

    joined = load_joined_boards(FIXTURES)
    result = with_defence_statistics(joined)

    assert isinstance(result, pl.DataFrame)
    assert {"BoardUID", "d_dolar", "dropped_before_dummy", "dropped_over_dummy"} <= set(
        result.columns
    )
    assert result.height == 11

    by_board = {
        row["BoardUID"]: (
            row["d_dolar"],
            row["dropped_before_dummy"],
            row["dropped_over_dummy"],
        )
        for row in result.iter_rows(named=True)
    }
    assert by_board == _EXPECTED
