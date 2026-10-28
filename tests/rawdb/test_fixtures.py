import csv
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def _rows(name: str) -> list[dict[str, str]]:
    with (FIXTURES / name).open(newline="") as f:
        return list(csv.DictReader(f))


def test_boards_fixture_has_empty_rawscore_with_tricks_made() -> None:
    row = next(r for r in _rows("boards.csv") if r["BoardUID"] == "1499299")
    assert row["RawScoreNS"] == ""
    assert row["TricksMade"] == "12"


def test_boards_fixture_has_claim_with_no_rawscore_or_lead() -> None:
    row = next(r for r in _rows("boards.csv") if r["BoardUID"] == "946801")
    assert row["Claim"] == "10"
    assert row["RawScoreNS"] == ""
    assert row["Lead"] == ""


def test_boards_fixture_has_doubled_contract() -> None:
    row = next(r for r in _rows("boards.csv") if r["BoardUID"] == "1400200")
    assert row["Contract"] == "4DX"


def test_boards_fixture_has_all_pass_with_empty_declarer() -> None:
    row = next(r for r in _rows("boards.csv") if r["BoardUID"] == "1117730")
    assert row["Contract"] == "AP"
    assert row["Declarer"] == ""


def test_hands_fixture_has_a_void_suit() -> None:
    row = next(r for r in _rows("hands.csv") if r["HandUID"] == "1")
    assert ".." in row["Hands"]


def test_deals_fixture_has_the_void_hand_with_no_matching_board() -> None:
    row = next(r for r in _rows("deals.csv") if r["HandUID"] == "1")
    assert row["DealUID"] == "602297"
    board_deal_uids = {r["DealUID"] for r in _rows("boards.csv")}
    assert row["DealUID"] not in board_deal_uids


def test_events_fixture_has_empty_location_and_date() -> None:
    row = next(
        r for r in _rows("events.csv") if r["EventUID"] == "251" and r["MatchID"] == "47"
    )
    assert row["EventLocation"] == ""
    assert row["MatchDate"] == ""
