from scipy.stats import multivariate_hypergeom as mhg
from typing import List, Dict, cast, Literal, Tuple
import copy
import itertools

_deckSize = 99
_cardsSeen = 7
_debug = False
_target_cards = None

type ParsedList[T] = List[T | ParsedList[T]]


class Card:
    def __init__(self, card_type, in_hand, deck_total, hand_max=None):
        self.card_type = card_type
        self.in_hand = in_hand
        self.deck_total = deck_total
        self.hand_max = hand_max

    def __str__(self):
        string = f'{self.in_hand} {self.card_type} of {self.deck_total} max {self.hand_max}'
        return string

    def __repr__(self):
        return self.__str__()


Operator = Literal['AND', 'OR']


class CardQuery:
    def __init__(self, cards: List[Card | CardQuery], operator: Operator = 'OR'):
        self.cards = cards
        self.operator = operator

    def __str__(self):
        return "\n OR ".join([card.__str__() for card in self.cards])

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        return iter(self.cards)


class HandAfterTurns:
    def __init__(self, cards: List[Card | CardQuery], turns_passed=0):
        self.cards = cards
        self.turns_passed = turns_passed

    def __str__(self):
        string = f'{self.turns_passed} Turns Passed, Cards in hand: {[str(card) for card in self.cards]}'
        return string

    def __repr__(self):
        return self.__str__()


def setDebug(state):
    global _debug
    _debug = True if state else False


def _printDebug(*toBePrinted):
    if _debug:
        print(toBePrinted)


def calculate_exact_draw(hand: List[Card]):
    x = []
    m = []
    deck_size_sum = 0
    hand_sum = 0
    hand_string = ''
    for cardType in hand:
        hand_sum += cardType.in_hand
        x.append(cardType.in_hand)
        deck_size_sum += cardType.deck_total
        m.append(cardType.deck_total)
        hand_string += f'{cardType.in_hand}/{cardType.deck_total} {cardType.card_type}, '
    hand_string = '[' + hand_string[:-2] + '}'

    if hand_sum > _cardsSeen or deck_size_sum > _deckSize:
        _printDebug("Too many cards. Check Hand Size and Deck Size.")
        return 0

    x.append(_cardsSeen - hand_sum)
    m.append(_deckSize - deck_size_sum)

    # Calculate the probability mass function (PMF)
    probability = mhg.pmf(x=x, m=m, n=_cardsSeen)
    _printDebug(f'{_deckSize} cards in deck, drawing {_cardsSeen}', f'{hand_string}:{probability}')
    return probability


def _calculate_next_draw(hand: List[Card]):
    hand_copy = copy.deepcopy(hand)

    index = len(hand) - 1

    # make sure there is another card in hand to increment
    while index >= 0:
        next_card_type = hand_copy[index]
        max_count = next_card_type.hand_max if next_card_type.hand_max is not None else next_card_type.deck_total
        hand_count = sum([ct.in_hand for ct in hand_copy if ct])
        if hand_count >= _cardsSeen or next_card_type.in_hand >= max_count:
            hand_copy[index].in_hand = _target_cards[index].in_hand
            index -= 1
        else:
            hand_copy[index].in_hand += 1
            return hand_copy

    return None


