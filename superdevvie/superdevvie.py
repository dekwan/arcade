# Build Pac-Man from Scratch in Python with PyGame!!
import copy
import math
import sys
from enum import Enum
from os import path
from random import randint

import pygame
from board import boards

FILE_PATH_PREFIX = path.dirname(path.realpath(__file__))
sys.path.insert(2, FILE_PATH_PREFIX + '/../high_score')
from high_score import HighScore

pygame.init()
pygame.joystick.init()
pygame.mouse.set_visible(False)

class Buttons:
    ADMIN_LEFT = 2
    ADMIN_RIGHT = 5
    PLAYER_LEFT = 8
    PLAYER_RIGHT = 3

    if sys.platform.startswith('darwin'): # MacOS seems to have different button numbers
        PLAYER_LEFT = 9

# [Right, Left, Up, Down]
class Direction:
    RIGHT = 0
    LEFT = 1
    UP = 2
    DOWN = 3

    # Return a random direction
    def random():
        return randint(0, 3)

# Display and Board
DISPLAY_WIDTH = 1920
DISPLAY_HEIGHT = 1080
BOARD_WIDTH = 900
BOARD_HEIGHT = 946
BOARD_TILE_WIDTH = BOARD_WIDTH // 30
BOARD_TILE_HEIGHT = (BOARD_HEIGHT - 50) // 32
WIDTH_OFFSET = (DISPLAY_WIDTH - BOARD_WIDTH) // 2
HEIGHT_OFFSET = (DISPLAY_HEIGHT - BOARD_HEIGHT) // 2
FPS = 60

# Coordinates and Direction
PLAYER = {'x': 428, 'y': 663, 'direction': Direction.RIGHT}
DOCUMENTATION = {'x': 365, 'y': 415, 'direction': Direction.random()}
LAB = {'x': 425, 'y': 415, 'direction': Direction.random()}
CODE = {'x': 490, 'y': 415, 'direction': Direction.random()}
SANDBOX = {'x': 425, 'y': 325, 'direction': Direction.RIGHT}

