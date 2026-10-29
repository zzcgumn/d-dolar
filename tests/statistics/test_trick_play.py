import pytest

_TRIVIAL_DEAL = (
    "N:AKQJT98765432... .AKQJT98765432.. ..AKQJT98765432. ...AKQJT98765432"
)


def test_parse_hands_splits_pbn_into_per_seat_card_sets() -> None:
    from d_dolar.statistics._trick_play import parse_hands

    hands = parse_hands(_TRIVIAL_DEAL)
    assert hands["N"] == {"S" + r for r in "AKQJT98765432"}
    assert hands["E"] == {"H" + r for r in "AKQJT98765432"}
    assert hands["S"] == {"D" + r for r in "AKQJT98765432"}
    assert hands["W"] == {"C" + r for r in "AKQJT98765432"}


def test_parse_hands_rejects_a_hands_string_with_fewer_than_four_hands() -> None:
    from d_dolar.statistics._trick_play import parse_hands

    incomplete_deal = "N:AKQJT98765432... .AKQJT98765432.. ..AKQJT98765432."
    with pytest.raises(ValueError):
        parse_hands(incomplete_deal)


def test_trick_winner_highest_card_of_suit_led_wins_without_a_ruff() -> None:
    from d_dolar.statistics._trick_play import _trick_winner

    assert _trick_winner(["H5", "H2", "HA", "H9"], trump_suit="S") == 2


def test_trick_winner_a_ruff_beats_any_non_trump_follow() -> None:
    from d_dolar.statistics._trick_play import _trick_winner

    assert _trick_winner(["H5", "HA", "S2", "H9"], trump_suit="S") == 2


def test_trick_winner_higher_trump_beats_lower_trump() -> None:
    from d_dolar.statistics._trick_play import _trick_winner

    assert _trick_winner(["H5", "S2", "S9", "H9"], trump_suit="S") == 2


def test_trick_winner_notrump_contract_never_lets_an_off_suit_card_win() -> None:
    from d_dolar.statistics._trick_play import _trick_winner

    assert _trick_winner(["H5", "S9", "HA", "H2"], trump_suit=None) == 2


def test_attribute_cards_passes_leadership_to_the_trick_winner() -> None:
    from d_dolar.statistics._trick_play import attribute_cards

    hands = {
        "N": {"H5", "DA"},
        "E": {"H2", "D5"},
        "S": {"HA", "D9"},
        "W": {"H9", "D2"},
    }
    seats = attribute_cards(
        hands, leader="N", play=["H5", "H2", "HA", "H9", "D9", "D2", "DA", "D5"], trump_suit=None
    )
    assert seats == ["N", "E", "S", "W", "S", "W", "N", "E"]


def test_attribute_cards_raises_on_a_card_not_available_to_the_attributed_seat() -> None:
    from d_dolar.statistics._trick_play import attribute_cards

    hands = {"N": {"H5"}, "E": {"H2"}, "S": {"HA"}, "W": {"H9"}}
    with pytest.raises(ValueError):
        attribute_cards(hands, leader="N", play=["H5", "H2", "HA", "H9", "D2"], trump_suit=None)
