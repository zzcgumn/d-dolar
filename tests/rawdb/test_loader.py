import shutil
from pathlib import Path

import polars as pl
import pytest

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


def test_load_boards_keeps_empty_play_as_empty_string_not_null() -> None:
    from d_dolar.rawdb.loader import load_boards

    df = load_boards(FIXTURES).collect()
    row = df.filter(pl.col("BoardUID") == 1499299).row(0, named=True)
    assert row["Play"] == ""
    # Lead is a different column and has no such exception: empty means null.
    row = df.filter(pl.col("BoardUID") == 946801).row(0, named=True)
    assert row["Lead"] is None


def test_load_joined_boards_joins_on_expected_keys() -> None:
    from d_dolar.rawdb.loader import load_joined_boards

    df = load_joined_boards(FIXTURES).collect()
    assert df.height == 4
    assert df.columns.count("Hands") == 1
    assert "Hands_right" not in df.columns
    for col in ("DD_W_N", "ParScoreNS", "ParContracts", "EventName", "MatchName"):
        assert col in df.columns


def test_load_joined_boards_raises_on_hands_mismatch(tmp_path: Path) -> None:
    from d_dolar.rawdb.loader import load_joined_boards

    for name in ("events.csv", "deals.csv", "hands.csv", "boards.csv"):
        shutil.copy(FIXTURES / name, tmp_path / name)

    hands = pl.read_csv(tmp_path / "hands.csv")
    hands = hands.with_columns(
        pl.when(pl.col("HandUID") == 215330)
        .then(pl.lit("N:AKQJT98765432....."))
        .otherwise(pl.col("Hands"))
        .alias("Hands")
    )
    hands.write_csv(tmp_path / "hands.csv")

    with pytest.raises(ValueError, match="Hands"):
        load_joined_boards(tmp_path).collect()
