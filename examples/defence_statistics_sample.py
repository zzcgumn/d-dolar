"""Load a RawDB directory, sample some boards at random, and report
how often the opening lead was double-dummy optimal.

Usage: python examples/defence_statistics_sample.py <rawdb_dir> [sample_size]
"""

import sys
from pathlib import Path

import polars as pl

from d_dolar.analysis.defence_statistics import with_defence_statistics
from d_dolar.rawdb.loader import load_joined_boards


def main(rawdb_dir: Path, sample_size: int) -> int:
    joined = load_joined_boards(rawdb_dir).collect()
    sample_size = min(sample_size, joined.height)
    sample = joined.sample(n=sample_size)

    result = with_defence_statistics(sample.lazy())
    judged = result.filter(pl.col("d_dolar").is_not_null())
    optimal = judged.filter(pl.col("d_dolar") == 1).height

    print(f"Sampled {sample.height} board(s) out of {joined.height}.")
    if judged.height:
        print(
            f"d_dolar == 1 (optimal opening lead) on {optimal}/{judged.height} "
            f"judged board(s) ({optimal / judged.height:.1%})."
        )
    else:
        print("No sampled board had a recorded opening lead to judge.")
    return 0


if __name__ == "__main__":
    rawdb_dir = Path(sys.argv[1])
    sample_size = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    raise SystemExit(main(rawdb_dir, sample_size))
