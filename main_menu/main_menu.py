import sys
from datetime import datetime
from os import path
from random import randint

import pygame
from led import LED

FILE_PATH_PREFIX = path.dirname(path.realpath(__file__))
sys.path.insert(2, FILE_PATH_PREFIX + '/../superdevvie')
sys.path.insert(2, FILE_PATH_PREFIX + '/../devbloks')
import superdevvie
import devbloks

pygame.init()
pygame.joystick.init()
pygame.mouse.set_visible(False)

class Buttons:
    ADMIN_LEFT = 8
    ADMIN_RIGHT = 9
    PLAYER_LEFT = 3
    PLAYER_RIGHT = 4

    if sys.platform.startswith('darwin'): # MacOS seems to have different button numbers
        PLAYER_LEFT = 2

DISPLAY_WIDTH = 1920
DISPLAY_HEIGHT = 1080

font_filepath = FILE_PATH_PREFIX + '/assets/fonts/retro_gaming.ttf'
font = pygame.font.Font(font_filepath, 40)

devvie_images = []
for i in range(1, 5):
    devvie_images.append(pygame.image.load(f'{FILE_PATH_PREFIX}/assets/devvie_images/devvie_student_{i}.png'))
devvie_graduate_img = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/devvie_images/devvie_graduate.png')
devvie_studying_img = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/devvie_images/devvie_studying.png')
devnet_logo_img = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/menu_images/devnet_logo.png')

flags = pygame.FULLSCREEN
screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), flags, vsync=1)
# screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))

joystick = None

