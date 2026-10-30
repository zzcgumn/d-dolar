"""Build a wide per-board dataframe combining all three
double-dummy-based defence statistics, for analyzing how they
interact."""

import polars as pl

from d_dolar.statistics._board_trajectory import board_trajectory, lead_trajectory
from d_dolar.statistics._seats import OPPOSITE


def with_defence_statistics(joined: pl.LazyFrame) -> pl.DataFrame:
    """Returns joined's rows, collected, with seven columns added:
    the four raw double-dummy trajectory primitives (lead_tricks,
    trajectory_leader, trajectory_seats, trajectory_tricks) plus the
    three statistics already derived from them (d_dolar,
    dropped_before_dummy, dropped_over_dummy). Each board's one
    necessary lead_trajectory solve and one necessary
    board_trajectory solve each run once, not twice, even though the
    three derived columns reduce over them."""
    collected = joined.collect()

    lead_tricks_values: list[list[int] | None] = []
    d_dolar_values: list[int | None] = []
    trajectory_leader_values: list[str | None] = []
    trajectory_seats_values: list[list[str] | None] = []
    trajectory_tricks_values: list[list[int] | None] = []
    dropped_before_dummy_values: list[int | None] = []
    dropped_over_dummy_values: list[int | None] = []

    for row in collected.iter_rows(named=True):
        hands, declarer, contract, lead, play = (
            row["Hands"],
            row["Declarer"],
            row["Contract"],
            row["Lead"],
            row["Play"],
        )

        tricks = lead_trajectory(hands, declarer, contract, lead, play)
        lead_tricks_values.append(tricks)
        d_dolar_values.append(None if tricks is None else (1 if tricks[1] == tricks[0] else 0))

        trajectory = board_trajectory(hands, declarer, contract, play)
        if trajectory is None:
            trajectory_leader_values.append(None)
            trajectory_seats_values.append(None)
            trajectory_tricks_values.append(None)
            dropped_before_dummy_values.append(None)
            dropped_over_dummy_values.append(None)
            continue

        leader, seats, trajectory_tricks = trajectory
        trajectory_leader_values.append(leader)
        trajectory_seats_values.append(seats)
        trajectory_tricks_values.append(trajectory_tricks)
        second_defender = OPPOSITE[leader]
        dropped_before_dummy_values.append(
            sum(
                trajectory_tricks[i] - trajectory_tricks[i - 1]
                for i in range(2, len(trajectory_tricks))
                if seats[i - 1] == leader
            )
        )
        dropped_over_dummy_values.append(
            sum(
                trajectory_tricks[i] - trajectory_tricks[i - 1]
                for i in range(1, len(trajectory_tricks))
                if seats[i - 1] == second_defender
            )
        )

    return collected.with_columns(
        pl.Series("lead_tricks", lead_tricks_values, dtype=pl.List(pl.Int64)),
        pl.Series("trajectory_leader", trajectory_leader_values, dtype=pl.String),
        pl.Series("trajectory_seats", trajectory_seats_values, dtype=pl.List(pl.String)),
        pl.Series("trajectory_tricks", trajectory_tricks_values, dtype=pl.List(pl.Int64)),
        pl.Series("d_dolar", d_dolar_values, dtype=pl.Int64),
        pl.Series("dropped_before_dummy", dropped_before_dummy_values, dtype=pl.Int64),
        pl.Series("dropped_over_dummy", dropped_over_dummy_values, dtype=pl.Int64),
    )
