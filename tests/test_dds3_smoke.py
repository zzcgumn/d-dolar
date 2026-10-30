import pytest

pytest.importorskip("dds3")

from dds3 import analyse_play_pbn, calc_all_tables_pbn, solve_board_pbn  # noqa: E402

# BoardUID 1499299 / HandUID 215330 (tests/rawdb/fixtures/): Declarer=W,
# Contract=6C, Lead=D5. hands.csv's own DD_W_C=12 and DD_W_N=12, computed
# independently by a different DDS build (endplay/DDS 2.9.0, via
# bridge-deals-ingest).
HANDS_PBN = "W:T963..J8.KQ98763 J8752.KT3.9654.4 KQ4.AQJ5.AKT.A52 A.987642.Q732.JT"
# trump: 0=S 1=H 2=D 3=C 4=NT (clubs). first: 0=N 1=E 2=S 3=W (North leads,
# the seat clockwise-after West, who is declarer here).


def test_analyse_play_pbn_has_the_documented_shape() -> None:
    result = analyse_play_pbn(HANDS_PBN, play="D5", trump=3, first=0)
    assert "number" in result
    assert "tricks" in result
    assert isinstance(result["tricks"], list)
    # Verified empirically: "number" is len(tricks), not the number of cards
    # played (play="" -> number=1, tricks=[v]; play="D5" -> number=2,
    # tricks=[v, v]; play="D5DA" -> number=3) -- docs/python_interface.md's
    # prose read as "after i cards" in a way that suggested number+1.
    assert result["number"] == len(result["tricks"])


def test_calc_all_tables_pbn_has_the_documented_shape() -> None:
    result = calc_all_tables_pbn([HANDS_PBN], mode=-1)
    # result["no_of_boards"] was observed to be 20 for this single
    # submitted deal -- looks like DDS's traditional 20-board batch-chunk
    # capacity leaking through dds3's wrapper, not an actual board count.
    # Deliberately not asserted on; len(result["tables"]) is the real count.
    assert len(result["tables"]) == 1
    assert len(result["tables"][0]["res_table"]) == 5  # one row per strain
    assert all(len(row) == 4 for row in result["tables"][0]["res_table"])


def test_analyse_play_pbn_cross_checks_against_the_known_dd_value() -> None:
    # The pre-lead trick count must equal hands.csv's own DD_W_C=12 for this
    # hand (computed independently, by a different DDS build/version).
    # Confirmed: dds3 agrees exactly.
    result = analyse_play_pbn(HANDS_PBN, play="", trump=3, first=0)
    assert result["tricks"] == [12]


def test_calc_all_tables_pbn_cross_checks_against_the_known_dd_value() -> None:
    # res_table[strain][hand]; strain order S,H,D,C,NT (0..4); hand order
    # N,E,S,W (0..3) -- confirmed empirically against hands.csv's
    # DD_W_C=12 and DD_W_N=12 for this same hand.
    result = calc_all_tables_pbn([HANDS_PBN], mode=-1)
    res_table = result["tables"][0]["res_table"]
    assert res_table[3][3] == 12  # clubs, West
    assert res_table[4][3] == 12  # notrump, West


def test_solve_board_pbn_has_the_documented_shape() -> None:
    result = solve_board_pbn(HANDS_PBN, trump=3, first=0)
    assert "cards" in result
    assert isinstance(result["cards"], int)
    # suit/rank/equals/score are always length 13, padded with
    # zeros past index "cards" -- confirmed empirically.
    for key in ("suit", "rank", "equals", "score"):
        assert len(result[key]) == 13


def test_solve_board_pbn_cross_checks_against_the_known_dd_value() -> None:
    # Every one of this hand's 10 distinct opening-lead choices
    # gives the defence exactly 1 trick -- confirmed empirically --
    # matching hands.csv's own DD_W_C=12 via 13 - 1 == 12. "score"
    # is the DEFENDERS' trick count, the opposite convention from
    # analyse_play_pbn's declarer-side "tricks".
    result = solve_board_pbn(HANDS_PBN, trump=3, first=0)
    assert result["cards"] == 10
    assert result["score"][:10] == (1,) * 10
