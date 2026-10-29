"""The second-defender-tricks-lost statistic: how many tricks the
defender who did NOT make the opening lead cost the defence, summed
across every card they played, compared to double-dummy-optimal
continuation at each point."""

from dds3 import analyse_play_pbn

from d_dolar.statistics._seats import LEADER_OF, OPPOSITE, SEAT_TO_FIRST, STRAIN_TO_TRUMP
from d_dolar.statistics._trick_play import attribute_cards, parse_hands


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
    Lead), or a Play string that fails the card-ownership check (a
    known, rare upstream data defect; see specs/rawdb-import.md)."""
    if not declarer or not contract or not play:
        return None

    leader = LEADER_OF[declarer]
    second_defender = OPPOSITE[leader]
    trump_suit = None if contract[1] == "N" else contract[1]

    cards = play.split("_")

    try:
        parsed_hands = parse_hands(hands)
        seats = attribute_cards(parsed_hands, leader, cards, trump_suit)
    except ValueError:
        return None

    trump = STRAIN_TO_TRUMP[contract[1]]
    first = SEAT_TO_FIRST[leader]
    result = analyse_play_pbn(hands, play="".join(cards), trump=trump, first=first)
    tricks: list[int] = result["tricks"]

    return sum(
        tricks[i] - tricks[i - 1]
        for i in range(1, len(tricks))
        if seats[i - 1] == second_defender
    )
