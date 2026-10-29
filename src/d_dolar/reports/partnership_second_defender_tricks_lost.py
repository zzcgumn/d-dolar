"""Aggregate second-defender-tricks-lost across a two-player defending
partnership."""

import argparse
from pathlib import Path

import polars as pl

from d_dolar.rawdb.loader import load_joined_boards
from d_dolar.reports.pairings import (
    partnership_defended_boards,
    player_as_other_defender_boards,
)
from d_dolar.statistics.second_defender_tricks_lost import second_defender_tricks_lost


def _summarize(defended: pl.DataFrame) -> dict[str, int | float | None]:
    boards_defended = defended.height
    results = [
        second_defender_tricks_lost(row["Hands"], row["Declarer"], row["Contract"], row["Play"])
        for row in defended.iter_rows(named=True)
    ]
    judged = [r for r in results if r is not None]
    boards_judged = len(judged)
    total_tricks_lost = sum(judged)
    return {
        "boards_defended": boards_defended,
        "boards_judged": boards_judged,
        "total_tricks_lost": total_tricks_lost,
        "average_tricks_lost": total_tricks_lost / boards_judged if boards_judged else None,
    }


def partnership_second_defender_summary(
    joined: pl.LazyFrame, player_a: str, player_b: str
) -> dict[str, int | float | None]:
    """Runs second_defender_tricks_lost over partnership_defended_boards'
    rows. See _summarize for the returned shape."""
    defended = partnership_defended_boards(joined, player_a, player_b).collect()
    return _summarize(defended)


def player_second_defender_summary(
    joined: pl.LazyFrame, player: str, exclude_partner: str | None = None
) -> dict[str, int | float | None]:
    """Runs second_defender_tricks_lost over
    player_as_other_defender_boards' rows. Same summary shape as
    partnership_second_defender_summary."""
    defended = player_as_other_defender_boards(joined, player, exclude_partner).collect()
    return _summarize(defended)


def two_player_second_defender_report(
    joined: pl.LazyFrame, player_a: str, player_b: str
) -> dict[str, dict[str, int | float | None]]:
    """{"partnership": ..., "player_a_other_partners": ...,
    "player_b_other_partners": ...}."""
    return {
        "partnership": partnership_second_defender_summary(joined, player_a, player_b),
        "player_a_other_partners": player_second_defender_summary(
            joined, player_a, exclude_partner=player_b
        ),
        "player_b_other_partners": player_second_defender_summary(
            joined, player_b, exclude_partner=player_a
        ),
    }


def _print_summary(summary: dict[str, int | float | None]) -> None:
    for key, value in summary.items():
        print(f"  {key}: {value}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Second-defender-tricks-lost report for a two-player defending partnership."
    )
    parser.add_argument("--rawdb-dir", type=Path, required=True)
    parser.add_argument("player_a")
    parser.add_argument("player_b")
    args = parser.parse_args()

    joined = load_joined_boards(args.rawdb_dir)
    report = two_player_second_defender_report(joined, args.player_a, args.player_b)

    print("Partnership")
    _print_summary(report["partnership"])
    print(f"{args.player_a} (other partners)")
    _print_summary(report["player_a_other_partners"])
    print(f"{args.player_b} (other partners)")
    _print_summary(report["player_b_other_partners"])
