from pathlib import Path

import polars as pl

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_events_returns_expected_rows() -> None:
    from d_dolar.rawdb.loader import load_events

    lf = load_events(FIXTURES)
    assert isinstance(lf, pl.LazyFrame)
    assert lf.collect().height == 5


def test_load_deals_returns_expected_rows() -> None:
    from d_dolar.rawdb.loader import load_deals

    lf = load_deals(FIXTURES)
    assert lf.collect().height == 5


def test_load_hands_returns_expected_rows() -> None:
    from d_dolar.rawdb.loader import load_hands

    lf = load_hands(FIXTURES)
    assert lf.collect().height == 5


def test_load_boards_returns_expected_rows() -> None:
    from d_dolar.rawdb.loader import load_boards

    df = load_boards(FIXTURES).collect()
    assert df.height == 4
    row = df.filter(pl.col("BoardUID") == 1499299).row(0, named=True)
    assert row["RawScoreNS"] is None
    assert row["TricksMade"] == 12