# Screen, Boards, Tiles
timer = pygame.time.Clock()
font_filepath = FILE_PATH_PREFIX + '/assets/fonts/retro_gaming.ttf'
font = pygame.font.Font(font_filepath, 30)
board = copy.deepcopy(boards)
board_tiles_width_num = len(boards[0])
min_x_tile_coord = (BOARD_TILE_WIDTH // 2) - 3 # 6 pixel square at the center of the tile
max_x_tile_coord = (BOARD_TILE_WIDTH // 2) + 3 # 6 pixel square at the center of the tile
min_y_tile_coord = (BOARD_TILE_HEIGHT // 2) - 3 # 6 pixel square at the center of the tile
max_y_tile_coord = (BOARD_TILE_HEIGHT // 2) + 3 # 6 pixel square at the center of the tile
def reset_board():
    global board
    board = copy.deepcopy(boards)

# Images
IMG_SIZE = 45
IMG_DIMENSIONS = (IMG_SIZE, IMG_SIZE)
player_images = []
for i in range(1, 5):
    player_images.append(pygame.transform.scale(pygame.image.load(f'{FILE_PATH_PREFIX}/assets/player_images/{i}.png'), IMG_DIMENSIONS))
player_dead_img = pygame.transform.scale(pygame.image.load(f'{FILE_PATH_PREFIX}/assets/player_images/devvie_dead.png'), IMG_DIMENSIONS)
title_img = pygame.transform.scale_by(pygame.image.load(f'{FILE_PATH_PREFIX}/assets/intro_images/title.png'), 1)
documentation_img = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/ghost_images/documentation.png')
lab_img = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/ghost_images/lab.png')
code_img = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/ghost_images/code.png')
sandbox_img = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/ghost_images/sandbox.png')
documentation_power_img = pygame.transform.scale(pygame.image.load(f'{FILE_PATH_PREFIX}/assets/ghost_images/documentation_powerpellet.png'), IMG_DIMENSIONS)
lab_power_img = pygame.transform.scale(pygame.image.load(f'{FILE_PATH_PREFIX}/assets/ghost_images/lab_powerpellet.png'), IMG_DIMENSIONS)
code_power_img = pygame.transform.scale(pygame.image.load(f'{FILE_PATH_PREFIX}/assets/ghost_images/code_powerpellet.png'), IMG_DIMENSIONS)
sandbox_power_img = pygame.transform.scale(pygame.image.load(f'{FILE_PATH_PREFIX}/assets/ghost_images/sandbox_powerpellet.png'), IMG_DIMENSIONS)
documentation_power_end_img = pygame.transform.scale(pygame.image.load(f'{FILE_PATH_PREFIX}/assets/ghost_images/documentation_powerpellet_end.png'), IMG_DIMENSIONS)
lab_power_end_img = pygame.transform.scale(pygame.image.load(f'{FILE_PATH_PREFIX}/assets/ghost_images/lab_powerpellet_end.png'), IMG_DIMENSIONS)
code_power_end_img = pygame.transform.scale(pygame.image.load(f'{FILE_PATH_PREFIX}/assets/ghost_images/code_powerpellet_end.png'), IMG_DIMENSIONS)
sandbox_power_end_img = pygame.transform.scale(pygame.image.load(f'{FILE_PATH_PREFIX}/assets/ghost_images/sandbox_powerpellet_end.png'), IMG_DIMENSIONS)
documentation_eaten_img = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/ghost_images/documentation_eaten.png')
lab_eaten_img = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/ghost_images/lab_eaten.png')
code_eaten_img = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/ghost_images/code_eaten.png')
sandbox_eaten_img = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/ghost_images/sandbox_eaten.png')
dead_img = pygame.transform.scale(pygame.image.load(f'{FILE_PATH_PREFIX}/assets/ghost_images/devnet_dead.png'), IMG_DIMENSIONS)

# Sounds
pygame.mixer.init(channels=1)
sound_start = pygame.mixer.Sound(FILE_PATH_PREFIX + '/assets/sounds/game_start.mp3')
sound_chomp = pygame.mixer.Sound(FILE_PATH_PREFIX + '/assets/sounds/chomp.mp3')
sound_power = pygame.mixer.Sound(FILE_PATH_PREFIX + '/assets/sounds/pacman_power.mp3')
sound_pacman_eat_ghost = pygame.mixer.Sound(FILE_PATH_PREFIX + '/assets/sounds/pacman_eat_ghost.mp3')
sound_ghost_eaten = pygame.mixer.Sound(FILE_PATH_PREFIX + '/assets/sounds/ghost_eaten.mp3')
sound_pacman_death = pygame.mixer.Sound(FILE_PATH_PREFIX + '/assets/sounds/pacman_death.mp3')
sound_channel = pygame.mixer.Channel(0)

def handle_sounds(sound=None, play=False, stop=False, loops=0):
    if stop:
        sound_channel.stop()
        pygame.mixer.music.unpause()
    elif play and sound:
        if loops == -1:
            pygame.mixer.music.pause()
        sound_channel.play(sound, loops=loops)

class Ghost:
    def __init__(self, id, x_coord, y_coord, direction, target, img, power_img, power_end_img, eaten_img):
        # Save the initial input/defaults to use when player
        # needs to reset a life or game
        self.initial_x_pos = x_coord
        self.initial_y_pos = y_coord
        self.initial_direction = direction
        self.initial_in_box = True
        self.initial_speed = 2
        self.initial_dead = False
        self.initial_eaten = False
        self.fudge_factor = 15

        self.id = id
        self.target = target
        self.img = img
        self.power_img = power_img
        self.power_end_img = power_end_img
        self.eaten_img = eaten_img

        self.reset()

    def set_dead(self, dead):
        self.dead = dead

        if dead:
            self.set_speed(4)
        else: 
            self.reset_speed()

    def set_eaten(self, eaten):
        self.eaten = eaten
        
        if self.eaten:
            self.set_dead(True)
        else:
            handle_sounds(stop=True)
            self.set_dead(False)
    
    def set_speed(self, speed):
        self.speed = speed

    def reset_speed(self):
        self.set_speed(self.initial_speed)

    def set_target(self, target):
        self.target = target

    def set_x_pos(self, x_coord):
        self.x_pos = x_coord
        self.center_x = self.x_pos + (IMG_SIZE // 2)

    def set_pos_direction(self, x_coord, y_coord, direction):
        self.set_x_pos(x_coord)

        self.y_pos = y_coord
        self.center_y = self.y_pos + (IMG_SIZE // 2)

        self.direction = direction

    def reset(self):
        self.set_pos_direction(self.initial_x_pos, self.initial_y_pos, self.initial_direction)
        self.speed = self.initial_speed
        self.dead = self.initial_dead
        self.eaten = self.set_eaten(self.initial_eaten)
        self.in_box = self.initial_in_box

    def is_in_box(self):
        if 345 < self.x_pos < 556 and 330 < self.y_pos < 491: # In the box
            return True
        else:
            return False
        
    def check_collisions(self):
        turns = [False, False, False, False]
        row = self.center_y // BOARD_TILE_HEIGHT
        column = self.center_x // BOARD_TILE_WIDTH

        # check collisions based on center x and center y of ghost +/- fudge number
        if self.center_x // board_tiles_width_num < (board_tiles_width_num - 1): # The player is within the board
            # Checking if the ghost can turn behind (180)
            if self.direction == Direction.RIGHT and \
               board[row][(self.center_x - self.fudge_factor) // BOARD_TILE_WIDTH] < 3 or \
               (board[row][(self.center_x - self.fudge_factor) // BOARD_TILE_WIDTH] == 9 and \
               (self.is_in_box() or self.dead)):
                turns[Direction.LEFT] = True
            if self.direction == Direction.LEFT and \
               board[row][(self.center_x + self.fudge_factor) // BOARD_TILE_WIDTH] < 3 or \
               (board[row][(self.center_x + self.fudge_factor) // BOARD_TILE_WIDTH] == 9 and \
               (self.is_in_box() or self.dead)):
                turns[Direction.RIGHT] = True
            if self.direction == Direction.UP and \
               board[(self.center_y + self.fudge_factor) // BOARD_TILE_HEIGHT][column] < 3 or \
               (board[(self.center_y + self.fudge_factor) // BOARD_TILE_HEIGHT][column] == 9 and \
               (self.is_in_box() or self.dead)):
                turns[Direction.DOWN] = True
            if self.direction == Direction.DOWN and \
               board[(self.center_y - self.fudge_factor) // BOARD_TILE_HEIGHT][column] < 3 or \
               (board[(self.center_y - self.fudge_factor) // BOARD_TILE_HEIGHT][column] == 9 and \
               (self.is_in_box() or self.dead)):
                turns[Direction.UP] = True

            # Check the ghost's active direction
            if self.direction == Direction.UP or self.direction == Direction.DOWN:
                if min_x_tile_coord <= self.center_x % BOARD_TILE_WIDTH <= max_x_tile_coord:
                    if board[(self.center_y + self.fudge_factor) // BOARD_TILE_HEIGHT][column] < 3 or \
                       (board[(self.center_y + self.fudge_factor) // BOARD_TILE_HEIGHT][column] == 9 and \
                        (self.is_in_box() or self.dead)):
                        turns[Direction.DOWN] = True
                    if board[(self.center_y - self.fudge_factor) // BOARD_TILE_HEIGHT][column] < 3 or \
                       (board[(self.center_y - self.fudge_factor) // BOARD_TILE_HEIGHT][column] == 9 and \
                       (self.is_in_box() or self.dead)):
                        turns[Direction.UP] = True
                if min_y_tile_coord <= self.center_y % BOARD_TILE_HEIGHT <= max_y_tile_coord:
                    if board[row][(self.center_x - BOARD_TILE_WIDTH) // BOARD_TILE_WIDTH] < 3 or \
                       (board[row][(self.center_x - BOARD_TILE_WIDTH) // BOARD_TILE_WIDTH] == 9 and \
                       (self.is_in_box() or self.dead)):
                        turns[Direction.LEFT] = True
                    if board[row][(self.center_x + BOARD_TILE_WIDTH) // BOARD_TILE_WIDTH] < 3 or \
                       (board[row][(self.center_x + BOARD_TILE_WIDTH) // BOARD_TILE_WIDTH] == 9 and \
                       (self.is_in_box() or self.dead)):
                        turns[Direction.RIGHT] = True
            if self.direction == Direction.RIGHT or self.direction == Direction.LEFT:
                if min_x_tile_coord <= self.center_x % BOARD_TILE_WIDTH <= max_x_tile_coord:
                    if board[(self.center_y + BOARD_TILE_HEIGHT) // BOARD_TILE_HEIGHT][column] < 3 or \
                       (board[(self.center_y + BOARD_TILE_HEIGHT) // BOARD_TILE_HEIGHT][column] == 9 and \
                       (self.is_in_box() or self.dead)):
                        turns[Direction.DOWN] = True
                    if board[(self.center_y - BOARD_TILE_HEIGHT) // BOARD_TILE_HEIGHT][column] < 3 or \
                       (board[(self.center_y - BOARD_TILE_HEIGHT) // BOARD_TILE_HEIGHT][column] == 9 and \
                       (self.is_in_box() or self.dead)):
                        turns[Direction.UP] = True
                if min_y_tile_coord <= self.center_y % BOARD_TILE_HEIGHT <= max_y_tile_coord:
                    if board[row][(self.center_x - self.fudge_factor) // BOARD_TILE_WIDTH] < 3 or \
                       (board[row][(self.center_x - self.fudge_factor) // BOARD_TILE_WIDTH] == 9 and \
                       (self.is_in_box() or self.dead)):
                        turns[Direction.LEFT] = True
                    if board[row][(self.center_x + self.fudge_factor) // BOARD_TILE_WIDTH] < 3 or \
                       (board[row][(self.center_x + self.fudge_factor) // BOARD_TILE_WIDTH] == 9 and \
                       (self.is_in_box() or self.dead)):
                        turns[Direction.RIGHT] = True
        else:
            turns[Direction.RIGHT] = True
            turns[Direction.LEFT] = True

        self.turns_allowed = turns

    def move_direction(self, direction):
        if direction == Direction.RIGHT:
            self.set_pos_direction(self.x_pos + self.speed, self.y_pos, direction)
        elif direction == Direction.LEFT:
            self.set_pos_direction(self.x_pos - self.speed, self.y_pos, direction)
        elif direction == Direction.UP:
            self.set_pos_direction(self.x_pos, self.y_pos - self.speed, direction)
        elif direction == Direction.DOWN:
            self.set_pos_direction(self.x_pos, self.y_pos + self.speed, direction)

    def move(self):
        self.check_collisions()
        
        if self.dead:
            if 345 < self.x_pos < 556 and 400 < self.y_pos < 491: # Back inside the box
                self.set_dead(self.initial_dead)
            else:
                self.move_sandbox()
        elif self.id == 0:
            self.move_documentation()
        elif self.id == 1:
            self.move_lab()
        elif self.id == 2:
            self.move_code()
        elif self.id == 3:
            self.move_sandbox()

    def move_documentation(self):
        if self.is_in_box():
            self.move_out_of_box()

        # documentation is going to turn whenever colliding with walls, otherwise continue straight
        elif self.direction == Direction.RIGHT:
            if self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                self.move_direction(Direction.RIGHT)
            elif not self.turns_allowed[Direction.RIGHT]:
                if self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                elif self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
            elif self.turns_allowed[Direction.RIGHT]:
                self.move_direction(Direction.RIGHT)
        elif self.direction == Direction.LEFT:
            if self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                self.move_direction(Direction.LEFT)
            elif not self.turns_allowed[Direction.LEFT]:
                if self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
                elif self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
            elif self.turns_allowed[Direction.LEFT]:
                self.move_direction(Direction.LEFT)
        elif self.direction == Direction.UP:
            if self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                self.direction = Direction.UP
                self.move_direction(Direction.UP)
            elif not self.turns_allowed[Direction.UP]:
                if self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
                elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                elif self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
                elif self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
            elif self.turns_allowed[Direction.UP]:
                self.move_direction(Direction.UP)
        elif self.direction == Direction.DOWN:
            if self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                self.move_direction(Direction.DOWN)
            elif not self.turns_allowed[Direction.DOWN]:
                if self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
                elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                elif self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
                elif self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
            elif self.turns_allowed[Direction.DOWN]:
                self.move_direction(Direction.DOWN)

        if self.x_pos < (-1*BOARD_TILE_WIDTH):
            self.set_x_pos(BOARD_WIDTH)
        elif self.x_pos > BOARD_WIDTH:
            self.set_x_pos(-1*BOARD_TILE_WIDTH)
    
    def move_lab(self):
        if self.is_in_box():
            self.move_out_of_box()

        # lab turns up or down at any point to pursue, but left and right only on collision
        elif self.direction == Direction.RIGHT:
            if self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                self.move_direction(Direction.RIGHT)
            elif not self.turns_allowed[Direction.RIGHT]:
                if self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                elif self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
            elif self.turns_allowed[Direction.RIGHT]:
                if self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                else:
                    self.move_direction(Direction.RIGHT)
        elif self.direction == Direction.LEFT:
            if self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                self.direction = Direction.DOWN
            elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                self.move_direction(Direction.LEFT)
            elif not self.turns_allowed[Direction.LEFT]:
                if self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
                elif self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
            elif self.turns_allowed[Direction.LEFT]:
                if self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                if self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                else:
                    self.move_direction(Direction.LEFT)
        elif self.direction == Direction.UP:
            if self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                self.direction = Direction.UP
                self.move_direction(Direction.UP)
            elif not self.turns_allowed[Direction.UP]:
                if self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
                elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                elif self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                elif self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
            elif self.turns_allowed[Direction.UP]:
                self.move_direction(Direction.UP)
        elif self.direction == Direction.DOWN:
            if self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                self.move_direction(Direction.DOWN)
            elif not self.turns_allowed[Direction.DOWN]:
                if self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
                elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                elif self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                elif self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
            elif self.turns_allowed[Direction.DOWN]:
                self.move_direction(Direction.DOWN)
        
        if self.x_pos < (-1*BOARD_TILE_WIDTH):
            self.set_x_pos(BOARD_WIDTH)
        elif self.x_pos > BOARD_WIDTH:
            self.set_x_pos(-1*BOARD_TILE_WIDTH)

    def move_code(self):
        if self.is_in_box():
            self.move_out_of_box()

        # code is going to turn left or right whenever advantageous, but only up or down on collision
        elif self.direction == Direction.RIGHT:
            if self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                self.move_direction(Direction.RIGHT)
            elif not self.turns_allowed[Direction.RIGHT]:
                if self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                elif self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
            elif self.turns_allowed[Direction.RIGHT]:
                self.move_direction(Direction.RIGHT)
        elif self.direction == Direction.LEFT:
            if self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                self.direction = Direction.DOWN
            elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                self.move_direction(Direction.LEFT)
            elif not self.turns_allowed[Direction.LEFT]:
                if self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
                elif self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
            elif self.turns_allowed[Direction.LEFT]:
                self.move_direction(Direction.LEFT)
        elif self.direction == Direction.UP:
            if self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                self.direction = Direction.LEFT
                self.move_direction(Direction.LEFT)
            elif self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                self.direction = Direction.UP
                self.move_direction(Direction.UP)
            elif not self.turns_allowed[Direction.UP]:
                if self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
                elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                elif self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                elif self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
            elif self.turns_allowed[Direction.UP]:
                if self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
                elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                else:
                    self.move_direction(Direction.UP)
        elif self.direction == Direction.DOWN:
            if self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                self.move_direction(Direction.DOWN)
            elif not self.turns_allowed[Direction.DOWN]:
                if self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
                elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                elif self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                elif self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
            elif self.turns_allowed[Direction.DOWN]:
                if self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
                elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                else:
                    self.move_direction(Direction.DOWN)
        
        if self.x_pos < (-1*BOARD_TILE_WIDTH):
            self.set_x_pos(BOARD_WIDTH)
        elif self.x_pos > BOARD_WIDTH:
            self.set_x_pos(-1*BOARD_TILE_WIDTH)
    
    def move_sandbox(self): 
        if self.is_in_box() and not self.dead:
            self.move_out_of_box()

        # sandbox is going to turn whenever advantageous for pursuit
        elif self.direction == Direction.RIGHT:
            if self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                self.move_direction(Direction.RIGHT)
            elif not self.turns_allowed[Direction.RIGHT]:
                if self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                elif self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
            elif self.turns_allowed[Direction.RIGHT]:
                if self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                else:
                    self.move_direction(Direction.RIGHT)
        elif self.direction == Direction.LEFT:
            if self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                self.direction = Direction.DOWN
            elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                self.move_direction(Direction.LEFT)
            elif not self.turns_allowed[Direction.LEFT]:
                if self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
                elif self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
            elif self.turns_allowed[Direction.LEFT]:
                if self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                else:
                    self.move_direction(Direction.LEFT)
        elif self.direction == Direction.UP:
            if self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                self.move_direction(Direction.LEFT)
            elif self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                self.move_direction(Direction.UP)
            elif not self.turns_allowed[Direction.UP]:
                if self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
                elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                elif self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                elif self.turns_allowed[Direction.DOWN]:
                    self.move_direction(Direction.DOWN)
                elif self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
            elif self.turns_allowed[Direction.UP]:
                if self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
                elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                else:
                    self.move_direction(Direction.UP)
        elif self.direction == Direction.DOWN:
            if self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
                self.move_direction(Direction.DOWN)
            elif not self.turns_allowed[Direction.DOWN]:
                if self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
                elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                elif self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.turns_allowed[Direction.UP]:
                    self.move_direction(Direction.UP)
                elif self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                elif self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
            elif self.turns_allowed[Direction.DOWN]:
                if self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
                    self.move_direction(Direction.RIGHT)
                elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
                    self.move_direction(Direction.LEFT)
                else:
                    self.move_direction(Direction.DOWN)
        
        if self.x_pos < (-1*BOARD_TILE_WIDTH):
            self.set_x_pos(BOARD_WIDTH)
        elif self.x_pos > BOARD_WIDTH:
            self.set_x_pos(-1*BOARD_TILE_WIDTH)

    def move_out_of_box(self):
        if (self.target[0] - 1) <= self.x_pos <= (self.target[0] + 1) and self.target[1] < self.y_pos:
            self.move_direction(Direction.UP)
        elif self.target[0] > self.x_pos and self.turns_allowed[Direction.RIGHT]:
            self.move_direction(Direction.RIGHT)
        elif self.target[0] < self.x_pos and self.turns_allowed[Direction.LEFT]:
            self.move_direction(Direction.LEFT)
        elif self.target[1] > self.y_pos and self.turns_allowed[Direction.DOWN]:
            self.move_direction(Direction.DOWN)
        elif self.target[1] < self.y_pos and self.turns_allowed[Direction.UP]:
            self.move_direction(Direction.UP)

    def draw(self, screen, powerup, power_counter, game_over, game_won):
        x_pos_offset = WIDTH_OFFSET + self.x_pos
        y_pos_offset = HEIGHT_OFFSET + self.y_pos

        if not game_over and not game_won:
            if (not powerup and not self.dead) or (self.eaten and powerup and not self.dead):
                screen.blit(self.img, (x_pos_offset, y_pos_offset))
            elif powerup and not self.dead and not self.eaten:
                # Alternate the powerup image
                if power_counter <= (8.75 * FPS) or \
                    int(8 * FPS) < power_counter <= int(8.25 * FPS) or \
                    int(8.5 * FPS) < power_counter <= int(8.75 * FPS) or \
                    int(9 * FPS) < power_counter <= int(9.25 * FPS) or \
                    int(9.5 * FPS) < power_counter <= int(9.75 * FPS):
                    screen.blit(self.power_img, (x_pos_offset, y_pos_offset))
                elif int(7.75 * FPS) < power_counter <= int(8 * FPS) or \
                     int(8.25 * FPS) < power_counter <= int(8.5 * FPS) or \
                     int(8.75 * FPS) < power_counter <= int(9 * FPS) or \
                     int(9.25 * FPS) < power_counter <= int(9.5 * FPS) or \
                     int(9.75 * FPS) < power_counter < int(10 * FPS) :
                    screen.blit(self.power_end_img, (x_pos_offset, y_pos_offset))
            else:
                screen.blit(dead_img, (x_pos_offset, y_pos_offset))
        
        self.rect = pygame.rect.Rect((self.center_x - 21, self.center_y - 21), (44, 44)) # Ghost hit box 

    def activate_powerup(self):
        if not self.eaten and not self.dead:
            self.set_speed(1)

class Player:
    def __init__(self, x_coord, y_coord, direction, imgs, dead_img):
        # Save the initial input/defaults to use when player
        # needs to reset a life or game
        self.initial_lives = 3
        self.initial_score = 0
        self.initial_turns_allowed = [False, False, False, False]
        self.initial_direction_command = 0
        self.initial_x_pos = x_coord
        self.initial_y_pos = y_coord
        self.initial_direction = direction
        self.speed = 2
        self.fudge_factor = 15

        self.new_game()
        self.imgs = imgs
        self.dead_img =  dead_img

    def set_direction(self, direction):
        self.direction = direction

    def set_direction_command(self, direction_command):
        self.direction_command = direction_command

    def set_lives(self, lives):
        self.lives = lives

    def set_score(self, score):
        self.score = score

    def set_x_pos(self, x_coord):
        self.x_pos = x_coord
        self.center_x = self.x_pos + (IMG_SIZE // 2) + 1 # +1 is arbritary based on trial and error

        # Handle the player going off screen to the other side
        if self.x_pos > BOARD_WIDTH:
            self.set_x_pos(-47) # Right off the board
        elif self.x_pos < -50:
            self.set_x_pos(BOARD_WIDTH - 3)

    def set_y_pos(self, y_coord):
        self.y_pos = y_coord
        self.center_y = self.y_pos + (IMG_SIZE // 2) + 2 # +2 is arbritary based on trial and error
    
    def reset(self):
        self.turns_allowed = self.initial_turns_allowed
        self.set_x_pos(self.initial_x_pos)
        self.set_y_pos(self.initial_y_pos)
        self.set_direction_command(self.initial_direction_command)
        self.set_direction(self.initial_direction)

    def new_life(self):
        self.reset()
        self.set_lives(self.lives - 1)

    def new_game(self):
        self.reset()
        self.set_lives(self.initial_lives)
        self.score = self.initial_score

    def change_direction(self):
        if self.direction_command == Direction.RIGHT and self.turns_allowed[Direction.RIGHT]:
            self.set_direction(Direction.RIGHT)
        if self.direction_command == Direction.LEFT and self.turns_allowed[Direction.LEFT]:
            self.set_direction(Direction.LEFT)
        if self.direction_command == Direction.UP and self.turns_allowed[Direction.UP]:
            self.set_direction(Direction.UP)
        if self.direction_command == Direction.DOWN and self.turns_allowed[Direction.DOWN]:
            self.set_direction(Direction.DOWN)

    def eat(self, power_up, power_count):
        if 0 < self.x_pos < (BOARD_WIDTH - BOARD_TILE_WIDTH):
            row = self.center_y // BOARD_TILE_HEIGHT
            column = self.center_x // BOARD_TILE_WIDTH
            # Player eats the dot, so make it empty
            if board[row][column] == 1:
                board[row][column] = 0
                self.set_score(self.score + 10)
                pygame.mixer.Sound.play(sound_chomp)
            
            # Player eats the power pellet, so make it empty
            if board[row][column] == 2:
                board[row][column] = 0
                self.set_score(self.score + 50)
                handle_sounds(sound_power, play=True, loops=-1)
                power_up = True
                power_count = 0
        
        return power_up, power_count
    
    def check_collisions(self):
        turns = [False, False, False, False]

        # check collisions based on center x and center y of player +/- fudge number
        if self.center_x // board_tiles_width_num < (board_tiles_width_num - 1): # The player is within the board

            # Checking if the player can turn behind (180)
            if self.direction == Direction.RIGHT and board[self.center_y // BOARD_TILE_HEIGHT][(self.center_x - self.fudge_factor) // BOARD_TILE_WIDTH] < 3:
                turns[Direction.LEFT] = True
            if self.direction == Direction.LEFT and board[self.center_y // BOARD_TILE_HEIGHT][(self.center_x + self.fudge_factor) // BOARD_TILE_WIDTH] < 3:
                turns[Direction.RIGHT] = True
            if self.direction == Direction.UP and board[(self.center_y + self.fudge_factor) // BOARD_TILE_HEIGHT][self.center_x // BOARD_TILE_WIDTH] < 3:
                turns[Direction.DOWN] = True
            if self.direction == Direction.DOWN and board[(self.center_y - self.fudge_factor) // BOARD_TILE_HEIGHT][self.center_x // BOARD_TILE_WIDTH] < 3:
                turns[Direction.UP] = True

            # Check the players active direction
            if self.direction == Direction.UP or self.direction == Direction.DOWN:
                if min_x_tile_coord <= self.center_x % BOARD_TILE_WIDTH <= max_x_tile_coord:
                    if board[(self.center_y + self.fudge_factor) // BOARD_TILE_HEIGHT][self.center_x // BOARD_TILE_WIDTH] < 3: # 3 because tiles 0, 1, 2 are the tiles the player can move within
                        turns[Direction.DOWN] = True
                    if board[(self.center_y - self.fudge_factor) // BOARD_TILE_HEIGHT][self.center_x // BOARD_TILE_WIDTH] < 3:
                        turns[Direction.UP] = True
                if min_y_tile_coord <= self.center_y % BOARD_TILE_HEIGHT <= max_y_tile_coord:
                    if board[self.center_y // BOARD_TILE_HEIGHT][(self.center_x - BOARD_TILE_WIDTH) // BOARD_TILE_WIDTH] < 3:
                        turns[Direction.LEFT] = True
                    if board[self.center_y // BOARD_TILE_HEIGHT][(self.center_x + BOARD_TILE_WIDTH) // BOARD_TILE_WIDTH] < 3:
                        turns[Direction.RIGHT] = True
            if self.direction == Direction.RIGHT or self.direction == Direction.LEFT:
                if min_x_tile_coord <= self.center_x % BOARD_TILE_WIDTH <= max_x_tile_coord:
                    if board[(self.center_y + BOARD_TILE_HEIGHT) // BOARD_TILE_HEIGHT][self.center_x // BOARD_TILE_WIDTH] < 3:
                        turns[Direction.DOWN] = True
                    if board[(self.center_y - BOARD_TILE_HEIGHT) // BOARD_TILE_HEIGHT][self.center_x // BOARD_TILE_WIDTH] < 3:
                        turns[Direction.UP] = True
                if min_y_tile_coord <= self.center_y % BOARD_TILE_HEIGHT <= max_y_tile_coord:
                    if board[self.center_y // BOARD_TILE_HEIGHT][(self.center_x - self.fudge_factor) // BOARD_TILE_WIDTH] < 3:
                        turns[Direction.LEFT] = True
                    if board[self.center_y // BOARD_TILE_HEIGHT][(self.center_x + self.fudge_factor) // BOARD_TILE_WIDTH] < 3:
                        turns[Direction.RIGHT] = True
        else:
            turns[Direction.RIGHT] = True
            turns[Direction.LEFT] = True

        self.turns_allowed = turns
    
    def move(self):
        self.check_collisions()

        if self.direction == Direction.RIGHT and self.turns_allowed[Direction.RIGHT]:
            self.set_x_pos(self.x_pos + self.speed)
        elif self.direction == Direction.LEFT and self.turns_allowed[Direction.LEFT]:
            self.set_x_pos(self.x_pos - self.speed)
        if self.direction == Direction.UP and self.turns_allowed[Direction.UP]:
            self.set_y_pos(self.y_pos - self.speed)
        elif self.direction == Direction.DOWN and self.turns_allowed[Direction.DOWN]:
            self.set_y_pos(self.y_pos + self.speed)

    def draw(self, screen, game_over, game_won, img_index):
        if not game_over and not game_won:
            player_x_offset = WIDTH_OFFSET + self.x_pos
            player_y_offset = HEIGHT_OFFSET + self.y_pos


            img = self.imgs[img_index] if img_index < 4 else self.dead_img

            if self.direction == Direction.RIGHT:
                screen.blit(img, (player_x_offset, player_y_offset))
            elif self.direction == Direction.LEFT:
                screen.blit(pygame.transform.flip(img, True, False), (player_x_offset, player_y_offset))
            elif self.direction == Direction.UP:
                screen.blit(pygame.transform.rotate(img, 90), (player_x_offset, player_y_offset))
            elif self.direction == Direction.DOWN:
                screen.blit(pygame.transform.rotate(img, 270), (player_x_offset, player_y_offset))
        

class Game:
    # Counters
    counter = 0
    power_counter = 0

    flicker = False
    powerup = False
    start_game = True
    start_life = True
    game_over = False
    game_won = False
    num_games = 0

    def __init__(self, player, ghost1, ghost2, ghost3, ghost4):        
        self.player = player
        self.ghost1 = ghost1
        self.ghost2 = ghost2
        self.ghost3 = ghost3
        self.ghost4 = ghost4
        
        pygame.mixer.music.load(FILE_PATH_PREFIX + '/assets/sounds/background.mp3')

        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
        else:
            self.joystick = None
                
    def draw_board(self, screen):
        LINE_COLOR = 'blue'
        PI = math.pi
        
        for row in range(len(board)):
            for column in range(len(board[row])):
                x_coordinate_left = WIDTH_OFFSET + column * BOARD_TILE_WIDTH
                x_coordinate_center = x_coordinate_left + (0.5 * BOARD_TILE_WIDTH)
                y_coordinate_top = HEIGHT_OFFSET + row * BOARD_TILE_HEIGHT
                y_coordinate_center = y_coordinate_top + (0.5 * BOARD_TILE_HEIGHT)

                if board[row][column] == 1:
                    pygame.draw.circle(screen, 'white', (x_coordinate_center, y_coordinate_center), 4)
                if board[row][column] == 2 and not self.flicker:
                    pygame.draw.circle(screen, 'white', (x_coordinate_center, y_coordinate_center), 10)
                if board[row][column] == 3:
                    pygame.draw.line(screen, LINE_COLOR, (x_coordinate_center, y_coordinate_top),
                                    (x_coordinate_center, y_coordinate_top + BOARD_TILE_HEIGHT), 3)
                if board[row][column] == 4:
                    pygame.draw.line(screen, LINE_COLOR, (x_coordinate_left, y_coordinate_center),
                                    (x_coordinate_left + BOARD_TILE_WIDTH, y_coordinate_center), 3)
                if board[row][column] == 5:
                    pygame.draw.arc(screen, LINE_COLOR, [(x_coordinate_left - (BOARD_TILE_WIDTH * 0.4)) - 2, y_coordinate_center,
                                                    BOARD_TILE_WIDTH, BOARD_TILE_HEIGHT], 0, PI / 2, 3)
                if board[row][column] == 6:
                    pygame.draw.arc(screen, LINE_COLOR,
                                    [x_coordinate_center, y_coordinate_center, BOARD_TILE_WIDTH, BOARD_TILE_HEIGHT], PI / 2, PI, 3)
                if board[row][column] == 7:
                    pygame.draw.arc(screen, LINE_COLOR, [x_coordinate_center, (y_coordinate_top - (0.4 * BOARD_TILE_HEIGHT)),
                                                    BOARD_TILE_WIDTH, BOARD_TILE_HEIGHT], PI, 3 * PI / 2, 3)
                if board[row][column] == 8:
                    pygame.draw.arc(screen, LINE_COLOR,
                                    [(x_coordinate_left - (0.4 * BOARD_TILE_WIDTH)) - 2, (y_coordinate_top - (0.4 * BOARD_TILE_HEIGHT)),
                                    BOARD_TILE_WIDTH, BOARD_TILE_HEIGHT], 3 * PI / 2, 2 * PI, 3)
                if board[row][column] == 9:
                    pygame.draw.line(screen, 'white', (x_coordinate_left, y_coordinate_center),
                                    (x_coordinate_left + BOARD_TILE_WIDTH, y_coordinate_center), 3)

    def draw_misc(self, screen, high_score):
        # Draw score
        score_text = font.render(f'SCORE: {self.player.score}', True, 'white')
        screen.blit(score_text, (WIDTH_OFFSET + BOARD_TILE_WIDTH * 3, HEIGHT_OFFSET - BOARD_TILE_HEIGHT - 6))

        # Draw high score
        if self.player.score > high_score:
            high_score = self.player.score
        high_score_text = font.render(f'HIGH SCORE: {high_score}', True, 'white')
        screen.blit(high_score_text, (WIDTH_OFFSET + BOARD_TILE_WIDTH * 15, HEIGHT_OFFSET - BOARD_TILE_HEIGHT - 6))

        # Draw player lives
        for i in range(self.player.lives):
            screen.blit(self.player.imgs[0], (WIDTH_OFFSET + BOARD_TILE_WIDTH * 3 + i * 50, HEIGHT_OFFSET + BOARD_HEIGHT - BOARD_TILE_HEIGHT))

    def get_list_of_ghosts(self):
        return [self.ghost1, self.ghost2, self.ghost3, self.ghost4]

    def update_targets(self):
        if self.player.x_pos < (BOARD_WIDTH // 2): # Left half of the screen
            runaway_x = BOARD_WIDTH
        else:
            runaway_x = 0

        if self.player.y_pos < (BOARD_HEIGHT // 2): # Top half of the screen
            runaway_y = BOARD_HEIGHT
        else:
            runaway_y = 0

        # Target coordinates
        return_target = (425, 420)
        outside_box_target = (429, 326) # Random coordinate outside of the ghost box
        player_target = (self.player.x_pos, self.player.y_pos)

        if self.powerup:
            if not self.ghost1.dead and not self.ghost1.eaten:
                ghost1_target = (runaway_x, runaway_y)
            elif not self.ghost1.dead and self.ghost1.eaten:
                if self.ghost1.is_in_box():
                    ghost1_target = outside_box_target
                else:
                    ghost1_target = player_target
            else:
                ghost1_target = return_target
            if not self.ghost2.dead and not self.ghost2.eaten:
                ghost2_target = (runaway_x, self.player.y_pos)
            elif not self.ghost2.dead and self.ghost2.eaten:
                if self.ghost2.is_in_box():
                    ghost2_target = outside_box_target
                else:
                    ghost2_target = (self.player.x_pos, self.player.y_pos)
            else:
                ghost2_target = return_target
            if not self.ghost3.dead and self.ghost3.eaten:
                if self.ghost3.is_in_box():
                    ghost3_target = outside_box_target
                else:
                    ghost3_target = player_target
            elif not self.ghost3.dead:
                ghost3_target = (self.player.x_pos, runaway_y)
            else:
                ghost3_target = return_target
            if not self.ghost4.dead and not self.ghost4.eaten:
                ghost4_target = (450, 450) # TODO: Change to whatever coordinates we want them to go to during a powerup
            elif not self.ghost4.dead and self.ghost4.eaten:
                if self.ghost4.is_in_box():
                    ghost4_target = outside_box_target
                else:
                    ghost4_target = player_target
            else:
                ghost4_target = return_target
        else:
            if not self.ghost1.dead:
                if self.ghost1.is_in_box():
                    ghost1_target = outside_box_target
                else:
                    ghost1_target = player_target
            else:
                ghost1_target = return_target
            if not self.ghost2.dead:
                if self.ghost2.is_in_box():
                    ghost2_target = outside_box_target
                else:
                    ghost2_target = player_target
            else:
                ghost2_target = return_target
            if not self.ghost3.dead:
                if self.ghost3.is_in_box():
                    ghost3_target = outside_box_target
                else:
                    ghost3_target = player_target
            else:
                ghost3_target = return_target
            if not self.ghost4.dead:
                if self.ghost4.is_in_box():
                    ghost4_target = outside_box_target
                else:
                    ghost4_target = player_target
            else:
                ghost4_target = return_target

        self.ghost1.set_target(ghost1_target)
        self.ghost2.set_target(ghost2_target)
        self.ghost3.set_target(ghost3_target)
        self.ghost4.set_target(ghost4_target)

    def reset(self):
        self.start_life = True
        self.powerup = False
        self.power_counter = 0
        self.counter = 0
        self.flicker = False
        self.ghost1.reset()
        self.ghost2.reset()
        self.ghost3.reset()
        self.ghost4.reset()

    def new_life(self):
        self.reset()
        self.player.new_life()
        
    def new_game(self):
        self.reset()
        self.player.new_game()
        self.game_over = False
        self.game_won = False
        self.start_game = True
        self.num_games += 1

        reset_board()

    def reset_eaten(self):
        ghosts = self.get_list_of_ghosts()

        for ghost in ghosts:
            ghost.set_eaten(False)

    def get_num_eaten(self):
        num_eaten = 0
        if self.ghost1.eaten:
            num_eaten += 1
        if self.ghost2.eaten:
            num_eaten += 1
        if self.ghost3.eaten:
            num_eaten += 1
        if self.ghost4.eaten:
            num_eaten += 1
        
        return num_eaten

    def check_ghosts_eaten(self, screen, player_circle):
        ghosts = self.get_list_of_ghosts()

        for ghost in ghosts:
            if player_circle.colliderect(ghost.rect):
                if self.powerup and not ghost.dead and not ghost.eaten:
                    ghost.set_eaten(True)
                    handle_sounds(sound_pacman_eat_ghost, play=True)
                    ghost_eaten_score = (2 ** self.get_num_eaten()) * 100
                    ghost_eaten_font = pygame.font.Font(font_filepath, 20)
                    eaten_img_x_coord = WIDTH_OFFSET + ghost.x_pos
                    score_y_coord = HEIGHT_OFFSET + ghost.y_pos
                    if self.player.direction == Direction.DOWN:
                        eaten_img_x_coord += IMG_SIZE
                        score_y_coord += IMG_SIZE
                    elif self.player.direction == Direction.LEFT:
                        eaten_img_x_coord -= ghost.eaten_img.get_width()
                        score_y_coord -= 30
                    else:
                        eaten_img_x_coord += IMG_SIZE
                        score_y_coord -= 30
                    screen.blit(ghost.eaten_img, (eaten_img_x_coord, HEIGHT_OFFSET + ghost.y_pos + (IMG_SIZE // 4) - (ghost.eaten_img.get_height() // 2)))
                    screen.blit(ghost_eaten_font.render(f'{ghost_eaten_score}', True, 'cyan'), (WIDTH_OFFSET + ghost.x_pos, score_y_coord))
                    pygame.display.flip()
                    pygame.time.delay(1000) # Game pauses for one second when a ghost gets eaten
                    
                    handle_sounds(sound_ghost_eaten, play=True, loops=-1)
                    self.player.set_score(self.player.score + ghost_eaten_score)
                elif (self.powerup and not ghost.dead and ghost.eaten) or \
                    (not self.powerup and not self.ghost1.dead):
                    self.player.draw(screen, False, False, 5)
                    pygame.display.flip()
                    pygame.mixer.music.stop()
                    pygame.mixer.Sound.play(sound_pacman_death)
                    pygame.time.delay(1000)
                    if self.player.lives > 0:
                        self.new_life()
                    else:
                        self.game_over = True

    def display_ready(self, screen):
        ready_text = font.render('READY!', True, (247, 246, 6))
        screen.blit(ready_text, ((DISPLAY_WIDTH - ready_text.get_width())/2, HEIGHT_OFFSET + 500))
        pygame.display.flip()

    def clear_key_presses(self):
        # Clear out any existing key presses
        pygame.event.clear()

    def getHighScore(self, highScore):
        if highScore:
            return highScore.get_high_score()
        else:
            with open(FILE_PATH_PREFIX + '/high_score.txt', 'r') as file:
                lines = file.readlines()        # reads all the lines and puts in a list
                score = int(lines[0].strip())   # remove \n

            return score
    
    def updateHighScore(self, highScore, new_score):
        if highScore:
            highScore.check_high_score(new_score)

            return highScore.get_is_top_10(), highScore.get_is_high_score()
        else:
            last_high_score = self.getHighScore(highScore)

            with open(FILE_PATH_PREFIX + '/high_score.txt', 'w') as file:
                if new_score > last_high_score:
                    file.write(str(new_score))
                    return True, True
                else:
                    file.write(str(last_high_score))

                    return False, False

    def run(self, screen, max_games=999, highScore=False):
        self.clear_key_presses()

        high_score = None
        if highScore:
            sys.path.insert(2, FILE_PATH_PREFIX + '/../high_score')
            from high_score import HighScore
            high_score = HighScore(screen, font, FILE_PATH_PREFIX + '/high_score_superdevvie.json', FPS)
        
        is_game_won = False
        is_top_10 = False
        is_high_score = False
        score = 0

        run = True
        while run:
            timer.tick(FPS)

            # Draw background and board
            screen.fill('black')
            player_circle = pygame.draw.circle(screen, 'black', (self.player.center_x, self.player.center_y), 20, 2)
            self.draw_board(screen)
            self.draw_misc(screen, self.getHighScore(high_score))

            # Check if game won
            self.game_won = True
            for i in range(len(board)):
                if 1 in board[i] or 2 in board[i]:
                    self.game_won = False
                    break
            
            # Handle game over or won
            if self.game_over or self.game_won:
                if self.game_over:
                    game_ending_text = font.render('GAME OVER', True, 'red')
                elif self.game_won:
                    game_ending_text = font.render('VICTORY', True, 'green')
                
                screen.blit(game_ending_text, ((DISPLAY_WIDTH - game_ending_text.get_width())/2, HEIGHT_OFFSET + 500))
                pygame.display.flip()

                pygame.mixer.music.stop()
                pygame.time.delay(3000) # wait for 3 seconds
                is_game_won = self.game_won
                is_top_10, is_high_score = self.updateHighScore(high_score, self.player.score)
                score = self.player.score
                self.new_game()

                if self.num_games == max_games:
                    run = False
                    break
                else:
                    continue

            # Show READY for a new game
            if self.start_game:
                handle_sounds(sound_start, play=True)
                self.display_ready(screen)
                pygame.time.delay(3000) # wait for 3 seconds
                self.start_game = False
                continue
            
            # Draw player and resources
            self.player.draw(screen, self.game_over, self.game_won, self.counter // 5) # 5 frames per image
            self.ghost1.draw(screen, self.powerup, self.power_counter, self.game_over, self.game_won)
            self.ghost2.draw(screen, self.powerup, self.power_counter, self.game_over, self.game_won)
            self.ghost3.draw(screen, self.powerup, self.power_counter, self.game_over, self.game_won)
            self.ghost4.draw(screen, self.powerup, self.power_counter, self.game_over, self.game_won)

            # Show READY with player & resources
            if self.start_life:
                self.display_ready(screen)
                pygame.time.delay(2000) # wait for 2 seconds
                pygame.mixer.music.play(-1)
                self.start_life = False
                continue

            # Handle flicker
            if self.counter < 19: # Determines how fast pacman cycles through the eating images
                self.counter += 1
                if self.counter > 3: # Determines how fast to flicker the powerpellet
                    self.flicker = False
            else:
                self.counter = 0
                self.flicker = True

            # Handle the powerup    
            if self.powerup:
                self.ghost1.activate_powerup()
                self.ghost2.activate_powerup()
                self.ghost3.activate_powerup()
                self.ghost4.activate_powerup()

                if self.power_counter < (10 * FPS): # powerup lasts 10 seconds
                    self.power_counter += 1
                else:
                    self.power_counter = 0
                    self.powerup = False
                    handle_sounds(stop=True)
                    pygame.mixer.music.play(-1)
                    self.reset_eaten()
            else:
                self.ghost1.reset_speed()
                self.ghost2.reset_speed()
                self.ghost3.reset_speed()
                self.ghost4.reset_speed()

            # Handle player moving
            self.player.move()
            self.update_targets()
            
            self.ghost1.move()
            self.ghost2.move()
            self.ghost3.move()
            self.ghost4.move()

            self.powerup, self.power_counter = self.player.eat(self.powerup, self.power_counter)

            # Handle collision with ghost
            self.check_ghosts_eaten(screen, player_circle)

            # Handle player movement
            for event in pygame.event.get():
                if (event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT) or \
                   (event.type == pygame.JOYAXISMOTION and self.joystick and round(self.joystick.get_axis(0)) == 1):
                    self.player.set_direction_command(Direction.RIGHT)
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT) or \
                     (event.type == pygame.JOYAXISMOTION and self.joystick and round(self.joystick.get_axis(0)) == -1):
                    self.player.set_direction_command(Direction.LEFT)
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_UP) or \
                     (event.type == pygame.JOYAXISMOTION and self.joystick and round(self.joystick.get_axis(1)) == -1):
                    self.player.set_direction_command(Direction.UP)
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN) or \
                     (event.type == pygame.JOYAXISMOTION and self.joystick and round(self.joystick.get_axis(1)) == 1):
                    self.player.set_direction_command(Direction.DOWN)
                elif event.type == pygame.JOYDEVICEADDED:
                    self.joystick = pygame.joystick.Joystick(event.device_index)
                    self.joystick.init()
                elif event.type == pygame.JOYDEVICEREMOVED:
                    self.joystick = None
                elif event.type == pygame.QUIT or \
                     (event.type == pygame.JOYBUTTONDOWN and self.joystick and self.joystick.get_button(Buttons.ADMIN_LEFT) and self.joystick.get_button(Buttons.ADMIN_RIGHT)):
                    pygame.mixer.music.stop()
                    sound_channel.stop()
                    run = False

            self.player.change_direction()

            pygame.display.flip()
        return is_game_won, is_top_10, is_high_score, score
                
def display_intro_screen(screen):
    resource_img_size = 144
    resource_y_coord = 596

    timer.tick(FPS)

    screen.fill('black')
    screen.blit(title_img, ((DISPLAY_WIDTH - title_img.get_size()[0])/2, 110))

    devvie_studying_img = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/intro_images/devvie-studying.png')
    screen.blit(devvie_studying_img, ((DISPLAY_WIDTH - devvie_studying_img.get_size()[0])/2, 438))
    screen.blit(pygame.transform.scale(documentation_img, (resource_img_size, resource_img_size)), (200, resource_y_coord))
    screen.blit(pygame.transform.scale(lab_img, (resource_img_size, resource_img_size)), (500, resource_y_coord))
    screen.blit(pygame.transform.scale(code_img, (resource_img_size, resource_img_size)), (1275, resource_y_coord))
    screen.blit(pygame.transform.scale(sandbox_img, (resource_img_size, resource_img_size)), (1575, resource_y_coord))

    pygame.display.flip()
    pygame.time.delay(1000) # wait for a seconds
    
def display_story_screen(screen):
    message_line1 = 'Devvie is studying for the DevNet Associate certification.'
    message_line2 = 'He is looking for hands-on API and developer experience, so he heads over'
    message_line3 = 'to developer.cisco.com. What resources are Devvie able to utilize? '
    line1_counter = 0
    line2_counter = 0
    line3_counter = 0
    speed = 2
    story_run = True
    devvie_studying_img = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/intro_images/devvie-studying.png')
    website_img = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/intro_images/website.png')

    while story_run:
        timer.tick(FPS)
        screen.fill('black')

        website_y_coord = 100
        screen.blit(website_img, (803, website_y_coord))
        screen.blit(devvie_studying_img, (290, website_y_coord + website_img.get_height() - devvie_studying_img.get_height()))

        line1_y_cord = 700
        text_height = 70
        screen.blit(font.render(message_line1[0:line1_counter//speed], True, 'white'), (100, line1_y_cord))
        if line1_counter < speed * len(message_line1):
            line1_counter += 1
        else:
            screen.blit(font.render(message_line2[0:line2_counter//speed], True, 'white'), (100, line1_y_cord + 1*text_height))
            if line2_counter < speed * len(message_line2):
                line2_counter += 1
            else:
                screen.blit(font.render(message_line3[0:line3_counter//speed], True, 'white'), (100, line1_y_cord + 2*text_height))
                if line3_counter < speed * len(message_line3):
                    line3_counter += 1
                elif line3_counter == speed * len(message_line3):
                    story_run = False
                
        pygame.display.flip()
    
    pygame.time.delay(1000) # wait for 1 second before changing to the next screen

def display_description_screen(screen):
    description_screen_counter = 0
    counter_per_change = 30
    resource_img_size = 72
    icon_x_coord = 100
    character_x_coord = 225
    description_x_coord = 600

    run_description_screen = True
    while run_description_screen:
        timer.tick(FPS)
        screen.fill('black')

        if description_screen_counter > 20*counter_per_change:
            run_description_screen = False
            break

        screen.blit(font.render('Character', True, 'white'), (character_x_coord, 60))
        screen.blit(font.render('Description', True, 'white'), (description_x_coord, 60))

        # Devvie
        if description_screen_counter > 1*counter_per_change:
            screen.blit(pygame.image.load(f'{FILE_PATH_PREFIX}/assets/intro_images/devvie-head.png'), (icon_x_coord, 135))
        if description_screen_counter > 2*counter_per_change:
            screen.blit(font.render('Devvie  - - - - - - - -', True, (247, 246, 6)), (character_x_coord, 150))
        if description_screen_counter > 3*counter_per_change:
            screen.blit(font.render('The DevNet mascot who is looking for resources on', True, (247, 246, 6)), (description_x_coord, 150))
            screen.blit(font.render('developer.cisco.com.', True, (247, 246, 6)), (description_x_coord, 185))

        # Documentation
        if description_screen_counter > 4*counter_per_change:
            screen.blit(pygame.transform.scale(documentation_img, (resource_img_size, resource_img_size)), (icon_x_coord, 225))
        if description_screen_counter > 5*counter_per_change:
            screen.blit(font.render('Documentation  - -', True, (153, 102, 204)), (character_x_coord, 250))
        if description_screen_counter > 6*counter_per_change:
            screen.blit(font.render('The DevNet site provides access to API, SDK, data model,', True, (153, 102, 204)), (description_x_coord, 250))
            screen.blit(font.render('documentation and more.', True, (153, 102, 204)), (description_x_coord, 285))

        # Lab
        if description_screen_counter > 7*counter_per_change:
            screen.blit(pygame.transform.scale(lab_img, (resource_img_size, resource_img_size)), (icon_x_coord, 325))
        if description_screen_counter > 8*counter_per_change:
            screen.blit(font.render('Learning Labs  - -', True, (30, 170, 215)), (character_x_coord, 350))
        if description_screen_counter > 9*counter_per_change:
            screen.blit(font.render('Efficient interactive self-paced tutorials with', True, (30, 170, 215)), (description_x_coord, 350))
            screen.blit(font.render('Cisco products.', True, (30, 170, 215)), (description_x_coord, 385))
        
        # Sample Code
        if description_screen_counter > 10*counter_per_change:
            screen.blit(pygame.transform.scale(code_img, (resource_img_size, resource_img_size)), (icon_x_coord, 425))
        if description_screen_counter > 11*counter_per_change:
            screen.blit(font.render('Sample Code  - - - -', True, (106, 191, 75)), (character_x_coord, 450))
        if description_screen_counter > 12*counter_per_change:
            screen.blit(font.render('The DevNet site contains sample solutions and', True, (106, 191, 75)), (description_x_coord, 450))
            screen.blit(font.render('implementations in Code Exchange.', True, (106, 191, 75)), (description_x_coord, 485))
        
        # Sandbox
        if description_screen_counter > 13*counter_per_change:
            screen.blit(pygame.transform.scale(sandbox_img, (resource_img_size, resource_img_size)), (icon_x_coord, 525))
        if description_screen_counter > 14*counter_per_change:
            screen.blit(font.render('Sandbox  - - - - - -', True, (251, 171, 25)), (character_x_coord, 550))
        if description_screen_counter > 15*counter_per_change:
            screen.blit(font.render('Free pre-built Cisco platforms to test APIs, SDKs, and', True, (251, 171, 25)), (description_x_coord, 550))
            screen.blit(font.render('solutions.', True, (251, 171, 25)), (description_x_coord, 585))
        
        # Score legend
        if description_screen_counter > 16*counter_per_change:
            pygame.draw.circle(screen, 'white', (910, 825), 4)
            screen.blit(font.render('10 PTS', True, 'white'), (950, 805))
            pygame.draw.circle(screen, 'white', (910, 875), 10)
            screen.blit(font.render('50 PTS', True, 'white'), (950, 855))

        description_screen_counter += 1
        pygame.display.flip()

def run_game(screen, max_games=999, highScore=False):
    display_intro_screen(screen)
    display_story_screen(screen)
    display_description_screen(screen)

    reset_board()

    player = Player(PLAYER['x'], PLAYER['y'], PLAYER['direction'], player_images, player_dead_img)
    documentation = Ghost(0, DOCUMENTATION['x'], DOCUMENTATION['y'], DOCUMENTATION['direction'], (player.x_pos, player.y_pos), pygame.transform.scale(documentation_img, IMG_DIMENSIONS), documentation_power_img, documentation_power_end_img, documentation_eaten_img)
    lab = Ghost(1, LAB['x'], LAB['y'], LAB['direction'], (player.x_pos, player.y_pos), pygame.transform.scale(lab_img, IMG_DIMENSIONS), lab_power_img, lab_power_end_img, lab_eaten_img)
    code = Ghost(2,CODE['x'], CODE['y'], CODE['direction'], (player.x_pos, player.y_pos), pygame.transform.scale(code_img, IMG_DIMENSIONS), code_power_img, code_power_end_img, code_eaten_img)
    sandbox = Ghost(3, SANDBOX['x'], SANDBOX['y'], SANDBOX['direction'], (player.x_pos, player.y_pos), pygame.transform.scale(sandbox_img, IMG_DIMENSIONS), sandbox_power_img, sandbox_power_end_img, sandbox_eaten_img)

    game = Game(player, documentation, lab, code, sandbox)
    return game.run(screen, max_games, highScore)

if __name__ == '__main__':
    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    flags = pygame.FULLSCREEN
    screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), flags, vsync=1)
    run_game(screen)
    pygame.joystick.quit()
    pygame.quit()
