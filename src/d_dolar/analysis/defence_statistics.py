"""Build a wide per-board dataframe combining all three
double-dummy-based defence statistics, for analyzing how they
interact."""

import polars as pl

from d_dolar.statistics._board_trajectory import board_trajectory
from d_dolar.statistics._seats import OPPOSITE
from d_dolar.statistics.d_dolar import d_dolar_base


def with_defence_statistics(joined: pl.LazyFrame) -> pl.DataFrame:
    """Returns joined's rows, collected, with three columns added:
    d_dolar (d_dolar_base's result), dropped_before_dummy (tricks
    dropped by the defender who WAS on lead --
    leader_tricks_lost_after_lead's result), and dropped_over_dummy
    (tricks dropped by the defender who was NOT on lead --
    second_defender_tricks_lost's result). Each board's one necessary
    double-dummy trajectory solve (board_trajectory) runs once, not
    twice, even though both drop columns derive from it."""
    collected = joined.collect()

    d_dolar_values: list[int | None] = []
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
        d_dolar_values.append(d_dolar_base(hands, declarer, contract, lead))

        trajectory = board_trajectory(hands, declarer, contract, play)
        if trajectory is None:
            dropped_before_dummy_values.append(None)
            dropped_over_dummy_values.append(None)
            continue

        leader, seats, tricks = trajectory
        second_defender = OPPOSITE[leader]
        dropped_before_dummy_values.append(
            sum(
                tricks[i] - tricks[i - 1]
                for i in range(2, len(tricks))
                if seats[i - 1] == leader
            )
        )
        dropped_over_dummy_values.append(
            sum(
                tricks[i] - tricks[i - 1]
                for i in range(1, len(tricks))
                if seats[i - 1] == second_defender
            )
        )

    return collected.with_columns(
        pl.Series("d_dolar", d_dolar_values, dtype=pl.Int64),
        pl.Series("dropped_before_dummy", dropped_before_dummy_values, dtype=pl.Int64),
        pl.Series("dropped_over_dummy", dropped_over_dummy_values, dtype=pl.Int64),
    )
