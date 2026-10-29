"""Shared trick-winner/card-attribution engine used by every
double-dummy-based defence statistic in this package that needs to
know which seat played which card -- a plain bridge trick-taking
simulation, with no double-dummy/dds3 involvement."""

_CLOCKWISE = ["N", "E", "S", "W"]
_SUITS = "SHDC"
_RANK_ORDER = "23456789TJQKA"


def parse_hands(hands: str) -> dict[str, set[str]]:
    """Parses a PBN deal string ("N:AKQJT98765432... ...") into each
    seat's set of 2-character card codes (e.g. "SA", "H5"). Raises
    ValueError if it doesn't contain exactly 4 space-separated hands --
    the only way attribute_cards can later be guaranteed a result for
    every seat it looks up, rather than a KeyError past this function's
    own error channel."""
    first_seat, rest = hands.split(":", 1)
    hand_strs = rest.split()
    if len(hand_strs) != 4:
        raise ValueError(f"expected 4 hands, got {len(hand_strs)}")
    start = _CLOCKWISE.index(first_seat)
    seats = [_CLOCKWISE[(start + i) % 4] for i in range(4)]
    result: dict[str, set[str]] = {}
    for seat, hand_str in zip(seats, hand_strs):
        cards: set[str] = set()
        for suit, ranks in zip(_SUITS, hand_str.split(".")):
            cards.update(suit + rank for rank in ranks)
        result[seat] = cards
    return result


def _trick_winner(cards: list[str], trump_suit: str | None) -> int:
    """Returns the index (0-3) of the winning card in a complete trick,
    `cards` given in play order (index 0 is the lead). Plain bridge
    trick-taking rules: the highest card of the suit led wins, unless a
    trump was played by someone not following suit (a ruff), in which
    case the highest trump wins. No double-dummy involved."""
    led_suit = cards[0][0]
    if trump_suit is not None:
        trumps = [i for i, card in enumerate(cards) if card[0] == trump_suit]
        if trumps:
            return max(trumps, key=lambda i: _RANK_ORDER.index(cards[i][1]))
    following = [i for i, card in enumerate(cards) if card[0] == led_suit]
    return max(following, key=lambda i: _RANK_ORDER.index(cards[i][1]))


def attribute_cards(
    hands: dict[str, set[str]], leader: str, play: list[str], trump_suit: str | None
) -> list[str]:
    """Returns the seat that played each card in `play`, in order. Also
    checks that every card was actually still held by the seat it's
    attributed to -- the only way to detect a corrupted or impossible
    play string (e.g. a card played twice), since the attribution
    itself is plain bridge rules, not double-dummy. Raises ValueError
    on a violation."""
    remaining = {seat: set(cards) for seat, cards in hands.items()}
    seats: list[str] = []
    current_leader = leader
    for i in range(0, len(play), 4):
        trick_cards = play[i : i + 4]
        start = _CLOCKWISE.index(current_leader)
        trick_seats = [_CLOCKWISE[(start + j) % 4] for j in range(len(trick_cards))]
        for seat, card in zip(trick_seats, trick_cards):
            if card not in remaining[seat]:
                raise ValueError(f"{card} is not available to {seat}")
            remaining[seat].remove(card)
            seats.append(seat)
        if len(trick_cards) == 4:
            winner_index = _trick_winner(trick_cards, trump_suit)
            current_leader = trick_seats[winner_index]
    return seats
