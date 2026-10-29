"""Aggregate d-dolar across a two-player defending partnership."""

import polars as pl

from d_dolar.statistics.d_dolar import d_dolar_base


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


def _summarize(defended: pl.DataFrame) -> dict[str, int | float | None]:
    boards_defended = defended.height
    results = [
        d_dolar_base(row["Hands"], row["Declarer"], row["Contract"], row["Lead"])
        for row in defended.iter_rows(named=True)
    ]
    boards_optimal = sum(1 for r in results if r == 1)
    boards_suboptimal = sum(1 for r in results if r == 0)
    boards_judged = boards_optimal + boards_suboptimal
    return {
        "boards_defended": boards_defended,
        "boards_judged": boards_judged,
        "boards_optimal": boards_optimal,
        "boards_suboptimal": boards_suboptimal,
        "d_dolar_rate": boards_optimal / boards_judged if boards_judged else None,
    }


def partnership_d_dolar_summary(
    joined: pl.LazyFrame, player_a: str, player_b: str
) -> dict[str, int | float | None]:
    """Runs d_dolar_base over partnership_defended_boards' rows. See
    _summarize for the returned shape."""
    defended = partnership_defended_boards(joined, player_a, player_b).collect()
    return _summarize(defended)
