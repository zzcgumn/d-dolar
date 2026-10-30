# Partnership D-dolar report

The contract `d_dolar.reports.partnership_d_dolar` implements:
aggregating the D-dolar base statistic (`specs/d-dolar.md`) across
every board a named two-player partnership defended, plus each
player's aggregate with every other partner they appear with in the
data.

## Behaviour & invariants

### What the report computes

Given two player names, three summaries, each shaped
`{"boards_defended": int, "boards_judged": int, "boards_optimal": int,
"boards_suboptimal": int, "d_dolar_rate": float | None}`:

- **Partnership**: boards where the two named players sat together as
  partners (`North`+`South` or `East`+`West`, either order) *and* were
  defending — `Declarer` held by the other pair. Boards where the
  named pair is declaring, where only one of the two names appears, or
  an all-pass board (`Declarer` null), are excluded entirely, not
  counted as zero.
- **Each player's "other partners"**: the same shape, for one named
  player, over every board where they **personally made the opening
  lead** while defending with any partner except the other named
  player — not merely every board where they were on the defending
  side, since `d_dolar_base` only ever judges the one specific seat
  that led. `exclude_partner` applied to this role-aware query is what
  makes the partnership figure and the two per-player figures partition
  a player's "as leader" boards rather than overlapping; without it, a
  board already counted in the partnership summary would also inflate
  "other partners."

`boards_judged` counts boards `d_dolar_base` judges: a recorded
`Lead`, or, when `Lead` is absent, a recorded `Play` whose first
card is used as the lead (`d_dolar_base` returns `0` or `1`);
`boards_defended - boards_judged` is boards with neither. `d_dolar_rate` is `boards_optimal / boards_judged`,
or `None` when `boards_judged == 0` — never a `ZeroDivisionError`.

The report does not filter or group by opponent identity: it
aggregates over every board the partnership (or player) defended,
against whoever the data happens to show them facing.

### Name matching

Exact, case-sensitive string match against `boards.csv`'s `North`/
`East`/`South`/`West` columns. No normalization — trimming,
case-folding, punctuation tolerance, or alias resolution are all out
of scope (see below).

### CLI

`d-dolar-partnership-report --rawdb-dir DIR "PLAYER A" "PLAYER B"`
(`[project.scripts]` in `pyproject.toml`) prints the three summaries as
plain text. The library functions
(`partnership_d_dolar_summary`/`player_d_dolar_summary`/
`two_player_d_dolar_report`) return plain `dict`s; formatting is the
CLI's job only.

## Out of scope

- The other two sibling defence statistics.
- A per-opponent breakdown (grouping results by who was faced) — the
  report is deliberately opponent-agnostic.
- Fuzzy or normalized player-name matching.
- A CLI framework beyond the standard library's `argparse`.
- Caching or memoizing `d_dolar_base` across repeated calls on the same
  board.
- Validating or normalizing the upstream `Declarer` casing bug —
  `d_dolar.rawdb.validate.check_invariants`'s job, not this report's.

---
last-updated: 2026-10-30
related-plans: partnership-d-dolar-report, second-defender-tricks-lost, board-trajectory-columns
