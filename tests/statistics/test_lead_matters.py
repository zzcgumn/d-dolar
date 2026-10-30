import csv
from pathlib import Path

FIXTURES = Path(__file__).parents[1] / "reports" / "fixtures"


def _row(name: str, key: str, value: str) -> dict[str, str]:
    with (FIXTURES / name).open(newline="") as f:
        return next(r for r in csv.DictReader(f) if r[key] == value)


def test_lead_matters_missing_declarer_returns_none() -> None:
    from d_dolar.statistics.lead_matters import lead_matters

    deal = "N:AKQJT98765432... .AKQJT98765432.. ..AKQJT98765432. ...AKQJT98765432"
    assert lead_matters(deal, None, "3N") is None


def test_lead_matters_is_false_when_every_choice_scores_the_same() -> None:
    # BoardUID 1499299: Declarer=W, Contract=6C, leader=North.
    # Confirmed via dds3.solve_board_pbn this session: all 10
    # distinct choices score 1 -- no choice could have changed
    # anything.
    from d_dolar.statistics.lead_matters import lead_matters

    board = _row("boards.csv", "BoardUID", "1499299")
    hand = _row("hands.csv", "HandUID", "215330")
    assert lead_matters(hand["Hands"], board["Declarer"], board["Contract"]) is False


def test_lead_matters_is_true_when_choices_differ() -> None:
    # BoardUID 408320: Declarer=E, Contract=3N, leader=South.
    # Confirmed via dds3.solve_board_pbn this session: scores range
    # 1-3 across the 13 distinct choices.
    from d_dolar.statistics.lead_matters import lead_matters

    board = _row("boards.csv", "BoardUID", "408320")
    hand = _row("hands.csv", "HandUID", "58343")
    assert lead_matters(hand["Hands"], board["Declarer"], board["Contract"]) is True
