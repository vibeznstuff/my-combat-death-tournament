import pygame
import time
import json
from random import uniform
import csv
import constants
import pandas as pd
import tournament

round_num = 0

def rescale(img, x, y):
    return pygame.transform.scale(img, (x,y))


def flip(img):
    return pygame.transform.flip(img, True, False)


def get_frames(character, action, flip_bool=False, p1_bool=True, slow_factor=0):
    img_prefix = mappings[character]['img_prefix']
    img_dir = mappings[character]['img_dir']
    ani_ranges = mappings[character]['actions'][action]
    
    global p1_limit
    global p2_limit


    frame_list = []

    if p1_bool:
        p1_limit = 0
    else:
        p2_limit = 0 

    for ani_range in ani_ranges:
        if ani_range[0] > ani_range[1]:
            step = -1
        else:
            step = 1

        for i in range(ani_range[0], ani_range[1] + 1, step):
            id = "_{}".format(str(i))

            tmp_slow_factor = slow_factor

            if flip_bool:
                if tmp_slow_factor == 0:
                    frame_list.append(flip(pygame.image.load(img_dir+img_prefix+id+".png")))
                else:
                     while tmp_slow_factor > 0:
                         frame_list.append(flip(pygame.image.load(img_dir+img_prefix+id+".png")))
                         tmp_slow_factor -= 1
            else:
                if tmp_slow_factor == 0:
                    frame_list.append(pygame.image.load(img_dir+img_prefix+id+".png"))
                else:
                    while tmp_slow_factor > 0:
                        frame_list.append(pygame.image.load(img_dir+img_prefix+id+".png"))
                        tmp_slow_factor -= 1

    if p1_bool:
        p1_limit = len(frame_list) * 3
    else:
        p2_limit = len(frame_list) * 3

    return frame_list

def get_players(round_number):
    global p1_name
    global p2_name
    global p1_rank
    global p2_rank
    global p1_class
    global p2_class
    global player_one
    global player_two
    global p1_health_max
    global p2_health_max
    global p1_health
    global p2_health
    global p1_dodge_space
    global p2_dodge_space
    global p1_dodge_sf
    global p2_dodge_sf
    global p1_defeat_sf
    global p2_defeat_sf
    global p1_victory_sf
    global p2_victory_sf
    global p1_rest_sf
    global p2_rest_sf
    global fighting

    p1_info = tournament_data[(tournament_data["round_number"] == round_number) & (tournament_data['combatant_number'] == 1)]
    p1_name = p1_info.iloc[0,3]
    p1_gender = p1_info.iloc[0,4]
    p1_class = p1_info.iloc[0,5]
    p1_rank = p1_info.iloc[0,6]
    p1_health_max = p1_info.iloc[0,8]

    p2_info = tournament_data[(tournament_data["round_number"] == round_number) & (tournament_data['combatant_number'] == 2)]
    p2_name = p2_info.iloc[0,3]
    p2_gender = p2_info.iloc[0,4]
    p2_class = p2_info.iloc[0,5]
    p2_rank = p2_info.iloc[0,6]
    p2_health_max = p2_info.iloc[0,8]

    player_one = "{0}_{1}".format(p1_class.lower(), p1_gender)
    player_two = "{0}_{1}".format(p2_class.lower(), p2_gender)

    # 350 Max
    p1_health = p1_health_max
    p2_health = p2_health_max


    p1_dodge_space = mappings[player_one]['dodge_space']
    p2_dodge_space = mappings[player_two]['dodge_space']

    p1_dodge_sf = mappings[player_one]['dodge_slow_factor']
    p2_dodge_sf = mappings[player_two]['dodge_slow_factor']

    p1_defeat_sf = mappings[player_one]['defeat_slow_factor']
    p2_defeat_sf = mappings[player_two]['defeat_slow_factor']

    p1_victory_sf = mappings[player_one]['victory_slow_factor']
    p2_victory_sf = mappings[player_two]['victory_slow_factor']

    p1_rest_sf = mappings[player_one]['rest_slow_factor']
    p2_rest_sf = mappings[player_two]['rest_slow_factor']
    print(p1_info)
    print(p2_info)

    fighting = True

