from pathlib import Path

import polars as pl

from d_dolar.rawdb.schema import (
    BOARDS_SCHEMA,
    DEALS_SCHEMA,
    EVENTS_SCHEMA,
    HANDS_SCHEMA,
)


def load_events(rawdb_dir: Path) -> pl.LazyFrame:
    return pl.scan_csv(rawdb_dir / "events.csv", schema=EVENTS_SCHEMA, null_values=[""])


def load_deals(rawdb_dir: Path) -> pl.LazyFrame:
    return pl.scan_csv(rawdb_dir / "deals.csv", schema=DEALS_SCHEMA, null_values=[""])


def load_hands(rawdb_dir: Path) -> pl.LazyFrame:
    return pl.scan_csv(rawdb_dir / "hands.csv", schema=HANDS_SCHEMA, null_values=[""])


def load_boards(rawdb_dir: Path) -> pl.LazyFrame:
    return pl.scan_csv(rawdb_dir / "boards.csv", schema=BOARDS_SCHEMA, null_values=[""])
