import csv
from pathlib import Path

FIXTURES = Path(__file__).parents[1] / "reports" / "fixtures"

_TRIVIAL_DEAL = (
    "N:AKQJT98765432... .AKQJT98765432.. ..AKQJT98765432. ...AKQJT98765432"
)


def _row(name: str, key: str, value: str) -> dict[str, str]:
    with (FIXTURES / name).open(newline="") as f:
        return next(r for r in csv.DictReader(f) if r[key] == value)


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


def test_hands_with_fewer_than_four_seats_returns_none() -> None:
    from d_dolar.statistics.second_defender_tricks_lost import second_defender_tricks_lost

    # Only 3 of the 4 space-separated hands are present (West's is
    # missing). Without parse_hands' own length check, this would
    # produce a seat mapping with no "W" key, so attributing the first
    # card anyone leads to W would raise an uncaught KeyError instead
    # of degrading to None like every other malformed-hands case.
    incomplete_deal = (
        "N:AKQJT98765432... .AKQJT98765432.. ..AKQJT98765432."
    )
    result = second_defender_tricks_lost(incomplete_deal, "W", "3N", "SA_HA_DA_C2")
    assert result is None
