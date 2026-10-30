"""Seat/strain dictionaries shared by every double-dummy-based
statistic in this package, and by the report modules that need to
resolve a board's leader/other-defender seat (d_dolar.reports.pairings)."""

# The opening leader is the defender to declarer's left: the next seat
# clockwise in the standard N -> E -> S -> W -> N rotation.
LEADER_OF = {"N": "E", "E": "S", "S": "W", "W": "N"}

# The defending pair's other member -- never the one on lead.
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}

# dds3's trump encoding: 0=S 1=H 2=D 3=C 4=NT.
STRAIN_TO_TRUMP = {"S": 0, "H": 1, "D": 2, "C": 3, "N": 4}

# dds3's seat encoding: 0=N 1=E 2=S 3=W.
SEAT_TO_FIRST = {"N": 0, "E": 1, "S": 2, "W": 3}

# dds3's suit encoding on a solve_board_pbn result: 0=S 1=H 2=D 3=C
# -- same as STRAIN_TO_TRUMP minus notrump, which can't describe a
# card. The reverse of STRAIN_TO_TRUMP's four suit entries.
SUIT_TO_STRAIN = {0: "S", 1: "H", 2: "D", 3: "C"}

# dds3's rank encoding on a solve_board_pbn result: 2..9 literal,
# 10=T 11=J 12=Q 13=K 14=A.
RANK_TO_CARD = {
    2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9",
    10: "T", 11: "J", 12: "Q", 13: "K", 14: "A",
}

# The reverse of RANK_TO_CARD -- decoding a card string's rank
# character back into dds3's integer encoding.
CARD_RANK_TO_INT = {v: k for k, v in RANK_TO_CARD.items()}
