from pathlib import Path

import polars as pl

FIXTURES = Path(__file__).parent / "fixtures"


def test_events_schema_matches_fixture() -> None:
    from d_dolar.rawdb.schema import EVENTS_SCHEMA

    df = pl.read_csv(FIXTURES / "events.csv", schema=EVENTS_SCHEMA, null_values=[""])
    assert df.schema == pl.Schema(EVENTS_SCHEMA)


def test_deals_schema_matches_fixture() -> None:
    from d_dolar.rawdb.schema import DEALS_SCHEMA

    df = pl.read_csv(FIXTURES / "deals.csv", schema=DEALS_SCHEMA, null_values=[""])
    assert df.schema == pl.Schema(DEALS_SCHEMA)


def test_hands_schema_matches_fixture() -> None:
    from d_dolar.rawdb.schema import HANDS_SCHEMA

    df = pl.read_csv(FIXTURES / "hands.csv", schema=HANDS_SCHEMA, null_values=[""])
    assert df.schema == pl.Schema(HANDS_SCHEMA)
    assert df.schema["DD_W_N"] == pl.Int8
    assert df.schema["N_Total_HCP"] == pl.Int8


def test_boards_schema_matches_fixture() -> None:
    from d_dolar.rawdb.schema import BOARDS_SCHEMA

    df = pl.read_csv(FIXTURES / "boards.csv", schema=BOARDS_SCHEMA, null_values=[""])
    assert df.schema == pl.Schema(BOARDS_SCHEMA)
    assert df.schema["TricksMade"] == pl.Int8
    assert df.schema["RawScoreNS"] == pl.Int16
    assert df.schema["TableID"] == pl.String
    assert df.schema["Contract"] == pl.String
