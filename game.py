from combatant import Combatant
from fight import fight

combatant_one = Combatant()
combatant_one.print_stats()

combatant_two = Combatant()
combatant_two.print_stats()

winner = fight(combatant_one, combatant_two)