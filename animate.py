import pygame
import time
import json
from random import uniform

pygame.init()

win = pygame.display.set_mode((1000,550))

pygame.display.set_caption("First game")

mappings = json.load(open("animation_mappings.json"))

print(mappings)

player_one = 'yuri'
player_two = 'rock'

x = -90
x_default = x
y = 135
x_2 = 445
x_2_default = x_2
y_2 = 130
width = 60
height = 20
velocity = 5

FRAME_RATE = 35

p1_step_count = 0
p2_step_count = 0

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

        for i in range(ani_range[0], ani_range[1], step):
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

swanky_background = pygame.image.load(r"C:\\Users\\Richard\\Documents\\sprite_sheets\\dark_forest_br.png")

swanky_background = rescale(swanky_background, 1000, 550)

clock = pygame.time.Clock()

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

    if p1_step_count + 1 >= p1_limit:
        p1_step_count = 0
        p1_attacking = False
        p1_recoiling = False
        p2_dodging = False

    if p2_step_count + 1 >= p2_limit:
        p2_step_count = 0
        p2_attacking = False
        p2_recoiling = False
        p1_dodging = False
    
    win.fill((0,0,0))
    win.blit(swanky_background,(0,0))
    if p1_attacking and not p2_attacking:
        win.blit(p2_frames[p2_step_count//3], (x_2, y_2))
        win.blit(p1_frames[p1_step_count//3], (x, y))
    elif p2_attacking and not p1_attacking:
        win.blit(p1_frames[p1_step_count//3], (x, y))
        win.blit(p2_frames[p2_step_count//3], (x_2, y_2))
    else:
        win.blit(p2_frames[p2_step_count//3], (x_2, y_2))
        win.blit(p1_frames[p1_step_count//3], (x, y)) 

    pygame.display.update()

run = True

p1_frames = get_frames(character=player_one, action='rest', flip_bool=True, p1_bool=True)
p2_frames = get_frames(character=player_two, action='rest', flip_bool=False, p1_bool=False)
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
acc = 0
acc_2 = 0

while run:

    clock.tick(FRAME_RATE)

    if not p1_resting and not p1_attacking and not p1_recoiling and not p1_dodging:
        p1_frames = get_frames(character=player_one, action='rest', flip_bool=True, p1_bool=True)
        p1_step_count = 0
        p1_resting = True
        x = -90

    if not p2_resting and not p2_attacking and not p2_recoiling and not p2_dodging:
        p2_frames = get_frames(character=player_two, action='rest', flip_bool=False, p1_bool=False)
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
        p2_frames = get_frames(character=player_two, action='dodge', flip_bool=False, p1_bool=False, slow_factor=2)
        p2_step_count = 0
        p2_resting = False
        p2_dodged = False
        p2_dodging = True
        acc_2 = 0

    if p2_dodging and p2_step_count > 0:
        if x_2 > x_2_default + 80:
            p2_frames = get_frames(character=player_two, action='rest', flip_bool=False, p1_bool=False)
            p2_step_count = 0
            x_2 = x_2_default + 80
        elif x_2 < x_2_default + 80:
            x_2 += (p2_step_count / p2_limit) * 10

    if p1_attacked:
        p1_frames = get_frames(character=player_one, action='dash_attack', flip_bool=True, p1_bool=True)
        p1_step_count = 0
        p1_resting = False
        p1_attacking = True
        p1_attacked = False

        if uniform(0,1) > 0.5:
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
        p1_frames = get_frames(character=player_one, action='dodge', flip_bool=True, p1_bool=True, slow_factor=2)
        p1_step_count = 0
        p1_resting = False
        p1_dodged = False
        p1_dodging = True
        acc = 0

    if p1_dodging and p1_step_count > 0:
        if x < x_default - 80:
            p1_frames = get_frames(character=player_one, action='rest', flip_bool=True, p1_bool=True)
            p1_step_count = 0
            x = x_default - 80
        elif x > x_default - 80:
            x -= (p1_step_count / p1_limit) * 10

    if p2_attacked:
        p2_frames = get_frames(character=player_two, action='dash_attack', flip_bool=False, p1_bool=False)
        p2_step_count = 0
        p2_resting = False
        p2_attacking = True
        p2_attacked = False

        if uniform(0,1) > 0.5:
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

    p1_step_count += 1
    p2_step_count += 1
    draw()

pygame.quit()