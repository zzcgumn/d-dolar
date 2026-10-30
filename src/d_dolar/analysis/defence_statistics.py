"""Build a wide per-board dataframe combining all three
double-dummy-based defence statistics, for analyzing how they
interact."""

import polars as pl

from d_dolar.statistics._board_trajectory import board_trajectory, lead_trajectory
from d_dolar.statistics._lead_choices import _solve_opening_lead
from d_dolar.statistics._seats import (
    CARD_RANK_TO_INT,
    OPPOSITE,
    RANK_TO_CARD,
    STRAIN_TO_TRUMP,
    SUIT_TO_STRAIN,
)


def with_defence_statistics(joined: pl.LazyFrame) -> pl.DataFrame:
    """Returns joined's rows, collected, with eleven columns added:
    the four raw double-dummy trajectory primitives (lead_tricks,
    trajectory_leader, trajectory_seats, trajectory_tricks), the
    four raw opening-lead-choice primitives (lead_choices,
    lead_choice_defender_tricks, lead_matters,
    recorded_lead_defender_tricks), and the three statistics
    derived from the first four (d_dolar, dropped_before_dummy,
    dropped_over_dummy). Each board's one necessary
    lead_trajectory solve, one necessary board_trajectory solve,
    and one necessary _solve_opening_lead solve each run once, not
    twice, even though several derived columns reduce over them."""
    collected = joined.collect()

    lead_tricks_values: list[list[int] | None] = []
    d_dolar_values: list[int | None] = []
    trajectory_leader_values: list[str | None] = []
    trajectory_seats_values: list[list[str] | None] = []
    trajectory_tricks_values: list[list[int] | None] = []
    dropped_before_dummy_values: list[int | None] = []
    dropped_over_dummy_values: list[int | None] = []
    lead_choices_values: list[list[str] | None] = []
    lead_choice_defender_tricks_values: list[list[int] | None] = []
    lead_matters_values: list[bool | None] = []
    recorded_lead_defender_tricks_values: list[int | None] = []

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

        solved = _solve_opening_lead(hands, declarer, contract)
        if solved is None:
            lead_choices_values.append(None)
            lead_choice_defender_tricks_values.append(None)
            lead_matters_values.append(None)
            recorded_lead_defender_tricks_values.append(None)
        else:
            suit, rank, equals, score = solved
            cards = [SUIT_TO_STRAIN[s] + RANK_TO_CARD[r] for s, r in zip(suit, rank)]
            lead_choices_values.append(cards)
            lead_choice_defender_tricks_values.append(list(score))
            lead_matters_values.append(len(set(score)) > 1)

            effective_lead = lead if lead else (play.split("_")[0] if play else None)
            matched: int | None = None
            if effective_lead:
                lead_suit = STRAIN_TO_TRUMP[effective_lead[0]]
                lead_rank = CARD_RANK_TO_INT[effective_lead[1]]
                for s, r, eq, sc in zip(suit, rank, equals, score):
                    if s == lead_suit and (r == lead_rank or eq & (1 << lead_rank)):
                        matched = sc
                        break
            recorded_lead_defender_tricks_values.append(matched)

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
        pl.Series("lead_choices", lead_choices_values, dtype=pl.List(pl.String)),
        pl.Series(
            "lead_choice_defender_tricks",
            lead_choice_defender_tricks_values,
            dtype=pl.List(pl.Int64),
        ),
        pl.Series("lead_matters", lead_matters_values, dtype=pl.Boolean),
        pl.Series(
            "recorded_lead_defender_tricks",
            recorded_lead_defender_tricks_values,
            dtype=pl.Int64,
        ),
    )
