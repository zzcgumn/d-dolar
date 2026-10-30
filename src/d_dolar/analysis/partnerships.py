"""Discovering which partnerships exist in a dataset and how many
boards they played together -- unlike every function in
d_dolar.reports.pairings, which requires the caller to already
know the two exact names to query for."""

import polars as pl


def enumerate_partnerships(
    joined: pl.LazyFrame,
    min_boards: int = 1,
    normalize: bool = True,
    aliases: dict[str, str] | None = None,
) -> pl.DataFrame:
    """Every pair of players who ever sat as partners (North+South
    or East+West, either order) in `joined`, with the number of
    boards they played together -- declaring, defending, and
    all-pass boards all count; this is NOT restricted to defending
    boards the way pairings.partnership_defended_boards is. Rows
    with a null seat name are dropped.

    `aliases`, if given, remaps a name (e.g. {"KOVACS GYORGY DR":
    "KOVACS GYORGY"}) against the RAW name, applied FIRST (before
    normalization) -- so a caller can paste names straight out of
    likely_duplicate_names' output without pre-normalizing the
    alias dict themselves. `normalize` (default True) then
    case/whitespace-folds every name (including whatever an alias
    substituted in), so e.g. "Jane Smith" and "JANE SMITH" are
    always one partnership -- lossless, safe to default on.
    `aliases` is the only mechanism that merges two
    genuinely-different-looking names; never automatic, never
    driven by a similarity score directly.

    Returns columns player_a, player_b (alphabetically canonical
    order) and boards_together, filtered to boards_together >=
    min_boards, sorted descending by boards_together. A pure
    Polars aggregation -- no dds3 call."""
    ns = joined.select(pl.col("North").alias("a"), pl.col("South").alias("b"))
    ew = joined.select(pl.col("East").alias("a"), pl.col("West").alias("b"))
    pairs = pl.concat([ns, ew]).filter(pl.col("a").is_not_null() & pl.col("b").is_not_null())

    if aliases:
        pairs = pairs.with_columns(
            pl.col("a").replace(aliases),
            pl.col("b").replace(aliases),
        )
    if normalize:
        pairs = pairs.with_columns(
            pl.col("a").str.strip_chars().str.to_lowercase(),
            pl.col("b").str.strip_chars().str.to_lowercase(),
        )

    pairs = pairs.with_columns(
        player_a=pl.min_horizontal("a", "b"),
        player_b=pl.max_horizontal("a", "b"),
    )
    return (
        pairs.group_by(["player_a", "player_b"])
        .agg(pl.len().alias("boards_together"))
        .filter(pl.col("boards_together") >= min_boards)
        .sort("boards_together", descending=True)
        .collect()
    )
