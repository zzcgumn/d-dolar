from pathlib import Path

import polars as pl
import pytest

from d_dolar.rawdb.loader import load_boards, load_deals, load_events, load_hands

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def frames() -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    return (
        load_events(FIXTURES).collect(),
        load_deals(FIXTURES).collect(),
        load_hands(FIXTURES).collect(),
        load_boards(FIXTURES).collect(),
    )


def test_clean_fixtures_have_no_violations(
    frames: tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame, pl.DataFrame],
) -> None:
    from d_dolar.rawdb.validate import check_invariants

    events, deals, hands, boards = frames
    assert check_invariants(events, deals, hands, boards) == []


def test_detects_dd_trick_out_of_range(
    frames: tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame, pl.DataFrame],
) -> None:
    from d_dolar.rawdb.validate import check_invariants

    events, deals, hands, boards = frames
    hands = hands.with_columns(
        pl.when(pl.col("HandUID") == 215330).then(99).otherwise(pl.col("DD_W_N")).alias("DD_W_N")
    )
    violations = check_invariants(events, deals, hands, boards)
    assert any("DD_W_N" in v for v in violations)


def test_detects_tricks_made_out_of_range(
    frames: tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame, pl.DataFrame],
) -> None:
    from d_dolar.rawdb.validate import check_invariants

    events, deals, hands, boards = frames
    boards = boards.with_columns(
        pl.when(pl.col("BoardUID") == 1499299)
        .then(97)
        .otherwise(pl.col("TricksMade"))
        .alias("TricksMade")
    )
    violations = check_invariants(events, deals, hands, boards)
    assert any("TricksMade" in v for v in violations)


def test_detects_hcp_sum_mismatch(
    frames: tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame, pl.DataFrame],
) -> None:
    from d_dolar.rawdb.validate import check_invariants

    events, deals, hands, boards = frames
    hands = hands.with_columns(
        pl.when(pl.col("HandUID") == 215330)
        .then(pl.col("N_Total_HCP") + 1)
        .otherwise(pl.col("N_Total_HCP"))
        .alias("N_Total_HCP")
    )
    violations = check_invariants(events, deals, hands, boards)
    assert any("Total_HCP" in v for v in violations)


def test_detects_length_sum_not_thirteen(
    frames: tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame, pl.DataFrame],
) -> None:
    from d_dolar.rawdb.validate import check_invariants

    events, deals, hands, boards = frames
    hands = hands.with_columns(
        pl.when(pl.col("HandUID") == 215330)
        .then(pl.col("N_Length_S") + 1)
        .otherwise(pl.col("N_Length_S"))
        .alias("N_Length_S")
    )
    violations = check_invariants(events, deals, hands, boards)
    assert any("sum to 13" in v for v in violations)


def test_detects_duplicate_board_uid(
    frames: tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame, pl.DataFrame],
) -> None:
    from d_dolar.rawdb.validate import check_invariants

    events, deals, hands, boards = frames
    boards = pl.concat([boards, boards.head(1)])
    violations = check_invariants(events, deals, hands, boards)
    assert any("BoardUID" in v and "duplicate" in v.lower() for v in violations)


def test_detects_orphaned_deal_uid(
    frames: tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame, pl.DataFrame],
) -> None:
    from d_dolar.rawdb.validate import check_invariants

    events, deals, hands, boards = frames
    boards = boards.with_columns(
        pl.when(pl.col("BoardUID") == 1499299)
        .then(999999999)
        .otherwise(pl.col("DealUID"))
        .alias("DealUID")
    )
    violations = check_invariants(events, deals, hands, boards)
    assert any("DealUID" in v for v in violations)


def test_detects_orphaned_hand_uid(
    frames: tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame, pl.DataFrame],
) -> None:
    from d_dolar.rawdb.validate import check_invariants

    events, deals, hands, boards = frames
    deals = deals.with_columns(
        pl.when(pl.col("DealUID") == 637157)
        .then(999999999)
        .otherwise(pl.col("HandUID"))
        .alias("HandUID")
    )
    violations = check_invariants(events, deals, hands, boards)
    assert any("HandUID" in v for v in violations)


def test_detects_orphaned_event_uid(
    frames: tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame, pl.DataFrame],
) -> None:
    from d_dolar.rawdb.validate import check_invariants

    events, deals, hands, boards = frames
    deals = deals.with_columns(
        pl.when(pl.col("DealUID") == 637157)
        .then(999999999)
        .otherwise(pl.col("EventUID"))
        .alias("EventUID")
    )
    violations = check_invariants(events, deals, hands, boards)
    assert any("EventUID" in v for v in violations)


def test_detects_vulnerability_outside_known_domain(
    frames: tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame, pl.DataFrame],
) -> None:
    from d_dolar.rawdb.validate import check_invariants

    events, deals, hands, boards = frames
    deals = deals.with_columns(
        pl.when(pl.col("DealUID") == 637157)
        .then(pl.lit("Q"))
        .otherwise(pl.col("Vulnerability").cast(pl.String))
        .cast(pl.Categorical())
        .alias("Vulnerability")
    )
    violations = check_invariants(events, deals, hands, boards)
    assert any("Vulnerability" in v for v in violations)


def test_detects_dealer_outside_known_domain(
    frames: tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame, pl.DataFrame],
) -> None:
    from d_dolar.rawdb.validate import check_invariants

    events, deals, hands, boards = frames
    hands = hands.with_columns(
        pl.when(pl.col("HandUID") == 215330)
        .then(pl.lit("Q"))
        .otherwise(pl.col("Dealer").cast(pl.String))
        .cast(pl.Categorical())
        .alias("Dealer")
    )
    violations = check_invariants(events, deals, hands, boards)
    assert any("Dealer" in v for v in violations)


def test_detects_declarer_outside_known_domain(
    frames: tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame, pl.DataFrame],
) -> None:
    from d_dolar.rawdb.validate import check_invariants

    events, deals, hands, boards = frames
    boards = boards.with_columns(
        pl.when(pl.col("BoardUID") == 1400200)
        .then(pl.lit("s"))
        .otherwise(pl.col("Declarer").cast(pl.String))
        .cast(pl.Categorical())
        .alias("Declarer")
    )
    violations = check_invariants(events, deals, hands, boards)
    assert any("Declarer" in v for v in violations)
