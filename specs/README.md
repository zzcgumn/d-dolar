# specs/

The design record: the contract each statistic implements, and why, written
so a coding agent — human or machine — can change behaviour correctly. A spec
is read *before* behaviour changes; it is not a summary written after the
fact.

- [`rawdb-import.md`](rawdb-import.md) — how a `bridge-deals-ingest` RawDB
  directory gets into a typed, validated Polars frame.
- [`d-dolar.md`](d-dolar.md) — the D-dolar base statistic (opening-lead
  optimality).
- [`dds3-dependency.md`](dds3-dependency.md) — the vendored DDS 3.1.1
  Python module, how it's built, and what's guaranteed about it.
- [`partnership-d-dolar-report.md`](partnership-d-dolar-report.md) —
  aggregating D-dolar across a named two-player defending partnership,
  and each player's aggregate with everyone else.
- [`second-defender-tricks-lost.md`](second-defender-tricks-lost.md) —
  the second sibling defence statistic: tricks cost by every card the
  non-leading defender played.
- [`second-defender-tricks-lost-report.md`](second-defender-tricks-lost-report.md)
  — aggregating it across a named two-player defending partnership,
  mirroring `partnership-d-dolar-report.md`.
- [`leader-tricks-lost-after-lead.md`](leader-tricks-lost-after-lead.md)
  — the third sibling defence statistic: tricks cost by the opening
  leader's own cards after their lead.
- [`leader-tricks-lost-after-lead-report.md`](leader-tricks-lost-after-lead-report.md)
  — aggregating it across a named two-player defending partnership,
  mirroring the other two reports.
- [`defence-statistics-frame.md`](defence-statistics-frame.md) —
  combining all three sibling statistics into one per-board frame,
  for analyzing how they interact.
- [`lead-matters.md`](lead-matters.md) — whether a board's opening
  lead was the only choice that mattered, using `dds3`'s
  `solve_board_pbn` to evaluate every legal lead at once.
