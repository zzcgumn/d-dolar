# Second-defender tricks lost (base statistic)

The contract `d_dolar.statistics.second_defender_tricks_lost`
implements: how many tricks the defender who did **not** make the
opening lead cost the defence, summed across every card they played,
compared to double-dummy-optimal play at each point. This is the
second of the three double-dummy-based defence statistics this package
computes; D-dolar (`specs/d-dolar.md`) is the first, and judges only
the opening lead itself.

## Behaviour & invariants

### What `second_defender_tricks_lost` computes

`d_dolar.statistics.second_defender_tricks_lost.second_defender_tricks_lost(hands, declarer, contract, play)`
takes the board's full deal (`Hands`, PBN format), the declaring seat
(`Declarer`), the contract (`Contract`), and the full card-by-card play
(`Play`, `boards.csv`'s underscore-joined sequence of every card
played, not just the opening lead `Lead`). It returns a non-negative
integer: the sum, over every card played by "the second defender" (the
defending pair's member who did not make the opening lead — the seat
opposite the opening leader), of the increase in declarer's
double-dummy-achievable trick count that one card caused, compared to
double-dummy-optimal continuation from the position immediately
before it. `0` means the second defender played every one of their
cards double-dummy optimally.

It returns `None` when there is no play to judge: `declarer`,
`contract`, or `play` is falsy, or the recorded `play` fails the
card-ownership check below. `play` is a stricter requirement than
D-dolar's `lead` — a board can have a recorded opening lead with no
full card-by-card play at all (confirmed on the full RawDB: roughly
31% of boards with a recorded `Lead` have no `Play`), so this
statistic judges strictly fewer boards than `d_dolar_base` can.

### How the second defender's cards are identified

The opening leader is `declarer`'s left-hand opponent (same derivation
as D-dolar); the second defender is the *other* member of the
defending pair — never the leader. Because the recorded `play` string
carries no seat labels (confirmed: neither this package's RawDB reader
nor DDS exposes any), which seat played each card must be derived
independently, by plain bridge trick-taking rules — not double-dummy:

- Within one trick, the four cards are played by the leader and the
  next three seats clockwise, in order.
- Which seat leads the *next* trick is whichever seat won the current
  one: the highest card of the suit led wins, unless a card of the
  trump suit was played by a seat not following suit (a ruff), in
  which case the highest trump wins. A notrump contract has no trump
  suit, so no card can ever win by ruffing.
- Each seat's remaining starting-hand cards (parsed from `hands`) are
  tracked as cards are attributed; if a card is attributed to a seat
  that doesn't actually hold it, that is treated as a corrupted or
  otherwise impossible `play` string, and `second_defender_tricks_lost`
  returns `None` for that board rather than raising. This is a
  deliberate difference from `d_dolar_base`'s "malformed `declarer`/
  `contract` raises `KeyError`" stance: a malformed `declarer`/
  `contract` is a programmer-error-shaped bad input, whereas a
  self-contradictory `Play` string is a real, rare upstream data defect
  (see `specs/rawdb-import.md`) — the same category as an all-pass
  board or an unrecorded lead, which already return `None`.

### How the per-card trick cost is computed

One call to `dds3.analyse_play_pbn`, passing the *entire* recorded
`play` (flattened, no underscores) rather than one card at a time.
`result["tricks"][i]` is the double-dummy-optimal trick count for
declarer's side after `i` cards have actually been played (`tricks[0]`
is the pre-play baseline); DDS stops appending once the result can no
longer change, so `len(tricks)` can be less than `len(cards) + 1` —
nothing is lost by this, since nothing left could change the total
anyway. For each card index `i` (1-indexed) attributed to the second
defender, `tricks[i] - tricks[i - 1]` is added to the total; this
difference is always `>= 0` for a card played by *any* defender, since
`tricks[i - 1]` already assumes double-dummy-optimal continuation by
whoever plays next — a real card can only match or fall short of that,
never beat it.

This computation — the card attribution and the one
`dds3.analyse_play_pbn` call — is shared verbatim with
`leader_tricks_lost_after_lead` via
`d_dolar.statistics._board_trajectory.board_trajectory`, which both
statistics call once per board; only the target seat and the
summation's starting index differ between them.

## Out of scope

- The opening leader's *own* subsequent (non-lead) cards during the
  defence — not scored by this statistic, nor by D-dolar. See
  `specs/leader-tricks-lost-after-lead.md`, the third sibling
  statistic.
- Declarer's or dummy's own misplays — irrelevant to a defence
  statistic, and these only ever *decrease* the tracked trick count,
  never increase it, so the per-card-cost formula naturally excludes
  them (the sum only includes cards attributed to the second
  defender's own seat) without a special case.
- Validating suit-following legality (revokes) beyond the
  card-ownership check already required for correctness — a recorded
  play is assumed otherwise legal.
- Aggregating this statistic across many boards — see
  `specs/second-defender-tricks-lost-report.md`.
- Caching across repeated evaluations of the same board.
- A new `d_dolar.rawdb.validate.check_invariants` check for either
  RawDB defect named above — documenting them is enough for now; a
  dedicated check is a candidate future improvement, not implemented
  here.

---
last-updated: 2026-10-29
related-plans: second-defender-tricks-lost, leader-tricks-lost-after-lead, defence-statistics-frame
