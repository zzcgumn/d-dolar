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

Via `endplay.dds.analyse_play` (`endplay`, a PyPI package that vendors
its own build of DDS — currently 2.9.0, independent of the `DD_<seat>_
<strain>` figures already in `hands.csv`, which come from
`bridge-deals-ingest`'s own `endplay` call). `analyse_play(deal, [lead])`
returns the double-dummy trick count for declarer's side both before and
after the lead is played; the lead is optimal exactly when those two
numbers are equal. This is a position-specific double-dummy solve — not
derivable from `hands.csv`'s whole-table `DD_<seat>_<strain>` columns
alone, which only give the result *before* anything is played.

A heavier option — vendoring `dds-bridge/dds` itself (tag `v3.1.1`) as a
git submodule, built with Bazel, for its own first-party `dds3` Python
module — was drafted (`plans/add-dds3-dependency.md`) and deliberately
deferred: `endplay` already does the job with a plain pip dependency, no
new build toolchain. Revisit that plan only if real evidence (a
correctness mismatch, a missing capability, or a performance problem)
shows `endplay`/DDS 2.9.0 insufficient.

**A known rough edge, worked around rather than fixed upstream**:
`endplay`'s own `SolvedPlay.__getitem__` mishandles negative indices
(`len(self) - i` instead of `len(self) + i`), so `result[-1]` raises
`IndexError` instead of returning the last element.
`d_dolar.statistics.d_dolar` avoids this by materializing
`analyse_play`'s result to a plain list and indexing forward from it.

## Out of scope

- The other two double-dummy-based defence statistics this package will
  eventually compute.
- Aggregating `d_dolar_base` across many boards, or any caching across
  repeated evaluations of the same board.
- Validating `declarer`/`contract` against a known domain before use —
  malformed input raises (`KeyError`) rather than being silently
  tolerated; `d_dolar.rawdb.validate.check_invariants` is where domain
  checks on RawDB data belong.

---
last-updated: 2026-10-28
related-plans: none (direct implementation, no make-plan/make-tasks run for this change)