def getHandChance(hand_after_turns: HandAfterTurns, deck_size=99):
    global _target_cards, _cardsSeen, _deckSize
    _deckSize = deck_size
    _target_cards = hand_after_turns.cards
    _cardsSeen = 7 + hand_after_turns.turns_passed
    prob_sum = 0
    next_hand = copy.deepcopy(hand_after_turns.cards)

    def dfs(cards: CardQuery | List[Card | CardQuery]) -> List[List[Card]]:
        hands: List[List[Card]] = []
        req_cards: List[Card] = []
        or_cards: List[Card] = []
        queued_cards: List[CardQuery] = []
        for card in cards:
            try:
                queued_cards.append(card) if card.cards else None
            except AttributeError:
                try:
                    if cards.operator == 'OR':
                        or_cards.append(card)
                    else:
                        req_cards.append(card)
                except AttributeError:
                    req_cards.append(card)

        hands.extend(get_card_combinations(req_cards, or_cards))

        for card in queued_cards:
            new_hands = []
            for hand in hands:
                for combos in dfs(card):
                    hand_copy = copy.deepcopy(hand)
                    hand_copy.extend(combos)
                    new_hands.append(hand_copy)
            hands = new_hands

        new_hands = []
        for hand in hands:
            card_types = {}
            for card in hand:
                card_types.setdefault(card.card_type, []).append(card)
            new_hand = []
            for card_type_list in card_types.values():
                if len(card_type_list) == 1:
                    new_hand.extend(card_type_list)
                else:
                    new_card: Card = copy.deepcopy(card_type_list[0])
                    new_card.in_hand = 0
                    new_card.hand_max = None
                    for card in card_type_list:
                        if card.hand_max is not None and new_card.hand_max is None:
                            new_card.hand_max = card.hand_max
                        elif card.hand_max is not None and new_card.hand_max is not None:
                            new_card.hand_max += card.hand_max
                        new_card.in_hand += card.in_hand
                    new_hand.append(new_card)
            new_hands.append(new_hand)

        return new_hands

    while next_hand:
        try:
            prob_sum += calculate_exact_draw(next_hand)
            next_hand = _calculate_next_draw(next_hand)
        except AttributeError:
            # CardQuery in hand generate all possible hands for CardQuery
            possible_hands = dfs(next_hand)
            for hand in possible_hands:
                prob_sum += getHandChance(HandAfterTurns(hand, hand_after_turns.turns_passed))
            next_hand = None

    _printDebug('chance of target hand:', prob_sum)
    return prob_sum


def getDrawChance(hand_after_turns: HandAfterTurns, start_turn=0):
    global _target_cards, _cardsSeen, _deckSize
    _deckSize = 99 - 7 - start_turn
    _target_cards = hand_after_turns.cards
    _cardsSeen = hand_after_turns.turns_passed
    probSum = 0
    nextHand = copy.deepcopy(hand_after_turns.cards)
    while nextHand:
        probSum += calculate_exact_draw(nextHand)
        nextHand = _calculate_next_draw(nextHand)

    _printDebug('chance of target draw', probSum)
    return probSum


def getHandChanceWithStartingMana(hand_after_turns: HandAfterTurns, start_mana: Card, end_mana: Card, deck_size=99):
    global _cardsSeen, _deckSize
    _deckSize = deck_size
    _cardsSeen = 7 + hand_after_turns.turns_passed

    max_start_mana = start_mana.hand_max if start_mana.hand_max is not None else start_mana.deck_total
    mana_chance = {}
    hands = {}
    cards_copy = copy.deepcopy(hand_after_turns.cards)
    cards_copy = [card for card in cards_copy if card.card_type != 'mana']
    # number of non-land cards in opening hand
    num_cards = sum([card.in_hand for card in cards_copy])

    # for each amount of mana in opening hand
    # calculate possible starting hands
    # and card draws needed to have the target cards in hand
    for mana in range(start_mana.in_hand, max_start_mana + 1):
        hands[mana] = {
            'start': [],
            'draws': []
        }
        mana_chance[mana] = []
        for num_targets_to_draw in range(0, num_cards + 1):
            target_combinations = _card_combinations_as_indexes(cards_copy, num_targets_to_draw)
            for combination in target_combinations:
                cards_in_hand = copy.deepcopy(cards_copy)
                start_mana_in_hand = copy.deepcopy(start_mana)
                start_mana_in_hand.in_hand = mana
                start_mana_in_hand.hand_max = mana
                draws_for_end_mana = copy.deepcopy(end_mana)
                draws_for_end_mana.in_hand -= mana if draws_for_end_mana.in_hand >= mana else draws_for_end_mana.in_hand
                draws_for_end_mana.deck_total -= mana
                if draws_for_end_mana.hand_max is not None:
                    draws_for_end_mana.hand_max -= mana
                    if draws_for_end_mana.hand_max < 0:
                        hands[mana]['start'].append([start_mana_in_hand])
                        hands[mana]['draws'].append([draws_for_end_mana])
                        mana_chance[mana].append(0)
                        continue
                start_hand = [start_mana_in_hand]
                draws = [draws_for_end_mana]
                for index in combination:
                    cards_in_hand[index].in_hand -= 1
                for index in range(len(cards_in_hand)):
                    missing_card = copy.deepcopy(cards_in_hand[index])
                    missing_card.in_hand = (cards_copy[index].in_hand - cards_in_hand[index].in_hand) if cards_copy[
                                                                                                             index].in_hand > \
                                                                                                         cards_in_hand[
                                                                                                             index].in_hand else 0
                    missing_card.deck_total = cards_copy[index].deck_total - cards_in_hand[index].in_hand
                    if missing_card.hand_max is not None:
                        missing_card.hand_max -= cards_in_hand[index].in_hand

                    draws.append(missing_card)
                for card_type in cards_in_hand:
                    card_type.hand_max = card_type.in_hand

                start_hand.extend(cards_in_hand)
                hands[mana]['start'].append(start_hand)
                hands[mana]['draws'].append(draws)
                mana_chance[mana].append(getHandChance(HandAfterTurns(start_hand)) * getDrawChance(
                    HandAfterTurns(draws, hand_after_turns.turns_passed), 0))
    _printDebug(hands)
    probSum = 0
    for mana in mana_chance:
        mana_sum = sum(chance for chance in mana_chance[mana])
        _printDebug(f"chance for {mana} mana: {mana_sum}")
        probSum += mana_sum
    _printDebug(hands)

    _printDebug('chance of target hand:', probSum)
    return probSum


