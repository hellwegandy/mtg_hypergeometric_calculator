import hand_calculator

turn_end = 5



rows = []
tutors = 1


def calc_win_chances():
    results = []
    for turn in range(0, turn_end+1):
        olivia_total_mana = 44
        olivia_tutors = 4
        olivia_end_mana = [5, olivia_total_mana, 'mana']
        print("Olivia")
        hand_calculator.getHandChanceWithStartingManaAndTutors([[1, 2, 'gain triggers'], [1, 2, 'loss triggers']], olivia_tutors, olivia_end_mana, [3, olivia_total_mana, 'mana', 5], turn)

        print("Blythe")
        blythe_total_mana = 40
        blythe_end_mana = [4, blythe_total_mana, 'mana']
        hand_calculator.getHandChanceWithStartingManaAndTutors([[1, 2, 'self damage']],
                                                               0, blythe_end_mana,
                                                               [2, blythe_total_mana, 'mana', 4], turn)

        mill_total_mana = 42
        mill_tutors = 2
        mill_end_mana = [4, mill_total_mana, 'mana']
        mill_win_hands = hand_calculator.get_tutor_combinations([[1, 2, 'illusionists bracers'], [2, 10, 'untappers']], mill_tutors, mill_end_mana)
        chance = sum([hand_calculator.getHandChance(hand, turn) for hand in mill_win_hands])
        results.append(f'Mill win chance turn {turn}: {chance * 100}')
        chance = sum([hand_calculator.getHandChanceWithStartingMana(hand, [3, mill_total_mana, 'mana', 5], mill_end_mana, turn) for hand in mill_win_hands])
        results.append(f'Mill (starting mana) win chance turn {turn}: {chance * 100}')

    for result in results:
        print(result)


def mana_chance():
    results = []
    olivia_total_mana = 44
    for mana in range(olivia_total_mana-3, olivia_total_mana + 4):
        open_mana = [3, mana, 'mana', 7]
        low = [0, mana, 'mana', 2]
        mid = [3, mana, 'mana', 6]
        high = [7, mana, 'mana']

        chance = hand_calculator.getHandChance([open_mana], 0)
        results.append(f'3-5 mana in hand with {mana} mana in deck: {chance * 100}')

        turn4_chance = hand_calculator.getHandChanceWithStartingMana([], open_mana, low, 4)
        results.append(f'    0-2 mana in hand turn 4: {turn4_chance * 100}')
        turn4_chance = hand_calculator.getHandChanceWithStartingMana([], open_mana, mid, 4)
        results.append(f'    and then 3-6 mana in hand turn 4: {turn4_chance * 100}')
        turn4_chance = hand_calculator.getHandChanceWithStartingMana([], open_mana, high, 4)
        results.append(f'    and then 7+ mana in hand turn 4: {turn4_chance * 100}')

    for result in results:
        print(result)


mana_chance()
