"""Load a RawDB directory, validate it, and print a summary.

Usage: python examples/rawdb_validate.py <rawdb_dir>
"""

import sys
from pathlib import Path

from d_dolar.rawdb.loader import load_boards, load_deals, load_events, load_hands
from d_dolar.rawdb.validate import check_invariants


def main(rawdb_dir: Path) -> int:
    events = load_events(rawdb_dir).collect()
    deals = load_deals(rawdb_dir).collect()
    hands = load_hands(rawdb_dir).collect()
    boards = load_boards(rawdb_dir).collect()

    for name, df in (("events", events), ("deals", deals), ("hands", hands), ("boards", boards)):
        print(f"{name}: {df.height} rows")
        for col in df.columns:
            null_count = df[col].null_count()
            if null_count:
                print(f"  {col}: {null_count / df.height:.1%} null")

    violations = check_invariants(events, deals, hands, boards)
    if violations:
        print(f"{len(violations)} invariant violation(s):")
        for v in violations:
            print(f"  - {v}")
        return 1

    print("No invariant violations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1])))
