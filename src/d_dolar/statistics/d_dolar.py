"""The D-dolar base statistic: was a board's opening lead double-dummy optimal."""

from dds3 import analyse_play_pbn

# The opening leader is the defender to declarer's left: the next seat
# clockwise in the standard N -> E -> S -> W -> N rotation.
_LEADER_OF = {"N": "E", "E": "S", "S": "W", "W": "N"}

# dds3's trump encoding: 0=S 1=H 2=D 3=C 4=NT.
_STRAIN_TO_TRUMP = {"S": 0, "H": 1, "D": 2, "C": 3, "N": 4}

# dds3's seat encoding: 0=N 1=E 2=S 3=W.
_SEAT_TO_FIRST = {"N": 0, "E": 1, "S": 2, "W": 3}


def d_dolar_base(hands: str, declarer: str | None, contract: str | None, lead: str | None) -> int | None:
    """Whether the opening lead against `declarer`'s `contract` was double-dummy optimal.

    1 if the lead cost the defence nothing against double-dummy-optimal
    play from everyone thereafter, 0 if it let declarer make at least one
    more trick than double-dummy optimal. None if there is no lead to
    judge: an all-pass board (no `declarer`), or one where the opening
    lead was never recorded (no `lead`).
    """
    if not declarer or not contract or not lead:
        return None

    trump = _STRAIN_TO_TRUMP[contract[1]]
    first = _SEAT_TO_FIRST[_LEADER_OF[declarer]]

    result = analyse_play_pbn(hands, play=lead, trump=trump, first=first)
    before_lead, after_lead = result["tricks"]
    return 1 if after_lead == before_lead else 0
