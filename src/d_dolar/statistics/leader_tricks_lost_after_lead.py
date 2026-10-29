"""The leader-tricks-lost-after-lead statistic: how many tricks the
opening leader's OWN cards cost the defence after their opening lead,
summed across every one of their later cards, compared to
double-dummy-optimal continuation at each point. Does not include the
opening lead's own cost -- d_dolar_base already judges that single
card."""

from dds3 import analyse_play_pbn

from d_dolar.statistics._seats import LEADER_OF, SEAT_TO_FIRST, STRAIN_TO_TRUMP
from d_dolar.statistics._trick_play import attribute_cards, parse_hands


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
    Lead), or a Play string that fails the card-ownership check (a
    known, rare upstream data defect; see specs/rawdb-import.md)."""
    if not declarer or not contract or not play:
        return None

    leader = LEADER_OF[declarer]
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
        for i in range(2, len(tricks))
        if seats[i - 1] == leader
    )
