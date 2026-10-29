# Defence statistics frame

The contract `d_dolar.analysis.defence_statistics` implements: putting
all three double-dummy-based defence statistics side by side for every
board in a frame, so their relationship to each other can be analyzed
across many boards at once. Unlike every `d_dolar.reports.*` module,
this is not a filtered report for a named partnership — it's a
composable building block over whatever rows the caller already has.

## Behaviour & invariants

### What `with_defence_statistics` computes

`d_dolar.analysis.defence_statistics.with_defence_statistics(joined)`
takes a `pl.LazyFrame` shaped like
`d_dolar.rawdb.loader.load_joined_boards`'s return value, and returns
a `pl.DataFrame` with the same rows plus three columns:

- `d_dolar` — `d_dolar.statistics.d_dolar.d_dolar_base`'s result for
  that row.
- `dropped_before_dummy` —
  `d_dolar.statistics.leader_tricks_lost_after_lead.leader_tricks_lost_after_lead`'s
  result: tricks dropped by the defender who WAS on lead.
- `dropped_over_dummy` —
  `d_dolar.statistics.second_defender_tricks_lost.second_defender_tricks_lost`'s
  result: tricks dropped by the defender who was NOT on lead.

Each is nullable, independently, per its own underlying statistic's
`None` conditions (`specs/d-dolar.md`,
`specs/second-defender-tricks-lost.md`,
`specs/leader-tricks-lost-after-lead.md`). The three columns are
**not** null-correlated with each other: `d_dolar` needs only a
recorded `Lead` to be non-null, while both drop columns need the full
`Play`, and real RawDB boards exist with one present and not the other
in either direction — a board can have `Lead` but no `Play` (`d_dolar`
present, both drops `None`), or, rarer, `Play` but no `Lead` (`d_dolar`
`None`, both drops present).

Input is a `pl.LazyFrame`, collected internally (the per-row
Python/dds3 computation can't stay lazy); output is a `pl.DataFrame`,
the honest representation of the now-materialized result, not
re-lazified.

### How it avoids doubling the double-dummy work

Both drop columns are derived from one call to
`d_dolar.statistics._board_trajectory.board_trajectory` per row, not
from calling
`second_defender_tricks_lost`/`leader_tricks_lost_after_lead` directly
(which would each independently re-run the same
`dds3.analyse_play_pbn` call). See
`specs/second-defender-tricks-lost.md` and
`specs/leader-tricks-lost-after-lead.md` for `board_trajectory` itself.

## Out of scope

- Filtering by player or partnership — compose with
  `d_dolar.reports.pairings`'s existing filters beforehand if a subset
  is wanted; this function operates on whatever rows it's given.
- A CLI — this returns a `DataFrame` for further programmatic or
  notebook use, not a printed report.
- Caching, parallelism, or batching of the per-row `dds3` calls for
  large-scale runs — a known, documented performance characteristic,
  not solved here.
- A new `d_dolar.rawdb.validate.check_invariants` check.

---
last-updated: 2026-10-29
related-plans: defence-statistics-frame
