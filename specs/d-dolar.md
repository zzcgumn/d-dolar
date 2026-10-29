# D-dolar (base statistic)

The contract `d_dolar.statistics.d_dolar` implements: whether a single
board's opening lead was double-dummy optimal. This is the base case of
the D-dolar statistic; the two sibling defence statistics this package
will eventually add are out of scope here.

## Behaviour & invariants

### What `d_dolar_base` computes

`d_dolar.statistics.d_dolar.d_dolar_base(hands, declarer, contract, lead)`
takes the board's full deal (`Hands`, PBN format), the declaring seat
(`Declarer`), the contract (`Contract`, e.g. `"4DX"`), and the card that
was actually led (`Lead`) — the same strings `d_dolar.rawdb.loader`
produces. It returns:

- `1` if the lead cost the defence nothing: with double-dummy-optimal
  play by everyone from that point on, declarer's side makes exactly as
  many tricks as the board's double-dummy table says they can (no more).
- `0` if the lead was legal but not optimal: it let declarer make at
  least one more trick than double-dummy optimal.
- `None` if there is no lead to judge: an all-pass board (`declarer` is
  empty) or a board whose opening lead was never recorded (`lead` is
  empty). Falsy `contract` is treated the same way, defensively.

The opening leader is derived, not taken as input: it is the seat to
`declarer`'s left, i.e. the next seat clockwise in the standard
`N -> E -> S -> W -> N` rotation. The trump strain is `contract[1]` (the
character after the level digit — `S`/`H`/`D`/`C`/`N`, `N` meaning
notrump), ignoring any doubling annotation after it.

### How it is computed

Via `dds3.analyse_play_pbn` (see `specs/dds3-dependency.md`) — DDS's own
first-party Python module, vendored as a git submodule at tag `v3.1.1`
and built with Bazel, independent of the `DD_<seat>_<strain>` figures
already in `hands.csv` (which come from `bridge-deals-ingest`'s own
`endplay`/DDS 2.9.0 call). `analyse_play_pbn(hands, play=lead,
trump=..., first=...)` returns the double-dummy trick count for
declarer's side both before and after the lead is played (`result["tricks"]`,
a 2-element list for a single-card `play`); the lead is optimal exactly
when those two numbers are equal. This is a position-specific
double-dummy solve — not derivable from `hands.csv`'s whole-table
`DD_<seat>_<strain>` columns alone, which only give the result *before*
anything is played.

This package originally used `endplay` (a PyPI package that vendors its
own, older build of DDS — 2.9.0) for this, since it was a plain pip
dependency with no new build toolchain. Switched to `dds3` once this
statistic's actual need — the trick count at a specific point *after*
a card is played, not just the whole-table result — turned out to be
exactly the evidence `plans/add-dds3-dependency.md` had said to wait
for. Cross-checked directly against the same real boards this statistic
was first tested against: both DDS builds agree exactly (see
`tests/statistics/test_d_dolar.py`'s fixture-based cases).

## Out of scope

- The other two double-dummy-based defence statistics this package
  computes — see `specs/second-defender-tricks-lost.md` and
  `specs/leader-tricks-lost-after-lead.md`.
- Aggregating `d_dolar_base` across many boards — see
  `specs/partnership-d-dolar-report.md`.
- Caching across repeated evaluations of the same board.
- Validating `declarer`/`contract` against a known domain before use —
  malformed input raises (`KeyError`) rather than being silently
  tolerated; `d_dolar.rawdb.validate.check_invariants` is where domain
  checks on RawDB data belong.

---
last-updated: 2026-10-29
related-plans: none (direct implementation, no make-plan/make-tasks run for this change); partnership-d-dolar-report, leader-tricks-lost-after-lead
