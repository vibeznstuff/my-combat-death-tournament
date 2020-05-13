from combatant import Combatant
from fight import fight

def run_tournament(combatants):
    if len(combatants) > 2:
        split = int(len(combatants)/2)

        bracket_one = combatants[:split]
        bracket_two = combatants[-split:]

        return fight(run_tournament(bracket_one), run_tournament(bracket_two))

    elif len(combatants) == 2:
        print("Going in")
        winner = fight(combatants[0], combatants[1])
        print(winner.name)
        return winner


combatant_list = []

my_profile = {
    'name': 'Vibey Wednesday',
    'strength': 0,
    'defense': 0,
    'agility': 0,
    'stamina': 0,
    'wisdom': 0
}

num_ai_combatants = 4

while num_ai_combatants > 0:
    num_ai_combatants = num_ai_combatants - 1
    combatant_list.append(Combatant())
    
winner = run_tournament(combatant_list)
print("Winner of the tournament is {}!".format(winner.name))
winner.print_stats()
