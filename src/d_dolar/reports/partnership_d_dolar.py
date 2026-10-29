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


def player_defended_boards(
    joined: pl.LazyFrame, player: str, exclude_partner: str | None = None
) -> pl.LazyFrame:
    """Boards where player sat in any of the 4 seats and was defending
    (Declarer held by the other pair). If exclude_partner is given,
    boards where player's partner for that board is exclude_partner
    are left out."""
    declarer = pl.col("Declarer").cast(pl.String)
    ns_defending = ((pl.col("North") == player) | (pl.col("South") == player)) & declarer.is_in(
        ["E", "W"]
    )
    ew_defending = ((pl.col("East") == player) | (pl.col("West") == player)) & declarer.is_in(
        ["N", "S"]
    )
    defended = joined.filter(ns_defending | ew_defending)
    if exclude_partner is not None:
        partner = (
            pl.when(pl.col("North") == player)
            .then(pl.col("South"))
            .when(pl.col("South") == player)
            .then(pl.col("North"))
            .when(pl.col("East") == player)
            .then(pl.col("West"))
            .otherwise(pl.col("East"))
        )
        defended = defended.filter(partner != exclude_partner)
    return defended


def player_d_dolar_summary(
    joined: pl.LazyFrame, player: str, exclude_partner: str | None = None
) -> dict[str, int | float | None]:
    """Runs d_dolar_base over player_defended_boards' rows. Same
    summary shape as partnership_d_dolar_summary."""
    defended = player_defended_boards(joined, player, exclude_partner).collect()
    return _summarize(defended)