def show_token_screen(game_won, top_10, high_score):
    num_tokens = 0
    if game_won:
        num_tokens += 1
    if high_score:
        num_tokens += 1
    if top_10:
        num_tokens += 1

    token_text = 'token'
    if num_tokens > 1:
        token_text += 's'

    devvie_img = devvie_images[randint(0, 3)]
    if num_tokens == 0:
        devvie_img = devvie_studying_img
    elif num_tokens == 3:
        devvie_img = devvie_graduate_img

    if joystick:
        joystick.init()

    run_token = True
    while run_token:
        screen.fill('black')

        if num_tokens > 0:
            line1 = font.render(f'You won {num_tokens} {token_text}!', True, 'white')
            line2 = font.render(f'Please call an attendant to collect your token.', True, 'white')
            line3 = font.render(f'Tokens can be redeemed at the DevNet Welcome Desk.', True, 'white')
            led.red(True)
        else:
            line1 = font.render(f'Thank you for playing!', True, 'white')
            line2 = font.render(f'Ask an attendant to redeem a DevNet sticker.', True, 'white')
            line3 = font.render(f'Visit our site at developer.cisco.com', True, 'white')


        multiline_offset = 20
        num_tokens_text_y_coord = (DISPLAY_HEIGHT - line1.get_height() - line2.get_height() - line3.get_height() - devvie_img.get_height() - 2*multiline_offset) // 2
        screen.blit(line1, ((DISPLAY_WIDTH - line1.get_width()) // 2, num_tokens_text_y_coord))
        screen.blit(line2, ((DISPLAY_WIDTH - line2.get_width()) // 2, num_tokens_text_y_coord + line1.get_height() + multiline_offset))
        screen.blit(line3, ((DISPLAY_WIDTH - line3.get_width()) // 2, num_tokens_text_y_coord + line1.get_height() + line2.get_height() + 2*multiline_offset))
        screen.blit(devvie_img, (100, DISPLAY_HEIGHT - devvie_img.get_height() - 100))
        devnet_logo_x_base = 100 + devvie_img.get_width()
        screen.blit(devnet_logo_img, (devnet_logo_x_base + ((DISPLAY_WIDTH - devnet_logo_x_base - devnet_logo_img.get_width()) // 2) - 14, DISPLAY_HEIGHT - devvie_img.get_height() // 2 - 100 - devnet_logo_img.get_height() // 2))

        pygame.display.flip()

        if num_tokens == 0:
            pygame.time.delay(2000)
            led.green(True)
            run_token = False
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                   (event.type == pygame.JOYBUTTONDOWN and joystick and joystick.get_button(Buttons.ADMIN_LEFT) and joystick.get_button(Buttons.ADMIN_RIGHT)):
                    led.green(True)
                    run_token = False
    
def show_score_screen(game_won, top_10, high_score, score):
    GAME_WON_POINTS = 1000
    HIGH_SCORE_POINTS = 5000
    TOP_10_POINTS = 2000

    total_score = score

    if game_won:
        total_score += GAME_WON_POINTS
    if high_score:
        total_score += HIGH_SCORE_POINTS
    if top_10:
        total_score += TOP_10_POINTS

    devvie_img = devvie_graduate_img

    if joystick:
        joystick.init()

    run_score = True
    while run_score:
        screen.fill('black')

        text_color = 'purple'
        score_color = 'white'
        line1_text = font.render(f'Game score', True, text_color)
        line1_score = font.render(f'+{score}', True, score_color)
        line2_text = font.render(f'Cleared board', True, text_color)
        line2_score = font.render(f'+{GAME_WON_POINTS if game_won else 0}', True, score_color)
        line3_text = font.render(f'High score', True, text_color)
        line3_score = font.render(f'+{HIGH_SCORE_POINTS if high_score else 0}', True, score_color)
        line4_text = font.render(f'Top 10 score', True, text_color)
        line4_score = font.render(f'+{TOP_10_POINTS if top_10 else 0}', True, score_color)
        line5 = font.render(f'-------', True, score_color)
        line6_text = font.render(f'Total score', True, text_color)
        line6_score = font.render(f'{total_score}', True, score_color)
        line7 = font.render(f'Please call an attendant to input your score into the leaderboard.', True, 'white')
        led.red(True)

        multiline_offset = font.get_height() + 20

        score_width = 600
        text_x_coord = (DISPLAY_WIDTH - score_width - line1_score.get_width()) // 2
        score_x_coord = text_x_coord + score_width
        start_y_coord = 100
        screen.blit(line1_text, (text_x_coord, start_y_coord + 0*multiline_offset))
        screen.blit(line1_score, (score_x_coord, start_y_coord + 0*multiline_offset))
        screen.blit(line2_text, (text_x_coord, start_y_coord + 1*multiline_offset))
        screen.blit(line2_score, (score_x_coord, start_y_coord + 1*multiline_offset))
        screen.blit(line3_text, (text_x_coord, start_y_coord + 2*multiline_offset))
        screen.blit(line3_score, (score_x_coord, start_y_coord + 2*multiline_offset))
        screen.blit(line4_text, (text_x_coord, start_y_coord + 3*multiline_offset))
        screen.blit(line4_score, (score_x_coord, start_y_coord + 3*multiline_offset))
        screen.blit(line5, (score_x_coord, start_y_coord + 4*multiline_offset))
        screen.blit(line6_text, (text_x_coord, start_y_coord + 5*multiline_offset))
        screen.blit(line6_score, (score_x_coord, start_y_coord + 5*multiline_offset))
        screen.blit(line7, ((DISPLAY_WIDTH - line7.get_width()) // 2, start_y_coord + 7*multiline_offset))
        screen.blit(devnet_logo_img, ((DISPLAY_WIDTH - devnet_logo_img.get_width()) // 2, start_y_coord + 9.85*multiline_offset))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
            (event.type == pygame.JOYBUTTONDOWN and joystick and joystick.get_button(Buttons.ADMIN_LEFT) and joystick.get_button(Buttons.ADMIN_RIGHT)):
                led.green(True)
                run_score = False

def show_thank_you_screen(score):
    devvie_img = devvie_graduate_img

    if joystick:
        joystick.init()

    screen.fill('black')

    line1 = font.render(f'Thank you for playing!', True, 'white')
    line2 = font.render(f'Your score was {score}.', True, 'white')
    line3 = font.render(f'Visit our site at developer.cisco.com', True, 'white')


    multiline_offset = 20
    num_tokens_text_y_coord = (DISPLAY_HEIGHT - line1.get_height() - line2.get_height() - line3.get_height() - devvie_img.get_height() - 2*multiline_offset) // 2
    screen.blit(line1, ((DISPLAY_WIDTH - line1.get_width()) // 2, num_tokens_text_y_coord))
    screen.blit(line2, ((DISPLAY_WIDTH - line2.get_width()) // 2, num_tokens_text_y_coord + line1.get_height() + multiline_offset))
    screen.blit(line3, ((DISPLAY_WIDTH - line3.get_width()) // 2, num_tokens_text_y_coord + line1.get_height() + line2.get_height() + 2*multiline_offset))
    screen.blit(devvie_img, (100, DISPLAY_HEIGHT - devvie_img.get_height() - 100))
    devnet_logo_x_base = 100 + devvie_img.get_width()
    screen.blit(devnet_logo_img, (devnet_logo_x_base + ((DISPLAY_WIDTH - devnet_logo_x_base - devnet_logo_img.get_width()) // 2) - 14, DISPLAY_HEIGHT - devvie_img.get_height() // 2 - 100 - devnet_logo_img.get_height() // 2))

    pygame.display.flip()

    pygame.time.delay(3000)
    led.green(True)
        

selected_tile = 0
selected_tile_time = datetime.now()
led = LED()
led.green(True) # Turn on the green light
run_main_menu = True
while run_main_menu:
    screen.fill('black')

    # Text to select
    select_text = pygame.font.Font(font_filepath, 60).render(f'Select a Game', True, 'white')
    select_text_y_coord = 100
    screen.blit(select_text, ((DISPLAY_WIDTH - select_text.get_width()) // 2, select_text_y_coord))
    select_text_bottom_y_coord = select_text_y_coord + select_text.get_height() - 15

    # Tile for Super Devvie
    mr_devvie_menu_tile = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/menu_images/superdevvie_menu_tile.png')

    tile_y_coord = select_text_bottom_y_coord + ((DISPLAY_HEIGHT - select_text_bottom_y_coord - mr_devvie_menu_tile.get_height()) // 2)
    screen.blit(mr_devvie_menu_tile, (360, tile_y_coord))
    if selected_tile == 0:
        selected_x_coord = 360

    # Tile for DevBloks
    api_devblok_menu_tile = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/menu_images/devbloks_menu_tile.png')
    screen.blit(api_devblok_menu_tile, (1060, tile_y_coord))
    if selected_tile == 1:
        selected_x_coord = 1060
    
    # Highlight the selected tile
    pygame.draw.rect(screen, 'white', [selected_x_coord, tile_y_coord, 500, 700], 5, 10)
    pygame.display.flip()

    # Run the selected game
    num_tokens = 1 # Get a token for playing
    for event in pygame.event.get():
        if selected_tile == 0 and ((event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT) or \
           (event.type == pygame.JOYAXISMOTION and joystick and round(joystick.get_axis(0)) == 1)):
            selected_tile = 1
            selected_tile_time = datetime.now()
            led.yellow(True)
        elif selected_tile == 1 and ((event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT) or \
             (event.type == pygame.JOYAXISMOTION and joystick and round(joystick.get_axis(0)) == -1)):
            selected_tile = 0
            selected_tile_time = datetime.now()
            led.yellow(True)
        elif ((event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or \
             (event.type == pygame.JOYBUTTONDOWN and joystick and (joystick.get_button(Buttons.PLAYER_LEFT) or joystick.get_button(Buttons.PLAYER_RIGHT)))):
            if selected_tile == 0:
                led.yellow(True)
                game_won, top_10, high_score, score = superdevvie.run_game(screen, max_games=1, highScore=True)
                show_thank_you_screen(score)
            elif selected_tile == 1:
                led.yellow(True)
                game_won, top_10, high_score, score = devbloks.run_game(screen, max_games=1, highScore=True)
                show_thank_you_screen(score)
        elif event.type == pygame.JOYDEVICEADDED:
            joystick = pygame.joystick.Joystick(0)
            joystick.init()
        elif event.type == pygame.JOYDEVICEREMOVED:
            joystick = None
        elif event.type == pygame.QUIT:
            run_main_menu = False
            led.all_off()

    if (datetime.now() - selected_tile_time).total_seconds() > 120: # Idle for 2 mins
        led.green(True)

led.all_off()
pygame.joystick.quit()
pygame.quit()