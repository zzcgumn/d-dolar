"""Board-filtering primitives shared by every partnership/player-level
report in this package: which boards a named pair, or a named player
in a specific role, defended."""

import polars as pl

from d_dolar.statistics._seats import LEADER_OF, OPPOSITE

_SEAT_COLUMN = {"N": "North", "E": "East", "S": "South", "W": "West"}
_OTHER_DEFENDER_OF = {d: OPPOSITE[LEADER_OF[d]] for d in LEADER_OF}


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


def _seat_role_name(declarer: pl.Expr, role_of_declarer: dict[str, str]) -> pl.Expr:
    """The player name sitting in whichever seat role_of_declarer maps
    each possible Declarer value to -- e.g. role_of_declarer=LEADER_OF
    resolves to the opening leader's name for every row."""
    return (
        pl.when(declarer == "N")
        .then(pl.col(_SEAT_COLUMN[role_of_declarer["N"]]))
        .when(declarer == "E")
        .then(pl.col(_SEAT_COLUMN[role_of_declarer["E"]]))
        .when(declarer == "S")
        .then(pl.col(_SEAT_COLUMN[role_of_declarer["S"]]))
        .otherwise(pl.col(_SEAT_COLUMN[role_of_declarer["W"]]))
    )


def player_as_leader_boards(
    joined: pl.LazyFrame, player: str, exclude_partner: str | None = None
) -> pl.LazyFrame:
    """Boards where `player` personally made the opening lead (and was
    therefore defending). If exclude_partner is given, boards where
    player's defending partner for that board is exclude_partner are
    left out."""
    declarer = pl.col("Declarer").cast(pl.String)
    leader_name = _seat_role_name(declarer, LEADER_OF)
    defended = joined.filter(declarer.is_not_null() & (leader_name == player))
    if exclude_partner is not None:
        other_defender_name = _seat_role_name(declarer, _OTHER_DEFENDER_OF)
        defended = defended.filter(other_defender_name != exclude_partner)
    return defended


def player_as_other_defender_boards(
    joined: pl.LazyFrame, player: str, exclude_partner: str | None = None
) -> pl.LazyFrame:
    """Boards where `player` was defending but did NOT make the opening
    lead. Same exclude_partner semantics as player_as_leader_boards,
    excluding the partner who actually led."""
    declarer = pl.col("Declarer").cast(pl.String)
    other_defender_name = _seat_role_name(declarer, _OTHER_DEFENDER_OF)
    defended = joined.filter(declarer.is_not_null() & (other_defender_name == player))
    if exclude_partner is not None:
        leader_name = _seat_role_name(declarer, LEADER_OF)
        defended = defended.filter(leader_name != exclude_partner)
    return defended
