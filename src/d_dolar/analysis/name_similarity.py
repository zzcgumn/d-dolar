"""Assigning a similarity score to player names, and flagging
likely-duplicate names for human review -- never used to merge
anything automatically. See d_dolar.analysis.partnerships'
`aliases` parameter for the actual, human-curated merge
mechanism."""

import difflib
import itertools

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
    North/East/South/West across `joined`, deduplicates by
    normalize_name first (pure case/whitespace variants are
    already unambiguously identical, never reported as
    "candidates"), then runs name_similarity over every remaining
    distinct pair -- O(n^2) over the DEDUPLICATED distinct-name
    count, not the row count -- and returns every pair scoring >=
    threshold, sorted descending by score. Candidates for human
    review ONLY; never merges anything. The O(n^2) cost is a known,
    accepted characteristic for this first cut; a cheap pre-filter
    (e.g. only compare names sharing a token) is a natural future
    improvement, not built here."""
    names_frame = pl.concat(
        [joined.select(pl.col(column).alias("name")) for column in _SEAT_COLUMNS]
    )
    names = names_frame.filter(pl.col("name").is_not_null()).unique().collect()["name"].to_list()

    seen: dict[str, str] = {}
    for name in names:
        seen.setdefault(normalize_name(name), name)
    distinct_names = list(seen.values())

    candidates = [
        (a, b, score)
        for a, b in itertools.combinations(distinct_names, 2)
        if (score := name_similarity(a, b)) >= threshold
    ]
    candidates.sort(key=lambda candidate: candidate[2], reverse=True)
    return candidates
