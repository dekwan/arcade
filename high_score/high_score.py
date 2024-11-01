import json
import math
import os
import sys

import pygame

class Buttons:
    ADMIN_LEFT = 8
    ADMIN_RIGHT = 9
    PLAYER_LEFT = 3
    PLAYER_RIGHT = 4

    if sys.platform.startswith('darwin'): # MacOS seems to have different button numbers
        PLAYER_LEFT = 2

class HighScore:
    pygame.init()
    pygame.joystick.init()

    timer = pygame.time.Clock()
    
    score_colors = [(153, 102, 204), (30, 170, 215), (106, 191, 75), (251, 171, 25)]
    initial_options = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    rank_strs = ['1ST', '2ND', '3RD', '4TH', '5TH', '6TH', '7TH', '8TH', '9TH', '10TH']

    def __init__(self, surface, font, filename, fps, ascending=False):
        self.surface = surface
        self.display_width = surface.get_width()
        self.display_height = surface.get_height()
        self.width_offset = 605 # Want to center the text
        self.height_offset = 20 # The display cuts off some pixels from the top
        self.fps = fps

        self.score = 0
        self.ascending = ascending
        self.is_score_high_score = False
        self.is_score_top_10 = False
        self.initial_indexes = [0, 0, 0]
        self.filename = filename
        self.load_high_score_list()

        self.font = font
        self.rank_text = self.font.render('Rank', True, 'white')
        self.score_text = self.font.render('Score', True, 'white')
        self.initials_text = self.font.render('Initials', True, 'white')

        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
        else:
            self.joystick = None

    def load_high_score_list(self):
        with open(self.filename, 'r') as reader:
            # Read the entire file
            self.high_score_list = json.loads(reader.read())

    def set_score(self, score):
        self.score = score

    def get_is_high_score(self):
        return self.is_score_high_score
    
    def get_is_top_10(self):
        return self.is_score_top_10
    
    def get_high_score(self):
        if len(self.high_score_list) == 0:
            return 0
        else:
            return self.high_score_list[0]['score']
    
    def is_high_score(self):
        len_high_score_list = len(self.high_score_list)
        if len_high_score_list < 10 or \
            (not self.ascending and self.score > self.high_score_list[len_high_score_list-1]['score']) or \
            (self.ascending and self.score < self.high_score_list[len_high_score_list-1]['score']):
            self.is_score_top_10 = True

            if (self.ascending and self.score < self.get_high_score()) or \
               (not self.ascending and self.score > self.get_high_score()):
                self.is_score_high_score = True
            else:
                self.is_score_high_score = False
        else:
            self.is_score_top_10 = False
            self.is_score_high_score = False

        return self.is_score_top_10
        
    def clear_key_presses(self):
        # Clear out any existing key presses
        pygame.event.clear()

    def clean_current_initial(self, current_initial):
        new_current_initial = round(current_initial)

        if new_current_initial < 0:
            new_current_initial = 0
        elif new_current_initial > len(self.initial_indexes) - 1:
            new_current_initial = len(self.initial_indexes) - 1
        
        return new_current_initial

    def high_score_input_screen(self):
        self.clear_key_presses()

        num_up = 0
        num_down = 0
        num_left = 0
        num_right = 0

        run_initials_input = self.is_high_score()
        current_initial = 0
        while run_initials_input:
            self.timer.tick(self.fps)

            self.surface.fill('black')

            # High Score
            high_score_header = self.font.render('HIGH SCORE', True, 'white')
            self.surface.blit(high_score_header, ((self.display_width - high_score_header.get_width()) // 2, self.height_offset + 100))

            # Enter Initials
            enter_initials = self.font.render('ENTER YOUR INITIALS', True, 'white')
            self.surface.blit(enter_initials, ((self.display_width - enter_initials.get_width()) // 2, self.height_offset + 200))
            
            # Initials
            initials_str = ''
            initials_x_coord = 900
            for i, initial_index in enumerate(self.initial_indexes):
                initial_index_int = round(initial_index)
                if initial_index_int > len(self.initial_options) - 1:
                    initial_index_int = len(self.initial_options) - 1
                elif initial_index_int < 0:
                    initial_index = 0
                initials_str += self.initial_options[initial_index_int]
                initial = self.font.render(self.initial_options[initial_index_int], True, 'white')
                initials_y_coord = self.height_offset + 400
                self.surface.blit(initial, (initials_x_coord, initials_y_coord))

                if current_initial == i:
                    pygame.draw.line(self.surface, 'white', (initials_x_coord, initials_y_coord + initial.get_height() + 5), (initials_x_coord + 24, initials_y_coord + initial.get_height() + 5), 5)

                initials_x_coord += 50
            
            # Instructions
            instructions_y_coord = initials_y_coord + initial.get_height() + 175
            instructions_line1 = self.font.render('USE THE JOYSTICK TO SELECT YOUR INITIALS.', True, 'white')
            self.surface.blit(instructions_line1, ((self.display_width - instructions_line1.get_width()) // 2, instructions_y_coord))
            instructions_line2 = self.font.render('PRESS ANY BUTTON TO SAVE.', True, 'white')
            self.surface.blit(instructions_line2, ((self.display_width - instructions_line2.get_width()) // 2, instructions_y_coord + 50))

            for event in pygame.event.get():
                if ((event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or \
                    (event.type == pygame.JOYBUTTONDOWN and self.joystick and \
                     (self.joystick.get_button(Buttons.PLAYER_LEFT) or self.joystick.get_button(Buttons.PLAYER_RIGHT) or \
                      self.joystock.get_button(Buttons.ADMIN_LEFT) or self.joystick.get_button(Buttons.ADMIN_RIGHT)))):
                    # Write Entry
                    new_score = {
                        'score': self.score,
                        'initials': initials_str
                    }

                    if len(self.high_score_list) == 0:
                        self.high_score_list.append(new_score)
                    else:
                        for index, high_score in enumerate(self.high_score_list):
                            if (self.ascending and new_score['score'] < high_score['score']) or \
                            (not self.ascending and new_score['score'] > high_score['score']):
                                self.high_score_list.insert(index, new_score)
                                break
                            elif index == len(self.high_score_list) - 1:
                                self.high_score_list.insert(index+1, new_score)
                                break
                    
                        if len(self.high_score_list) > 10:
                            self.high_score_list = self.high_score_list[0:10]

                    # Save the high score
                    with open(self.filename, 'w') as writer:
                        # Read & print the entire file
                        writer.write(json.dumps(self.high_score_list, indent=4))
                    
                    run_initials_input = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        if self.initial_indexes[current_initial] == 0:
                            self.initial_indexes[current_initial] = len(self.initial_options) - 1
                        else:
                            self.initial_indexes[current_initial] -= 1
                    elif event.key == pygame.K_DOWN:
                        if self.initial_indexes[current_initial] == len(self.initial_options) - 1:
                            self.initial_indexes[current_initial] = 0
                        else:
                            self.initial_indexes[current_initial] += 1
                    elif event.key == pygame.K_LEFT:
                        if current_initial != 0:
                            current_initial -= 1
                    elif event.key == pygame.K_RIGHT:
                        if current_initial != len(self.initial_indexes) - 1:
                            current_initial += 1
                elif event.type == pygame.JOYDEVICEADDED:
                    self.joystick = pygame.joystick.Joystick(event.device_index)
                    self.joystick.init()
                elif event.type == pygame.JOYDEVICEREMOVED:
                    self.joystick = None

            # Unfortunately it isn't possible to consolidate the keyboard and joystick
            # code because they don't fire the same number of events per move so have
            # to duplicate code.
            try:
                speed = 1
                if self.joystick:
                    if round(self.joystick.get_axis(1)) == -1: # UP
                        if num_up == 0 or num_up > 8:
                            if self.initial_indexes[current_initial] == 0:
                                self.initial_indexes[current_initial] = len(self.initial_options) - 1
                            else:
                                self.initial_indexes[current_initial] -= speed
                        num_up += 1
                    elif round(self.joystick.get_axis(1)) == 1: # DOWN
                        if num_down == 0 or num_down > 8:
                            if self.initial_indexes[current_initial] == len(self.initial_options) - 1:
                                self.initial_indexes[current_initial] = 0
                            else:
                                self.initial_indexes[current_initial] += 1
                        num_down += 1
                    elif round(self.joystick.get_axis(0)) == -1: # LEFT
                        if num_left == 0 or num_left > 8:
                            if current_initial != 0:
                                current_initial -= speed
                        num_left += 1
                    elif round(self.joystick.get_axis(0)) == 1: # RIGHT
                        if num_right == 0 or num_right > 8:
                            if current_initial != len(self.initial_indexes) - 1:
                                current_initial += speed
                        num_right += 1
                    elif round(self.joystick.get_axis(0)) == 0 and round(self.joystick.get_axis(1)) == 0:
                        num_up = 0
                        num_down = 0
                        num_left = 0
                        num_right = 0
            except:
                print(f'In except - resetting current_initial: {current_initial}')
                current_initial = 0
                pass
                
            pygame.display.flip()

    def high_score_list_screen(self):
        high_score_sleep_timer = 0
        while high_score_sleep_timer < self.fps*3: # ~ 3 sec:
            self.timer.tick(self.fps)

            self.surface.fill('black')

            # High Score
            high_score_header = self.font.render('HIGH SCORE', True, 'white')
            self.surface.blit(high_score_header, ((self.display_width - high_score_header.get_width()) // 2, self.height_offset + 100))

            # Header
            rank_start_x = self.width_offset + 0
            initials_start_x = rank_start_x + 250
            score_start_x = initials_start_x + 350
            self.surface.blit(self.rank_text, (rank_start_x, self.height_offset + 200))
            self.surface.blit(self.initials_text, (initials_start_x, self.height_offset + 200))
            self.surface.blit(self.score_text, (score_start_x, self.height_offset + 200))

            # Entries
            high_score_y_coord = self.height_offset + 250
            for rank, high_score in enumerate(self.high_score_list):
                score_color = tuple(self.score_colors[rank % 4])
                entry_rank = self.font.render(self.rank_strs[rank], True, score_color)
                self.surface.blit(entry_rank, (rank_start_x + self.rank_text.get_width() - entry_rank.get_width(), high_score_y_coord))
                entry_initials = self.font.render(high_score['initials'], True, score_color)
                self.surface.blit(entry_initials, (initials_start_x + self.initials_text.get_width() - entry_initials.get_width(), high_score_y_coord))
                entry_score = self.font.render(str(high_score['score']), True, score_color)
                self.surface.blit(entry_score, (score_start_x + self.score_text.get_width() - entry_score.get_width(), high_score_y_coord))

                high_score_y_coord += 50

            high_score_sleep_timer += 1
            pygame.display.flip()
        
        self.clear_key_presses()

    def check_high_score(self, score):
        self.score = score
        self.high_score_input_screen()
        self.high_score_list_screen()
        self.load_high_score_list()

        self.score = 0
        self.initial_indexes = [0, 0, 0]
        self.clear_key_presses()

if __name__ == '__main__':
    flags = pygame.FULLSCREEN
    screen = pygame.display.set_mode((1920, 1080))
    font = pygame.font.Font(os.path.dirname(os.path.realpath(__file__)) + '/assets/fonts/retro_gaming.ttf', 30)
    hs = HighScore(screen, font, 'high_score.json', 60)
    hs.check_high_score(100)
    pygame.joystick.quit()
    pygame.quit()
