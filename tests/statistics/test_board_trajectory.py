import csv
from pathlib import Path

FIXTURES = Path(__file__).parents[1] / "reports" / "fixtures"


def _row(name: str, key: str, value: str) -> dict[str, str]:
    with (FIXTURES / name).open(newline="") as f:
        return next(r for r in csv.DictReader(f) if r[key] == value)


def test_missing_declarer_returns_none() -> None:
    from d_dolar.statistics._board_trajectory import board_trajectory

    deal = "N:AKQJT98765432... .AKQJT98765432.. ..AKQJT98765432. ...AKQJT98765432"
    assert board_trajectory(deal, None, "3N", "H5_H2_HA_H9") is None


def test_missing_play_returns_none() -> None:
    from d_dolar.statistics._board_trajectory import board_trajectory

    deal = "N:AKQJT98765432... .AKQJT98765432.. ..AKQJT98765432. ...AKQJT98765432"
    assert board_trajectory(deal, "E", "3N", "") is None


def test_corrupted_play_returns_none() -> None:
    from d_dolar.statistics._board_trajectory import board_trajectory

    board = _row("boards.csv", "BoardUID", "583742")
    hand = _row("hands.csv", "HandUID", "83133")
    # Same corrupted-play construction already used to test
    # second_defender_tricks_lost's/leader_tricks_lost_after_lead's
    # corruption handling: trick 1 and trick 2, then trick 1's
    # cards again.
    corrupted_play = "HA_HJ_H2_H9_C2_CQ_CK_C7_HA_HJ_H2_H9"
    result = board_trajectory(
        hand["Hands"], board["Declarer"], board["Contract"], corrupted_play
    )
    assert result is None


def test_returns_leader_seats_and_tricks_matching_both_statistics() -> None:
    from d_dolar.statistics._board_trajectory import board_trajectory
    from d_dolar.statistics._seats import OPPOSITE

    board = _row("boards.csv", "BoardUID", "408320")
    hand = _row("hands.csv", "HandUID", "58343")
    trajectory = board_trajectory(
        hand["Hands"], board["Declarer"], board["Contract"], board["Play"]
    )
    assert trajectory is not None
    leader, seats, tricks = trajectory

    assert leader == "S"  # HEGYI ANDRAS led (board["Lead"] == "H6")
    assert len(seats) == len(board["Play"].split("_"))

    second_defender = OPPOSITE[leader]
    dropped_over_dummy = sum(
        tricks[i] - tricks[i - 1]
        for i in range(1, len(tricks))
        if seats[i - 1] == second_defender
    )
    dropped_before_dummy = sum(
        tricks[i] - tricks[i - 1] for i in range(2, len(tricks)) if seats[i - 1] == leader
    )
    # Cross-checked against second_defender_tricks_lost's/
    # leader_tricks_lost_after_lead's own already-confirmed results
    # for this exact board.
    assert dropped_over_dummy == 1
    assert dropped_before_dummy == 0
