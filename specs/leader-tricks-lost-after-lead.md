# Leader tricks lost after lead (base statistic)

The contract `d_dolar.statistics.leader_tricks_lost_after_lead`
implements: how many tricks the opening leader's OWN cards cost the
defence, summed across every card they play AFTER their opening lead,
compared to double-dummy-optimal play at each point. This is the third
and final of the three double-dummy-based defence statistics this
package computes; D-dolar (`specs/d-dolar.md`) judges the opening lead
itself, and `specs/second-defender-tricks-lost.md` judges the other
defender's cards.

## Behaviour & invariants

### What `leader_tricks_lost_after_lead` computes

`d_dolar.statistics.leader_tricks_lost_after_lead.leader_tricks_lost_after_lead(hands, declarer, contract, play)`
takes the same four inputs as `second_defender_tricks_lost`. It
returns a non-negative integer: the sum, over every card played by the
opening leader AFTER their initial lead, of the increase in declarer's
double-dummy-achievable trick count that one card caused, compared to
double-dummy-optimal continuation from the position immediately
before it. `0` means the leader played every one of their later cards
double-dummy optimally -- regardless of whether their opening lead
itself was optimal, which this statistic deliberately does not score
(see below).

`None` under the same conditions as `second_defender_tricks_lost`:
`declarer`, `contract`, or `play` is falsy, or the recorded `play`
fails the card-ownership check. If the leader's seat never plays again
after the opening lead (the recorded `play` ends during or right after
the first trick), the result is `0`, not `None` -- there is nothing
further to judge, which is not an error.

### How the opening lead's own cost is excluded

This statistic shares its entire trajectory computation with
`second_defender_tricks_lost` via
`d_dolar.statistics._board_trajectory.board_trajectory` (itself built
on `d_dolar.statistics._trick_play`'s lower-level card-attribution and
trick-winner engine) -- the same `dds3.analyse_play_pbn` call, the
same `tricks[i]` trajectory, the same per-card
`tricks[i] - tricks[i - 1]` diff, run once per board regardless of how
many sibling statistics need it. The one structural difference between
the two statistics: the summation here starts at `tricks` index
`i = 2`, not `i = 1`. Index `i = 1` is always the very first card
played in the whole deal, which is always the opening leader's own
lead (the first seat `attribute_cards` returns is always the leader)
-- and `d_dolar_base` already judges that exact card. Starting at
`i = 2` instead of `i = 1` is what keeps this statistic and D-dolar
from scoring the same card twice.

## Out of scope

- The opening lead itself -- `specs/d-dolar.md`'s subject.
- The other defender's cards -- `specs/second-defender-tricks-lost.md`'s
  subject.
- Declarer's or dummy's own misplays -- same reasoning as
  `specs/second-defender-tricks-lost.md`: these only ever decrease the
  tracked trick count, so the per-card-cost formula naturally excludes
  them.
- Validating suit-following legality (revokes) beyond the
  card-ownership check already required for correctness.
- Aggregating this statistic across many boards -- see
  `specs/leader-tricks-lost-after-lead-report.md`.
- Caching across repeated evaluations of the same board.
- A new `d_dolar.rawdb.validate.check_invariants` check for any RawDB
  data defect -- same posture as the other two statistics.

---
last-updated: 2026-10-29
related-plans: leader-tricks-lost-after-lead, defence-statistics-frame
