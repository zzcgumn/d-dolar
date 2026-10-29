# Leader-tricks-lost-after-lead report

The contract `d_dolar.reports.partnership_leader_tricks_lost_after_lead`
implements: aggregating the leader-tricks-lost-after-lead base
statistic (`specs/leader-tricks-lost-after-lead.md`) across every
board a named two-player partnership defended, plus each player's
aggregate with every other partner they appear with in the data. It
mirrors `specs/second-defender-tricks-lost-report.md` exactly in shape
and style.

## Behaviour & invariants

### What the report computes

Given two player names, three summaries, each shaped
`{"boards_defended": int, "boards_judged": int, "total_tricks_lost":
int, "average_tricks_lost": float | None}`:

- **Partnership**: boards where the two named players sat together as
  partners and were defending -- identical filter to the other two
  statistics' partnership summaries
  (`d_dolar.reports.pairings.partnership_defended_boards`, shared by
  all three reports, unchanged).
- **Each player's "other partners"**: the same shape, for one named
  player, over every board where they personally made the opening
  lead with any partner except the other named player. This reuses
  `d_dolar.reports.pairings.player_as_leader_boards` unchanged -- the
  exact same role-aware filter `player_d_dolar_summary` already uses,
  since this statistic's subject (the opening leader) is the same
  role D-dolar judges. Unlike `specs/second-defender-tricks-lost-report.md`,
  this report needed no new `pairings.py` primitive.

`boards_judged` counts boards where `leader_tricks_lost_after_lead`
didn't return `None`; `average_tricks_lost` is
`total_tricks_lost / boards_judged`, or `None` when
`boards_judged == 0`.

### Name matching

Exact, case-sensitive string match -- identical to the other two
reports.

### CLI

`d-dolar-leader-report --rawdb-dir DIR "PLAYER A" "PLAYER B"`
(`[project.scripts]` in `pyproject.toml`) prints the three summaries as
plain text, same style as the other two reports. The library functions
return plain `dict`s; formatting is the CLI's job only.

## Out of scope

- The other two sibling defence statistics' reports.
- A per-opponent breakdown, fuzzy or normalized player-name matching, a
  CLI framework beyond `argparse`, caching -- same posture as the
  other two reports.
- A unified multi-statistic report or CLI spanning all three
  statistics -- each keeps its own dedicated report module and CLI
  entry point.
- A shared report-summary abstraction across the three statistics'
  report modules -- `_summarize`/`_print_summary`/`main()` are
  deliberately duplicated per report module, matching the existing,
  unflagged precedent between `partnership_d_dolar.py` and
  `partnership_second_defender_tricks_lost.py`.

---
last-updated: 2026-10-29
related-plans: leader-tricks-lost-after-lead
