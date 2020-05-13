from combatant import Combatant
from random import uniform
import time

MAX_FIGHT_MOMENTS = 300

def fight(combatant_one, combatant_two):
    time.sleep(10)
    fight_timer = MAX_FIGHT_MOMENTS

    combat_one_cooldown = 20 - combatant_one.stamina
    combat_two_cooldown = 20 - combatant_two.stamina

    combat_one_attack = False
    combat_two_attack = False

    combat_one_dmg = max(combatant_one.strength - combatant_two.defense, 1)
    combat_two_dmg =  max(combatant_two.strength - combatant_one.defense, 1)

    winner = None

    while combatant_one.health > 0 and combatant_two.health > 0 and fight_timer > 0:
        print("\n Fight Timer: {}\n".format(fight_timer))
        time.sleep(2)
        fight_timer = max(0, fight_timer - 1)
        combat_one_cooldown = max(combat_one_cooldown - 1, 0)
        combat_two_cooldown = max(combat_two_cooldown - 1, 0)

        print("Cooldown for {0}: {1}".format(combatant_one.name, combat_one_cooldown))
        print("Cooldown for {0}: {1}".format(combatant_two.name, combat_two_cooldown))

        dodge_chances_1 = combatant_one.wisdom
        combat_one_dodge = False

        while dodge_chances_1 > 0 and not combat_one_dodge:
            dodge_chances_1 = dodge_chances_1 - 1
            if uniform(0,1) > 0.9:
                combat_one_dodge = True

        dodge_chances_2 = combatant_two.wisdom
        combat_two_dodge = False

        while dodge_chances_2 > 0 and not combat_two_dodge:
            dodge_chances_2 = dodge_chances_2 - 1
            if uniform(0,1) > 0.9:
                combat_two_dodge = True
    
        if combat_one_cooldown == 0:
            combat_one_attack = True
            combat_one_cooldown = 20 - combatant_one.stamina
            if combat_two_dodge:
                print("{0} dodged {1}'s Attack!".format(combatant_two.name, combatant_one.name))
                combat_one_attack = False

        if combat_two_cooldown == 0:
            combat_two_attack = True
            combat_two_cooldown = 20 - combatant_two.stamina
            if combat_one_dodge:
                print("{0} dodged {1}'s Attack!".format(combatant_one.name, combatant_two.name))
                combat_two_attack = False

        combat_one_first = combatant_one.agility > combatant_two.agility
        combat_two_first = combatant_two.agility > combatant_one.agility

        if combat_one_first:
            if combat_one_attack:
                print("{0} Attacks {1}!".format(combatant_one.name, combatant_two.name))
                combatant_two.health = max(0, combatant_two.health - combat_one_dmg * round(uniform(1, combatant_one.agility)))
                combatant_two.print_health()
                combat_one_attack = False
                if combatant_two.health == 0:
                    print("{} has been Defeated!".format(combatant_two.name))
                    winner = combatant_one
                    break
            if combat_two_attack:
                print("{0} Attacks {1}!".format(combatant_two.name, combatant_one.name))
                combatant_one.health = max(0, combatant_one.health - combat_two_dmg * round(uniform(1, combatant_two.agility)))
                combatant_one.print_health()
                combat_two_attack = False
                if combatant_one.health == 0:
                    print("{} has been Defeated!".format(combatant_one.name))
                    winner = combatant_two
                    break
        elif combat_two_first:
            if combat_two_attack:
                print("{0} Attacks {1}!".format(combatant_two.name, combatant_one.name))
                combatant_one.health = max(0, combatant_one.health - combat_two_dmg * round(uniform(1, combatant_two.agility)))
                combatant_one.print_health()
                combat_two_attack = False
                if combatant_one.health == 0:
                    print("{} has been Defeated!".format(combatant_one.name))
                    winner = combatant_two
                    break
            if combat_one_attack:
                print("{0} Attacks {1}!".format(combatant_one.name, combatant_two.name))
                combatant_two.health = max(0, combatant_two.health - combat_one_dmg * round(uniform(1, combatant_one.agility)))
                combatant_two.print_health()
                combat_one_attack = False
                if combatant_two.health == 0:
                    print("{} has been Defeated!".format(combatant_two.name))
                    winner = combatant_one
                    break  
        elif not combat_one_first and not combat_two_first:
            if uniform(0,1) > 0.5:
                # Combat one attacks first
                if combat_one_attack:
                    print("{0} Attacks {1}!".format(combatant_one.name, combatant_two.name))
                    combatant_two.health = max(0, combatant_two.health - combat_one_dmg * round(uniform(1, combatant_one.agility)))
                    combatant_two.print_health()
                    combat_one_attack = False
                    if combatant_two.health == 0:
                        print("{} has been Defeated!".format(combatant_two.name))
                        winner = combatant_one
                        break
                if combat_two_attack:
                    print("{0} Attacks {1}!".format(combatant_two.name, combatant_one.name))
                    combatant_one.health = max(0, combatant_one.health - combat_two_dmg * round(uniform(1, combatant_two.agility)))
                    combatant_one.print_health()
                    combat_two_attack = False
                    if combatant_one.health == 0:
                        print("{} has been Defeated!".format(combatant_one.name))
                        winner = combatant_two
                        break
            else:
                # Combat two attacks first
                if combat_two_attack:
                    print("{0} Attacks {1}!".format(combatant_two.name, combatant_one.name))
                    combatant_one.health = max(0, combatant_one.health - combat_two_dmg * round(uniform(1, combatant_two.agility)))
                    combatant_one.print_health()
                    combat_two_attack = False
                    if combatant_one.health == 0:
                        print("{} has been Defeated!".format(combatant_one.name))
                        winner = combatant_two
                        break
                if combat_one_attack:
                    print("{0} Attacks {1}!".format(combatant_one.name, combatant_two.name))
                    combatant_two.health = max(0, combatant_two.health - combat_one_dmg * round(uniform(1, combatant_one.agility)))
                    combatant_two.print_health()
                    combat_one_attack = False
                    if combatant_two.health == 0:
                        print("{} has been Defeated!".format(combatant_two.name))
                        winner = combatant_one
                        break
    
    if winner == None:
        if combatant_one.health > combatant_two.health:
            winner = combatant_one
        else:
            winner = combatant_two
        
    return winner

    