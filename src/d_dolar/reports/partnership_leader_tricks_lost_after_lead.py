"""Aggregate leader-tricks-lost-after-lead across a two-player
defending partnership."""

import argparse
from pathlib import Path

import polars as pl

from d_dolar.rawdb.loader import load_joined_boards
from d_dolar.reports.pairings import partnership_defended_boards, player_as_leader_boards
from d_dolar.statistics.leader_tricks_lost_after_lead import leader_tricks_lost_after_lead


def _summarize(defended: pl.DataFrame) -> dict[str, int | float | None]:
    boards_defended = defended.height
    results = [
        leader_tricks_lost_after_lead(row["Hands"], row["Declarer"], row["Contract"], row["Play"])
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


def partnership_leader_tricks_lost_after_lead_summary(
    joined: pl.LazyFrame, player_a: str, player_b: str
) -> dict[str, int | float | None]:
    """Runs leader_tricks_lost_after_lead over partnership_defended_boards'
    rows. See _summarize for the returned shape."""
    defended = partnership_defended_boards(joined, player_a, player_b).collect()
    return _summarize(defended)


def player_leader_tricks_lost_after_lead_summary(
    joined: pl.LazyFrame, player: str, exclude_partner: str | None = None
) -> dict[str, int | float | None]:
    """Runs leader_tricks_lost_after_lead over player_as_leader_boards'
    rows -- the same role-aware filter player_d_dolar_summary already
    uses, since this statistic's subject is the same opening leader.
    Same summary shape as partnership_leader_tricks_lost_after_lead_summary."""
    defended = player_as_leader_boards(joined, player, exclude_partner).collect()
    return _summarize(defended)


def two_player_leader_tricks_lost_after_lead_report(
    joined: pl.LazyFrame, player_a: str, player_b: str
) -> dict[str, dict[str, int | float | None]]:
    """{"partnership": ..., "player_a_other_partners": ...,
    "player_b_other_partners": ...}."""
    return {
        "partnership": partnership_leader_tricks_lost_after_lead_summary(joined, player_a, player_b),
        "player_a_other_partners": player_leader_tricks_lost_after_lead_summary(
            joined, player_a, exclude_partner=player_b
        ),
        "player_b_other_partners": player_leader_tricks_lost_after_lead_summary(
            joined, player_b, exclude_partner=player_a
        ),
    }


def _print_summary(summary: dict[str, int | float | None]) -> None:
    for key, value in summary.items():
        print(f"  {key}: {value}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Leader-tricks-lost-after-lead report for a two-player defending partnership."
    )
    parser.add_argument("--rawdb-dir", type=Path, required=True)
    parser.add_argument("player_a")
    parser.add_argument("player_b")
    args = parser.parse_args()

    joined = load_joined_boards(args.rawdb_dir)
    report = two_player_leader_tricks_lost_after_lead_report(joined, args.player_a, args.player_b)

    print("Partnership")
    _print_summary(report["partnership"])
    print(f"{args.player_a} (other partners)")
    _print_summary(report["player_a_other_partners"])
    print(f"{args.player_b} (other partners)")
    _print_summary(report["player_b_other_partners"])
