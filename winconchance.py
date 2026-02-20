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
    olivia_total_mana = 44
    for mana in range(olivia_total_mana-3, olivia_total_mana + 4):
        open_mana = Card('mana', 3, mana, 7)
        low = Card('mana', 0, mana, 2)
        mid = Card('mana', 3, mana, 6)
        high = Card('mana', 7, mana)

        chance = hand_calculator.getHandChance([open_mana], 0)
        results.append(f'3-5 mana in hand with {mana} mana in deck: {chance * 100}')

        chance = 0
        turn4_chance = hand_calculator.getHandChanceWithStartingMana([], open_mana, low, 4)
        chance += turn4_chance
        results.append(f'    0-2 mana in hand turn 4: {turn4_chance * 100}')
        turn4_chance = hand_calculator.getHandChanceWithStartingMana([], open_mana, mid, 4)
        chance += turn4_chance
        results.append(f'    and then 3-6 mana in hand turn 4: {turn4_chance * 100}')
        turn4_chance = hand_calculator.getHandChanceWithStartingMana([], open_mana, high, 4)
        chance += turn4_chance
        results.append(f'    and then 7+ mana in hand turn 4: {turn4_chance * 100}')
        results.append(f'    total: {chance * 100}')

    for result in results:
        print(result)


mana_chance()
