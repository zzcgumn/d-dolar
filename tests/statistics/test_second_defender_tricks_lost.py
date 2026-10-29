import csv
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parents[1] / "reports" / "fixtures"

_TRIVIAL_DEAL = (
    "N:AKQJT98765432... .AKQJT98765432.. ..AKQJT98765432. ...AKQJT98765432"
)


def _row(name: str, key: str, value: str) -> dict[str, str]:
    with (FIXTURES / name).open(newline="") as f:
        return next(r for r in csv.DictReader(f) if r[key] == value)


def test_parse_hands_splits_pbn_into_per_seat_card_sets() -> None:
    from d_dolar.statistics.second_defender_tricks_lost import _parse_hands

    hands = _parse_hands(_TRIVIAL_DEAL)
    assert hands["N"] == {"S" + r for r in "AKQJT98765432"}
    assert hands["E"] == {"H" + r for r in "AKQJT98765432"}
    assert hands["S"] == {"D" + r for r in "AKQJT98765432"}
    assert hands["W"] == {"C" + r for r in "AKQJT98765432"}


def test_trick_winner_highest_card_of_suit_led_wins_without_a_ruff() -> None:
    from d_dolar.statistics.second_defender_tricks_lost import _trick_winner

    assert _trick_winner(["H5", "H2", "HA", "H9"], trump_suit="S") == 2


def test_trick_winner_a_ruff_beats_any_non_trump_follow() -> None:
    from d_dolar.statistics.second_defender_tricks_lost import _trick_winner

    assert _trick_winner(["H5", "HA", "S2", "H9"], trump_suit="S") == 2


def test_trick_winner_higher_trump_beats_lower_trump() -> None:
    from d_dolar.statistics.second_defender_tricks_lost import _trick_winner

    assert _trick_winner(["H5", "S2", "S9", "H9"], trump_suit="S") == 2


def test_trick_winner_notrump_contract_never_lets_an_off_suit_card_win() -> None:
    from d_dolar.statistics.second_defender_tricks_lost import _trick_winner

    assert _trick_winner(["H5", "S9", "HA", "H2"], trump_suit=None) == 2


def test_attribute_cards_passes_leadership_to_the_trick_winner() -> None:
    from d_dolar.statistics.second_defender_tricks_lost import _attribute_cards

    hands = {
        "N": {"H5", "DA"},
        "E": {"H2", "D5"},
        "S": {"HA", "D9"},
        "W": {"H9", "D2"},
    }
    seats = _attribute_cards(
        hands, leader="N", play=["H5", "H2", "HA", "H9", "D9", "D2", "DA", "D5"], trump_suit=None
    )
    assert seats == ["N", "E", "S", "W", "S", "W", "N", "E"]


def test_attribute_cards_raises_on_a_card_not_available_to_the_attributed_seat() -> None:
    from d_dolar.statistics.second_defender_tricks_lost import _attribute_cards

    hands = {"N": {"H5"}, "E": {"H2"}, "S": {"HA"}, "W": {"H9"}}
    with pytest.raises(ValueError):
        _attribute_cards(hands, leader="N", play=["H5", "H2", "HA", "H9", "D2"], trump_suit=None)


def test_hegyi_as_second_defender_played_perfectly() -> None:
    from d_dolar.statistics.second_defender_tricks_lost import second_defender_tricks_lost

    board = _row("boards.csv", "BoardUID", "583742")
    hand = _row("hands.csv", "HandUID", "83133")
    result = second_defender_tricks_lost(
        hand["Hands"], board["Declarer"], board["Contract"], board["Play"]
    )
    assert result == 0


def test_levai_as_second_defender_cost_one_trick() -> None:
    from d_dolar.statistics.second_defender_tricks_lost import second_defender_tricks_lost

    board = _row("boards.csv", "BoardUID", "408320")
    hand = _row("hands.csv", "HandUID", "58343")
    result = second_defender_tricks_lost(
        hand["Hands"], board["Declarer"], board["Contract"], board["Play"]
    )
    assert result == 1


def test_hegyi_with_other_partner_cost_two_tricks() -> None:
    from d_dolar.statistics.second_defender_tricks_lost import second_defender_tricks_lost

    board = _row("boards.csv", "BoardUID", "512007")
    hand = _row("hands.csv", "HandUID", "72598")
    result = second_defender_tricks_lost(
        hand["Hands"], board["Declarer"], board["Contract"], board["Play"]
    )
    assert result == 2


def test_levai_with_other_partner_played_perfectly() -> None:
    from d_dolar.statistics.second_defender_tricks_lost import second_defender_tricks_lost

    board = _row("boards.csv", "BoardUID", "1313031")
    hand = _row("hands.csv", "HandUID", "188325")
    result = second_defender_tricks_lost(
        hand["Hands"], board["Declarer"], board["Contract"], board["Play"]
    )
    assert result == 0


def test_missing_declarer_returns_none() -> None:
    from d_dolar.statistics.second_defender_tricks_lost import second_defender_tricks_lost

    assert second_defender_tricks_lost(_TRIVIAL_DEAL, None, "3N", "H5_H2_HA_H9") is None


def test_missing_play_returns_none() -> None:
    from d_dolar.statistics.second_defender_tricks_lost import second_defender_tricks_lost

    assert second_defender_tricks_lost(_TRIVIAL_DEAL, "E", "3N", "") is None


def test_corrupted_play_with_a_repeated_card_returns_none() -> None:
    from d_dolar.statistics.second_defender_tricks_lost import second_defender_tricks_lost

    board = _row("boards.csv", "BoardUID", "583742")
    hand = _row("hands.csv", "HandUID", "83133")
    # Real trick 1 and trick 2 (8 cards), then trick 1's cards again --
    # every one of those 4 cards was already played and removed from its
    # seat's hand, so re-attributing them anywhere must fail the
    # ownership check -- the same shape of defect BoardUID 770156 has in
    # the real RawDB (a repeated 4-card block).
    corrupted_play = "HA_HJ_H2_H9_C2_CQ_CK_C7_HA_HJ_H2_H9"
    result = second_defender_tricks_lost(
        hand["Hands"], board["Declarer"], board["Contract"], corrupted_play
    )
    assert result is None
