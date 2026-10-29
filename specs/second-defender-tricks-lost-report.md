# Second-defender-tricks-lost report

The contract `d_dolar.reports.partnership_second_defender_tricks_lost`
implements: aggregating the second-defender-tricks-lost base statistic
(`specs/second-defender-tricks-lost.md`) across every board a named
two-player partnership defended, plus each player's aggregate with
every other partner they appear with in the data. It mirrors
`specs/partnership-d-dolar-report.md` exactly, except for the summary
shape (see below), since the per-board statistic there is a
`0`/`1`/`None` judgement and here is an unbounded non-negative integer.

## Behaviour & invariants

### What the report computes

Given two player names, three summaries, each shaped
`{"boards_defended": int, "boards_judged": int, "total_tricks_lost":
int, "average_tricks_lost": float | None}`:

- **Partnership**: boards where the two named players sat together as
  partners and were defending — identical filter to
  `specs/partnership-d-dolar-report.md`'s partnership summary
  (`d_dolar.reports.pairings.partnership_defended_boards`, shared by
  both reports).
- **Each player's "other partners"**: the same shape, for one named
  player, over every board where they were defending *and did not make
  the opening lead* with any partner except the other named player.
  Unlike the partnership summary, this is **not** simply "every board
  the player defended minus the named partner's" — a board where the
  player personally made the opening lead is excluded even with no
  `exclude_partner` collision, because on that board the player wasn't
  "the second defender" at all. This mirrors the fixed
  opening-lead-misattribution bug in
  `d_dolar.reports.partnership_d_dolar.player_d_dolar_summary`: both
  reports now use a role-aware filter
  (`d_dolar.reports.pairings.player_as_leader_boards` there,
  `player_as_other_defender_boards` here) rather than "player was
  anywhere on the defending side".

`boards_judged` counts boards where `second_defender_tricks_lost`
didn't return `None`; `average_tricks_lost` is
`total_tricks_lost / boards_judged`, or `None` when
`boards_judged == 0` — never a `ZeroDivisionError`.

The report does not filter or group by opponent identity, same as
`specs/partnership-d-dolar-report.md`.

### Name matching

Exact, case-sensitive string match — identical to
`specs/partnership-d-dolar-report.md`.

### CLI

`d-dolar-second-defender-report --rawdb-dir DIR "PLAYER A" "PLAYER B"`
(`[project.scripts]` in `pyproject.toml`) prints the three summaries as
plain text, same style as `d-dolar-partnership-report`. The library
functions
(`partnership_second_defender_summary`/`player_second_defender_summary`/
`two_player_second_defender_report`) return plain `dict`s; formatting
is the CLI's job only.

## Out of scope

- The other two sibling defence statistics' reports.
- A per-opponent breakdown, fuzzy or normalized player-name matching, a
  CLI framework beyond `argparse`, caching — same posture as
  `specs/partnership-d-dolar-report.md`.
- A unified multi-statistic report or CLI spanning D-dolar and this
  statistic together — each keeps its own dedicated report module and
  CLI entry point; a combined view is future work only if asked.

---
last-updated: 2026-10-29
related-plans: second-defender-tricks-lost