def reset_fight():
    global p1_resting
    global p2_resting
    global p1_attacking
    global p2_attacking
    global p1_attacked
    global p2_attacked
    global p1_recoiling
    global p2_recoiling
    global p1_dodging
    global p2_dodging
    global p1_dodged
    global p2_dodged
    global p1_defeat
    global p2_defeat
    global p1_victory
    global p2_victory
    global p1_wait_cycles
    global p2_wait_cycles

    p1_resting = True
    p2_resting = True
    p1_attacking = False
    p1_attacked = False
    p2_attacking = False
    p2_attacked = False
    p1_recoiling = False
    p2_recoiling = False
    p1_dodging = False
    p1_dodged = False
    p2_dodging = False
    p2_dodged = False
    p1_defeat = False
    p2_defeat = False
    p1_victory = False
    p2_victory = False
    p1_wait_cycles = 0
    p2_wait_cycles = 0

def update_health(p1_bool, health):
    global p1_health
    global p2_health
    pass

def draw(p1_health_new, p2_health_new):
    global p1_step_count
    global p2_step_count
    global p1_frames
    global p2_frames
    global p1_attacking
    global p2_attacking
    global p1_recoiling
    global p2_recoiling
    global p1_dodging
    global p2_dodging
    global p1_resting
    global p2_resting
    global p1_health_max
    global p2_health_max
    global p1_health
    global p2_health
    global p1_defeat
    global p2_defeat
    global p1_victory
    global p2_victory
    global p1_name
    global p2_name
    global p1_rank
    global p2_rank
    global p1_class
    global p2_class
    global fighting
    global p1_wait_cycles
    global p2_wait_cycles
    global timer
    global gui_timer1
    global gui_timer2
    global round_num
    global leaderboard

    if p1_step_count + 1 >= p1_limit and not (p1_defeat or p1_victory):
        p1_step_count = 0
        p1_attacking = False
        if p1_recoiling and not p2_attacking:
            p1_health = p1_health_new
            p1_recoiling = False
        p2_dodging = False
        if p1_wait_cycles > 0 and p1_resting:
            p1_wait_cycles -= 1
            gui_timer1 -= 1

    if p2_step_count + 1 >= p2_limit and not (p2_defeat or p2_victory):
        p2_step_count = 0
        p2_attacking = False
        if p2_recoiling and not p1_attacking:
            p2_health = p2_health_new
            p2_recoiling = False
        p1_dodging = False
        if p2_wait_cycles > 0 and p2_resting:
            p2_wait_cycles -= 1
            gui_timer2 -= 1

    end_by_defeat = ((p2_defeat and (p1_step_count + 1 >= p1_limit)) or (p1_defeat and (p2_step_count + 1 >= p2_limit)))
    end_by_timer = ((p2_defeat or p1_defeat) and timer == 0)

    if end_by_defeat or end_by_timer:
        
        if round_num < constants.FIGHTER_COUNT - 1:
            font = pygame.font.SysFont(None, 50)
            if p1_victory:
                win_text = "{} wins the fight!".format(p1_name)
            elif p2_victory:
                win_text = "{} wins the fight!".format(p2_name)
            
            text_width, text_height = font.size(win_text)
            img3 = font.render(win_text, True, (255,255,255))
            win.blit(img3, (500 -  (text_width/2), 250))
            pygame.display.update()
            time.sleep(5)
            print("Resetting fight")
        fighting = False
    
    win.fill((0,0,0))
    win.blit(background,(0,0))

    if p1_attacking and not p2_attacking:
        win.blit(p2_frames[p2_step_count//3], (x_2, y_2))
        win.blit(p1_frames[p1_step_count//3], (x, y))
    elif p2_attacking and not p1_attacking:
        win.blit(p1_frames[p1_step_count//3], (x, y))
        win.blit(p2_frames[p2_step_count//3], (x_2, y_2))
    else:
        win.blit(p2_frames[p2_step_count//3], (x_2, y_2))
        win.blit(p1_frames[p1_step_count//3], (x, y)) 


    # Draw health bar boarders
    pygame.draw.rect(win, (255, 255, 255), (50-2, 75-2, p1_health_max+4, 30+4))
    pygame.draw.rect(win, (255, 255, 255), (1000 - p2_health_max - 50 - 2, 75-2, p2_health_max+4, 30+4))

    # Draw red health bar background
    pygame.draw.rect(win, (255, 0, 0), (50, 75, p1_health_max, 30))
    pygame.draw.rect(win, (255, 0, 0), (1000 - p2_health_max - 50, 75, p2_health_max, 30))

    # Draw green health bar foreground
    if p1_health > 0:
        pygame.draw.rect(win, (0, 255, 0), (50, 75, p1_health, 30))

    if p2_health > 0:
        pygame.draw.rect(win, (0, 255, 0), (1000 - p2_health - 50, 75, p2_health, 30))

    # Player One Name & Details
    font = pygame.font.SysFont(None, 24)
    if p1_rank in ("ELITE", "MASTER", "LEGENDARY"):
        p1_name_details = "{0} ({1})".format(p1_name, p1_rank.capitalize())
    else:
        p1_name_details = p1_name
    name_txt = font.render(p1_name_details, True, (255,255,255))
    win.blit(name_txt, (50, 35))

    font = pygame.font.SysFont(None, 20)
    class_txt = font.render(p1_class.replace("_"," ").capitalize(), True, (255,255,255))
    win.blit(class_txt, (50, 55))

    # Player Two Name & Details
    font = pygame.font.SysFont(None, 24)
    if p2_rank in ("ELITE", "MASTER", "LEGENDARY"):
        p2_name_details = "{0} ({1})".format(p2_name, p2_rank.capitalize())
    else:
        p2_name_details = p2_name
    
    p2_width, p2_height = font.size(p2_name_details)
    name_txt2 = font.render(p2_name_details, True, (255,255,255))
    win.blit(name_txt2, (1000 - 50 - p2_width, 35))

    font = pygame.font.SysFont(None, 20)
    p2_width, p2_height = font.size(p2_class.replace("_"," ").capitalize())
    class_txt = font.render(p2_class.replace("_"," ").capitalize(), True, (255,255,255))
    win.blit(class_txt, (1000 - 50 - p2_width, 55))

    # Round Number
    if round_num < constants.FIGHTER_COUNT:
        font = pygame.font.SysFont(None, 30)
        round_width, round_height = font.size("Round Number {0}".format(round_num))
        img3 = font.render("Round Number {0}".format(round_num), True, (255,255,255))
        win.blit(img3, (500 -  (round_width/2), 25))

    # Round Number
    font = pygame.font.SysFont(None, 30)
    gui_timer = min(gui_timer1, gui_timer2)
    round_width, round_height = font.size(str(gui_timer))
    img3 = font.render(str(gui_timer), True, (255,255,255))
    win.blit(img3, (500 -  (round_width/2), 80))

    # Leaderboard

    leaderboard = {k: v for k, v in sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)}
    i = 0

    for player in leaderboard:
        i += 1
        font = pygame.font.SysFont(None, 16)
        player_win_text = "{0} [{1} Wins]".format(player, leaderboard[player])
        round_width, round_height = font.size(player_win_text)
        img3 = font.render(player_win_text, True, (255,255,255))
        win.blit(img3, (500 -  (round_width/2), 120 + i * 12))

        if i == 8:
            break

    pygame.display.update()

pygame.init()

win = pygame.display.set_mode((1000,550))

pygame.display.set_caption("Combat Death Tournament Simulator")

mappings = json.load(open("animation_mappings.json"))

#print(mappings)

p1_dodge_rate = 0.25
p2_dodge_rate = 0.25

reset_fight()

x = -90
x_default = x
y = 135
x_2 = 445
x_2_default = x_2
y_2 = 130
velocity = 5

run = True


clock = pygame.time.Clock()
FRAME_RATE = 35

background = pygame.image.load(r"C:\\Users\\Richard\\Documents\\sprite_sheets\\dark_forest_br.png")
background = rescale(background, 1000, 550)

acc = 0
acc_2 = 0
fighting = False

tournament_data = pd.read_csv('tournament_log.csv')

fight_log = open('fight_log.csv', 'r', newline='')
csv_reader = csv.reader(fight_log)
#skip header
next(csv_reader)
fight_event = next(csv_reader)
timer = constants.MAX_FIGHT_MOMENTS
gui_timer1 = timer
gui_timer2 = timer
p1_wait_cycles = 0
p2_wait_cycles = 0
leaderboard = {}

while run:

    if not fighting:
        round_num += 1
        print(round_num)
        print(p1_victory, p2_victory)
        if round_num == constants.FIGHTER_COUNT:
            run = False
            if p1_victory:
                win_text = "{} has won the tournament!".format(p1_name)
            elif p2_victory:
                win_text = "{} has won the tournament!".format(p2_name)
                
            font = pygame.font.SysFont(None, 50)
            text_width, text_height = font.size(win_text)
            img3 = font.render(win_text, True, (255,255,255))
            win.blit(img3, (500 -  (text_width/2), 250))
            pygame.display.update()

            time.sleep(10)
        else:
            reset_fight()
            get_players(round_num)
            timer = constants.MAX_FIGHT_MOMENTS
            gui_timer1 = timer
            gui_timer2 = timer
            p1_frames = get_frames(character=player_one, action='rest', flip_bool=True, p1_bool=True, slow_factor=p1_rest_sf)
            p2_frames = get_frames(character=player_two, action='rest', flip_bool=False, p1_bool=False, slow_factor=p2_rest_sf)

            round_num_tmp = round_num - 1
            while round_num_tmp < round_num:
                fight_event = next(csv_reader)
                round_num_tmp = int(fight_event[0])
            
            p1_step_count = 0
            p2_step_count = 0

    clock.tick(FRAME_RATE)

    if min(p1_wait_cycles, p2_wait_cycles) == 0:

        time_elapsed = timer - int(fight_event[2])
        p1_wait_cycles = max(1,round(time_elapsed))
        p2_wait_cycles = max(1,round(time_elapsed))
        timer = int(fight_event[2])

        if timer == 0 and not (p1_recoiling or p1_attacking or p1_dodging or p2_recoiling or p2_attacking or p2_dodging):
            if p1_health > p2_health:
                p2_defeat = True
                
            else:
                p1_defeat = True
            
            p1_recoiling = False
            p1_dodging = False
            p1_attacking = False
            p2_recoiling = False
            p2_dodging = False
            p2_attacking = False
        
        print("\n")
        print("Time Left:", fight_event[2])

        if fight_event[6] == 'True':
            p1_dodged = True
        else:
            p1_dodged = False

        if fight_event[7] == 'True':
            p1_attacked = True
        else:
            p1_attacked = False

        if fight_event[10] == 'True':
            p2_dodged = True
        else:
            p2_dodged = False

        if fight_event[11] == 'True':
            p2_attacked = True
        else:
            p2_attacked = False
        
        print(fight_event[3])
        print("P1 Defeat: ",p1_defeat)
        print("P2 Defeat: ",p2_defeat)
        print((p1_step_count, p1_limit))
        #print(fight_event[5], fight_event[9])
        #print(p1_health, p2_health)

        if (int(fight_event[5]) == 0 or int(fight_event[9]) == 0) or int(fight_event[2]) == 0:
            pass
        else:
            fight_event = next(csv_reader)

    #print((timer == 0 and p2_defeat == True))

    if ((p2_health == 0 and not p2_defeat) or (timer == 0 and p2_defeat == True)) and (not p1_attacking and not p2_recoiling and not p2_dodging):
        p2_defeat = True
        p2_attacking = False
        p2_dodging = False
        p2_resting = False
        p2_frames = get_frames(character=player_two, action='defeat', flip_bool=False, p1_bool=False, slow_factor=p2_defeat_sf)
        p2_step_count = 0
        p1_frames = get_frames(character=player_one, action='victory', flip_bool=True, p1_bool=True, slow_factor=p1_victory_sf)
        p1_step_count = 0
        p1_victory = True
        print("P2 was defeated")

        if p1_rank in ('ELITE', 'MASTER', 'LEGENDARY'):
            p1_key = "{} ({}) - {}".format(p1_name, p1_rank, p1_class.replace("_", " "))
        else:
            p1_key = "{} - {}".format(p1_name, p1_class) 
        
        if p2_rank in ('ELITE', 'MASTER', 'LEGENDARY'):
            p2_key = "{} ({}) - {}".format(p2_name, p2_rank, p2_class.replace("_"," "))
        else:
            p2_key = "{} - {}".format(p2_name, p2_class) 

        leaderboard.pop(p2_key, None)

        if p1_key in leaderboard:
            leaderboard[p1_key] = leaderboard[p1_key] + 1
        else:
            leaderboard[p1_key] = 1

    if ((p1_health == 0 and not p1_defeat) or (timer == 0 and p1_defeat == True)) and (not p2_attacking and not p1_recoiling and not p1_dodging):
        p1_defeat = True
        p1_attacking = False
        p1_dodging = False
        p1_resting = False
        p1_frames = get_frames(character=player_one, action='defeat', flip_bool=True, p1_bool=True, slow_factor=p1_defeat_sf)
        p1_step_count = 0
        p2_frames = get_frames(character=player_two, action='victory', flip_bool=False, p1_bool=False, slow_factor=p2_victory_sf)
        p2_step_count = 0
        p2_victory = True
        print("P1 was defeated")
        
        if p1_rank in ('ELITE', 'MASTER', 'LEGENDARY'):
            p1_key = "{} ({}) - {}".format(p1_name, p1_rank, p1_class.replace("_"," "))
        else:
            p1_key = "{} - {}".format(p1_name, p1_class) 
        
        if p2_rank in ('ELITE', 'MASTER', 'LEGENDARY'):
            p2_key = "{} ({}) - {}".format(p2_name, p2_rank, p2_class.replace("_"," "))
        else:
            p2_key = "{} - {}".format(p2_name, p2_class) 

        leaderboard.pop(p1_key, None)

        if p2_key in leaderboard:
            leaderboard[p2_key] = leaderboard[p2_key] + 1
        else:
            leaderboard[p2_key] = 1

    if not p1_resting and not p1_attacking and not p1_recoiling and not p1_dodging and not p1_defeat and not p1_victory:
        p1_frames = get_frames(character=player_one, action='rest', flip_bool=True, p1_bool=True, slow_factor=p1_rest_sf)
        p1_step_count = 0
        p1_resting = True
        x = -90

    if not p2_resting and not p2_attacking and not p2_recoiling and not p2_dodging and not p2_defeat and not p2_victory:
        p2_frames = get_frames(character=player_two, action='rest', flip_bool=False, p1_bool=False,slow_factor=p2_rest_sf)
        p2_step_count = 0
        p2_resting = True
        x_2 = 445

    if p1_attacking and not p1_recoiling and not p1_dodging:
        x += acc
        x_2_min = min(x_2, x_2_default)
        if x < x_2_min - 90:
            acc += 1
        if x > x_2_min - 90:
            acc = 0

    if acc == 0 and p1_attacking and not p2_recoiling and not p2_dodged and not p2_dodging:
        p2_frames = get_frames(character=player_two, action='injured', flip_bool=False, p1_bool=False, slow_factor=3)
        p2_step_count = 0
        p2_resting = False
        p2_recoiling = True
        acc_2 = 0

    if (x_2 - x) < 350 and p1_attacking and not p2_recoiling and p2_dodged and not p2_dodging:
        p2_frames = get_frames(character=player_two, action='dodge', flip_bool=False, p1_bool=False, slow_factor=p2_dodge_sf)
        p2_step_count = 0
        p2_resting = False
        p2_dodged = False
        p2_dodging = True
        acc_2 = 0

    if p2_dodging and p2_step_count > 0:
        if x_2 > x_2_default + p2_dodge_space:
            p2_frames = get_frames(character=player_two, action='rest', flip_bool=False, p1_bool=False, slow_factor=p2_rest_sf)
            p2_step_count = 0
            x_2 = x_2_default + p2_dodge_space
        elif x_2 < x_2_default + p2_dodge_space:
            x_2 += (p2_step_count / p2_limit) * 10

    if p1_attacked:
        p1_frames = get_frames(character=player_one, action='dash_attack', flip_bool=True, p1_bool=True)
        p1_step_count = 0
        p1_resting = False
        p1_attacking = True
        p1_attacked = False
    
    if p2_attacking and not p2_recoiling and not p2_dodging:
        x_2 -= acc_2
        x_max = max(x, x_default)
        if x_2 > x_max + 90:
            acc_2 += 1
        if x_2 < x_max + 90:
            acc_2 = 0

    if acc_2 == 0 and p2_attacking and not p1_recoiling and not p1_dodged and not p1_dodging:
        p1_frames = get_frames(character=player_one, action='injured', flip_bool=True, p1_bool=True, slow_factor=3)
        p1_step_count = 0
        p1_resting = False
        p1_recoiling = True
        acc = 0

    if (x_2 - x) < 350 and p2_attacking and not p1_recoiling and p1_dodged and not p1_dodging:
        p1_frames = get_frames(character=player_one, action='dodge', flip_bool=True, p1_bool=True, slow_factor=p1_dodge_sf)
        p1_step_count = 0
        p1_resting = False
        p1_dodged = False
        p1_dodging = True
        acc = 0

    if p1_dodging and p1_step_count > 0:
        if x < x_default - p1_dodge_space:
            p1_frames = get_frames(character=player_one, action='rest', flip_bool=True, p1_bool=True, slow_factor=p1_rest_sf)
            p1_step_count = 0
            x = x_default - p1_dodge_space
        elif x > x_default - p1_dodge_space:
            x -= (p1_step_count / p1_limit) * 10

    if p2_attacked:
        p2_frames = get_frames(character=player_two, action='dash_attack', flip_bool=False, p1_bool=False)
        p2_step_count = 0
        p2_resting = False
        p2_attacking = True
        p2_attacked = False

    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        p2_attacked = True
        #print("x: {0}, y: {1}".format(x,y))
    if keys[pygame.K_RIGHT]:
        p1_attacked = True
        #print("x: {0}, y: {1}".format(x,y))
    if keys[pygame.K_UP]:
        y -= velocity
        print("x: {0}, y: {1}".format(x,y))
    if keys[pygame.K_DOWN]:
        y += velocity
        print("x: {0}, y: {1}".format(x,y))

    if not ((p1_defeat or p1_victory) and p1_step_count + 1 >= p1_limit):
        p1_step_count += 1
    
    if not ((p2_defeat or p2_victory) and p2_step_count + 1 >= p2_limit):
        p2_step_count += 1

    # Update health bars
    draw(p1_health_new=int(fight_event[5]), p2_health_new=int(fight_event[9]))

pygame.quit()