import polars as pl


def test_name_frequencies_counts_non_null_occurrences_across_seats() -> None:
    from d_dolar.analysis.dedup import name_frequencies

    joined = pl.LazyFrame(
        {
            "North": ["Jane Smith", None, None],
            "East": ["Bob Jones", "Bob Jones", None],
            "South": [None, "Jane Smith", "Carol King"],
            "West": [None, None, "Bob Jones"],
        }
    )

    result = name_frequencies(joined)

    assert result == {"Jane Smith": 2, "Bob Jones": 3, "Carol King": 1}


def test_cluster_names_groups_transitively_connected_pairs() -> None:
    from d_dolar.analysis.dedup import cluster_names

    pairs = [("A", "B", 0.9), ("B", "C", 0.86)]

    clusters = cluster_names(pairs)

    assert sorted(sorted(c) for c in clusters) == [["A", "B", "C"]]


def test_cluster_names_keeps_disjoint_pairs_in_separate_clusters() -> None:
    # Not a true singleton (a name with zero edges) -- cluster_names
    # only takes `pairs`, so it has no way to observe a name that
    # never appears in any pair; this is the closest reachable case.
    from d_dolar.analysis.dedup import cluster_names

    pairs = [("A", "B", 0.9), ("C", "D", 0.87)]

    clusters = cluster_names(pairs)

    assert sorted(sorted(c) for c in clusters) == [["A", "B"], ["C", "D"]]


def test_canonical_aliases_picks_highest_frequency_member() -> None:
    from d_dolar.analysis.dedup import canonical_aliases

    clusters = [["Jane Smith", "JANE SMITH DR", "J Smith"]]
    frequency = {"Jane Smith": 2, "JANE SMITH DR": 5, "J Smith": 1}

    aliases = canonical_aliases(clusters, frequency)

    assert aliases == {"Jane Smith": "JANE SMITH DR", "J Smith": "JANE SMITH DR"}


def test_canonical_aliases_breaks_frequency_ties_by_higher_sort_order() -> None:
    from d_dolar.analysis.dedup import canonical_aliases

    clusters = [["Alice", "Bob"]]
    frequency = {"Alice": 3, "Bob": 3}

    aliases = canonical_aliases(clusters, frequency)

    assert aliases == {"Alice": "Bob"}


def test_canonical_aliases_omits_singleton_clusters() -> None:
    from d_dolar.analysis.dedup import canonical_aliases

    clusters = [["Solo Name"], ["Jane Smith", "JANE SMITH DR"]]
    frequency = {"Solo Name": 10, "Jane Smith": 1, "JANE SMITH DR": 5}

    aliases = canonical_aliases(clusters, frequency)

    assert aliases == {"Jane Smith": "JANE SMITH DR"}
