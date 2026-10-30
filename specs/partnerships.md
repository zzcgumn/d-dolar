# Partnerships

The contract `d_dolar.analysis.partnerships` implements:
discovering which partnerships exist in a dataset, and how many
boards each pair played together — unlike every function in
`d_dolar.reports.pairings`, which requires the caller to already
know the two exact names to query for.

## Behaviour & invariants

### What `enumerate_partnerships` computes

`d_dolar.analysis.partnerships.enumerate_partnerships(joined,
min_boards=1, normalize=True, aliases=None)` takes a `pl.LazyFrame`
shaped like `d_dolar.rawdb.loader.load_joined_boards`'s return
value, and returns a `pl.DataFrame` with columns `player_a`,
`player_b` (alphabetically canonical order, so the same two people
are always one row regardless of which seats/roles they occupied
across different boards) and `boards_together` (an int count),
filtered to `boards_together >= min_boards`, sorted descending by
`boards_together`.

Counts every board where the two sat as partners in either
seat-pair (`North`+`South` or `East`+`West`, either order) —
declaring boards, defending boards, and all-pass boards
(`Declarer` null) all count. This is a strictly broader notion than
`d_dolar.reports.pairings.partnership_defended_boards`'s, which only
counts boards where the named pair was defending;
`enumerate_partnerships` deliberately does not reuse that filter. A
row with a null seat name is dropped, never treated as a pair.

A pure Polars aggregation — no `dds3` call, and the input stays
lazy until the final internal `.collect()`.

### `normalize` and `aliases`

`aliases`, if given, is matched against the *raw* name and applied
*first*, before normalization — a human-curated remapping (e.g.
`{"KOVACS GYORGY DR": "KOVACS GYORGY"}`) so a caller can paste names
straight out of
`d_dolar.analysis.name_similarity.likely_duplicate_names`'s output
without separately normalizing the alias dict. This is the *only*
mechanism by which two genuinely-different-looking names are ever
merged — never automatic, never driven by a similarity score
directly (see `specs/name-similarity.md`).

`normalize` (default `True`) then case/whitespace-folds every name
(`str.strip().casefold()`, applied via Polars string expressions) —
including whatever an alias substituted in — so e.g. `"Jane Smith"`
and `"JANE SMITH"` are always counted as one partnership. This is
lossless and safe to default on, unlike `aliases`: folding case and
whitespace can never conflate two different real people the way a
spelling-similarity merge could. `normalize=False` restores raw,
exact-string grouping, matching `specs/partnership-d-dolar-report.md`'s
own exact-match posture for callers who explicitly want it.

## Out of scope

- Changing `d_dolar.reports.pairings`'s existing functions or any
  of the three existing `partnership_*` report modules — all stay
  exact-match, unchanged; see `specs/partnership-d-dolar-report.md`.
- Automatic merging of names by similarity score alone — see
  `specs/name-similarity.md`.
- A CLI — returns a `DataFrame` for further programmatic/notebook
  use, matching `d_dolar.analysis.defence_statistics`'s own
  posture.
- A new `d_dolar.rawdb.validate.check_invariants` check.

---
last-updated: 2026-10-30
related-plans: partnerships
