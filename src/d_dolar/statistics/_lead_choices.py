"""Shared raw primitive for every statistic in this package that
needs to know the outcome of EVERY legal opening-lead choice, not
just the one that was actually made -- unlike _board_trajectory.py,
which scores one specific recorded card or sequence."""

from dds3 import solve_board_pbn

from d_dolar.statistics._seats import (
    LEADER_OF,
    RANK_TO_CARD,
    SEAT_TO_FIRST,
    STRAIN_TO_TRUMP,
    SUIT_TO_STRAIN,
)


def _solve_opening_lead(
    hands: str, declarer: str | None, contract: str | None
) -> tuple[list[int], list[int], list[int], list[int]] | None:
    """Internal: one solve_board_pbn call, sliced to its own `cards`
    count. Returns dds3's raw per-choice encoding -- (suit, rank,
    equals, score) -- or None if declarer/contract is falsy.
    lead_choices and recorded_lead_defender_tricks both build on
    this single call; with_defence_statistics calls it directly
    too, so the one necessary solve per row is never repeated."""
    if not declarer or not contract:
        return None
    leader = LEADER_OF[declarer]
    trump = STRAIN_TO_TRUMP[contract[1]]
    first = SEAT_TO_FIRST[leader]
    result = solve_board_pbn(hands, trump=trump, first=first)
    n: int = result["cards"]
    return result["suit"][:n], result["rank"][:n], result["equals"][:n], result["score"][:n]


def lead_choices(
    hands: str, declarer: str | None, contract: str | None
) -> tuple[list[str], list[int]] | None:
    """Returns (cards, defender_tricks): every distinct opening-lead
    choice (dds3's own equivalence grouping -- strategically
    identical cards collapse to one entry) the leader could make,
    as this package's card-string notation, paired with the
    double-dummy trick count the DEFENCE gets if that card is led
    -- the opposite convention from analyse_play_pbn's
    declarer-side tricks used by every other statistic in this
    package. None only if declarer or contract is falsy -- this
    needs no Lead or Play at all, so it is non-null on a strictly
    larger set of boards than lead_tricks/d_dolar."""
    solved = _solve_opening_lead(hands, declarer, contract)
    if solved is None:
        return None
    suit, rank, _equals, score = solved
    cards = [SUIT_TO_STRAIN[s] + RANK_TO_CARD[r] for s, r in zip(suit, rank)]
    return cards, list(score)
