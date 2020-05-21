import pygame
import time
import csv
import tournament

pygame.init()

win = pygame.display.set_mode((500,500))

pygame.display.set_caption("First game")

fight_log = open('fight_log.csv', 'r', newline='')
fight_data = csv.DictReader(fight_log)



def run_game():
    
    x = 50
    y = 50
    width = 60
    height = 20

    last_round_number = 1
    round_number = 1
    time_elapsed = 300

    for row in fight_data:
        round_number = row['round_number']
        fight_name = row['fight_name']
        new_time = row['time_elapsed']
        combatant_one_health = row['combatant_one_health']
        combatant_two_health = row['combatant_two_health']

        if new_time == 300:
            time.sleep(10)
            print("New fight beginning! {0}".format(fight_name))

        time.sleep((old_time - new_time) / 5)

        old_time = time_elapsed

        if round_number != last_round_number:
            last_round_number = round_number
            
        

    run = True
    while run:
        pygame.time.delay(100)
        pygame.draw.rect(win, (255, 0, 0), (x, y, width, height))
        pygame.display.update()
        time.sleep(10)
        run = False

    pygame.quit()