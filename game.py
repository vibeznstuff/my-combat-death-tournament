from combatant import Combatant
from fight import fight



def run_tournament(combatants, log_results=True, spectate=False, tournament_start=False):

    if tournament_start:
        global round_number
        round_number = 1

    if len(combatants) > 2:
        split = int(len(combatants)/2)

        bracket_one = combatants[:split]
        bracket_two = combatants[-split:]

        return fight(run_tournament(bracket_one), run_tournament(bracket_two), log_results=log_results, spectate=spectate, round_number=round_number)

    elif len(combatants) == 2:
        print("Going in")
        winner = fight(combatants[0], combatants[1], log_results=log_results, spectate=spectate, round_number=round_number)
        round_number = round_number + 1
        print(winner.name)
        return winner


def generate_combatants(num_combatants=4):
    num_ai_combatants = num_combatants
    combatant_list = []

    while num_ai_combatants > 0:
        num_ai_combatants = num_ai_combatants - 1
        combatant_list.append(Combatant())

    return combatant_list


# Decide how many AI fighters for tournament
combatant_list = generate_combatants(31)

# Add manually created fighter
my_fighter = {
    'name': 'Vibey Wednesday',
    'strength': 10,
    'defense': 5,
    'agility': 10,
    'stamina': 0,
    'wisdom': 5
}
combatant_list.append(Combatant(my_fighter))

# Clear out contents of tournament log
out_file = open('tournament_log.csv', 'w', newline='')
out_file.close()

winner = run_tournament(combatant_list, spectate=False, tournament_start=True)

print("Winner of the tournament is {}!".format(winner.name))
winner.print_stats()

out_file.close()
