import hand_calculator
from hand_calculator import HandAfterTurns

Card = hand_calculator.Card


def calc_win_chances():
    turn_end = 5
    results = []
    for turn in range(turn_end, turn_end+1):
        olivia_total_mana = 41
        olivia_tutors = 4
        olivia_end_mana = Card('mana', 5, olivia_total_mana)
        print("Olivia")
        win_hand = [Card('gain trigger', 1, 2), Card('loss trigger', 1, 2)]
        prob = hand_calculator.getHandChanceWithStartingManaAndTutors(HandAfterTurns(win_hand, turn), olivia_tutors, olivia_end_mana, Card('mana', 3, olivia_total_mana, 5))
        results.append(prob*100)
    for result in results:
        print(result)


def mana_chance():
    results = []
    olivia_total_mana = 4
    for mana in range(olivia_total_mana-3, olivia_total_mana + 4):
        open_mana = Card('mana', 3, mana, 5)

        chance = hand_calculator.getHandChance(hand_calculator.HandAfterTurns([open_mana]))
        results.append(f'{open_mana.in_hand}-{open_mana.hand_max} mana in opening hand with {mana} mana in deck: {chance * 100}')

        turn4_mana = Card('mana', 4, mana, 6)
        turn4_chance = hand_calculator.getHandChanceWithStartingMana(hand_calculator.HandAfterTurns([], 4), open_mana, turn4_mana)
        results.append(f'then {turn4_mana.in_hand}-{turn4_mana.hand_max} in hand turn 4: {turn4_chance * 100}')
        chance = hand_calculator.getHandChance(hand_calculator.HandAfterTurns([turn4_mana], 4))
        results.append(f'{turn4_mana.in_hand}-{turn4_mana.hand_max} mana in turn 4 hand with {mana} mana in deck: {chance * 100}')

    for result in results:
        print(result)


# mana_chance()
# calc_win_chances()
# queryString = '''
#  SET MANA 41
#  SET part_a 2
#  SET part_b 2
#  SET tutor 4
#  GET { 3 MANA MAX 5 ) } TURN 0
#  THEN { 5 MANA, ( 1 part_a OR 1 tutor ), ( 1 part_b OR 1 tutor ) } TURN 5
# '''
# print(hand_calculator.Query(queryString).probability * 100)

queryString = '''
 SET MANA 41
 SET part_a 2
 SET part_b 2
 SET tutor 4
 GET { 3 MANA MAX 5 ) } TURN 0
 THEN { 5 MANA, ( 2 tutor OR ( 1 part_a AND 1 tutor ) OR ( 1 part_b AND 1 tutor ) ) } TURN 5
'''
print(hand_calculator.Query(queryString).probability * 100)

# queryString = '''
#  SET MANA 41
#  SET part_a 2
#  SET part_b 2
#  GET { 5 MANA, ( 1 part_a OR 1 part_b ) } TURN 5
# '''
# print(hand_calculator.Query(queryString).probability * 100)
#
# queryString = '''
#  SET MANA 41
#  SET part_a 2
#  SET part_b 2
#  GET { ( 5 MANA, 1 part_a ) OR ( 5 MANA, 1 part_b ) } TURN 5
# '''
# print(hand_calculator.Query(queryString).probability * 100)
#
# queryString = '''
#  SET MANA 41
#  GET { ( 5 MANA MAX 5 OR 6 MANA MAX 6 ) } TURN 5
# '''
# print(hand_calculator.Query(queryString).probability * 100)
#
# queryString = '''
#  SET MANA 41
#  GET { 5 MANA MAX 6 } TURN 5
# '''
# print(hand_calculator.Query(queryString).probability * 100)
#
# queryString = '''
#  SET MANA 46
#  SET untap 6
#  SET draw 7
#  SET staff 1
#  GET { 4 MANA, ( 1 staff OR ( 1 untap, 1 draw ) ) ) } TURN 5
# '''
# print(hand_calculator.Query(queryString).probability * 100)
#
# queryString = '''
#  SET MANA 46
#  SET untap 6
#  SET draw 7
#  SET staff 1
#  GET { 4 MANA, 1 staff } TURN 5
# '''
# staff_chance = hand_calculator.Query(queryString).probability * 100
# queryString = '''
#  SET MANA 46
#  SET untap 6
#  SET draw 7
#  SET staff 1
#  GET { 4 MANA, 1 untap, 1 draw, 0 staff MAX 0 } TURN 5
# '''
# both_chance = hand_calculator.Query(queryString).probability * 100
# print(staff_chance + both_chance)