"""Shared raw primitive for every statistic in this package that
needs to know the outcome of EVERY legal opening-lead choice, not
just the one that was actually made -- unlike _board_trajectory.py,
which scores one specific recorded card or sequence."""

from dds3 import solve_board_pbn

from d_dolar.statistics._seats import (
    CARD_RANK_TO_INT,
    LEADER_OF,
    RANK_TO_CARD,
    SEAT_TO_FIRST,
    STRAIN_TO_TRUMP,
    SUIT_TO_STRAIN,
)


def _solve_opening_lead(
    hands: str, declarer: str | None, contract: str | None
) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...], tuple[int, ...]] | None:
    """Internal: one solve_board_pbn call, sliced to its own `cards`
    count. Returns dds3's raw per-choice encoding -- (suit, rank,
    equals, score), each a tuple since slicing dds3's own
    tuple-shaped result yields a tuple -- or None if
    declarer/contract is falsy. lead_choices and
    recorded_lead_defender_tricks both build on this single call;
    with_defence_statistics calls it directly too, so the one
    necessary solve per row is never repeated."""
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


def recorded_lead_defender_tricks(
    hands: str, declarer: str | None, contract: str | None, lead: str | None, play: str | None
) -> int | None:
    """The defender-tricks score solve_board_pbn assigns to the
    actual opening lead -- `lead`, falling back to `play`'s first
    card when `lead` is absent (same precedence as lead_trajectory;
    specs/d-dolar.md) -- located by matching the card's (suit,
    rank) to one of lead_choices' equivalence groups via `equals`'s
    bitmask (bit `rank` sets membership within a group's own suit
    -- confirmed empirically, see specs/lead-matters.md). None
    under _solve_opening_lead's own None condition, if neither
    `lead` nor `play` supplies a usable card, or if the effective
    lead isn't actually held by the leader (falls through every
    group -- the same "not held" case lead_trajectory already
    returns None for)."""
    solved = _solve_opening_lead(hands, declarer, contract)
    if solved is None:
        return None
    effective_lead = lead if lead else (play.split("_")[0] if play else None)
    if not effective_lead:
        return None

    lead_suit = STRAIN_TO_TRUMP[effective_lead[0]]
    lead_rank = CARD_RANK_TO_INT[effective_lead[1]]
    suit, rank, equals, score = solved
    for s, r, eq, sc in zip(suit, rank, equals, score):
        if s == lead_suit and (r == lead_rank or eq & (1 << lead_rank)):
            return sc
    return None
