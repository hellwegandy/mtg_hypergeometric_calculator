import hand_calculator

turn_end = 5


results = []
rows = []
tutors = 1


def olivia_win1(turn=0):
    mana_in_hand = [5, 42, 'mana sources']
    A_B = [[1, 2, 'gain triggers'], [2, 10, 'loss triggers']]
    A_1tutor_no_B = [[1, 2, 'gain triggers'], [1, tutors, 'tutors'], [0, 2, 'loss triggers', 0]]
    B_1tutor_no_A = [[1, tutors, 'tutors'], [1, 2, 'loss triggers'], [0, 2, 'gain triggers', 0]]
    no_A_no_B_2tutors = [[2, tutors, 'tutors'], [0, 2, 'gain triggers', 0], [0, 2, 'loss triggers', 0]]

    chance = 0
    for hand in [A_B, A_1tutor_no_B, B_1tutor_no_A, no_A_no_B_2tutors]:
        hand.append(mana_in_hand)
        chance += hand_calculator.getHandChance(hand, turn)

    results.append(f'Olivia win chance turn {turn}: {chance}')


def olivia_win2(turn=0):
    mana_in_hand = [5, 42, 'mana sources']
    A_B = [[1, 2, 'gain triggers'], [1, 2, 'loss triggers']]
    A_1tutor_no_B = [[1, 2, 'gain triggers'], [1, tutors, 'tutors', 1], [0, 2, 'loss triggers', 0]]
    B_1tutor_no_A = [[1, tutors, 'tutors', 1], [1, 2, 'loss triggers'], [0, 2, 'gain triggers', 0]]
    no_A_2tutors = [[2, tutors, 'tutors'], [0, 2, 'loss triggers', 0]]
    no_B_2tutors = [[2, tutors, 'tutors'], [0, 2, 'gain triggers', 0]]
    no_A_no_B_2tutors = [[2, tutors, 'tutors'], [0, 2, 'gain triggers', 0], [0, 2, 'loss triggers', 0]]

    chance = 0
    for hand in [A_B, A_1tutor_no_B, B_1tutor_no_A, no_A_2tutors, no_B_2tutors]:
        hand.append(mana_in_hand)
        chance += hand_calculator.getHandChance(hand, turn)

    no_A_no_B_2tutors.append(mana_in_hand)
    chance -= hand_calculator.getHandChance(no_A_no_B_2tutors, turn)
    results.append(f'Olivia 2 win chance turn {turn}: {chance}')


def rk_win1(turn=0):
    win_hand = [[1, 2, 'red wins'], [4, 40, 'mana sources']]

    chance = hand_calculator.getHandChance(win_hand, turn)

    results.append(f'RK win chance turn {turn}: {chance*100}')


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

    # olivia_win1(turn)
    # olivia_win2(turn)
    # rk_win1(turn)
    # rk_win2(turn)


for result in results:
    print(result)
