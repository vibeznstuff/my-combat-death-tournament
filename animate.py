import pygame
import time
import json
from random import uniform
import csv


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

def draw():
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

    if p1_step_count + 1 >= p1_limit and not (p1_defeat or p1_victory):
        p1_step_count = 0
        p1_attacking = False
        if p1_recoiling and p2_resting:
            p1_health = max(0, p1_health - 50)
            p1_recoiling = False
        p2_dodging = False

    if p2_step_count + 1 >= p2_limit and not (p2_defeat or p2_victory):
        p2_step_count = 0
        p2_attacking = False
        if p2_recoiling and p1_resting:
            p2_health = max(0, p2_health - 50)
            p2_recoiling = False
        p1_dodging = False
    
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
    p1_name = 'Player One Name'
    img = font.render(p1_name, True, (255,255,255))
    win.blit(img, (50, 50))

    # Player Two Name & Details
    font = pygame.font.SysFont(None, 24)
    p2_name = 'Player Two Name'
    p2_width, p2_height = font.size(p2_name)
    img2 = font.render(p2_name, True, (255,255,255))
    win.blit(img2, (1000 - 50 - p2_width, 50))

    pygame.display.update()

pygame.init()

win = pygame.display.set_mode((1000,550))

pygame.display.set_caption("Combat Death Tournament Simulator")

mappings = json.load(open("animation_mappings.json"))

print(mappings)

player_one = 'heart_female'
player_two = 'berserker_male'

# 350 Max
p1_health_max = 200
p2_health_max = 200
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

p1_dodge_rate = 0.25
p2_dodge_rate = 0.25


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

p1_frames = get_frames(character=player_one, action='rest', flip_bool=True, p1_bool=True, slow_factor=p1_rest_sf)
p2_frames = get_frames(character=player_two, action='rest', flip_bool=False, p1_bool=False, slow_factor=p2_rest_sf)
p1_step_count = 0
p2_step_count = 0
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
acc = 0
acc_2 = 0

while run:

    clock.tick(FRAME_RATE)

    if p2_health == 0 and not p2_defeat:
        p2_defeat = True
        p2_attacking = False
        p2_dodging = False
        p2_resting = False
        p2_frames = get_frames(character=player_two, action='defeat', flip_bool=False, p1_bool=False, slow_factor=p2_defeat_sf)
        p2_step_count = 0
        p1_frames = get_frames(character=player_one, action='victory', flip_bool=True, p1_bool=True, slow_factor=p1_victory_sf)
        p1_step_count = 0
        p1_victory = True

    if p1_health == 0 and not p1_defeat:
        p1_defeat = True
        p1_attacking = False
        p1_dodging = False
        p1_resting = False
        p1_frames = get_frames(character=player_one, action='defeat', flip_bool=True, p1_bool=True, slow_factor=p1_defeat_sf)
        p1_step_count = 0
        p2_frames = get_frames(character=player_two, action='victory', flip_bool=False, p1_bool=False, slow_factor=p2_victory_sf)
        p2_step_count = 0
        p2_victory = True

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

    if p1_attacking and not p1_recoiling:
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

        if uniform(0,1) < p2_dodge_rate:
            p2_dodged = True
    
    if p2_attacking and not p2_recoiling:
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

        if uniform(0,1) < p1_dodge_rate:
            p1_dodged = True

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

    draw()

pygame.quit()