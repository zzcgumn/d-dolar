"""Clustering likely-duplicate names from a candidate-pairs list,
and picking a canonical spelling per cluster -- the logic behind
scripts/dedup_sweep.py, factored out so it is tested and reusable
on its own. See d_dolar.analysis.name_similarity for where the
candidate pairs themselves come from, and
d_dolar.analysis.partnerships' `aliases` parameter for where
canonical_aliases' output is meant to be used."""

import polars as pl

_SEAT_COLUMNS = ("North", "East", "South", "West")


def name_frequencies(joined: pl.LazyFrame) -> dict[str, int]:
    """Real occurrence count of every non-null raw name across
    North/East/South/West in `joined` -- used by canonical_aliases
    to pick the most-frequently-recorded spelling per merge
    group."""
    counts = (
        pl.concat([joined.select(pl.col(column).alias("name")) for column in _SEAT_COLUMNS])
        .filter(pl.col("name").is_not_null())
        .group_by("name")
        .len()
        .collect()
    )
    return dict(zip(counts["name"].to_list(), counts["len"].to_list()))


class _UnionFind:
    def __init__(self) -> None:
        self._parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        self._parent.setdefault(x, x)
        root = x
        while self._parent[root] != root:
            root = self._parent[root]
        while self._parent[x] != root:
            self._parent[x], x = root, self._parent[x]
        return root

    def union(self, a: str, b: str) -> None:
        root_a, root_b = self.find(a), self.find(b)
        if root_a != root_b:
            self._parent[root_a] = root_b


def cluster_names(pairs: list[tuple[str, str, float]]) -> list[list[str]]:
    """Connected-components clustering (union-find) over a
    candidate-pairs list shaped like candidate_pairs'/
    likely_duplicate_names' own return type -- the score is
    accepted but ignored (the caller has already thresholded).
    Every name that appears in `pairs` ends up in exactly one
    returned cluster; two pairs that share no name stay in
    separate clusters. Transitive: if A pairs with B and B pairs
    with C, A/B/C end up in one cluster even though A and C never
    appear together directly -- the exact shape that produced a
    real, documented 427-name over-merged cluster in this
    project's own data (see docs/dedup_sweep.md)."""
    union_find = _UnionFind()
    for name_a, name_b, _score in pairs:
        union_find.union(name_a, name_b)

    clusters: dict[str, list[str]] = {}
    for name in union_find._parent:
        clusters.setdefault(union_find.find(name), []).append(name)
    return list(clusters.values())


def canonical_aliases(clusters: list[list[str]], frequency: dict[str, int]) -> dict[str, str]:
    """For every cluster with more than one member, the member
    with the highest frequency.get(member, 0) becomes canonical.
    Ties (equal frequency) are broken by `max`'s own tie-break on
    the `(frequency, member)` key: whichever member sorts LATER
    alphabetically wins (e.g. "Bob" over "Alice") -- not, as
    "alphabetical" could otherwise be read, whichever sorts first.
    This matches this session's own real full-sweep run. Returns
    {other_member: canonical} for every other member of that
    cluster -- directly usable as enumerate_partnerships' `aliases`
    argument. A cluster with only one member contributes nothing (a
    name is never aliased to itself)."""
    aliases: dict[str, str] = {}
    for members in clusters:
        if len(members) <= 1:
            continue
        canonical = max(members, key=lambda member: (frequency.get(member, 0), member))
        for member in members:
            if member != canonical:
                aliases[member] = canonical
    return aliases
