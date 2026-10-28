import shutil
import subprocess
import sys
from pathlib import Path

import polars as pl

REPO_ROOT = Path(__file__).parents[2]
FIXTURES = Path(__file__).parent / "fixtures"
SCRIPT = REPO_ROOT / "examples" / "rawdb_validate.py"


def test_clean_fixtures_exit_zero() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURES)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "No invariant violations." in result.stdout
    assert "boards: 4 rows" in result.stdout
    # 3 of the 4 fixture boards have no RawScoreNS.
    assert "RawScoreNS: 75.0% null" in result.stdout


def test_corrupted_fixtures_exit_nonzero(tmp_path: Path) -> None:
    for name in ("events.csv", "deals.csv", "hands.csv", "boards.csv"):
        shutil.copy(FIXTURES / name, tmp_path / name)
    boards = pl.read_csv(tmp_path / "boards.csv")
    boards = boards.with_columns(
        pl.when(pl.col("BoardUID") == 1499299)
        .then(97)
        .otherwise(pl.col("TricksMade"))
        .alias("TricksMade")
    )
    boards.write_csv(tmp_path / "boards.csv")

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "TricksMade" in result.stdout
