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


_TRIVIAL_DEAL = (
    "N:AKQJT98765432... .AKQJT98765432.. ..AKQJT98765432. ...AKQJT98765432"
)


def test_lead_trajectory_missing_declarer_returns_none() -> None:
    from d_dolar.statistics._board_trajectory import lead_trajectory

    assert lead_trajectory(_TRIVIAL_DEAL, None, "3N", "DA", None) is None


def test_lead_trajectory_missing_contract_returns_none() -> None:
    from d_dolar.statistics._board_trajectory import lead_trajectory

    assert lead_trajectory(_TRIVIAL_DEAL, "E", "", "DA", None) is None


def test_lead_trajectory_both_lead_and_play_missing_returns_none() -> None:
    from d_dolar.statistics._board_trajectory import lead_trajectory

    assert lead_trajectory(_TRIVIAL_DEAL, "E", "3N", "", "") is None


def test_lead_trajectory_card_not_held_by_leader_returns_none() -> None:
    from d_dolar.statistics._board_trajectory import lead_trajectory

    # declarer=E -> leader=South, who holds only diamonds in the
    # trivial deal. HA belongs to East, not South.
    assert lead_trajectory(_TRIVIAL_DEAL, "E", "3N", "HA", None) is None


def test_lead_trajectory_uses_lead_even_when_it_disagrees_with_play() -> None:
    from d_dolar.statistics._board_trajectory import lead_trajectory

    # declarer=E -> leader=South, who holds only diamonds (DA..D2).
    # play's first card (D2) differs from lead (DA); lead must win,
    # and play's garbage tail is never even inspected.
    with_conflicting_play = lead_trajectory(
        _TRIVIAL_DEAL, "E", "3N", "DA", "D2_not_a_real_play"
    )
    without_play = lead_trajectory(_TRIVIAL_DEAL, "E", "3N", "DA", None)
    assert with_conflicting_play is not None
    assert with_conflicting_play == without_play


def test_lead_trajectory_falls_back_to_plays_first_card_when_lead_absent() -> None:
    from d_dolar.statistics._board_trajectory import lead_trajectory

    # BoardUID 946801: Declarer=E, Contract=3D, Lead empty, Play
    # starts H4. Leader (South) holds H4. Confirmed directly via
    # dds3.analyse_play_pbn this session: [10, 10].
    board = _row("boards.csv", "BoardUID", "946801")
    hand = _row("hands.csv", "HandUID", "135387")
    assert board["Lead"] == ""
    result = lead_trajectory(
        hand["Hands"], board["Declarer"], board["Contract"], board["Lead"], board["Play"]
    )
    assert result == [10, 10]
