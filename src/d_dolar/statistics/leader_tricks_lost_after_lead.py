"""The leader-tricks-lost-after-lead statistic: how many tricks the
opening leader's OWN cards cost the defence after their opening lead,
summed across every one of their later cards, compared to
double-dummy-optimal continuation at each point. Does not include the
opening lead's own cost -- d_dolar_base already judges that single
card."""

from d_dolar.statistics._board_trajectory import board_trajectory


def leader_tricks_lost_after_lead(
    hands: str, declarer: str | None, contract: str | None, play: str | None
) -> int | None:
    """Sum, across every card the opening leader plays AFTER their
    opening lead, of the tricks that card cost the defence (the
    increase in declarer's double-dummy-achievable trick count caused
    by that one card, vs. double-dummy-optimal play from the position
    just before it). Excludes the lead itself -- that is d_dolar_base's
    subject, not this statistic's.

    None if there is no play to judge: an all-pass board (no declarer),
    a board with no recorded Play (distinct from -- and rarer than --
    Lead), a Play string that fails the card-ownership check (a
    known, rare upstream data defect; see specs/rawdb-import.md), or
    a Contract that doesn't encode a playable strain (the same
    all-pass quirk that can leave Declarer/Play non-empty too --
    see specs/rawdb-import.md and specs/d-dolar.md)."""
    trajectory = board_trajectory(hands, declarer, contract, play)
    if trajectory is None:
        return None
    leader, seats, tricks = trajectory

    return sum(
        tricks[i] - tricks[i - 1]
        for i in range(2, len(tricks))
        if seats[i - 1] == leader
    )
