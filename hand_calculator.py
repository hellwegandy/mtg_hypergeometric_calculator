from scipy.stats import multivariate_hypergeom as mhg
from typing import List
import copy
import itertools

_deckSize = 99
_cardsSeen = 7
_debug=False


class Card:
    def __init__(self, card_type, in_hand, deck_total, hand_max=None):
        self.card_type = card_type
        self.in_hand = in_hand
        self.deck_total = deck_total
        self.hand_max = hand_max

    def __str__(self):
        string = f'{self.in_hand} {self.card_type} of {self.deck_total} max {self.hand_max}'
        return string


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

    index = len(hand)-1

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


def getHandChance(target_hand: List[Card], turns=0, deck_size=99):
    global _target_cards, _cardsSeen, _deckSize
    _deckSize = deck_size
    _target_cards = target_hand
    _cardsSeen = 7 + turns
    probSum = 0
    nextHand = copy.deepcopy(target_hand)
    while nextHand:
        probSum += calculate_exact_draw(nextHand)
        nextHand = _calculate_next_draw(nextHand)

    _printDebug('chance of target hand:', probSum)
    return probSum


def getDrawChance(target_cards: List[Card], turn=0, num_draws=1):
    global _target_cards, _cardsSeen, _deckSize
    _deckSize = 99 - 7 - turn
    _target_cards = target_cards
    _cardsSeen = num_draws
    probSum = 0
    nextHand = copy.deepcopy(target_cards)
    while nextHand:
        probSum += calculate_exact_draw(nextHand)
        nextHand = _calculate_next_draw(nextHand)

    _printDebug('chance of target draw', probSum)
    return probSum


def getHandChanceWithStartingMana(target_cards: List[Card], start_mana: Card, end_mana: Card, turns=0, deck_size=99):
    global _cardsSeen, _deckSize
    _deckSize = deck_size
    _cardsSeen = 7 + turns

    max_start_mana = start_mana.hand_max if start_mana.hand_max is not None else start_mana.deck_total
    mana_chance = {}
    hands = {}
    cards_copy = copy.deepcopy(target_cards)
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
                    missing_card.in_hand = (cards_copy[index].in_hand - cards_in_hand[index].in_hand) if cards_copy[index].in_hand > cards_in_hand[index].in_hand else 0
                    missing_card.deck_total = cards_copy[index].deck_total - cards_in_hand[index].in_hand
                    if missing_card.hand_max is not None:
                        missing_card.hand_max -= cards_in_hand[index].in_hand

                    draws.append(missing_card)
                for card_type in cards_in_hand:
                    card_type.hand_max = card_type.in_hand

                start_hand.extend(cards_in_hand)
                hands[mana]['start'].append(start_hand)
                hands[mana]['draws'].append(draws)
                mana_chance[mana].append(getHandChance(start_hand, 0) * getDrawChance(draws, 0, turns))
    _printDebug(hands)
    probSum = 0
    for mana in mana_chance:
        mana_sum = sum(chance for chance in mana_chance[mana])
        _printDebug(f"chance for {mana} mana: {mana_sum}")
        probSum += mana_sum
    _printDebug(hands)

    _printDebug('chance of target hand:', probSum)
    return probSum


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
                if hand_copy[index].hand_max is not None:
                    hand_copy[index].hand_max = hand_copy[index].in_hand
                else:
                    hand_copy[index].append(hand_copy[index].in_hand)

            hand_copy.append([num_swaps, num_tutors, 'tutors'])
            hands.append(hand_copy)
    for hand in hands:
        hand.append(total_mana)
    return hands


def getHandChanceWithStartingManaAndTutors(target_cards: List[Card], num_tutors: int, target_mana: Card, starting_mana: Card, turn: int):
    results = []
    starting_mana_multiplier3 = getHandChance([starting_mana], 0)
    results.append(f'opening mana chance: {starting_mana_multiplier3 * 100}')
    olivia_win_hands = get_tutor_combinations(target_cards, num_tutors, target_mana)
    chance1 = sum([getHandChance(hand, turn) for hand in olivia_win_hands])
    results.append(f'win chance turn {turn}: {chance1 * 100}')
    chance = sum([getHandChanceWithStartingMana(hand, starting_mana, target_mana, turn) for hand in olivia_win_hands])
    results.append(f'(starting mana) win chance turn {turn}: {chance * 100}')
    results.append(f'(starting mana):total ratio is  {chance/chance1}')
    results.append(f'ratio vs open mana chance: {starting_mana_multiplier3/(chance/chance1)}')
    for result in results:
        print(result)
    return chance
