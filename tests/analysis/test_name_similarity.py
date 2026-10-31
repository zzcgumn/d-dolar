from pathlib import Path

import polars as pl
import pytest

from d_dolar.rawdb.loader import load_joined_boards

FIXTURES = Path(__file__).parents[1] / "reports" / "fixtures"


def test_normalize_name_strips_and_casefolds() -> None:
    from d_dolar.analysis.name_similarity import normalize_name

    assert normalize_name("  Jane Smith  ") == "jane smith"
    assert normalize_name("JANE SMITH") == "jane smith"


def test_name_similarity_is_one_for_identical_names() -> None:
    from d_dolar.analysis.name_similarity import name_similarity

    assert name_similarity("Jane Smith", "Jane Smith") == 1.0


def test_name_similarity_is_symmetric() -> None:
    from d_dolar.analysis.name_similarity import name_similarity

    assert name_similarity("KOVACS GYORGY", "KOVACS GYORGY DR") == name_similarity(
        "KOVACS GYORGY DR", "KOVACS GYORGY"
    )


def test_name_similarity_true_positive_from_real_data() -> None:
    # BoardUID 583742 and 142234, both paired with NOVOTTNY ERNO --
    # almost certainly the same person with an inconsistently
    # recorded "DR" suffix. Confirmed via difflib this session.
    from d_dolar.analysis.name_similarity import name_similarity

    score = name_similarity("KOVACS GYORGY", "KOVACS GYORGY DR")
    assert score == pytest.approx(0.897, abs=0.001)


def test_name_similarity_real_false_positive_shaped_pair_from_real_data() -> None:
    # BoardUID 408320's real East-West partnership -- same surname,
    # different people. Confirmed via difflib this session: scores
    # clearly lower than the true positive above, but still high
    # enough to demonstrate why a similarity score alone must never
    # auto-merge names.
    from d_dolar.analysis.name_similarity import name_similarity

    score = name_similarity("WELKER JACINT", "WELKER KATALIN")
    assert score == pytest.approx(0.741, abs=0.001)


def test_likely_duplicate_names_finds_the_real_near_duplicate() -> None:
    from d_dolar.analysis.name_similarity import likely_duplicate_names

    joined = load_joined_boards(FIXTURES)
    candidates = likely_duplicate_names(joined)

    assert len(candidates) == 1
    a, b, score = candidates[0]
    assert {a, b} == {"KOVACS GYORGY", "KOVACS GYORGY DR"}
    assert score == pytest.approx(0.897, abs=0.001)


def test_likely_duplicate_names_excludes_the_real_distinct_partnership() -> None:
    from d_dolar.analysis.name_similarity import likely_duplicate_names

    joined = load_joined_boards(FIXTURES)
    candidates = likely_duplicate_names(joined)

    pairs = [{a, b} for a, b, _ in candidates]
    assert {"WELKER JACINT", "WELKER KATALIN"} not in pairs


def test_distinct_names_dedupes_and_sorts_deterministically() -> None:
    from d_dolar.analysis.name_similarity import distinct_names, normalize_name

    joined = pl.LazyFrame(
        {
            "North": ["Jane Smith", "JANE SMITH "],
            "East": ["Ann Lee", None],
            "South": ["Bob Jones", "Carol King"],
            "West": [None, "Dan Fox"],
        }
    )

    result = distinct_names(joined)

    assert len(result) == 5
    assert [normalize_name(n) for n in result] == sorted(
        {"jane smith", "ann lee", "bob jones", "carol king", "dan fox"}
    )
    assert distinct_names(joined) == result  # deterministic across calls


def test_distinct_names_drops_nulls() -> None:
    from d_dolar.analysis.name_similarity import distinct_names

    joined = pl.LazyFrame(
        {
            "North": ["Jane Smith", None],
            "East": [None, None],
            "South": ["Bob Jones", None],
            "West": [None, None],
        }
    )

    result = distinct_names(joined)

    assert None not in result
    assert set(result) == {"Jane Smith", "Bob Jones"}


def test_candidate_pairs_matches_known_threshold_boundary() -> None:
    from d_dolar.analysis.name_similarity import candidate_pairs, name_similarity

    names = ["Jane Smith", "Jane Smyth", "Bob Jones"]
    score = name_similarity("Jane Smith", "Jane Smyth")

    assert candidate_pairs(names, 0, len(names), score + 0.01) == []
    assert candidate_pairs(names, 0, len(names), score - 0.01) == [
        ("Jane Smith", "Jane Smyth", score)
    ]


def test_candidate_pairs_full_range_matches_brute_force_combinations() -> None:
    import itertools

    from d_dolar.analysis.name_similarity import candidate_pairs, name_similarity

    names = ["Jane Smith", "JANE SMYTH", "Bob Jones", "Bob Jonas", "Carol King"]
    threshold = 0.5

    expected = sorted(
        (a, b, score)
        for a, b in itertools.combinations(names, 2)
        if (score := name_similarity(a, b)) >= threshold
    )
    actual = sorted(candidate_pairs(names, 0, len(names), threshold))

    assert actual == expected


def test_candidate_pairs_chunked_concatenation_matches_single_chunk() -> None:
    from d_dolar.analysis.name_similarity import candidate_pairs

    names = [
        "Jane Smith",
        "JANE SMYTH",
        "Bob Jones",
        "Bob Jonas",
        "Carol King",
        "Carol Kingley",
    ]
    threshold = 0.5
    mid = len(names) // 2

    single = candidate_pairs(names, 0, len(names), threshold)
    chunked = candidate_pairs(names, 0, mid, threshold) + candidate_pairs(
        names, mid, len(names), threshold
    )

    assert sorted(single) == sorted(chunked)
    assert len(chunked) == len(set(chunked))


def test_candidate_pairs_rejects_invalid_start_stop() -> None:
    from d_dolar.analysis.name_similarity import candidate_pairs

    names = ["A", "B", "C"]

    with pytest.raises(ValueError):
        candidate_pairs(names, -1, 3, 0.85)
    with pytest.raises(ValueError):
        candidate_pairs(names, 0, 4, 0.85)
    with pytest.raises(ValueError):
        candidate_pairs(names, 2, 1, 0.85)
