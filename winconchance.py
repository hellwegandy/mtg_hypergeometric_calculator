import hand_calculator
Card = hand_calculator.Card


def calc_win_chances():
    turn_end = 5
    results = []
    for turn in range(0, turn_end+1):
        olivia_total_mana = 44
        olivia_tutors = 4
        olivia_end_mana = Card('mana', 5, olivia_total_mana)
        print("Olivia")
        win_hand = [Card('gain trigger', 1, 2), Card('loss trigger', 1, 2)]
        hand_calculator.getHandChanceWithStartingManaAndTutors(win_hand, olivia_tutors, olivia_end_mana, Card('mana', 3, olivia_total_mana, 5), turn)

    for result in results:
        print(result)


def mana_chance():
    results = []
    olivia_total_mana = 4
    for mana in range(olivia_total_mana-3, olivia_total_mana + 4):
        open_mana = Card('mana', 3, mana, 5)

        chance = hand_calculator.getHandChance([open_mana], 0)
        results.append(f'{open_mana.in_hand}-{open_mana.hand_max} mana in opening hand with {mana} mana in deck: {chance * 100}')

        turn4_mana = Card('mana', 4, mana, 6)
        turn4_chance = hand_calculator.getHandChanceWithStartingMana([], open_mana, turn4_mana, 4)
        results.append(f'then {turn4_mana.in_hand}-{turn4_mana.hand_max} in hand turn 4: {turn4_chance * 100}')
        chance = hand_calculator.getHandChance([turn4_mana], 4)
        results.append(f'{turn4_mana.in_hand}-{turn4_mana.hand_max} mana in turn 4 hand with {mana} mana in deck: {chance * 100}')

    for result in results:
        print(result)


# mana_chance()
# calc_win_chances()
queryString = '''
 SET MANA 40
 SET part_a 2
 SET part_b 2
 SET tutor 4
 GET { 5 MANA 1 part_a 1 part_b } TURN 5
'''
print(hand_calculator.HandQuery(queryString))
