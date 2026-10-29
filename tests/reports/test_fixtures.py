import csv
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


def _row(name: str, key: str, value: str) -> dict[str, str]:
    with (FIXTURES / name).open(newline="") as f:
        return next(r for r in csv.DictReader(f) if r[key] == value)


def test_hegyi_levai_defending_optimal() -> None:
    row = _row("boards.csv", "BoardUID", "583742")
    assert row["North"] == "LEVAI FERENC"
    assert row["South"] == "HEGYI ANDRAS"
    assert row["Declarer"] == "W"
    assert row["Lead"] == "HA"


def test_hegyi_levai_defending_suboptimal() -> None:
    row = _row("boards.csv", "BoardUID", "408320")
    assert row["South"] == "HEGYI ANDRAS"
    assert row["Declarer"] == "E"
    assert row["Lead"] == "H6"


def test_hegyi_levai_declaring() -> None:
    row = _row("boards.csv", "BoardUID", "102648")
    assert row["North"] == "LEVAI FERENC"
    assert row["South"] == "HEGYI ANDRAS"
    assert row["Declarer"] == "N"


def test_only_hegyi_present() -> None:
    row = _row("boards.csv", "BoardUID", "142234")
    assert row["South"] == "HEGYI ANDRAS"
    assert row["North"] == "KIRSCHNER JOZSEF"


def test_hegyi_with_other_partner_optimal() -> None:
    row = _row("boards.csv", "BoardUID", "512007")
    assert row["South"] == "HEGYI ANDRAS"
    assert row["North"] == "MARJAN GYORGY"
    assert row["Declarer"] == "W"


def test_hegyi_with_other_partner_suboptimal() -> None:
    row = _row("boards.csv", "BoardUID", "283292")
    assert row["South"] == "HEGYI ANDRAS"
    assert row["North"] == "KIRSCHNER JOZSEF"
    assert row["Declarer"] == "E"


def test_levai_with_other_partner_optimal() -> None:
    row = _row("boards.csv", "BoardUID", "1313031")
    assert row["North"] == "LEVAI FERENC"
    assert row["South"] == "DORNYEI ZSOLT"
    assert row["Declarer"] == "E"


def test_levai_with_other_partner_and_hegyi_present_but_declaring() -> None:
    row = _row("boards.csv", "BoardUID", "1109355")
    assert row["North"] == "LEVAI FERENC"
    assert row["South"] == "MURKL MATE"
    assert row["West"] == "HEGYI ANDRAS"
    assert row["Declarer"] == "W"


def test_unrecorded_lead_board_present() -> None:
    row = _row("boards.csv", "BoardUID", "946801")
    assert row["Declarer"] == "E"
    assert row["Lead"] == ""


def test_lead_without_play_board_present() -> None:
    row = _row("boards.csv", "BoardUID", "1499299")
    assert row["Declarer"] == "W"
    assert row["Lead"] == "D5"
    assert row["Play"] == ""


def test_all_pass_board_present() -> None:
    row = _row("boards.csv", "BoardUID", "1117730")
    assert row["Declarer"] == ""
    assert row["Contract"] == "AP"


def test_fixture_row_counts() -> None:
    for name, expected in (("boards.csv", 11), ("deals.csv", 11), ("hands.csv", 11), ("events.csv", 10)):
        with (FIXTURES / name).open(newline="") as f:
            assert sum(1 for _ in csv.DictReader(f)) == expected
