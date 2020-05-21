import pygame
import time
import json

pygame.init()

win = pygame.display.set_mode((1000,550))

pygame.display.set_caption("First game")

mappings = json.load(open("animation_mappings.json"))

print(mappings)

x = -90
y = 135
x_2 = 445
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


def get_frames(character, action, flip_bool=False, p1_bool=True):
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

            if flip_bool:
                frame_list.append(flip(pygame.image.load(img_dir+img_prefix+id+".png")))
            else:
                frame_list.append(pygame.image.load(img_dir+img_prefix+id+".png"))

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
    global p1_attacking
    global p1_resting
    global p2_resting

    if p1_step_count + 1 >= p1_limit:
        p1_step_count = 0
        p1_attacking = False

    if p2_step_count + 1 >= p2_limit:
        p2_step_count = 0
    
    win.fill((0,0,0))
    win.blit(swanky_background,(0,0))
    win.blit(p2_frames[p1_step_count//3], (x_2, y_2))
    win.blit(p1_frames[p1_step_count//3], (x, y))
    pygame.display.update()

run = True

p1_frames = get_frames(character='rock', action='rest', flip_bool=True, p1_bool=True)
p2_frames = get_frames(character='haohmaru', action='rest', flip_bool=False, p1_bool=False)
p1_resting = True
p2_resting = True
p1_attacking = False
p1_attacked = False
acc = 0

while run:

    clock.tick(FRAME_RATE)

    if not p1_resting and not p1_attacking:
        p1_frames = get_frames(character='rock', action='rest', flip_bool=True)
        p1_resting = True
        x = -90

    if not p2_resting and not p2_attacking:
        p2_frames = get_frames(character='haohmaru', action='rest', flip_bool=True)
        p2_resting = True
        x_2 = -445

    if p1_attacking:
        x += acc
        if x < x_2 - 90:
            acc += 1
        if x > x_2 - 90:
            acc = 0

    if p1_attacked:
        p1_frames = get_frames(character='rock', action='dash_attack', flip_bool=True)
        p1_resting = False
        p1_attacking = True
        p1_attacked = False

    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        x -= velocity
        print("x: {0}, y: {1}".format(x,y))
    if keys[pygame.K_RIGHT]:
        p1_attacked = True
        p1_step_count = 0
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