"""The D-dolar base statistic: was a board's opening lead double-dummy optimal."""

from d_dolar.statistics._board_trajectory import lead_trajectory


def d_dolar_base(
    hands: str, declarer: str | None, contract: str | None, lead: str | None, play: str | None
) -> int | None:
    """Whether the opening lead against `declarer`'s `contract` was double-dummy optimal.

    1 if the lead cost the defence nothing against double-dummy-optimal
    play from everyone thereafter, 0 if it let declarer make at least one
    more trick than double-dummy optimal. None if there is no lead to
    judge -- see lead_trajectory for the exact conditions, including the
    fallback to play's first card when lead is absent.
    """
    tricks = lead_trajectory(hands, declarer, contract, lead, play)
    if tricks is None:
        return None
    before_lead, after_lead = tricks
    return 1 if after_lead == before_lead else 0
