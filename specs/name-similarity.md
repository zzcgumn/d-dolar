# Name similarity

The contract `d_dolar.analysis.name_similarity` implements:
assigning a similarity score to two player names, and using it to
flag likely-duplicate names for human review — never to merge
anything automatically.
`d_dolar.analysis.partnerships.enumerate_partnerships`'s `aliases`
parameter is the only mechanism in this package that actually
merges two names, and it is always an explicit, human-supplied
decision.

## Behaviour & invariants

### What `normalize_name` computes

`d_dolar.analysis.name_similarity.normalize_name(name)` returns
`name.strip().casefold()` — a cheap, lossless case/whitespace
canonicalization. This is the plain-Python equivalent of
`enumerate_partnerships`'s own Polars string expression; the two
are a deliberate, acknowledged duplication (different APIs, no
clean single implementation), not an oversight.

### What `name_similarity` computes

`d_dolar.analysis.name_similarity.name_similarity(a, b)` returns a
similarity score in `[0, 1]` via Python's standard library,
`difflib.SequenceMatcher(None, normalize_name(a),
normalize_name(b)).ratio()` — no new dependency. Symmetric:
`name_similarity(a, b) == name_similarity(b, a)`. `1.0` for
identical (post-normalization) names.

**Confirmed on real data** (`tests/reports/fixtures`, 11 boards, 30
distinct player names): `name_similarity("KOVACS GYORGY", "KOVACS
GYORGY DR")` scores `0.897` — the highest-scoring distinct-name
pair in that set, and a genuine real-data true positive (both
names are paired with `NOVOTTNY ERNO`, on different boards, almost
certainly the same person with an inconsistently-recorded "DR"
suffix). `name_similarity("WELKER JACINT", "WELKER KATALIN")`
scores `0.741` — the next-highest, but these are **not** the same
person: they are a real East-West partnership (`BoardUID 408320`)
who merely share a surname. This pair is the concrete reason a
similarity score must never drive an automatic merge.

### What `likely_duplicate_names` computes

`d_dolar.analysis.name_similarity.likely_duplicate_names(joined,
threshold=0.85)` collects the distinct non-null name universe from
`North`/`East`/`South`/`West` across `joined`, deduplicates by
`normalize_name` first (so pure case/whitespace variants are never
reported as "candidates" — they're already unambiguously
identical), then runs `name_similarity` over every remaining
distinct pair, returning every pair scoring `>= threshold` as
`(name_a, name_b, score)`, sorted descending by score.

Returns candidates for human review **only** — it never merges
anything itself, and nothing else in this package consumes its
output automatically. A human reviewing its result decides which
pairs (if any) are really the same person, and passes that
decision explicitly to `enumerate_partnerships`'s `aliases`
parameter.

The default `threshold=0.85` is calibrated against the real numbers
above (catches `0.897`, excludes `0.741`) — a reasonable starting
point, not a universal constant; a caller with different data
should recalibrate against their own confirmed examples the same
way.

### Performance

`O(n^2)` over the deduplicated distinct-name count (not the row
count) — a known, accepted characteristic for this first cut,
matching `d_dolar.analysis.defence_statistics`'s own
documented-not-solved per-row `dds3` cost. A cheap pre-filter (e.g.
only compare names sharing a token) is a natural future
improvement, not built here.

## Out of scope

- Automatic merging of names by similarity score alone.
- A new PyPI dependency for fuzzy matching (e.g.
  `rapidfuzz`/`jellyfish`) — `difflib` is stdlib and sufficient for
  what's confirmed so far.
- A pre-filtering/blocking optimization for the `O(n^2)` comparison.
- Any change to `d_dolar.reports.partnership_d_dolar`'s exact-match
  name matching — see `specs/partnership-d-dolar-report.md`.

---
last-updated: 2026-10-30
related-plans: partnerships
