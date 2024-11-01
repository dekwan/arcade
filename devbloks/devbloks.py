import math
import random
import sys
import time
from os import path
from random import randint

import pygame
import requests
from requests.auth import HTTPBasicAuth

FILE_PATH_PREFIX = path.dirname(path.realpath(__file__))

"""
10 x 20 grid
play_height = 2 * play_width

tetriminos:
    0 - S - green
    1 - Z - red
    2 - I - cyan
    3 - O - yellow
    4 - J - blue
    5 - L - orange
    6 - T - purple
"""
pygame.init()
pygame.joystick.init()
pygame.font.init()
pygame.mouse.set_visible(False)

class Buttons:
    ADMIN_LEFT = 8
    ADMIN_RIGHT = 9
    PLAYER_LEFT = 3
    PLAYER_RIGHT = 4
    
    if sys.platform.startswith('darwin'): # MacOS seems to have different button numbers
        PLAYER_LEFT = 2

# global variables
s_width = 1920  # window width
s_height = 1080  # window height
play_width = 900  # play window width
play_height = 1080  # play window height
block_size = 30  # size of block
col = play_width // block_size  # columns
row = play_height // block_size  # rows
brick_width = 85
fps = 60

make_api_request = False
offline_api_request = True

top_left_x = brick_width*2 + 4
top_left_y = 0

FILE_PATH_PREFIX = path.dirname(path.realpath(__file__))
high_score_json_filepath = FILE_PATH_PREFIX + '/high_score_devbloks.json'
high_score_txt_filepath = FILE_PATH_PREFIX + '/high_score.txt'
fontpath = FILE_PATH_PREFIX + '/assets/fonts/retro_gaming.ttf'