# TODO: get chance to hit hands in turn order
# def get_hands_in_order(hands_after_turns: List[HandAfterTurns], deck_size=99):
#     global _cardsSeen, _deckSize
#     _deckSize = deck_size
#     _cardsSeen = 7 + hands_after_turns[-1].turns_passed
#
#     turns_with_cards = {}
#     for hand in reversed(hands_after_turns):
#         turns_with_cards.setdefault(hand.turns_passed, hand.cards)
#
#
#     max_start_mana = start_mana.hand_max if start_mana.hand_max is not None else start_mana.deck_total
#     mana_chance = {}
#     hands = {}
#     cards_copy = copy.deepcopy(hand_after_turns.cards)
#     cards_copy = [card for card in cards_copy if card.card_type != 'mana']
#     # number of non-land cards in opening hand
#     num_cards = sum([card.in_hand for card in cards_copy])
#
#     # for each amount of mana in opening hand
#     # calculate possible starting hands
#     # and card draws needed to have the target cards in hand
#     for mana in range(start_mana.in_hand, max_start_mana + 1):
#         hands[mana] = {
#             'start': [],
#             'draws': []
#         }
#         mana_chance[mana] = []
#         for num_targets_to_draw in range(0, num_cards + 1):
#             target_combinations = _card_combinations_as_indexes(cards_copy, num_targets_to_draw)
#             for combination in target_combinations:
#                 cards_in_hand = copy.deepcopy(cards_copy)
#                 start_mana_in_hand = copy.deepcopy(start_mana)
#                 start_mana_in_hand.in_hand = mana
#                 start_mana_in_hand.hand_max = mana
#                 draws_for_end_mana = copy.deepcopy(end_mana)
#                 draws_for_end_mana.in_hand -= mana if draws_for_end_mana.in_hand >= mana else draws_for_end_mana.in_hand
#                 draws_for_end_mana.deck_total -= mana
#                 if draws_for_end_mana.hand_max is not None:
#                     draws_for_end_mana.hand_max -= mana
#                     if draws_for_end_mana.hand_max < 0:
#                         hands[mana]['start'].append([start_mana_in_hand])
#                         hands[mana]['draws'].append([draws_for_end_mana])
#                         mana_chance[mana].append(0)
#                         continue
#                 start_hand = [start_mana_in_hand]
#                 draws = [draws_for_end_mana]
#                 for index in combination:
#                     cards_in_hand[index].in_hand -= 1
#                 for index in range(len(cards_in_hand)):
#                     missing_card = copy.deepcopy(cards_in_hand[index])
#                     missing_card.in_hand = (cards_copy[index].in_hand - cards_in_hand[index].in_hand) if cards_copy[index].in_hand > cards_in_hand[index].in_hand else 0
#                     missing_card.deck_total = cards_copy[index].deck_total - cards_in_hand[index].in_hand
#                     if missing_card.hand_max is not None:
#                         missing_card.hand_max -= cards_in_hand[index].in_hand
#
#                     draws.append(missing_card)
#                 for card_type in cards_in_hand:
#                     card_type.hand_max = card_type.in_hand
#
#                 start_hand.extend(cards_in_hand)
#                 hands[mana]['start'].append(start_hand)
#                 hands[mana]['draws'].append(draws)
#                 mana_chance[mana].append(getHandChance(HandAfterTurns(start_hand)) * getDrawChance(HandAfterTurns(draws, hand_after_turns.turns_passed), 0))
#     _printDebug(hands)
#     probSum = 0
#     for mana in mana_chance:
#         mana_sum = sum(chance for chance in mana_chance[mana])
#         _printDebug(f"chance for {mana} mana: {mana_sum}")
#         probSum += mana_sum
#     _printDebug(hands)
#
#     _printDebug('chance of target hand:', probSum)
#     return probSum


