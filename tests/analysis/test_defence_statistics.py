from pathlib import Path

import polars as pl

from d_dolar.rawdb.loader import load_joined_boards

FIXTURES = Path(__file__).parents[1] / "reports" / "fixtures"

_EXPECTED = {
    583742: (1, 2, 0),
    408320: (0, 0, 1),
    102648: (1, 0, 0),
    142234: (1, 0, 0),
    512007: (1, 1, 2),
    283292: (0, 0, 0),
    1313031: (1, 0, 0),
    1109355: (0, 0, 0),
    946801: (1, 0, 2),
    1499299: (1, None, None),
    1117730: (None, None, None),
}


def test_with_defence_statistics_adds_three_columns_matching_each_statistic() -> None:
    from d_dolar.analysis.defence_statistics import with_defence_statistics

    joined = load_joined_boards(FIXTURES)
    result = with_defence_statistics(joined)

    assert isinstance(result, pl.DataFrame)
    assert {"BoardUID", "d_dolar", "dropped_before_dummy", "dropped_over_dummy"} <= set(
        result.columns
    )
    assert result.height == 11

    by_board = {
        row["BoardUID"]: (
            row["d_dolar"],
            row["dropped_before_dummy"],
            row["dropped_over_dummy"],
        )
        for row in result.iter_rows(named=True)
    }
    assert by_board == _EXPECTED


def test_with_defence_statistics_adds_the_four_raw_trajectory_columns() -> None:
    from d_dolar.analysis.defence_statistics import with_defence_statistics

    joined = load_joined_boards(FIXTURES)
    result = with_defence_statistics(joined)

    assert {
        "lead_tricks",
        "trajectory_leader",
        "trajectory_seats",
        "trajectory_tricks",
    } <= set(result.columns)

    by_board = {row["BoardUID"]: row for row in result.iter_rows(named=True)}

    # BoardUID 946801: Lead empty, Play recorded -- the fallback
    # makes lead_tricks non-null (and d_dolar == 1, see _EXPECTED).
    assert by_board[946801]["lead_tricks"] == [10, 10]

    # BoardUID 1499299: Lead present, Play absent -- lead_tricks is
    # non-null but the Play-only trajectory columns are null.
    assert by_board[1499299]["lead_tricks"] is not None
    assert by_board[1499299]["trajectory_leader"] is None
    assert by_board[1499299]["trajectory_seats"] is None
    assert by_board[1499299]["trajectory_tricks"] is None

    # BoardUID 1117730: all-pass board -- every raw column is null.
    assert by_board[1117730]["lead_tricks"] is None
    assert by_board[1117730]["trajectory_leader"] is None
    assert by_board[1117730]["trajectory_seats"] is None
    assert by_board[1117730]["trajectory_tricks"] is None


def test_the_three_existing_statistics_are_pure_reductions_of_the_raw_columns() -> None:
    """Proves the user's actual question: re-deriving d_dolar,
    dropped_before_dummy, and dropped_over_dummy purely from the
    four stored raw columns -- no call to d_dolar_base,
    board_trajectory, lead_trajectory, or dds3 -- reproduces
    with_defence_statistics' own values for every row."""
    from d_dolar.analysis.defence_statistics import with_defence_statistics
    from d_dolar.statistics._seats import OPPOSITE

    joined = load_joined_boards(FIXTURES)
    result = with_defence_statistics(joined)

    for row in result.iter_rows(named=True):
        tricks = row["lead_tricks"]
        derived_d_dolar = None if tricks is None else (1 if tricks[1] == tricks[0] else 0)
        assert derived_d_dolar == row["d_dolar"]

        leader = row["trajectory_leader"]
        seats = row["trajectory_seats"]
        traj_tricks = row["trajectory_tricks"]
        if leader is None:
            assert row["dropped_before_dummy"] is None
            assert row["dropped_over_dummy"] is None
            continue

        second_defender = OPPOSITE[leader]
        derived_dropped_before_dummy = sum(
            traj_tricks[i] - traj_tricks[i - 1]
            for i in range(2, len(traj_tricks))
            if seats[i - 1] == leader
        )
        derived_dropped_over_dummy = sum(
            traj_tricks[i] - traj_tricks[i - 1]
            for i in range(1, len(traj_tricks))
            if seats[i - 1] == second_defender
        )
        assert derived_dropped_before_dummy == row["dropped_before_dummy"]
        assert derived_dropped_over_dummy == row["dropped_over_dummy"]


