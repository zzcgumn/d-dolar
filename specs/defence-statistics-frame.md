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
`d_dolar.rawdb.loader.load_joined_boards`'s return value, and
returns a `pl.DataFrame` with the same rows plus seven columns: four
raw double-dummy trajectory columns, and the three statistics
already derived from them.

### The four raw columns

- `lead_tricks` (`pl.List(pl.Int64)`) — the `[before, after]`
  trick-count pair
  `d_dolar.statistics._board_trajectory.lead_trajectory` computes
  across the opening-lead card (see `specs/d-dolar.md` for which
  card that is, and the `None` conditions).
- `trajectory_leader` (`pl.String`), `trajectory_seats`
  (`pl.List(pl.String)`), `trajectory_tricks` (`pl.List(pl.Int64)`)
  — the `(leader, seats, tricks)` triple
  `d_dolar.statistics._board_trajectory.board_trajectory` computes
  over the board's full recorded `Play`.

Each is nullable independently, exactly under `lead_trajectory`'s or
`board_trajectory`'s own existing `None` conditions — no new
`None`-condition is introduced; these columns materialize values
each primitive already computes internally, so a new statistic can
be derived from them without triggering a new `dds3` call or
reading `_board_trajectory`/`_trick_play`.

### The three derived columns

- `d_dolar` — `1 if lead_tricks[1] == lead_tricks[0] else 0`, `None`
  if `lead_tricks` is `None`. The same result
  `d_dolar.statistics.d_dolar.d_dolar_base` returns for that row.
- `dropped_before_dummy` — tricks dropped by the defender who WAS on
  lead, summed over `trajectory_tricks`/`trajectory_seats` from
  index 2 onward where the seat is the leader. Same result as
  `d_dolar.statistics.leader_tricks_lost_after_lead.leader_tricks_lost_after_lead`.
- `dropped_over_dummy` — tricks dropped by the defender who was NOT
  on lead, summed the same way from index 1 where the seat is the
  second defender. Same result as
  `d_dolar.statistics.second_defender_tricks_lost.second_defender_tricks_lost`.

Each nullable, independently, per its own underlying statistic's
`None` conditions (`specs/d-dolar.md`,
`specs/second-defender-tricks-lost.md`,
`specs/leader-tricks-lost-after-lead.md`).

Input is a `pl.LazyFrame`, collected internally (the per-row
Python/dds3 computation can't stay lazy); output is a
`pl.DataFrame`, the honest representation of the now-materialized
result, not re-lazified.

### Null correlation between `lead_tricks` and the trajectory columns

`d_dolar`/`lead_tricks` and the two drop/trajectory columns are not,
in general, null-correlated: a board can have `Lead` but no `Play`
(`lead_tricks` present, `trajectory_*` and both drops `None` —
`BoardUID 1499299`). The other direction is more precise than it
used to be: since `lead_trajectory` now falls back to `Play`'s first
card when `Lead` is absent (`specs/d-dolar.md`), a board with `Play`
but no `Lead` no longer makes `lead_tricks` null on that account
alone — `lead_tricks`'s and the trajectory columns' null-ness
instead become *correlated* through `Play`'s own validity in that
case, since both `lead_trajectory`'s and `board_trajectory`'s
card-ownership checks test the exact same first card against the
exact same seat's full hand when `Lead` is absent, so they succeed
or fail together (`BoardUID 946801`: `Lead` empty, `Play` present
and valid — `lead_tricks` and all three trajectory columns are
present together, not one without the other). The still-
demonstrated **independent** direction remains `Lead` present with
`Play` absent (`BoardUID 1499299`).

### How it avoids doubling the double-dummy work

Both drop columns are derived from one call to
`d_dolar.statistics._board_trajectory.board_trajectory` per row, and
`d_dolar` is derived from one call to
`d_dolar.statistics._board_trajectory.lead_trajectory` per row — not
from calling
`second_defender_tricks_lost`/`leader_tricks_lost_after_lead`/
`d_dolar_base` directly, each of which would independently re-run
the same `dds3.analyse_play_pbn` call. See
`specs/second-defender-tricks-lost.md`,
`specs/leader-tricks-lost-after-lead.md`, and `specs/d-dolar.md` for
these primitives themselves.

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
last-updated: 2026-10-30
related-plans: defence-statistics-frame, board-trajectory-columns
