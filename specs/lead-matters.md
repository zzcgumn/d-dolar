# Lead matters

The contract `d_dolar.statistics._lead_choices`/
`d_dolar.statistics.lead_matters` implements: whether a board's
opening lead was the only choice that mattered — whether every legal
opening lead gives the same double-dummy outcome, or whether the
leader's actual choice could have changed the result. Unlike
`specs/d-dolar.md`, which judges only the one card that was actually
led, this evaluates the full space of legal opening leads at once.

## Behaviour & invariants

### What `lead_choices` computes

`d_dolar.statistics._lead_choices.lead_choices(hands, declarer,
contract)` takes the board's full deal, declaring seat, and contract
— no `Lead`/`Play` — and returns `(cards, defender_tricks)`: every
distinct opening-lead choice available to the derived opening leader
(`dds3`'s own equivalence grouping — strategically identical cards
collapse to one entry), as this package's card-string notation (e.g.
`"H9"`), paired with the double-dummy trick count for each.

**`defender_tricks` counts the DEFENDING side's tricks, not
declarer's** — the opposite convention from every other statistic in
this package (`d_dolar_base`, `lead_trajectory`, `board_trajectory`,
`second_defender_tricks_lost`, `leader_tricks_lost_after_lead`), which
all report declarer's-side trick counts via `analyse_play_pbn`'s
`result["tricks"]`. This is the single easiest thing to get backwards
when working with this module.

`None` only if `declarer` or `contract` is falsy. This needs no `Lead`
or `Play` at all, so it is non-null on a strictly larger set of boards
than `d_dolar_base`/`lead_trajectory`.

### How it is computed

Via `dds3.solve_board_pbn(hands, trump=..., first=...)` (see
`specs/dds3-dependency.md`) — the same `trump`/`first` encoding as
`analyse_play_pbn`, but it solves the position *before* any card is
played, returning a dict whose `cards` field counts the distinct
strategic choices after DDS's own equivalence-grouping, and whose
`suit`/`rank`/`equals`/`score` tuples are always length 13, padded
with zeros past index `cards`. `suit` uses the same `0=S 1=H 2=D 3=C`
encoding as `STRAIN_TO_TRUMP` (minus notrump, which can't describe a
card); `rank` is `2`..`9` literal, `10=T 11=J 12=Q 13=K 14=A` —
decoded to this package's card-string notation via the
`SUIT_TO_STRAIN`/`RANK_TO_CARD` dicts in `d_dolar.statistics._seats`.

### What `recorded_lead_defender_tricks` computes

`d_dolar.statistics._lead_choices.recorded_lead_defender_tricks(hands,
declarer, contract, lead, play)` locates the board's *actual* opening
lead — `lead`, falling back to `play`'s first card when `lead` is
absent (the same precedence `lead_trajectory` applies;
`specs/d-dolar.md`) — within `lead_choices`' equivalence groups, and
returns that group's `defender_tricks` value.

**Its `None` domain is narrower than `lead_choices`'** — it also needs
an effective lead, and that card must actually be held by the leader
— matching `lead_trajectory`'s/`d_dolar_base`'s domain instead, even
though it's built on the same underlying `solve_board_pbn` call.
`None` if: `declarer`/`contract` is falsy; neither `lead` nor `play`
supplies a usable card; or the effective lead isn't one of the
leader's legal cards (the same RawDB defect `lead_trajectory` already
guards against, see `specs/rawdb-import.md`) — this case is detected
implicitly, by the effective lead's card falling through every
equivalence group with no match, not by an explicit ownership
pre-check.

### How the equivalence-group match works

A card belongs to a `solve_board_pbn` result's group `i` if either it
*is* that group's own representative (`suit[i]`/`rank[i]` match
exactly), or its rank bit is set in that group's `equals` bitmask:
`equals[i] & (1 << rank)`, where the bit position is the card's own
rank integer directly, scoped to the group's own suit (a card is never
equivalent to one of a different suit) — confirmed empirically against
real `dds3` output, not assumed from documentation.

### What `lead_matters` computes

`d_dolar.statistics.lead_matters.lead_matters(hands, declarer,
contract)` is a thin public reduction over `lead_choices`, mirroring
how `d_dolar_base` reduces `lead_trajectory`: `True` if at least two of
the returned `defender_tricks` values differ (some choice of opening
lead would have changed the outcome), `False` if every choice gives
the same outcome. Shares `lead_choices`' `None` domain.

### Relationship to D-dolar

These two computations stay genuinely independent — `lead_choices`/
`lead_matters` never call `lead_trajectory`/`d_dolar_base`, and vice
versa — but they describe the same real position, so two cross-checks
hold wherever both sides are non-null (verified against real `dds3`
output on `BoardUID 1499299` and `BoardUID 408320`, see
`tests/analysis/test_defence_statistics.py`):

- `recorded_lead_defender_tricks == 13 - lead_tricks[1]` (total tricks
  in a deal is always 13, so the defenders' tricks and declarer's
  tricks for the SAME recorded lead, computed via two different `dds3`
  entry points, must sum to it).
- `lead_matters is False` implies `d_dolar_base`'s result is `1` — if
  no possible lead could have done better, the actual lead can't have
  been suboptimal.

## Out of scope

- Expanding the `equals` bitmask into a stored list of every
  individual equivalent card — equivalence means an identical score by
  definition, so this adds no new information; it's used only
  internally by `recorded_lead_defender_tricks`'s matching.
- Reconciling the two independent computations into one shared code
  path — the cross-checks above are consistency assertions, not a
  merge.
- Aggregating `lead_matters`/`recorded_lead_defender_tricks` across
  many boards into a partnership-style report — a natural follow-up,
  not implemented here.
- A new `d_dolar.rawdb.validate.check_invariants` check.
- Caching across repeated evaluations of the same board.

---
last-updated: 2026-10-30
related-plans: lead-matters
