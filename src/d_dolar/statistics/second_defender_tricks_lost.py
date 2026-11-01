"""The second-defender-tricks-lost statistic: how many tricks the
defender who did NOT make the opening lead cost the defence, summed
across every card they played, compared to double-dummy-optimal
continuation at each point."""

from d_dolar.statistics._board_trajectory import board_trajectory
from d_dolar.statistics._seats import OPPOSITE


def second_defender_tricks_lost(
    hands: str, declarer: str | None, contract: str | None, play: str | None
) -> int | None:
    """Sum, across every card played by the defender who did NOT make
    the opening lead, of the tricks that card cost the defence: the
    increase in declarer's double-dummy-achievable trick count caused
    by that one card, compared to double-dummy-optimal play from the
    position just before it.

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
    second_defender = OPPOSITE[leader]

    return sum(
        tricks[i] - tricks[i - 1]
        for i in range(1, len(tricks))
        if seats[i - 1] == second_defender
    )
