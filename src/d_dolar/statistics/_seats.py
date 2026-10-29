"""Seat/strain dictionaries shared by every double-dummy-based
statistic in this package."""

# The opening leader is the defender to declarer's left: the next seat
# clockwise in the standard N -> E -> S -> W -> N rotation.
LEADER_OF = {"N": "E", "E": "S", "S": "W", "W": "N"}

# The defending pair's other member -- never the one on lead.
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}

# dds3's trump encoding: 0=S 1=H 2=D 3=C 4=NT.
STRAIN_TO_TRUMP = {"S": 0, "H": 1, "D": 2, "C": 3, "N": 4}

# dds3's seat encoding: 0=N 1=E 2=S 3=W.
SEAT_TO_FIRST = {"N": 0, "E": 1, "S": 2, "W": 3}
