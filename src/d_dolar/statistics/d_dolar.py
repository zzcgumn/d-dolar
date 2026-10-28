"""The D-dolar base statistic: was a board's opening lead double-dummy optimal."""

from endplay.dds import analyse_play
from endplay.types import Deal, Denom, Player

# The opening leader is the defender to declarer's left: the next seat
# clockwise in the standard N -> E -> S -> W -> N rotation.
_LEADER_OF = {"N": "E", "E": "S", "S": "W", "W": "N"}

_STRAIN_TO_DENOM = {
    "S": Denom.spades,
    "H": Denom.hearts,
    "D": Denom.diamonds,
    "C": Denom.clubs,
    "N": Denom.nt,
}

_SEAT_TO_PLAYER = {
    "N": Player.north,
    "E": Player.east,
    "S": Player.south,
    "W": Player.west,
}


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

    deal = Deal.from_pbn(hands)
    deal.trump = _STRAIN_TO_DENOM[contract[1]]
    deal.first = _SEAT_TO_PLAYER[_LEADER_OF[declarer]]

    # SolvedPlay.__getitem__ mishandles negative indices (a bug in endplay
    # itself: `len(self) - i` instead of `len(self) + i`), so index forward
    # from a materialized list rather than risk relying on `[-1]`.
    before_lead, after_lead = list(analyse_play(deal, [lead]))
    return 1 if after_lead == before_lead else 0
