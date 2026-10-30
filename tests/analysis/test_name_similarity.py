from pathlib import Path

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
