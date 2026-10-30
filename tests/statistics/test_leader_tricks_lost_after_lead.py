import csv
from pathlib import Path

FIXTURES = Path(__file__).parents[1] / "reports" / "fixtures"

_TRIVIAL_DEAL = (
    "N:AKQJT98765432... .AKQJT98765432.. ..AKQJT98765432. ...AKQJT98765432"
)


def _row(name: str, key: str, value: str) -> dict[str, str]:
    with (FIXTURES / name).open(newline="") as f:
        return next(r for r in csv.DictReader(f) if r[key] == value)


def test_levai_as_leader_cost_two_tricks_after_an_optimal_lead() -> None:
    from d_dolar.statistics.leader_tricks_lost_after_lead import leader_tricks_lost_after_lead

    board = _row("boards.csv", "BoardUID", "583742")
    hand = _row("hands.csv", "HandUID", "83133")
    result = leader_tricks_lost_after_lead(
        hand["Hands"], board["Declarer"], board["Contract"], board["Play"]
    )
    assert result == 2


def test_hegyi_as_leader_excludes_the_already_judged_suboptimal_lead_cost() -> None:
    from d_dolar.statistics.d_dolar import d_dolar_base
    from d_dolar.statistics.leader_tricks_lost_after_lead import leader_tricks_lost_after_lead

    board = _row("boards.csv", "BoardUID", "408320")
    hand = _row("hands.csv", "HandUID", "58343")
    # d_dolar_base already judges THIS board's opening lead as
    # suboptimal (0, it cost a trick) -- leader_tricks_lost_after_lead
    # must still return 0, since it only scores what Hegyi did AFTER
    # that lead (which was, in fact, perfect). A naive "sum every card
    # the leader plays, including the first" would not return 0 here.
    assert d_dolar_base(
        hand["Hands"], board["Declarer"], board["Contract"], board["Lead"], board["Play"]
    ) == 0
    result = leader_tricks_lost_after_lead(
        hand["Hands"], board["Declarer"], board["Contract"], board["Play"]
    )
    assert result == 0


def test_marjan_gyorgy_as_leader_cost_one_trick() -> None:
    from d_dolar.statistics.leader_tricks_lost_after_lead import leader_tricks_lost_after_lead

    board = _row("boards.csv", "BoardUID", "512007")
    hand = _row("hands.csv", "HandUID", "72598")
    result = leader_tricks_lost_after_lead(
        hand["Hands"], board["Declarer"], board["Contract"], board["Play"]
    )
    assert result == 1


def test_dornyei_zsolt_as_leader_played_perfectly() -> None:
    from d_dolar.statistics.leader_tricks_lost_after_lead import leader_tricks_lost_after_lead

    board = _row("boards.csv", "BoardUID", "1313031")
    hand = _row("hands.csv", "HandUID", "188325")
    result = leader_tricks_lost_after_lead(
        hand["Hands"], board["Declarer"], board["Contract"], board["Play"]
    )
    assert result == 0


def test_hegyi_with_other_partner_as_leader_played_perfectly() -> None:
    from d_dolar.statistics.leader_tricks_lost_after_lead import leader_tricks_lost_after_lead

    board = _row("boards.csv", "BoardUID", "283292")
    hand = _row("hands.csv", "HandUID", "40283")
    result = leader_tricks_lost_after_lead(
        hand["Hands"], board["Declarer"], board["Contract"], board["Play"]
    )
    assert result == 0


def test_levai_with_other_partner_as_leader_played_perfectly() -> None:
    from d_dolar.statistics.leader_tricks_lost_after_lead import leader_tricks_lost_after_lead

    board = _row("boards.csv", "BoardUID", "1109355")
    hand = _row("hands.csv", "HandUID", "158729")
    result = leader_tricks_lost_after_lead(
        hand["Hands"], board["Declarer"], board["Contract"], board["Play"]
    )
    assert result == 0


def test_play_ending_right_after_the_lead_returns_zero_not_none() -> None:
    from d_dolar.statistics.leader_tricks_lost_after_lead import leader_tricks_lost_after_lead

    # Only trick 1's 4 cards are recorded -- the leader (N) never plays
    # again. There's nothing further to judge, which is not an error:
    # the result must be 0, not None.
    result = leader_tricks_lost_after_lead(_TRIVIAL_DEAL, "W", "3N", "SA_HA_DA_CA")
    assert result == 0


def test_missing_declarer_returns_none() -> None:
    from d_dolar.statistics.leader_tricks_lost_after_lead import leader_tricks_lost_after_lead

    assert leader_tricks_lost_after_lead(_TRIVIAL_DEAL, None, "3N", "H5_H2_HA_H9") is None


def test_missing_play_returns_none() -> None:
    from d_dolar.statistics.leader_tricks_lost_after_lead import leader_tricks_lost_after_lead

    assert leader_tricks_lost_after_lead(_TRIVIAL_DEAL, "E", "3N", "") is None


def test_corrupted_play_with_a_repeated_card_returns_none() -> None:
    from d_dolar.statistics.leader_tricks_lost_after_lead import leader_tricks_lost_after_lead

    board = _row("boards.csv", "BoardUID", "583742")
    hand = _row("hands.csv", "HandUID", "83133")
    corrupted_play = "HA_HJ_H2_H9_C2_CQ_CK_C7_HA_HJ_H2_H9"
    result = leader_tricks_lost_after_lead(
        hand["Hands"], board["Declarer"], board["Contract"], corrupted_play
    )
    assert result is None
