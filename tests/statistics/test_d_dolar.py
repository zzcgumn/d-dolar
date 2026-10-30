import csv
from pathlib import Path

FIXTURES = Path(__file__).parents[1] / "rawdb" / "fixtures"


def _row(name: str, key: str, value: str) -> dict[str, str]:
    with (FIXTURES / name).open(newline="") as f:
        return next(r for r in csv.DictReader(f) if r[key] == value)


def test_optimal_lead_returns_one() -> None:
    from d_dolar.statistics.d_dolar import d_dolar_base

    # BoardUID 1499299: Declarer=W, Contract=6C, Lead=D5; DD_W_C=12 and the
    # lead keeps declarer at exactly 12 (confirmed with dds3.analyse_play_pbn).
    board = _row("boards.csv", "BoardUID", "1499299")
    hand = _row("hands.csv", "HandUID", "215330")
    assert d_dolar_base(
        hand["Hands"], board["Declarer"], board["Contract"], board["Lead"], board["Play"]
    ) == 1


def test_optimal_lead_confirmed_on_a_second_known_board() -> None:
    from d_dolar.statistics.d_dolar import d_dolar_base

    # BoardUID 1400200: Declarer=W, Contract=4DX, Lead=SA; DD_W_D=8 and the
    # recorded lead keeps declarer at exactly 8.
    board = _row("boards.csv", "BoardUID", "1400200")
    hand = _row("hands.csv", "HandUID", "201140")
    assert d_dolar_base(
        hand["Hands"], board["Declarer"], board["Contract"], board["Lead"], board["Play"]
    ) == 1


def test_suboptimal_lead_returns_zero() -> None:
    from d_dolar.statistics.d_dolar import d_dolar_base

    # Same board as above, but H9 (also a legal lead from the same hand) is
    # confirmed NOT double-dummy optimal: it lets declarer make 9 tricks
    # instead of the double-dummy-optimal 8.
    board = _row("boards.csv", "BoardUID", "1400200")
    hand = _row("hands.csv", "HandUID", "201140")
    assert d_dolar_base(
        hand["Hands"], board["Declarer"], board["Contract"], "H9", board["Play"]
    ) == 0


def test_all_pass_board_returns_none() -> None:
    from d_dolar.statistics.d_dolar import d_dolar_base

    # BoardUID 1117730: Contract=AP, Declarer and Lead both empty -- no lead to judge.
    board = _row("boards.csv", "BoardUID", "1117730")
    hand = _row("hands.csv", "HandUID", "160021")
    assert d_dolar_base(
        hand["Hands"], board["Declarer"], board["Contract"], board["Lead"], board["Play"]
    ) is None


def test_falls_back_to_plays_first_card_when_lead_absent() -> None:
    from d_dolar.statistics.d_dolar import d_dolar_base

    # BoardUID 946801: Declarer=E, Contract=3D, Lead empty, Play
    # starts H4. d_dolar_base now falls back to Play's first card
    # as the lead -- confirmed via dds3.analyse_play_pbn this
    # session: tricks before and after are both 10, so the result
    # is 1, not None.
    board = _row("boards.csv", "BoardUID", "946801")
    hand = _row("hands.csv", "HandUID", "135387")
    assert d_dolar_base(
        hand["Hands"], board["Declarer"], board["Contract"], board["Lead"], board["Play"]
    ) == 1


def test_lead_not_held_by_leader_returns_none() -> None:
    from d_dolar.statistics.d_dolar import d_dolar_base

    # BoardUID 1194011: Declarer=W, so leader=North. North's hand
    # (975.A54.6.AJ9732) holds only the D6, not the recorded Lead
    # (D7) -- a real, confirmed RawDB data defect (~3.3% of judged
    # boards in the full RawDB have this). Must return None, not
    # raise the RuntimeError dds3 itself raises for an illegal lead.
    board = _row("boards.csv", "BoardUID", "1194011")
    hand = _row("hands.csv", "HandUID", "171224")
    assert d_dolar_base(
        hand["Hands"], board["Declarer"], board["Contract"], board["Lead"], board["Play"]
    ) is None


def test_both_lead_and_play_absent_returns_none() -> None:
    from d_dolar.statistics.d_dolar import d_dolar_base

    # BoardUID 1499299 has a real Declarer/Contract/Hands but we
    # override lead and play to simulate a board where neither was
    # ever recorded -- no such row exists in the current fixtures.
    board = _row("boards.csv", "BoardUID", "1499299")
    hand = _row("hands.csv", "HandUID", "215330")
    assert d_dolar_base(hand["Hands"], board["Declarer"], board["Contract"], "", "") is None


def test_lead_wins_over_conflicting_plays_first_card() -> None:
    from d_dolar.statistics.d_dolar import d_dolar_base

    # BoardUID 1400200: Declarer=W, Contract=4DX, Lead=SA, which is
    # confirmed optimal (test_optimal_lead_confirmed_on_a_second_known_board).
    # A synthetic play starting with a different card must be
    # ignored entirely -- lead always wins when present.
    board = _row("boards.csv", "BoardUID", "1400200")
    hand = _row("hands.csv", "HandUID", "201140")
    result = d_dolar_base(
        hand["Hands"], board["Declarer"], board["Contract"], board["Lead"], "D2_not_a_real_play"
    )
    assert result == 1
