from scipy.stats import multivariate_hypergeom as mhg
import copy
import itertools

_deckSize = 99
_cardsSeen = 7
_debug=False


def setDebug(state):
    global _debug
    _debug = True if state else False


def _printDebug(*toBePrinted):
    if _debug:
        print(toBePrinted)


def calculate_exact_draw(hand):
    x = []
    m = []
    deck_size_sum = 0
    hand_sum = 0
    hand_string = ''
    for cardType in hand:
        hand_sum += cardType[0]
        x.append(cardType[0])
        deck_size_sum += cardType[1]
        m.append(cardType[1])
        hand_string += f'{cardType[0]}/{cardType[1]} {cardType[2]}, '
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


def _calculate_next_draw(hand):
    hand_copy = copy.deepcopy(hand)

    index = len(hand)-1

    # make sure there is another card in hand to increment
    while index >= 0:
        next_card_type = hand_copy[index]
        max_count = next_card_type[3] if len(next_card_type) == 4 else next_card_type[1]
        hand_count = sum([ct[0] for ct in hand_copy if ct])
        if hand_count >= _cardsSeen or next_card_type[0] >= max_count:
            hand_copy[index][0] = _target_cards[index][0]
            index -= 1
        else:
            hand_copy[index][0] += 1
            return hand_copy

    return None


def getHandChance(target_hand, turns=0, deck_size=99):
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


def getDrawChance(target_cards, turn=0, num_draws=1):
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


def getHandChanceWithStartingMana(target_cards, start_mana, end_mana, turns=0, deck_size=99):
    global _cardsSeen, _deckSize
    _deckSize = deck_size
    _cardsSeen = 7 + turns

    max_start_mana = start_mana[3] if len(start_mana) >= 4 else start_mana[1]
    mana_chance = {}
    hands = {}
    cards_copy = copy.deepcopy(target_cards)
    cards_copy = [card for card in cards_copy if card[2] != 'mana']
    # number of non-land cards in opening hand
    num_cards = sum([card[0] for card in cards_copy])

    # for each amount of mana in opening hand
    # calculate possible starting hands
    # and card draws needed to have the target cards in hand
    for mana in range(start_mana[0], max_start_mana + 1):
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
                start_mana_in_hand[0] = mana
                if len(start_mana_in_hand) >= 4:
                    start_mana_in_hand[3] = mana
                else:
                    start_mana_in_hand.append(mana)
                draws_for_end_mana = copy.deepcopy(end_mana)
                draws_for_end_mana[0] -= mana if draws_for_end_mana[0] >= mana else draws_for_end_mana[0]
                draws_for_end_mana[1] -= mana
                if len(draws_for_end_mana) >= 4:
                    draws_for_end_mana[3] -= mana
                    if draws_for_end_mana[3] < 0:
                        hands[mana]['start'].append([start_mana_in_hand])
                        hands[mana]['draws'].append([draws_for_end_mana])
                        mana_chance[mana].append(0)
                        continue
                start_hand = [start_mana_in_hand]
                draws = [draws_for_end_mana]
                for index in combination:
                    cards_in_hand[index][0] -= 1
                for index in range(len(cards_in_hand)):
                    missing_card = copy.deepcopy(cards_in_hand[index])
                    missing_card[0] = (cards_copy[index][0] - cards_in_hand[index][0]) if cards_copy[index][0] > cards_in_hand[index][0] else 0
                    missing_card[1] = cards_copy[index][1] - cards_in_hand[index][0]
                    if len(missing_card) >= 4:
                        missing_card[3] -= cards_in_hand[index][0]

                    draws.append(missing_card)
                for card_type in cards_in_hand:
                    if len(card_type) >= 4:
                        card_type[3] = card_type[0]
                    else:
                        card_type.append(card_type[0])

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


def _card_combinations_as_indexes(hand, choose):
    cards = []
    for index in range(len(hand)):
        cards.extend([index] * hand[index][0])

    return list(dict.fromkeys(itertools.combinations(cards, choose)))


def get_tutor_combinations(target_cards, num_tutors, total_mana):
    hands = list()
    hands.append(copy.deepcopy(target_cards))
    total_parts = sum(part[0] for part in target_cards)
    for num_swaps in range(1, min(num_tutors, total_parts) + 1):
        combination_indexes = _card_combinations_as_indexes(target_cards, num_swaps)

        for replace_indexes in combination_indexes:
            hand_copy = copy.deepcopy(target_cards)
            _printDebug(replace_indexes)
            for index in replace_indexes:
                hand_copy[index][0] -= 1
                if len(hand_copy[index]) >= 4:
                    hand_copy[index][3] = hand_copy[index][0]
                else:
                    hand_copy[index].append(hand_copy[index][0])

            hand_copy.append([num_swaps, num_tutors, 'tutors'])
            hands.append(hand_copy)
    for hand in hands:
        hand.append(total_mana)
    return hands


def getHandChanceWithStartingManaAndTutors(target_cards, num_tutors, target_mana, starting_mana, turn):
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
