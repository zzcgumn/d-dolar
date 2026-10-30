"""Shared double-dummy trick-trajectory computation for every defence
statistic in this package that needs to score cards played after the
opening lead."""

from dds3 import analyse_play_pbn

from d_dolar.statistics._seats import LEADER_OF, SEAT_TO_FIRST, STRAIN_TO_TRUMP
from d_dolar.statistics._trick_play import attribute_cards, parse_hands


def lead_trajectory(
    hands: str, declarer: str | None, contract: str | None, lead: str | None, play: str | None
) -> list[int] | None:
    """Returns [before, after] double-dummy trick counts for declarer's
    side across the opening-lead card -- the raw pair d_dolar_base
    reduces to its 0/1/None result. Uses `lead` whenever it's present,
    even on the ~105 documented boards where it disagrees with `play`'s
    first card (specs/rawdb-import.md) -- no reconciliation attempted.
    Only when `lead` is empty does it fall back to `play`'s first card
    (by construction the leader's own card, per attribute_cards'
    rotation). None if neither `lead` nor `play` supplies a usable
    card, if `declarer`/`contract` is falsy, or if the resulting card
    isn't held by the computed leader."""
    if not declarer or not contract:
        return None
    effective_lead = lead if lead else (play.split("_")[0] if play else None)
    if not effective_lead:
        return None

    leader = LEADER_OF[declarer]
    try:
        parsed_hands = parse_hands(hands)
    except ValueError:
        return None
    if effective_lead not in parsed_hands[leader]:
        return None

    trump = STRAIN_TO_TRUMP[contract[1]]
    first = SEAT_TO_FIRST[leader]
    result = analyse_play_pbn(hands, play=effective_lead, trump=trump, first=first)
    tricks: list[int] = result["tricks"]
    return tricks


def board_trajectory(
    hands: str, declarer: str | None, contract: str | None, play: str | None
) -> tuple[str, list[str], list[int]] | None:
    """Returns (leader, seats, tricks) for a board's full recorded
    play -- leader is the opening leader's seat, seats[i] is who
    played cards[i] (cards = play.split("_")), tricks[i] is the
    double-dummy trick count for declarer's side after i cards
    (tricks[0] is the pre-play baseline). None under the same
    conditions second_defender_tricks_lost/leader_tricks_lost_after_lead
    already return None for: falsy declarer/contract/play, or a Play
    string that fails attribute_cards' card-ownership check."""
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
    return leader, seats, tricks
