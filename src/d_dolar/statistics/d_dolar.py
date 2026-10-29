"""The D-dolar base statistic: was a board's opening lead double-dummy optimal."""

from dds3 import analyse_play_pbn

from d_dolar.statistics._seats import LEADER_OF, SEAT_TO_FIRST, STRAIN_TO_TRUMP


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

    trump = STRAIN_TO_TRUMP[contract[1]]
    first = SEAT_TO_FIRST[LEADER_OF[declarer]]

    result = analyse_play_pbn(hands, play=lead, trump=trump, first=first)
    before_lead, after_lead = result["tricks"]
    return 1 if after_lead == before_lead else 0
