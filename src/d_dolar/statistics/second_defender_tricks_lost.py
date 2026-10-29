"""The second-defender-tricks-lost statistic: how many tricks the
defender who did NOT make the opening lead cost the defence, summed
across every card they played, compared to double-dummy-optimal
continuation at each point."""

from dds3 import analyse_play_pbn

from d_dolar.statistics._seats import LEADER_OF, OPPOSITE, SEAT_TO_FIRST, STRAIN_TO_TRUMP

_CLOCKWISE = ["N", "E", "S", "W"]
_SUITS = "SHDC"
_RANK_ORDER = "23456789TJQKA"


def _parse_hands(hands: str) -> dict[str, set[str]]:
    """Parses a PBN deal string ("N:AKQJT98765432... ...") into each
    seat's set of 2-character card codes (e.g. "SA", "H5")."""
    first_seat, rest = hands.split(":", 1)
    hand_strs = rest.split()
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


def _attribute_cards(
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
    parsed_hands = _parse_hands(hands)

    try:
        seats = _attribute_cards(parsed_hands, leader, cards, trump_suit)
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
