"""Aggregate d-dolar across a two-player defending partnership."""

import polars as pl


def partnership_defended_boards(
    joined: pl.LazyFrame, player_a: str, player_b: str
) -> pl.LazyFrame:
    """Boards where player_a and player_b sat as partners (North+South
    or East+West, either order) and were defending -- Declarer is a
    seat held by the *other* pair. Excludes boards where the named pair
    is declaring, where only one of the two names appears, and
    all-pass boards (Declarer null)."""
    declarer = pl.col("Declarer").cast(pl.String)
    is_ns_pair = ((pl.col("North") == player_a) & (pl.col("South") == player_b)) | (
        (pl.col("North") == player_b) & (pl.col("South") == player_a)
    )
    is_ew_pair = ((pl.col("East") == player_a) & (pl.col("West") == player_b)) | (
        (pl.col("East") == player_b) & (pl.col("West") == player_a)
    )
    ns_defending = is_ns_pair & declarer.is_in(["E", "W"])
    ew_defending = is_ew_pair & declarer.is_in(["N", "S"])
    return joined.filter(ns_defending | ew_defending)
