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