# shapes formats

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['.....',
      '..0..',
      '..0..',
      '..0..',
      '..0..'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['....',
      '....',
      '.00.',
      '.00.',
      '....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

# index represents the shape

two_by_one = [['.....',
               '.00..',
               '.....',
               '.....',
               '.....']]

three_by_one = [['.....',
                '.000.',
                '.....',
                '.....',
                '.....']]

five_by_one = [['.....',
                '00000',
                '.....',
                '.....',
                '.....']]

six_by_one = [['.....',
               '000000',
               '.....',
               '.....',
               '.....']]

seven_by_one = [['.....',
                 '0000000',
                 '.....',
                 '.....',
                 '.....']]

eight_by_one = [['.....',
                 '00000000',
                 '.....',
                 '.....',
                 '.....']]

nine_by_one = [['.....',
                '000000000',
                '.....',
                '.....',
                '.....']]

#shapes = [S, Z, I, O, J, L, T]
#shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
shapes = [two_by_one, three_by_one, five_by_one, six_by_one, seven_by_one, eight_by_one, nine_by_one, O, J, L, T]
# shape_colors = ['black', 'black', 'black', 'black', 'black', 'black', 'black', (247, 150, 34), (253, 225, 0), (221, 135, 225), (0, 255, 255)]
shape_colors = ['white', 'green', 'blue', 'yellow', 'red', 'purple', 'pink', (247, 150, 34), (253, 225, 0), (221, 135, 225), (0, 255, 255)]
shape_outline = ['black', 'black', 'black', 'black', 'black', 'black', 'black', (249, 171, 78), (254, 237, 102), (235, 185, 255), (204, 255, 255)]
shape_text = [
    ['GET','PUT','POST', 'GET', 'GET'],
    ['https://', 'https://', 'https://'],
    ['readonly/ISEisC00L', '/api/v1/endpoint', 'readonly/ISEisC00L', 'readonly/ISEisC00L', '/api/v1/endpoint', '/api/v1/endpoint'],
    ['devnetuser/RG!_Yw919_83', 'devnetuser/Cisco123!', 'sandboxdnac2.cisco.com'],
    ['devnetsandboxise.cisco.com', 'sandbox-sdwan-2.cisco.com', 'devnetsandboxise.cisco.com', 'devnetsandboxise.cisco.com'],
    ['/dataservice/network/status'],
    ['/dna/intent/api/v1/licenses/device/count'],
    [''],
    [''],
    [''],
    ['']]

# class to represent each of the pieces
class Piece(object):
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        shape_index = shapes.index(shape)
        self.color = shape_colors[shape_index]  # choose color from the shape_color list
        self.rotation = 0  # chooses the rotation according to index
        text_index = randint(0, len(shape_text[shape_index])-1)
        self.text = shape_text[shape_index][text_index]
        self.img = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/images/{shape_index}_{text_index}.png')

# initialize the grid
def create_grid(locked_pos={}):
    grid = [[(0, 0, 0) for x in range(col)] for y in range(row)]  # grid represented rgb tuples

    # locked_positions dictionary
    # (x,y):(r,g,b)
    for y in range(row):
        for x in range(col):
            if (x, y) in locked_pos:
                color = locked_pos[
                    (x, y)]  # get the value color (r,g,b) from the locked_positions dictionary using key (x,y)
                grid[y][x] = color  # set grid position to color

    return grid

def convert_shape_format(piece):
    positions = []
    shape_format = piece.shape[piece.rotation % len(piece.shape)]  # get the desired rotated shape from piece

    '''
    e.g.
       ['.....',
        '.....',
        '..00.',
        '.00..',
        '.....']
    '''
    for i, line in enumerate(shape_format):  # i gives index; line gives string
        row = list(line)  # makes a list of char from string
        for j, column in enumerate(row):  # j gives index of char; column gives char
            if column == '0':
                positions.append((math.ceil(piece.x) + j, math.ceil(piece.y) + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)  # offset according to the input given with dot and zero

    return positions

# checks if current position of piece in grid is valid
def valid_space(piece, grid):
    # makes a 2D list of all the possible (x,y)
    accepted_pos = [[(x, y) for x in range(col) if grid[y][x] == (0, 0, 0)] for y in range(row)]
    # removes sub lists and puts (x,y) in one list; easier to search
    accepted_pos = [x for item in accepted_pos for x in item]

    formatted_shape = convert_shape_format(piece)

    for pos in formatted_shape:
        if pos not in accepted_pos:
            if pos[1] >= 0:
                return False
    return True


# check if piece is out of board
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


# chooses a shape randomly from shapes list
def get_shape():
    return Piece(5, 3, random.choice(shapes))

# draws text in the middle
def draw_text_middle_play_area(text, font_size, color, surface):
    font = pygame.font.Font(fontpath, font_size) #, bold=False, italic=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width//2 - (label.get_width()//2), top_left_y + play_height//2 - (label.get_height()//2)))        

# draws the lines of the grid for the game
def draw_grid(surface):
    r = g = b = 0
    grid_color = (r, g, b)
    grid_color = 'yellow'

    for i in range(row):
        # draw grey horizontal lines
        pygame.draw.line(surface, grid_color, (top_left_x, top_left_y + i * block_size),
                         (top_left_x + play_width, top_left_y + i * block_size))
        for j in range(col):
            # draw grey vertical lines
            pygame.draw.line(surface, grid_color, (top_left_x + j * block_size, top_left_y),
                             (top_left_x + j * block_size, top_left_y + play_height))
    
def check_api_call(text_grid, coord_list):
    sorted_coord_list = sorted(list(coord_list), key=lambda a: a[0])

    text_list = []
    for coord in sorted_coord_list:
        piece_text = text_grid[coord].text
        if len(piece_text) > 0:
            text_list.append(piece_text)

    if (len(text_list) == 5):
        http_method_txt = text_list[0]
        auth_txt = text_list[1]
        scheme_txt = text_list[2]
        domain_txt = text_list[3]
        endpoint_txt = text_list[4]

        credentials = auth_txt.split('/')
        url = scheme_txt + domain_txt + endpoint_txt
        print(f'method is: {http_method_txt}, credentials are: {credentials}, url is: {url}')

        if make_api_request:
            mapping = {}
            mapping['devnetsandboxise.cisco.com'] = ['GET', 'readonly/ISEisC00L', '/api/v1/endpoint']
            mapping['sandboxdnac2.cisco.com'] = ['GET', 'devnetuser/Cisco123!', '/dna/intent/api/v1/licenses/device/count']
            mapping['sandbox-sdwan-2.cisco.com'] = ['GET', 'devnetuser/RG!_Yw919_83', '/dataservice/network/status']
            
            if offline_api_request:
                print("offline")

                try:
                    pygame.time.delay(250)  # wait a tiny bit to mimic an API request
                    if auth_txt == mapping[domain_txt][1]:
                        if http_method_txt == mapping[domain_txt][0]:
                            if endpoint_txt == mapping[domain_txt][2]:
                                return 200
                            else:
                                return 404
                        else:
                            return 403
                    else:
                        return 401
                except:
                    return 9999
            else:
                try:
                    if "devnetsandboxise" in domain_txt:
                        if http_method_txt == 'POST':
                            resp = requests.post(url, auth=HTTPBasicAuth(credentials[0], credentials[1]))
                        elif http_method_txt == 'PUT':
                            resp = requests.put(url, auth=HTTPBasicAuth(credentials[0], credentials[1]))
                        else:
                            resp = requests.get(url, auth=HTTPBasicAuth(credentials[0], credentials[1]))
                        return resp.status_code
                    elif "sandboxdnac2" in domain_txt:
                        auth_token = requests.post('https://sandboxdnac2.cisco.com/dna/system/api/v1/auth/token', auth=HTTPBasicAuth(credentials[0], credentials[1]), verify=False)
                        if auth_token.status_code == 200:
                            session = requests.session()
                            session.headers = {'X-Auth-Token': auth_token.json()['Token']}
                            if http_method_txt == 'POST':
                                resp = session.post(url, verify=False)
                            elif http_method_txt == 'PUT':
                                resp = session.put(url, verify=False)
                            else:
                                resp = session.get(url, verify=False)

                            return resp.status_code
                        else:
                            return auth_token.status_code
                    elif "sandbox-sdwan-2" in domain_txt:
                        login_url = 'https://sandbox-sdwan-2.cisco.com/j_security_check'
                        login_data = {'j_username' : credentials[0], 'j_password' : credentials[1]}
                        login_headers = {'Content-Type' : 'application/x-www-form-urlencoded'}
                        session = requests.session()
                        login_response = session.post(url=login_url, headers=login_headers, data=login_data, verify=False)

                        if len(login_response.text) == 0:
                            if http_method_txt == 'POST':
                                resp = session.post(url, verify=False)
                            elif http_method_txt == 'PUT':
                                resp = session.put(url, verify=False)
                            else:
                                resp = session.get(url, verify=False)
                            return resp.status_code
                        else:
                            return 401 # login response returns a 200 whether or not it failed
                    else:
                        return 9999
                except requests.exceptions.ConnectionError:
                    return -1 # No connection
                except:
                    return 9999
        else:
            if len(http_method_txt) > 4 or \
               auth_txt.count('/') != 1 or \
               scheme_txt != 'https://' or \
               'cisco.com' not in domain_txt or \
               not endpoint_txt.startswith('/'):
                return 9999
            
            # This version of the game just needs you to have the components in the right order
            mapping = {}
            mapping['method'] = ['GET', 'PUT', 'POST']
            mapping['auth'] = ['readonly/ISEisC00L', 'devnetuser/Cisco123!', 'devnetuser/RG!_Yw919_83']
            mapping['domain'] = ['devnetsandboxise.cisco.com', 'sandboxdnac2.cisco.com', 'sandbox-sdwan-2.cisco.com']
            mapping['endpoint'] = ['/api/v1/endpoint', '/dna/intent/api/v1/licenses/device/count', '/dataservice/network/status']

            try:
                pygame.time.delay(250)  # wait a tiny bit to mimic an API request
                if http_method_txt in mapping['method']:
                    if auth_txt in mapping['auth']:
                        if domain_txt in mapping['domain']:
                            if endpoint_txt in mapping['endpoint']:
                                return 200
                            else:
                                return 404
                        else:
                            return 404
                    else:
                        return 401
                else:
                    return 405
            except:
                return 9999

    return 9999

# clear a row when it is filled
def clear_rows(grid, locked, text_grid):
    # need to check if row is clear then shift every other row above down one
    api_result = None
    increment = 0
    clear_row_sound = pygame.mixer.Sound(FILE_PATH_PREFIX + '/assets/sounds/row-clear.mp3')
    for i in range(len(grid) - 1, -1, -1):      # start checking the grid backwards
        grid_row = grid[i]                      # get the last row
        if (0, 0, 0) not in grid_row:           # if there are no empty spaces (i.e. black blocks)
            increment += 1
            # add positions to remove from locked
            index = i                           # row index will be constant
            print(f'clearing row {i}')
            
            pygame.mixer.Sound.play(clear_row_sound)

            for j in range(len(grid_row)):
                try:
                    del locked[(j, i)]          # delete every locked element in the bottom row
                except ValueError:
                    continue
            values = [x for x in text_grid if x[1] == i]
            api_result = check_api_call(text_grid, values)
            for x in values:
                text_grid.pop(x)

    # shift every row one step down
    # delete filled bottom row
    # add another empty row on the top
    # move down one step
    if increment > 0:
        # sort the locked list according to y value in (x,y) and then reverse
        # reversed because otherwise the ones on the top will overwrite the lower ones
        for key in sorted(list(locked), key=lambda a: a[1])[::-1]:
            x, y = key
            if y < index:                       # if the y value is above the removed index
                new_key = (x, y + increment)    # shift position to down
                locked[new_key] = locked.pop(key)
        
        for key in sorted(list(text_grid), key=lambda a: a[1])[::-1]:
            x, y = key
            if y < index:                       # if the y value is above the removed index
                new_key = (x, y + increment)    # shift position to down
                text_grid[new_key] = text_grid.pop(key)
    return api_result

# draws the upcoming piece
def draw_next_shape(piece, surface, start_x, start_y):
    if len(piece.text) > 0:
        surface.blit(piece.img, (start_x, start_y))
    else:
        # set up shape text 
        shape_format = piece.shape[piece.rotation % len(piece.shape)]

        block_y = 0
        for line in shape_format:
            row = list(line)
            if '0' in row:            
                for j, column in enumerate(row):
                    if column == '0':
                        pygame.draw.rect(surface, piece.color, (start_x + j*block_size, start_y + block_y*block_size, block_size, block_size), 0)
                        shape_index = shape_colors.index(piece.color)
                        pygame.draw.rect(surface, shape_outline[shape_index], (start_x + j*block_size, start_y + block_y*block_size, block_size, block_size), 1)

                block_y += 1

    

def draw_label_box(surface, start_x, start_y, width, height, inner_line_offset):
    pygame.draw.rect(surface, 'black', [start_x, start_y, width, height], 0, 10)
    pygame.draw.rect(surface, (99, 101, 98), [start_x + inner_line_offset, start_y + inner_line_offset, width - (2 * inner_line_offset), height - (2 * inner_line_offset)], 4, 10)

def get_centered_coord(outer_start_coord, outer_size, inner_size):
    return outer_start_coord + ((outer_size - inner_size) // 2)

def get_shape_font(text):
    text_length = len(text)
    size = 0
    if 0 <= text_length <= 4:
        size = 19
    elif 5 <= text_length <= 20:
        size = 16
    elif 21 <= text_length <= 30:
        size = 15
    elif 31 <= text_length <= 50: # block is longer so font size 16
        size = 16
    elif 51 <= text_length <= 60:
        size = 14
    elif 61 <= text_length <= 70:
        size = 11
    else:
        size = 8

    return pygame.font.Font(fontpath, size)

# draws the content of the window
def draw_window(surface, grid, text_grid, curr_text_pos, next_piece, current_time, high_score, http_status=0):
    # surface.fill((0, 0, 0))  # fill the surface with black
    # surface.fill((83, 88, 181))  # fill the surface with light purple
    surface.fill((32, 65, 94))  # fill the surface with dark blue

    pygame.font.init()  # initialize font
    font = pygame.font.Font(fontpath, 40)

    # Calculate the start coordinates of the right panel
    start_x_panel = top_left_x + play_width + brick_width + 1 # Added a pixel to accomodate for white line width
    start_y_panel = top_left_y

    # Labels
    label_top = font.render(f'TOP TIME', True, 'white')
    label_time = font.render(f'TIME', True, 'white')
    label_status = font.render(f'HTTP STATUS', True, 'white')
    label_next = font.render(f'NEXT', True, 'white')

    # Calculate the start x coordinate of the boxes for the labels
    multiline_spacing = 10
    longest_text_width = label_status.get_width()
    longest_text_height = label_status.get_height()
    width_box = longest_text_width + 60 # 50 px buffer
    single_line_height_box = longest_text_height + 50 # 40 px buffer
    two_line_height_box = 2*longest_text_height + 50 # 40 px buffer
    start_x_box = get_centered_coord(start_x_panel, s_width - start_x_panel, width_box)
    inner_line_offset = 10

    # draw time
    start_y_time = 125
    # start_y_line = start_y_time + (single_line_height_box // 2)
    # pygame.draw.rect(surface, (148, 164, 178), (start_x_panel, start_y_line, s_width - start_x_panel, start_y_time_value - start_y_line), 0)
    # pygame.draw.line(surface, (99, 101, 98), (start_x_panel, start_y_line), (s_width, start_y_line), 4)
    draw_label_box(surface, start_x_box, start_y_time, width_box, single_line_height_box, inner_line_offset)
    surface.blit(label_time, (get_centered_coord(start_x_box, width_box, label_time.get_width()), get_centered_coord(start_y_time, single_line_height_box, label_time.get_height())))

    # draw time value
    start_y_time_value = start_y_time + single_line_height_box + 15
    pygame.draw.rect(surface, 'black', [start_x_panel, start_y_time_value, s_width - start_x_panel, single_line_height_box], 0)
    value_time = font.render(f'{math.floor(current_time)}', True, 'white')
    surface.blit(value_time, (get_centered_coord(start_x_panel, s_width - start_x_panel, value_time.get_width()), get_centered_coord(start_y_time_value, single_line_height_box, value_time.get_height())))
    pygame.draw.line(surface, (99, 101, 98), (start_x_panel, start_y_time_value + inner_line_offset), (s_width, start_y_time_value + inner_line_offset), 4)
    pygame.draw.line(surface, (99, 101, 98), (start_x_panel, start_y_time_value + single_line_height_box - inner_line_offset - 2), (s_width, start_y_time_value + single_line_height_box - inner_line_offset - 2), 4)

    # draw top label and value
    start_y_top = start_y_time_value + single_line_height_box + 50
    draw_label_box(surface, start_x_box, start_y_top, width_box, two_line_height_box, inner_line_offset)
    line1_y_coord_top = get_centered_coord(start_y_top, two_line_height_box, 2*longest_text_height + multiline_spacing) + 5
    surface.blit(label_top, (get_centered_coord(start_x_box, width_box, label_top.get_width()), line1_y_coord_top))
    value_top = font.render(f'{high_score}', True, 'white')
    surface.blit(value_top, (get_centered_coord(start_x_box, width_box, value_top.get_width()), line1_y_coord_top + label_top.get_height()))

    # draw status label
    start_y_status = start_y_top + single_line_height_box + longest_text_height + 50
    draw_label_box(surface, start_x_box, start_y_status, width_box, two_line_height_box, inner_line_offset)
    line1_y_coord_status = get_centered_coord(start_y_status, two_line_height_box, 2*longest_text_height + multiline_spacing) + 5
    surface.blit(label_status, (get_centered_coord(start_x_box, width_box, label_status.get_width()), line1_y_coord_status))
    if http_status == 0:
        status = '----'
    elif http_status == 9999:
        status = 'INVALID'
    else:
        status = http_status
    value_status = font.render(f'{status}', True, 'white')
    surface.blit(value_status, (get_centered_coord(start_x_box, width_box, value_status.get_width()), line1_y_coord_status + label_top.get_height()))

    # draw next label
    start_y_next = start_y_status + single_line_height_box + longest_text_height + 50
    width_next_box = s_width - start_x_panel - 50
    height_next_box = two_line_height_box + 1.5*block_size
    draw_label_box(surface, start_x_panel + 25, start_y_next, width_next_box, height_next_box, inner_line_offset)
    start_y_label = get_centered_coord(start_y_next, single_line_height_box, label_next.get_height())
    surface.blit(label_next, (get_centered_coord(start_x_panel + 25, width_next_box, label_next.get_width()), start_y_label))
    width_piece = len(next_piece.shape[0][0])*block_size if len(next_piece.text) == 0 else next_piece.img.get_width()
    start_x_piece = get_centered_coord(start_x_panel + 25, width_next_box, width_piece)
    start_y_piece = get_centered_coord(start_y_label + label_next.get_height(), start_y_next + height_next_box - start_y_label - label_next.get_height(), next_piece.img.get_height()) - 12
    draw_next_shape(next_piece, surface, start_x_piece, start_y_piece)

    # draw content of the grid
    for i in range(row):
        for j in range(col):
            pygame.draw.rect(surface, grid[i][j],
                             (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)
            if grid[i][j] != (0,0,0):
                shape_index = shape_colors.index(grid[i][j])
                pygame.draw.rect(surface, shape_outline[shape_index],
                                (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 1)
   
    # draw shape locked
    for x in text_grid:
        surface.blit(getImg(text_grid[x]), (top_left_x + x[0] * block_size, top_left_y + x[1] * block_size))
    
    # draw shape falling
    for key, value in curr_text_pos.items():
        surface.blit(getImg(value), (top_left_x + key[0] * block_size, top_left_y + key[1] * block_size))
        
    # draw vertical and horizontal grid lines
    # draw_grid(surface)

    # draw bricks to surround the play area
    bricks = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/images/bricks.png')
    surface.blit(pygame.transform.scale(bricks, (brick_width, play_height)), (top_left_x - brick_width, start_y_panel))
    surface.blit(pygame.transform.scale(bricks, (brick_width, play_height)), (top_left_x + play_width, start_y_panel))

    # draw line border around play area
    border_color = (255, 255, 255)
    pygame.draw.line(surface, border_color, (brick_width, start_y_panel), (brick_width, start_y_panel + play_height), 4)
    pygame.draw.line(surface, border_color, (start_x_panel, start_y_panel), (start_x_panel, start_y_panel + play_height), 4)
    
def clear_window(surface):
    surface.fill((0, 0, 0)) 
    pygame.display.update()

def clear_key_presses():
    # Clear out any existing key presses
    pygame.event.clear()

def getHighScore(highScore):
    if highScore:
        return highScore.get_high_score()
    else:
        with open(high_score_txt_filepath, 'r') as file:
            lines = file.readlines()        # reads all the lines and puts in a list
            score = int(lines[0].strip())   # remove \n

        return score
    
def updateHighScore(highScore, new_score):
    if highScore:
        highScore.check_high_score(new_score)

        return highScore.get_is_top_10(), highScore.get_is_high_score()
    else:
        last_high_score = getHighScore(highScore)

        with open(high_score_txt_filepath, 'w') as file:
            if new_score > last_high_score:
                file.write(str(new_score))
                return True, True
            else:
                file.write(str(last_high_score))

                return False, False
            
def getImgPos(positions):
    x = play_width
    y = play_height
    for pos_x, pos_y in positions:
        if pos_x < x:
            x = pos_x
        if pos_y < y:
            y = pos_y
    
    return (x, y)

def getImg(piece):
    direction = piece.rotation % len(piece.shape)
    if direction == 0:
        return piece.img
    elif direction == 1:
        return pygame.transform.rotate(piece.img, 270)
    elif direction == 2:
        return pygame.transform.rotate(piece.img, 180)
    elif direction == 3:
        return pygame.transform.rotate(piece.img, 90)
    
def main(window, highScore=False):
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
    else:
        joystick = None

    locked_positions = {}
    text_grid = {}
    create_grid(locked_positions)

    change_piece = False
    run = True
    win = False
    error = False
    current_piece = get_shape()
    next_piece = get_shape()

    clear_key_presses()
    pygame.key.set_repeat(200, 50)

    high_score = None
    if highScore:
        sys.path.insert(2, FILE_PATH_PREFIX + '/../high_score')
        from high_score import HighScore
        high_score = HighScore(window, pygame.font.Font(fontpath, 30), high_score_json_filepath, fps, True)
    http_status = 0
    score = 0

    pygame.mixer.init()
    pygame.mixer.music.load(FILE_PATH_PREFIX + '/assets/sounds/a-type-music.mp3')

    piece_bottom_sound = pygame.mixer.Sound(FILE_PATH_PREFIX + '/assets/sounds/piece-bottom.mp3')
    piece_move_sound = pygame.mixer.Sound(FILE_PATH_PREFIX + '/assets/sounds/piece-move.mp3')
    piece_rotate_sound = pygame.mixer.Sound(FILE_PATH_PREFIX + '/assets/sounds/piece-rotate.mp3')

    countdown_screen(window)

    clock = pygame.time.Clock()
    start_time = time.time()
    fall_time = 0
    fall_speed = 0.35
    level_time = 0
    
    num_left = 0
    num_right = 0
    
    pygame.mixer.music.play(-1)

    while run:
        # need to constantly make new grid as locked positions always change
        grid = create_grid(locked_positions)
        text_pos = (0,0)

        # helps run the same on every computer
        # add time since last tick() to fall_time
        fall_time += clock.get_rawtime()  # returns in milliseconds
        level_time += clock.get_rawtime()

        clock.tick(fps)  # updates clock

        if level_time/1000 > 5:    # make the difficulty harder every 10 seconds
            level_time = 0
            if fall_speed > 0.15:   # until fall speed is 0.15
                fall_speed -= 0.005

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                # since only checking for down - either reached bottom or hit another piece
                # need to lock the piece position
                # need to generate new piece
                change_piece = True
                pygame.mixer.Sound.play(piece_bottom_sound)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
               (event.type == pygame.JOYBUTTONDOWN and joystick and joystick.get_button(Buttons.ADMIN_LEFT) and joystick.get_button(Buttons.ADMIN_RIGHT)):
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1  # move x position left
                    pygame.mixer.Sound.play(piece_move_sound)
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1

                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1  # move x position right
                    pygame.mixer.Sound.play(piece_move_sound)
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1

                elif event.key == pygame.K_DOWN:
                    # move shape down
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1

                elif event.key == pygame.K_UP:
                    # rotate shape
                    current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
                    pygame.mixer.Sound.play(piece_rotate_sound)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)
            elif (event.type == pygame.JOYBUTTONDOWN and joystick and (joystick.get_button(Buttons.PLAYER_LEFT) or joystick.get_button(Buttons.PLAYER_RIGHT))):
                # rotate shape
                current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
                pygame.mixer.Sound.play(piece_rotate_sound)
                if not valid_space(current_piece, grid):
                    current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)
            elif event.type == pygame.JOYDEVICEADDED:
                joystick = pygame.joystick.Joystick(event.device_index)
                joystick.init()
            elif event.type == pygame.JOYDEVICEREMOVED:
                joystick = None

        # Unfortunately it isn't possible to consolidate the keyboard and joystick
        # code because they don't fire the same number of events per move so have
        # to duplicate code.
        speed = 1
        if joystick:
            if joystick.get_button(Buttons.ADMIN_LEFT) and joystick.get_button(Buttons.ADMIN_RIGHT):
                run = False
            elif round(joystick.get_axis(0)) == -1: # LEFT
                if num_left == 0 or num_left > 8:
                    current_piece.x -= speed  # move x position left
                num_left += 1
                
                pygame.mixer.Sound.play(piece_move_sound)
                if not valid_space(current_piece, grid):
                    current_piece.x += speed

            elif round(joystick.get_axis(0)) == 1: # RIGHT
                if num_right == 0 or num_right > 8:
                    current_piece.x += speed  # move x position right
                num_right += 1

                pygame.mixer.Sound.play(piece_move_sound)
                if not valid_space(current_piece, grid):
                    current_piece.x -= speed

            elif round(joystick.get_axis(1)) == 1: # DOWN
                # move shape down
                current_piece.y += 1
                if not valid_space(current_piece, grid):
                    current_piece.y -= 1
                    
            elif round(joystick.get_axis(0)) == 0 and round(joystick.get_axis(1)) == 0:
                num_left = 0
                num_right = 0

        piece_pos = convert_shape_format(current_piece)

        # draw the piece on the grid by giving color in the piece locations
        for i in range(len(piece_pos)):
            x, y = piece_pos[i]
            if y >= 0:
                grid[y][x] = current_piece.color
        text_pos = getImgPos(piece_pos)
        curr_text_pos = {text_pos: current_piece}
        if change_piece:  # if the piece is locked
            for pos in piece_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color       # add the key and value in the dictionary
            text_grid[text_pos] = current_piece
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            tmp_http_status = clear_rows(grid, locked_positions, text_grid) # * 10    # increment score by 10 for every row cleared
            if tmp_http_status is not None:
                if tmp_http_status == -1:
                    error = True
                    run = False
                    continue
                else:
                    http_status = tmp_http_status
            clear_key_presses()

        current_time = time.time() - start_time
        draw_window(window, grid, text_grid, curr_text_pos, next_piece, current_time, getHighScore(high_score), http_status)
        pygame.display.update()

        if check_lost(locked_positions):
            run = False
        elif http_status == 200:
            win = True
            run = False
            # Need to update the screen one more time to clear the row
            grid = create_grid(locked_positions)
            current_time = time.time() - start_time
            draw_window(window, grid, text_grid, curr_text_pos, next_piece, current_time, getHighScore(high_score), http_status)

    pygame.key.set_repeat()
    pygame.mixer.music.stop()
    
    game_over_sound = pygame.mixer.Sound(FILE_PATH_PREFIX + '/assets/sounds/game-over.mp3')

    if win:
        text = 'You Win!'
        pygame.mixer.Sound.play(game_over_sound)
    elif error:
        text = 'Out of order. An error occurred.'
    else:
        text = 'You Lost.'
        pygame.mixer.Sound.play(game_over_sound)
    draw_text_middle_play_area(text, 40, (255, 255, 255), window)
    pygame.display.update()
    pygame.time.delay(2000)  # wait for 2 seconds

    is_top_10 = False
    is_high_score = False
    if win:
        is_top_10, is_high_score = updateHighScore(high_score, math.floor(current_time))
        score = math.floor(current_time)
    elif high_score and not error:
        high_score.high_score_list_screen()

    return win, is_top_10, is_high_score, score

def run_game(window, max_games=999, highScore=False):
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
    else:
        joystick = None

    intro_screen(window)
    story_screen(window)
    instructions_one_screen(window)
    instructions_two_screen(window)

    win = False     
    is_top_10 = False
    is_high_score = False
    num_games = 0
    score = 0

    run_main = True
    while run_main:
        win, is_top_10, is_high_score, score = main(window, highScore)

        num_games += 1
        if num_games == max_games:
            run_main = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run_main = False

        if joystick and (joystick.get_button(Buttons.PLAYER_LEFT) or joystick.get_button(Buttons.PLAYER_RIGHT)):
            run_main = False

    return win, is_top_10, is_high_score, score

def intro_screen(window):
    window.fill('black')

    # Draw the title image
    title_y_coord = 65
    title = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/images/intro_title.png')
    window.blit(title, ((s_width - title.get_width()) // 2, title_y_coord))

    # Draw the image with the buildings
    building_y_coord = title_y_coord + title.get_height() + 10
    building = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/images/intro_buildings.png')
    window.blit(building, ((s_width - building.get_width()) // 2, building_y_coord))

    # Draw the rectangle
    rect_y_coord = building_y_coord + building.get_height() + 45
    pygame.draw.rect(window, 'white', [0, rect_y_coord, s_width, s_height - building_y_coord], 0)

    # Draw arrow and '1 PLAYER' text
    font = pygame.font.Font(FILE_PATH_PREFIX + '/assets/fonts/tetris-gb.ttf', 60) #, bold=False, italic=True)
    text = font.render('1 player', 1, 'black')
    text_height = 45 # Seems like the height doesn't match the displayed height

    arrow_width = 35
    space_between = 28
    arrow_x_coord = (s_width - arrow_width - text.get_width() + space_between) // 2
    arrow_y_coord = rect_y_coord + 20
    pygame.draw.polygon(window, 'black', ((arrow_x_coord, arrow_y_coord), (arrow_x_coord, arrow_y_coord + text_height), (arrow_x_coord + arrow_width, arrow_y_coord + (text_height // 2))))

    text_x_coord = arrow_x_coord + arrow_width + space_between
    window.blit(text, (text_x_coord, arrow_y_coord - ((text.get_height() - text_height) // 2)))
    line_y_coord = arrow_y_coord + text_height + 14
    pygame.draw.line(window, (197, 115, 197), (text_x_coord - 8, line_y_coord), (text_x_coord + text.get_width(), line_y_coord), 6)
    
    # Draw copyright
    copyright = font.render('© 2024 devnet', 1, 'black')
    window.blit(copyright, ((s_width - copyright.get_width()) // 2, line_y_coord + (s_height - line_y_coord - copyright.get_height()) // 2))

    pygame.display.update()
    
    pygame.time.delay(500) # wait for half a second

def story_screen(window):
    message_line1 = 'Devvie goes to the DevNet Sandbox catalog at devnetsandbox.cisco.com and discovers'
    message_line2 = 'there are sandboxes that can be used to study for the exam. There are always-on as'
    message_line3 = 'well as reservable sandboxes. Best of all, they are FREE! Help Devvie use the'
    message_line4 = 'always-on sandboxes to make various API requests. '
    line1_counter = 0
    line2_counter = 0
    line3_counter = 0
    line4_counter = 0
    speed = 3
    story_run = True
    devvie_studying_img = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/images/devvie-studying.png')
    website_img = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/images/sandbox_website.png')
    font = pygame.font.Font(fontpath, 30)
    color = (78, 183, 72)

    while story_run:
        window.fill('black')

        website_y_coord = 100
        window.blit(website_img, (803, website_y_coord))
        window.blit(devvie_studying_img, (290, website_y_coord + website_img.get_height() - devvie_studying_img.get_height()))

        line1_y_cord = 700
        text_height = 70
        window.blit(font.render(message_line1[0:line1_counter//speed], True, color), (100, line1_y_cord))
        if line1_counter < speed * len(message_line1):
            line1_counter += 1
        else:
            window.blit(font.render(message_line2[0:line2_counter//speed], True, color), (100, line1_y_cord + 1*text_height))
            if line2_counter < speed * len(message_line2):
                line2_counter += 1
            else:
                window.blit(font.render(message_line3[0:line3_counter//speed], True, color), (100, line1_y_cord + 2*text_height))
                if line3_counter < speed * len(message_line3):
                    line3_counter += 1
                else:
                    window.blit(font.render(message_line4[0:line4_counter//speed], True, color), (100, line1_y_cord + 3*text_height))
                    if line4_counter < speed * len(message_line4):
                        line4_counter += 1
                    elif line4_counter == speed * len(message_line4):
                        story_run = False
                
        pygame.display.update()
    
    pygame.time.delay(1000) # wait for 1 second before changing to the next screen

def instructions_one_screen(window):
    window.fill('black')

    color = (42, 172, 226)

    # Title
    title_font = pygame.font.Font(fontpath, 50)
    instructions_title = title_font.render('Instructions', 1, color)
    instructions_title_y_coord = 90
    window.blit(instructions_title, ((s_width - instructions_title.get_width()) // 2, instructions_title_y_coord))

    # Object
    text_font = pygame.font.Font(fontpath, 30)
    instructions_text1 = text_font.render('* Put the pieces together in a single row in the correct format of an API request.', 1, color)
    instructions_text2 = text_font.render('* There are two types of pieces:', 1, color)
    instructions_text3 = text_font.render('       1. Pieces with text:', 1, color)
    instructions_text4 = text_font.render('           ', 1, color)
    instructions_text5 = text_font.render('            * Represents a part of an API request.', 1, color)
    instructions_text6 = text_font.render('            * Cannot rotate.', 1, color)
    instructions_text7 = text_font.render('       2. Pieces without text:', 1, color)
    instructions_text8 = text_font.render('            ', 1, color)
    instructions_text9 = text_font.render('            * Are used as fillers to complete the row.', 1, color)
    instructions_text10 = text_font.render('            * Can rotate using either button to the right of the joystick.', 1, color)
    instructions_text11 = text_font.render('* Use filler pieces to complete the row.', 1, color)

    text_height = 80
    text_x_coord = 100
    text_y_coord = instructions_title_y_coord + instructions_title.get_height() - 15
    window.blit(instructions_text1, (text_x_coord, text_y_coord + 1*text_height))
    window.blit(instructions_text2, (text_x_coord, text_y_coord + 2*text_height))
    window.blit(instructions_text3, (text_x_coord, text_y_coord + 3*text_height))
    window.blit(pygame.image.load(f'{FILE_PATH_PREFIX}/assets/images/3_1.png'), (text_x_coord + instructions_text4.get_width(), text_y_coord + 4*text_height))
    window.blit(instructions_text5, (text_x_coord, text_y_coord + 5*text_height))
    window.blit(instructions_text6, (text_x_coord, text_y_coord + 6*text_height))
    window.blit(instructions_text7, (text_x_coord, text_y_coord + 7*text_height))
    window.blit(pygame.image.load(f'{FILE_PATH_PREFIX}/assets/images/9_0_visible.png'), (text_x_coord + instructions_text8.get_width(), text_y_coord + 8*text_height))
    window.blit(instructions_text9, (text_x_coord, text_y_coord + 9*text_height))
    window.blit(instructions_text10, (text_x_coord, text_y_coord + 10*text_height))
    window.blit(instructions_text11, (text_x_coord, text_y_coord + 11*text_height))

    pygame.display.update()

    pygame.time.delay(7000) # wait for 7 seconds before changing to the next screen

def instructions_two_screen(window):
    window.fill('black')

    color = (146, 43, 140)

    # Title
    title_font = pygame.font.Font(fontpath, 50)
    instructions_title = title_font.render('API Format & Examples', 1, color)
    instructions_title_y_coord = 90
    window.blit(instructions_title, ((s_width - instructions_title.get_width()) // 2, instructions_title_y_coord))

    # Object
    text_font = pygame.font.Font(fontpath, 30)
    instructions_text1 = text_font.render('Examples:', 1, color)

    text_height = 80
    text_x_coord = 100
    text_y_coord = instructions_title_y_coord + instructions_title.get_height() - 15
    window.blit(pygame.image.load(f'{FILE_PATH_PREFIX}/assets/images/api_format.png'), (text_x_coord, text_y_coord + 1*text_height))    
    window.blit(instructions_text1, (text_x_coord, text_y_coord + 3*text_height))
    api_examples = pygame.image.load(f'{FILE_PATH_PREFIX}/assets/images/api_examples.png')
    window.blit(api_examples, ((s_width-api_examples.get_width())/2, text_y_coord + 4*text_height))    

    pygame.display.update()

    pygame.time.delay(7000) # wait for 7 seconds before changing to the next screen
    
def countdown_screen(window):
    # Countdown
    countdown_font = pygame.font.Font(fontpath, 450)
    for i in reversed(range(3)):
        window.fill('black')
        number = countdown_font.render(str(i + 1), 1, 'white')
        window.blit(number, ((s_width -  number.get_width()) // 2, (s_height - number.get_height()) // 2))
        pygame.display.flip()
        pygame.time.delay(1000)

if __name__ == '__main__':
    win = pygame.display.set_mode((s_width, s_height))
    flags = pygame.FULLSCREEN
    win = pygame.display.set_mode((s_width, s_height), flags, vsync=1)
    pygame.display.set_caption('Devbloks')

    run_game(win)

    pygame.joystick.quit()
    pygame.quit()