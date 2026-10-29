import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parents[2]
FIXTURES = Path(__file__).parents[1] / "reports" / "fixtures"
SCRIPT = REPO_ROOT / "examples" / "defence_statistics_sample.py"


def test_sample_larger_than_available_rows_uses_the_whole_fixture_set() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURES)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    # Only 11 boards exist, fewer than the default sample size of 100 --
    # the whole fixture set is used instead of raising. With all 11
    # rows sampled (not a random subset), the d_dolar numbers are
    # deterministic: 6 of the 9 judged boards (946801/1117730 have no
    # recorded Lead) have an optimal opening lead.
    assert "Sampled 11 board(s) out of 11." in result.stdout
    assert "d_dolar == 1 (optimal opening lead) on 6/9 judged board(s) (66.7%)." in result.stdout


def test_explicit_sample_size_smaller_than_available_rows() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURES), "3"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Sampled 3 board(s) out of 11." in result.stdout
