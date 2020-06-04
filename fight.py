from combatant import Combatant
from random import uniform
import time
from copy import deepcopy
import csv
import constants

MAX_FIGHT_MOMENTS = constants.MAX_FIGHT_MOMENTS

def fight(combatant_one, combatant_two, log_results=True, spectate=False):

    if not spectate:
        fight_start_sleep = 0
        round_sleep = 0
    else:
        fight_start_sleep = 10
        round_sleep = 1
           
    combatant_one.print_stats()
    combatant_two.print_stats()
    print("FIGHT!")
    time.sleep(fight_start_sleep)
    fight_timer = MAX_FIGHT_MOMENTS

    fight_name = "{0} vs {1}".format(combatant_one.name, combatant_two.name)

    if log_results:
        # Open fight log to append new records for events
        out_file2 = open('fight_log.csv', 'a', newline='')
        writer2 = csv.writer(out_file2)
        writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, 'Fight starts!', combatant_one.name, combatant_one.health, \
            False, False, combatant_two.name, combatant_two.health, False, False])

    healthy_combat_one = deepcopy(combatant_one)
    healthy_combat_two = deepcopy(combatant_two)

    final_combat_one = combatant_one
    final_combat_two = combatant_two

    combat_one_cooldown = constants.DEFAULT_COOLDOWN - combatant_one.stamina
    combat_two_cooldown = constants.DEFAULT_COOLDOWN - combatant_two.stamina

    combat_one_attack = False
    combat_two_attack = False

    combat_one_dmg = max(combatant_one.strength - combatant_two.defense, 1)
    combat_two_dmg =  max(combatant_two.strength - combatant_one.defense, 1)

    winner = None

    while combatant_one.health > 0 and combatant_two.health > 0 and fight_timer > 0:
        print("\n Fight Timer: {}\n".format(fight_timer))
        time.sleep(round_sleep)
        fight_timer = max(0, fight_timer - 1)
        combat_one_cooldown = max(combat_one_cooldown - 1, 0)
        combat_two_cooldown = max(combat_two_cooldown - 1, 0)

        print("Cooldown for {0}: {1}".format(combatant_one.name, combat_one_cooldown))
        print("Cooldown for {0}: {1}".format(combatant_two.name, combat_two_cooldown))

        dodge_chances_1 = combatant_one.wisdom
        combat_one_dodge = False

        while dodge_chances_1 > 0 and not combat_one_dodge:
            dodge_chances_1 = dodge_chances_1 - 1
            if uniform(0,1) > constants.DODGE_THRESHOLD:
                combat_one_dodge = True

        dodge_chances_2 = combatant_two.wisdom
        combat_two_dodge = False

        while dodge_chances_2 > 0 and not combat_two_dodge:
            dodge_chances_2 = dodge_chances_2 - 1
            if uniform(0,1) > constants.DODGE_THRESHOLD:
                combat_two_dodge = True
    
        if combat_one_cooldown == 0:
            combat_one_attack = True
            combat_one_cooldown = 20 - combatant_one.stamina
            if combat_two_dodge:
                event = "{0} dodged {1}'s Attack!".format(combatant_two.name, combatant_one.name)
                writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, event, combatant_one.name, \
                    combatant_one.health, False, True, combatant_two.name, combatant_two.health, True, False])
                combat_one_attack = False

        if combat_two_cooldown == 0:
            combat_two_attack = True
            combat_two_cooldown = 20 - combatant_two.stamina
            if combat_one_dodge:
                event = "{0} dodged {1}'s Attack!".format(combatant_one.name, combatant_two.name)
                writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, event, combatant_one.name, \
                    combatant_one.health, True, False, combatant_two.name, combatant_two.health, False, True])
                combat_two_attack = False

        combat_one_first = combatant_one.agility > combatant_two.agility
        combat_two_first = combatant_two.agility > combatant_one.agility

        if combat_one_first:
            if combat_one_attack:
                event = "{0} Attacks {1}!".format(combatant_one.name, combatant_two.name)
                combatant_two.health = round(max(0, combatant_two.health - combat_one_dmg * round(uniform(1, combatant_one.agility)) * constants.DAMAGE_MULTIPLIER))
                writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, event, combatant_one.name, combatant_one.health, \
                    False, True, combatant_two.name, combatant_two.health, False, False])
                combatant_two.print_health()
                combat_one_attack = False
                if combatant_two.health == 0:
                    event = "{} has been Defeated!".format(combatant_two.name)
                    writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, event, combatant_one.name, combatant_one.health, \
                        False, False, combatant_two.name, combatant_two.health, False, False])
                    winner = final_combat_one
                    break
            if combat_two_attack:
                event = "{0} Attacks {1}!".format(combatant_two.name, combatant_one.name)
                combatant_one.health = round(max(0, combatant_one.health - combat_two_dmg * round(uniform(1, combatant_two.agility)) * constants.DAMAGE_MULTIPLIER))
                writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, event, combatant_one.name, combatant_one.health, \
                    False, False, combatant_two.name, combatant_two.health, False, True])
                combatant_one.print_health()
                combat_two_attack = False
                if combatant_one.health == 0:
                    event = "{} has been Defeated!".format(combatant_one.name)
                    writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, event, combatant_one.name, combatant_one.health, \
                        False, False, combatant_two.name, combatant_two.health, False, False])
                    winner = final_combat_two
                    break
        elif combat_two_first:
            if combat_two_attack:
                event = "{0} Attacks {1}!".format(combatant_two.name, combatant_one.name)
                combatant_one.health = round(max(0, combatant_one.health - combat_two_dmg * round(uniform(1, combatant_two.agility)) * constants.DAMAGE_MULTIPLIER))
                writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, event, combatant_one.name, combatant_one.health, \
                    False, False, combatant_two.name, combatant_two.health, False, True])
                combatant_one.print_health()
                combat_two_attack = False
                if combatant_one.health == 0:
                    event = "{} has been Defeated!".format(combatant_one.name)
                    writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, event, combatant_one.name, combatant_one.health, \
                        False, False, combatant_two.name, combatant_two.health, False, False])
                    winner = final_combat_two
                    break
            if combat_one_attack:
                event = "{0} Attacks {1}!".format(combatant_one.name, combatant_two.name)
                combatant_two.health = round(max(0, combatant_two.health - combat_one_dmg * round(uniform(1, combatant_one.agility)) * constants.DAMAGE_MULTIPLIER))
                writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, event, combatant_one.name, combatant_one.health, \
                    False, True, combatant_two.name, combatant_two.health, False, False])
                combatant_two.print_health()
                combat_one_attack = False
                if combatant_two.health == 0:
                    event = "{} has been Defeated!".format(combatant_two.name)
                    writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, event, combatant_one.name, combatant_one.health, \
                        False, False, combatant_two.name, combatant_two.health, False, False])
                    winner = final_combat_one
                    break  
        elif not combat_one_first and not combat_two_first:
            if uniform(0,1) > 0.5:
                # Combat one attacks first
                if combat_one_attack:
                    event = "{0} Attacks {1}!".format(combatant_one.name, combatant_two.name)
                    combatant_two.health = round(max(0, combatant_two.health - combat_one_dmg * round(uniform(1, combatant_one.agility)) * constants.DAMAGE_MULTIPLIER))
                    writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, event, combatant_one.name, combatant_one.health, \
                        False, True, combatant_two.name, combatant_two.health, False, False])
                    combatant_two.print_health()
                    combat_one_attack = False
                    if combatant_two.health == 0:
                        event = "{} has been Defeated!".format(combatant_two.name)
                        writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, event, combatant_one.name, combatant_one.health, \
                            False, False, combatant_two.name, combatant_two.health, False, False])
                        winner = final_combat_one
                        break
                if combat_two_attack:
                    event = "{0} Attacks {1}!".format(combatant_two.name, combatant_one.name)
                    combatant_one.health = round(max(0, combatant_one.health - combat_two_dmg * round(uniform(1, combatant_two.agility)) * constants.DAMAGE_MULTIPLIER))
                    writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, event, combatant_one.name, combatant_one.health, \
                        False, False, combatant_two.name, combatant_two.health, False, True])
                    combatant_one.print_health()
                    combat_two_attack = False
                    if combatant_one.health == 0:
                        event = "{} has been Defeated!".format(combatant_one.name)
                        writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, event, combatant_one.name, combatant_one.health, \
                            False, False, combatant_two.name, combatant_two.health, False, False])
                        winner = final_combat_two
                        break
            else:
                # Combat two attacks first
                if combat_two_attack:
                    event = "{0} Attacks {1}!".format(combatant_two.name, combatant_one.name)
                    combatant_one.health = round(max(0, combatant_one.health - combat_two_dmg * round(uniform(1, combatant_two.agility)) * constants.DAMAGE_MULTIPLIER))
                    writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, event, combatant_one.name, combatant_one.health, \
                        False, False, combatant_two.name, combatant_two.health, False, True])
                    combatant_one.print_health()
                    combat_two_attack = False
                    if combatant_one.health == 0:
                        event = "{} has been Defeated!".format(combatant_one.name)
                        writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, event, combatant_one.name, combatant_one.health, \
                            False, False, combatant_two.name, combatant_two.health, False, False])
                        winner = final_combat_two
                        break
                if combat_one_attack:
                    event = "{0} Attacks {1}!".format(combatant_one.name, combatant_two.name)
                    combatant_two.health = round(max(0, combatant_two.health - combat_one_dmg * round(uniform(1, combatant_one.agility)) * constants.DAMAGE_MULTIPLIER))
                    writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, event, combatant_one.name, combatant_one.health, \
                        False, True, combatant_two.name, combatant_two.health, False, False])
                    combatant_two.print_health()
                    combat_one_attack = False
                    if combatant_two.health == 0:
                        event = "{} has been Defeated!".format(combatant_two.name)
                        writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, event, combatant_one.name, combatant_one.health, \
                            False, False, combatant_two.name, combatant_two.health, False, False])
                        winner = final_combat_one
                        break
    
    if winner == None:
        if combatant_one.health > combatant_two.health:
            winner = final_combat_one
        else:
            winner = final_combat_two
        
    event = "{} wins the fight!".format(winner.name)
    writer2.writerow([constants.ROUND_NUMBER, fight_name, fight_timer, event, combatant_one.name, combatant_one.health, \
        False, False, combatant_two.name, combatant_two.health, False, False])
    

    if log_results:

        out_file = open('tournament_log.csv', 'a', newline='')
        field_names = ['round_number', 'combatant_number', 'fight_name', 'combatant', 'gender', 'combat_class', 'rank', 'max_health', \
            'health', 'strength', 'defense', 'agility', 'stamina', 'wisdom', 'fight_result', 'remaining_health']

        writer = csv.DictWriter(out_file, fieldnames=field_names)

        if winner == final_combat_one:
            win_result = healthy_combat_one.get_result_data(1, constants.ROUND_NUMBER, fight_name, 'Won', combatant_one.health)
            writer.writerow(win_result)

            loss_result = healthy_combat_two.get_result_data(2, constants.ROUND_NUMBER, fight_name, 'Lost', combatant_two.health)
            writer.writerow(loss_result)
        elif winner == final_combat_two:
            win_result = healthy_combat_two.get_result_data(2, constants.ROUND_NUMBER, fight_name, 'Won', combatant_two.health)
            writer.writerow(win_result)

            loss_result = healthy_combat_one.get_result_data(1, constants.ROUND_NUMBER, fight_name, 'Lost', combatant_one.health)
            writer.writerow(loss_result)

    winner.recooperate()
    out_file2.close()
    
    return winner

    