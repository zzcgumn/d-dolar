import csv
from pathlib import Path

FIXTURES = Path(__file__).parents[1] / "reports" / "fixtures"


def _row(name: str, key: str, value: str) -> dict[str, str]:
    with (FIXTURES / name).open(newline="") as f:
        return next(r for r in csv.DictReader(f) if r[key] == value)


def test_lead_choices_missing_declarer_returns_none() -> None:
    from d_dolar.statistics._lead_choices import lead_choices

    deal = "N:AKQJT98765432... .AKQJT98765432.. ..AKQJT98765432. ...AKQJT98765432"
    assert lead_choices(deal, None, "3N") is None


def test_lead_choices_missing_contract_returns_none() -> None:
    from d_dolar.statistics._lead_choices import lead_choices

    deal = "N:AKQJT98765432... .AKQJT98765432.. ..AKQJT98765432. ...AKQJT98765432"
    assert lead_choices(deal, "E", "") is None


def test_lead_choices_all_pass_contract_with_declarer_filled_returns_none() -> None:
    # Real RawDB quirk (specs/rawdb-import.md): Contract == "AP" does
    # NOT reliably come with an empty Declarer -- 629 real all-pass
    # boards have Declarer filled in anyway. lead_choices must not
    # crash (contract[1] == "P" is not a strain) and must still
    # report "no lead to judge", the same as a genuinely empty
    # Declarer would.
    from d_dolar.statistics._lead_choices import lead_choices

    deal = "N:AKQJT98765432... .AKQJT98765432.. ..AKQJT98765432. ...AKQJT98765432"
    assert lead_choices(deal, "E", "AP") is None


def test_lead_choices_works_with_no_recorded_lead_or_play_at_all() -> None:
    # lead_choices doesn't take Lead/Play parameters at all -- it's
    # computable from Hands/Declarer/Contract alone, a strictly
    # broader domain than lead_tricks/d_dolar.
    from d_dolar.statistics._lead_choices import lead_choices

    deal = "N:AKQJT98765432... .AKQJT98765432.. ..AKQJT98765432. ...AKQJT98765432"
    choices = lead_choices(deal, "E", "3N")
    assert choices is not None
    cards, defender_tricks = choices
    assert len(cards) == len(defender_tricks) > 0


def test_lead_choices_every_choice_gives_the_same_score_on_board_1499299() -> None:
    # BoardUID 1499299: Declarer=W, Contract=6C, leader=North.
    # Confirmed via dds3.solve_board_pbn this session: all 10
    # distinct choices score 1 (declarer always makes 12, matching
    # DD_W_C=12).
    from d_dolar.statistics._lead_choices import lead_choices

    board = _row("boards.csv", "BoardUID", "1499299")
    hand = _row("hands.csv", "HandUID", "215330")
    choices = lead_choices(hand["Hands"], board["Declarer"], board["Contract"])
    assert choices is not None
    cards, defender_tricks = choices
    assert len(cards) == 10
    assert defender_tricks == [1] * 10


def test_lead_choices_includes_the_recorded_lead_on_board_408320() -> None:
    # BoardUID 408320: Declarer=E, Contract=3N, leader=South,
    # recorded Lead=H6. Confirmed via dds3.solve_board_pbn this
    # session: 13 distinct choices, scores ranging 1-3, H6 scores 2.
    from d_dolar.statistics._lead_choices import lead_choices

    board = _row("boards.csv", "BoardUID", "408320")
    hand = _row("hands.csv", "HandUID", "58343")
    choices = lead_choices(hand["Hands"], board["Declarer"], board["Contract"])
    assert choices is not None
    cards, defender_tricks = choices
    assert len(cards) == 13
    assert set(defender_tricks) == {1, 2, 3}
    by_card = dict(zip(cards, defender_tricks))
    assert by_card["H6"] == 2


def test_recorded_lead_defender_tricks_matches_the_recorded_lead_on_board_1499299() -> None:
    from d_dolar.statistics._lead_choices import recorded_lead_defender_tricks

    board = _row("boards.csv", "BoardUID", "1499299")
    hand = _row("hands.csv", "HandUID", "215330")
    result = recorded_lead_defender_tricks(
        hand["Hands"], board["Declarer"], board["Contract"], board["Lead"], board["Play"]
    )
    assert result == 1


def test_recorded_lead_defender_tricks_matches_the_recorded_lead_on_board_408320() -> None:
    from d_dolar.statistics._lead_choices import recorded_lead_defender_tricks

    board = _row("boards.csv", "BoardUID", "408320")
    hand = _row("hands.csv", "HandUID", "58343")
    result = recorded_lead_defender_tricks(
        hand["Hands"], board["Declarer"], board["Contract"], board["Lead"], board["Play"]
    )
    assert result == 2


def test_recorded_lead_defender_tricks_resolves_an_equivalence_absorbed_fallback_card() -> None:
    # BoardUID 408320: override Lead to empty and supply a synthetic
    # Play whose first card is "S9" -- not itself a group
    # representative (that's "S7") but strategically identical to
    # it (confirmed via dds3.solve_board_pbn this session: both
    # score 3). Proves the equals-bitmask matching, not just an
    # exact-string lookup against group representatives.
    from d_dolar.statistics._lead_choices import recorded_lead_defender_tricks

    board = _row("boards.csv", "BoardUID", "408320")
    hand = _row("hands.csv", "HandUID", "58343")
    result = recorded_lead_defender_tricks(
        hand["Hands"], board["Declarer"], board["Contract"], "", "S9_not_a_real_play"
    )
    assert result == 3


def test_recorded_lead_defender_tricks_missing_declarer_returns_none() -> None:
    from d_dolar.statistics._lead_choices import recorded_lead_defender_tricks

    deal = "N:AKQJT98765432... .AKQJT98765432.. ..AKQJT98765432. ...AKQJT98765432"
    assert recorded_lead_defender_tricks(deal, None, "3N", "DA", None) is None


def test_recorded_lead_defender_tricks_both_lead_and_play_absent_returns_none() -> None:
    from d_dolar.statistics._lead_choices import recorded_lead_defender_tricks

    deal = "N:AKQJT98765432... .AKQJT98765432.. ..AKQJT98765432. ...AKQJT98765432"
    assert recorded_lead_defender_tricks(deal, "E", "3N", "", "") is None


def test_recorded_lead_defender_tricks_not_held_by_leader_returns_none() -> None:
    # declarer=E -> leader=South, who holds only diamonds in this
    # deal. HA belongs to East, not South -- falls through every
    # equivalence group with no match.
    from d_dolar.statistics._lead_choices import recorded_lead_defender_tricks

    deal = "N:AKQJT98765432... .AKQJT98765432.. ..AKQJT98765432. ...AKQJT98765432"
    assert recorded_lead_defender_tricks(deal, "E", "3N", "HA", None) is None
