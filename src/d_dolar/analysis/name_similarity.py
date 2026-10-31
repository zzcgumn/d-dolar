"""Assigning a similarity score to player names, and flagging
likely-duplicate names for human review -- never used to merge
anything automatically. See d_dolar.analysis.partnerships'
`aliases` parameter for the actual, human-curated merge
mechanism."""

import difflib

import polars as pl

_SEAT_COLUMNS = ("North", "East", "South", "West")


def normalize_name(name: str) -> str:
    """Cheap, lossless case/whitespace canonicalization -- the
    plain-Python equivalent of
    d_dolar.analysis.partnerships.enumerate_partnerships' Polars
    expression. Kept as a separate, parallel implementation (not
    shared code) since Polars string expressions and plain Python
    string methods are different APIs with no clean single
    implementation."""
    return name.strip().casefold()


def name_similarity(a: str, b: str) -> float:
    """A similarity SCORE in [0, 1] between two names, via Python's
    standard library (no new dependency). Symmetric. Never used to
    merge anything automatically -- see module docstring."""
    return difflib.SequenceMatcher(None, normalize_name(a), normalize_name(b)).ratio()


def candidate_pairs(
    names: list[str], start: int, stop: int, threshold: float
) -> list[tuple[str, str, float]]:
    """Pairs (names[p], names[q]) for p in [start, stop), q in
    (p, len(names)) -- the upper-triangular slice of the full
    all-pairs sweep over `names` that chunk [start, stop) owns.

    This splits an O(n^2) all-pairs comparison into independent
    chunks without double-counting work or needing a merge/de-dup
    step afterwards: every unordered pair across the whole `names`
    list is produced by exactly one chunk, because each
    name is compared only against names at a STRICTLY LATER index in
    the same fixed list -- never against the full list. (Comparing a
    chunk against the full list instead was tried and rejected: it
    double-counts every cross-chunk pair, once from each side, and
    double-counts within-chunk pairs too, since a chunk is itself a
    subset of the full list it would be compared against.) Chunk
    results can therefore be concatenated directly.

    `names` must be a fixed, deterministically-ordered list across
    calls meant to be combined -- see distinct_names. Raises
    ValueError if start < 0, stop > len(names), or start > stop."""
    n = len(names)
    if start < 0 or stop > n or start > stop:
        raise ValueError(f"invalid chunk [{start}, {stop}) for {n} names")

    out: list[tuple[str, str, float]] = []
    for p in range(start, stop):
        a = names[p]
        for q in range(p + 1, n):
            b = names[q]
            score = name_similarity(a, b)
            if score >= threshold:
                out.append((a, b, score))
    return out


def distinct_names(joined: pl.LazyFrame) -> list[str]:
    """Collects the distinct non-null name universe from
    North/East/South/West across `joined`, deduplicating by
    normalize_name (first-seen representative wins). Returned sorted
    by normalize_name(name) -- a FIXED, deterministic order two calls
    against the same data always agree on, which candidate_pairs'
    chunk index ranges depend on for correctness: Polars' own
    `.unique().collect()` order is not a documented stable-order
    guarantee to rely on across runs/processes."""
    names_frame = pl.concat(
        [joined.select(pl.col(column).alias("name")) for column in _SEAT_COLUMNS]
    )
    names = names_frame.filter(pl.col("name").is_not_null()).unique().collect()["name"].to_list()

    seen: dict[str, str] = {}
    for name in names:
        seen.setdefault(normalize_name(name), name)
    return sorted(seen.values(), key=normalize_name)


def likely_duplicate_names(
    joined: pl.LazyFrame, threshold: float = 0.85
) -> list[tuple[str, str, float]]:
    """Collects the distinct non-null name universe from
    North/East/South/West across `joined` (via distinct_names),
    then runs candidate_pairs over the whole list in one chunk --
    every pair scoring >= threshold, sorted descending by score.
    Candidates for human review ONLY; never merges anything. See
    candidate_pairs for how this same O(n^2) sweep can be split
    into independent chunks instead of run as one call."""
    names = distinct_names(joined)
    candidates = candidate_pairs(names, 0, len(names), threshold)
    candidates.sort(key=lambda candidate: candidate[2], reverse=True)
    return candidates