def test_with_defence_statistics_handles_all_pass_contract_with_declarer_filled() -> None:
    # Real RawDB quirk (specs/rawdb-import.md): Contract == "AP"
    # boards don't reliably have an empty Declarer -- 629 real boards
    # have it filled in anyway. Previously this crashed
    # with_defence_statistics with a KeyError on contract[1] ("P"
    # isn't a strain) inside _solve_opening_lead, which (unlike
    # lead_trajectory/board_trajectory) has no Lead/Play to fall back
    # on to short-circuit first. No fixture board reproduces this
    # (the one all-pass fixture board, 1117730, happens to have an
    # empty Declarer), so this builds the row directly.
    from d_dolar.analysis.defence_statistics import with_defence_statistics

    deal = "N:AKQJT98765432... .AKQJT98765432.. ..AKQJT98765432. ...AKQJT98765432"
    joined = pl.LazyFrame(
        {
            "Hands": [deal],
            "Declarer": ["E"],
            "Contract": ["AP"],
            "Lead": [None],
            "Play": [""],
        }
    )

    result = with_defence_statistics(joined)
    row = result.row(0, named=True)
    assert row["lead_choices"] is None
    assert row["lead_choice_defender_tricks"] is None
    assert row["lead_matters"] is None
    assert row["recorded_lead_defender_tricks"] is None
    assert row["d_dolar"] is None


def test_with_defence_statistics_adds_the_lead_choice_columns() -> None:
    from d_dolar.analysis.defence_statistics import with_defence_statistics

    joined = load_joined_boards(FIXTURES)
    result = with_defence_statistics(joined)

    assert {
        "lead_choices",
        "lead_choice_defender_tricks",
        "lead_matters",
        "recorded_lead_defender_tricks",
    } <= set(result.columns)

    by_board = {row["BoardUID"]: row for row in result.iter_rows(named=True)}

    # BoardUID 1499299: every choice scores 1 -- the lead didn't
    # matter, and the recorded lead (D5) matches that same score.
    assert by_board[1499299]["lead_matters"] is False
    assert set(by_board[1499299]["lead_choice_defender_tricks"]) == {1}
    assert by_board[1499299]["recorded_lead_defender_tricks"] == 1

    # BoardUID 408320: scores range 1-3 -- the lead did matter, and
    # the recorded lead (H6) scored 2, not the best available (3).
    assert by_board[408320]["lead_matters"] is True
    assert set(by_board[408320]["lead_choice_defender_tricks"]) == {1, 2, 3}
    assert by_board[408320]["recorded_lead_defender_tricks"] == 2


def test_recorded_lead_defender_tricks_cross_checks_against_lead_tricks() -> None:
    """The exact-value cross-check: wherever both are non-null,
    recorded_lead_defender_tricks must equal 13 - lead_tricks[1] --
    total tricks is always 13, so this is the same card's outcome
    computed via two completely independent dds3 entry points
    (solve_board_pbn vs. analyse_play_pbn)."""
    from d_dolar.analysis.defence_statistics import with_defence_statistics

    joined = load_joined_boards(FIXTURES)
    result = with_defence_statistics(joined)

    checked = 0
    for row in result.iter_rows(named=True):
        recorded = row["recorded_lead_defender_tricks"]
        tricks = row["lead_tricks"]
        if recorded is None or tricks is None:
            continue
        assert recorded == 13 - tricks[1]
        checked += 1
    assert checked >= 2  # at least BoardUID 1499299 and 408320


def test_lead_matters_false_implies_d_dolar_optimal() -> None:
    """The Boolean cross-check: wherever both are non-null,
    lead_matters is False must imply d_dolar == 1 -- if no possible
    lead could have done better, the actual lead can't have been
    suboptimal."""
    from d_dolar.analysis.defence_statistics import with_defence_statistics

    joined = load_joined_boards(FIXTURES)
    result = with_defence_statistics(joined)

    lead_matters_false_checked = 0
    for row in result.iter_rows(named=True):
        lead_matters = row["lead_matters"]
        d_dolar = row["d_dolar"]
        if lead_matters is None or d_dolar is None:
            continue
        if lead_matters is False:
            assert d_dolar == 1
            lead_matters_false_checked += 1
    assert lead_matters_false_checked >= 1  # BoardUID 1499299