def _card_combinations_as_indexes(hand: List[Card], choose: int):
    cards = []
    for index in range(len(hand)):
        cards.extend([index] * hand[index].in_hand)

    return list(dict.fromkeys(itertools.combinations(cards, choose)))


def get_tutor_combinations(target_cards: List[Card], num_tutors: int, total_mana: Card):
    hands = list()
    hands.append(copy.deepcopy(target_cards))
    total_parts = sum(part.in_hand for part in target_cards)
    for num_swaps in range(1, min(num_tutors, total_parts) + 1):
        combination_indexes = _card_combinations_as_indexes(target_cards, num_swaps)

        for replace_indexes in combination_indexes:
            hand_copy = copy.deepcopy(target_cards)
            _printDebug(replace_indexes)
            for index in replace_indexes:
                hand_copy[index].in_hand -= 1
                hand_copy[index].hand_max = hand_copy[index].in_hand

            hand_copy.append(Card('tutors', num_swaps, num_tutors))
            hands.append(hand_copy)
    for hand in hands:
        hand.append(total_mana)
    return hands


def get_card_combinations(req_cards: List[Card], or_cards: List[Card]) -> List[List[Card]]:
    hands: List[List[Card]] = [copy.deepcopy(or_cards)]

    def sum_nested(nested_list: List[Card | CardQuery]):
        total = 0
        for item in nested_list:
            try:
                total += sum_nested(item.cards)
            except AttributeError:
                total += item.in_hand
        return total

    total_parts = sum_nested(or_cards)
    for num_swaps in range(1, total_parts):
        combination_indexes = _card_combinations_as_indexes(or_cards, num_swaps)
        for replace_indexes in combination_indexes:
            hand_copy = copy.deepcopy(or_cards)
            _printDebug(replace_indexes)
            for index in replace_indexes:
                hand_copy[index].in_hand -= 1
                hand_copy[index].hand_max = hand_copy[index].in_hand
            hands.append(hand_copy)
    for hand in hands:
        hand.extend(req_cards)
    return hands


def getHandChanceWithStartingManaAndTutors(hand_after_turns: HandAfterTurns, num_tutors: int, target_mana: Card,
                                           starting_mana: Card):
    results = []
    starting_mana_multiplier3 = getHandChance(HandAfterTurns([starting_mana], 0))
    results.append(f'opening mana chance: {starting_mana_multiplier3 * 100}')
    results.append(f'Probabilities for Turn {hand_after_turns.turns_passed}')
    # win % straight up (no tutors, no starting mana)
    straight_hand = copy.deepcopy(hand_after_turns)
    straight_hand.cards.append(target_mana)
    prob_straight = getHandChance(straight_hand)
    results.append(f'straight up (tutors, starting hand not considered): {prob_straight * 100}')

    # win % with tutors (not considered: starting mana)
    win_hands = get_tutor_combinations(hand_after_turns.cards, num_tutors, target_mana)
    prob_tutors = sum([getHandChance(HandAfterTurns(hand, hand_after_turns.turns_passed)) for hand in win_hands])
    results.append(f'with tutors (starting hand not considered): {prob_tutors * 100}')

    # win % with starting mana (not considered: tutors)
    winning_hand_no_tutors = copy.deepcopy(hand_after_turns)
    prob_start_mana = getHandChanceWithStartingMana(winning_hand_no_tutors, starting_mana, target_mana)
    results.append(f'with starting mana (tutors not considered):: {prob_start_mana}')

    # win % with starting mana and tutors
    prob_smt = sum(
        [getHandChanceWithStartingMana(HandAfterTurns(hand, hand_after_turns.turns_passed), starting_mana, target_mana)
         for hand in win_hands])
    results.append(f'with starting mana and tutors: {prob_smt * 100}')

    for result in results:
        print(result)
    return prob_smt


