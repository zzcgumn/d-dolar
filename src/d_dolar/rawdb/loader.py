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
    # Play's "" means "not recorded" per the source format itself, not
    # "unknown" -- unlike every other column, it must never become null.
    return pl.scan_csv(rawdb_dir / "boards.csv", schema=BOARDS_SCHEMA, null_values=[""]).with_columns(
        pl.col("Play").fill_null("")
    )


def load_joined_boards(rawdb_dir: Path) -> pl.LazyFrame:
    """boards ⋈ deals (DealUID) ⋈ hands (HandUID) ⋈ events (EventUID, MatchID)."""
    boards = load_boards(rawdb_dir)
    deals = load_deals(rawdb_dir).rename({"Hands": "_deals_hands"})
    hands = load_hands(rawdb_dir).rename({"Hands": "_hands_hands"})
    events = load_events(rawdb_dir)

    joined = (
        boards.join(deals, on="DealUID", how="inner")
        .join(hands, on="HandUID", how="inner")
        .join(events, on=["EventUID", "MatchID"], how="inner")
    )

    mismatch_count = (
        joined.filter(pl.col("_deals_hands") != pl.col("_hands_hands"))
        .select(pl.len())
        .collect()
        .item()
    )
    if mismatch_count:
        raise ValueError(
            f"{mismatch_count} row(s) have a Hands mismatch between deals.csv and hands.csv"
        )

    return joined.rename({"_deals_hands": "Hands"}).drop("_hands_hands")