# SET MANA 40
# GET { 5 MANA } TURN 0
class Query:
    parsed_query: ParsedList
    probability: float

    def __init__(self, query_string: str):
        self.query_string = query_string.strip()
        self.item_index = 0
        self.current_depth = 0
        self.card_types_in_deck: Dict[str, int] = {}
        self.init_card_totals()

    def __str__(self):
        string = f'{self.probability}'
        return string

    def __repr__(self):
        return self.__str__()

    def init_card_totals(self):
        query_lines = []
        for line in self.query_string.splitlines():
            line = line.strip()
            if line[:3] == "SET":
                config = line.split()
                self.card_types_in_deck[config[1]] = int(config[2])
            else:
                query_lines.append(line)
        self.query(" ".join(query_lines))

    def _parse(self, expr: str, start='(', end=')') -> Tuple[ParsedList[str], bool]:
        def _helper(it) -> Tuple[ParsedList[str], bool]:
            items: ParsedList = []
            for item in it:
                if item == start:
                    result, close = _helper(it)
                    if not close:
                        raise ValueError("bad expression -- unbalanced parentheses")
                    items.append(result)
                elif self._comma_check(item) == end:
                    return items, True
                else:
                    items.append(item)
            return items, False

        return _helper(iter(expr.split()))

    def _parse_query(self, expr: str) -> ParsedList[str]:
        parsed_query, closed = self._parse(expr, '{', '}')
        for index, query_item in enumerate(parsed_query):
            if not isinstance(query_item, str):
                hand_content = " ".join(query_item)
                parsed_query[index], closed = self._parse(hand_content, '(', ')')
        return parsed_query

    def _parse_card(self, expr: str):
        print('test')

    def query(self, expr):
        def _get_next_item(inc_by=0):
            self.item_index += inc_by
            return self.parsed_query[self.item_index]

        def _process_hand(hand_query_item: ParsedList[str]) -> HandAfterTurns:
            hand_query_item = _get_next_item(1)
            if not isinstance(hand_query_item, str):
                hand_after_turns = HandAfterTurns(self.get_next_hand(hand_query_item), hand_query_item)
                hand_query_item = _get_next_item(1)
                if hand_query_item.upper() == 'TURN':
                    hand_after_turns.turns_passed = int(self.parsed_query[self.item_index + 1])
                    self.item_index += 2
                else:
                    raise ValueError("bad expression -- missing TURN value")
            else:
                raise ValueError("bad expression -- missing or unbalanced brackets")
            return hand_after_turns

        self.parsed_query = self._parse_query(expr)
        hands: List[HandAfterTurns] = []
        while self.item_index < len(self.parsed_query):
            query_item = _get_next_item()
            if query_item.upper() == "GET":
                hands.append(_process_hand(query_item))
                continue
            if query_item.upper() == 'THEN':
                hands.append(_process_hand(query_item))
                continue
            if query_item.upper() == 'AND':
                self.item_index += 1
                continue
            if query_item.upper() == 'OR':
                self.item_index += 1
                continue
        if len(hands) == 1:
            self.probability = getHandChance(hands[0])
        elif len(hands) > 1:
            self.probability = getHandChance(hands[0]) * getHandChance(hands[1])

    def get_next_hand(self, card_query: ParsedList[str]):
        hand = []
        index = 0
        while index < len(card_query):
            card, index = self.get_next_card(card_query, index)
            hand.append(card)
        return hand

    def _comma_check(self, string: str) -> str:
        try:
            string.index(',')  # throws error if substring is not found
            return string.replace(',', '')
        except ValueError:
            return string

    def get_next_card(self, card_query: ParsedList[str], index) -> Tuple[Card, int]:
        if isinstance(card_query[index], str):
            in_hand = int(card_query[index])
            card_type = self._comma_check(card_query[index + 1])
            deck_total = self.card_types_in_deck[card_type]
            card = Card(card_type, in_hand, deck_total)
            index += 2
            if index < len(card_query):
                if card_query[index] == 'MAX':
                    card.hand_max = int(self._comma_check(card_query[index + 1]))
                    index += 2
                if card_query[index] == 'OR':
                    index += 1
        else:
            sub_index = 0
            card = CardQuery([])
            while sub_index < len(card_query[index]):
                sub_card, sub_index = self.get_next_card(card_query[index], sub_index)
                card.cards.append(sub_card)
            index += 1
        return card, index
