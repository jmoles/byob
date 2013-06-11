#!/usr/bin/python
################################################################################
# Portland State University
# ECE-544: Embedded Design with FPGA's 
# 
# Project Members: Tejashree Chaudhari
#                  Dimitriy A. Labunsky
#                  Josh Moles
#                  Tejas Tapsale
#
# Demonstration Date: June 11, 2013 (Spring Term)
#
# Description: This is a multi-level, multi-player maze game with obstacles.
#              Players compete to finish the maze while collecting the most 
#              points (good obstacles) while avoiding bad obstacles which
#              impact maze completion. This game utilizes the python "pygame"
#              library.
################################################################################

import pygame as game
from pygame.locals import *
import random
import sys
import threading
import os

#sys.path.append("/usr/local/lib64/python2.7/site-packages/") # <-- Temp code
import uinput

from lib.Pubnub import Pubnub

FPS = 15                # refresh rate
MAX_GAME_LEVELS  = 4    # max game levels
MAX_GAME_PLAYERS = 4    # max game players
MAX_TYPE_COUNT   = 5    # max obstacle types

PLAYER_1 = 1
PLAYER_2 = 2
PLAYER_3 = 3
PLAYER_4 = 4

AUTHORS_STRING="Dimitriy A. Labunsky - Josh Moles - Tejashree Chaudhari - Tejas Tapsale"

# obstacle apply action delay
OBSTACLE_ACTION_DELAY = 50

# game colors (R : G : B)
WHITE     = (255, 255, 255) 
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0) 
DARKGRAY  = ( 40,  40,  40)
YELLOW    = (255, 255,   0)
BLUE      = (  0,   0, 255)
CYAN      = (  0, 255, 255)
LIME      = (  0, 255,   0)
GRAY      = (128, 128, 128)
SILVER    = (192, 192, 192)
PURPLE    = (128,   0, 128)
OLIVE     = (128, 128,   0)
NAVY      = (0  ,   0, 128)
CYAN      = (0  , 255, 255)
MAROON    = (128,   0,   0)

# define direction
STOP  = 0  
UP    = 1
DOWN  = 2
LEFT  = 3 
RIGHT = 4

# define pubnub communication strings
PN_BTN_UP   = "-up"
PN_BTN_DOWN = "-down"
PN_UP       = "up"
PN_DOWN     = "down"
PN_LEFT     = "left"
PN_RIGHT    = "right"

# defines for controller types
CONTROL_AVAILABLE = 0
CONTROL_KEYBOARD  = 1
CONTROL_ANDROID   = 2

IMAGE_PATH   = './/image//'
SOUND_PATH_1 = './/sound//'
SOUND_PATH_2 = '../assets/audio/shawshank73/'
SOUND_PATH_3 = '../assets/audio/djgriffin/'

CHARACTER_PATH = IMAGE_PATH + 'character//'
FLOOR_PATH     = IMAGE_PATH + 'floor//'
OBSTACLE_PATH  = IMAGE_PATH + 'obstacle//'
WALL_PATH      = IMAGE_PATH + 'wall//'
OTHER_PATH     = IMAGE_PATH + 'other//'

# Get environment veriables and configure pubnub
game_pass = os.environ.get('BYOB_GAME_PASS', 'demo')
sub_key = os.environ.get('BYOB_GAME_PN_SUB', 'demo')
pub_key = os.environ.get('BYOB_GAME_PN_PUB', 'demo')
pubnub = Pubnub(
    pub_key,  ## PUBLISH_KEY
    sub_key,  ## SUBSCRIBE_KEY
    None,     ## SECRET_KEY
    False     ## SSL_ON?
)

# The lobby thread for pubnub
lobbyThread = None

# The python-uinput device
events = (uinput.KEY_W, 
    uinput.KEY_A, 
    uinput.KEY_S, 
    uinput.KEY_D, 
    uinput.KEY_I, 
    uinput.KEY_J, 
    uinput.KEY_K, 
    uinput.KEY_L)
device = uinput.Device(events)

################################################################################
# Player Class
################################################################################
class Player(game.sprite.Sprite):

    def __init__(self, name, id, color, character, control):
        game.sprite.Sprite.__init__(self)

        self.name         = name                  # player name
        self.id           = id                    # player id number
        self.color        = color                 # player color
        self.image        = character             # player character
        self.rect         = character.get_rect()  # player position data (x,y)      
        self.score        = 0                     # player score 
        self.controller   = control               # controller type
        self.direction    = STOP                  # move direction
        self.is_alive     = True                  # is player alive
        self.default_x    = 0                     # default player x coord
        self.default_y    = 0                     # default player y coord
        self.speed        = 20                    # object move speed
        self.apply_action = 0                     # how long to effect speed
        self.move_delay   = 1                     # number of moves to ignore
        self.delay_count  = 0                     # running delay counter
        self.player_id    = 0                     # Player Android Device ID
        self.player_thd   = None                  # Thread that Pubnub is on for player

    ###########################################################################
    def update(self, direction, do_update=True):
        """Player update class -- used by base class"""

        self.direction = direction
        
        if(do_update):

            # check if obstacle action should be applied
            if(self.apply_action):
                self.apply_action -= 1
            else:
                # restore default step divisor
                self.speed = 20
                self.move_delay = 1

            if(self.delay_count < self.move_delay):
                self.delay_count += 1
                return
            else:
                self.delay_count = 0

        # move player in "direction" at player speed
        if(direction == STOP):    return
        elif(direction == UP):    self.rect.y -= self.speed
        elif(direction == RIGHT): self.rect.x += self.speed
        elif(direction == DOWN):  self.rect.y += self.speed
        elif(direction == LEFT):  self.rect.x -= self.speed

    ###########################################################################
    def setStartPosition(self, x, y):
        """Set player initial starting x,y coordinates"""
        self.rect.x = x; self.default_x = x
        self.rect.y = y; self.default_y = y

    ###########################################################################
    def getPosition(self):
        """Get player x,y coordinates."""
        return (self.rect.x, self.rect.y)

    ###########################################################################
    def setPosition(self, x, y):
        """Set player x,y coordinates"""
        self.rect.x = x
        self.rect.y = y

    ###########################################################################
    def resetPosition(self):
        """Reset player x,y coordinates"""
        self.rect.x = self.default_x
        self.rect.y = self.default_y

    ###########################################################################
    def getScore(self):
        """Get Player Color."""
        return self.score

    ###########################################################################
    def getColor(self):
        """Get Player Color."""
        return self.color

    ###########################################################################
    def addPoints(self, score):
        """Give Player Points"""
        self.score += score

    ###########################################################################
    def goFast(self):
        """Increase players speed"""
        self.move_delay   = 0
        self.apply_action = OBSTACLE_ACTION_DELAY

    ###########################################################################
    def goSlow(self):
        """Decrease players speed"""
        self.move_delay   = 2 
        self.apply_action = OBSTACLE_ACTION_DELAY

    ###########################################################################
    def freeze(self):
        """Stop player from moving"""
        self.speed        = 0
        self.apply_action = OBSTACLE_ACTION_DELAY

    ###########################################################################
    def getDirection(self):
        """Get Player Direction"""
        return self.direction

    ###########################################################################
    def setDirection(self, direction):
        """Set Player Direction"""
        self.direction = direction

    ###########################################################################
    def resetSettings(self):
        """Reset settings between levels"""
        self.speed        = 20
        self.direction    = STOP
        self.apply_action = 0
        self.move_delay   = 1
        self.score        = 0

    ###########################################################################
    def draw(self, screen):
        """Render player on screen."""
        screen.blit(self.image, self.rect)

    ###########################################################################
    def pubNubPlayerThreadCallback(self, message):
        """Called when a message is received on player channel in pubNub."""

        if(message.startswith("goodbye")):
            # Player has left the game.
            # Set controller as available and close thread.
            self.controller = CONTROL_AVAILABLE
            self.player_id  = 0
            pubnub.exit()

        elif(self.id == 1):
            if(message.startswith(PN_UP)):
                if(message.endswith(PN_BTN_UP)):
                    device.emit(uinput.KEY_W, 0)
                elif(message.endswith(PN_BTN_DOWN)):
                    device.emit(uinput.KEY_W, 1)

            elif(message.startswith(PN_DOWN)):
                if(message.endswith(PN_BTN_UP)):
                    device.emit(uinput.KEY_S, 0)
                elif(message.endswith(PN_BTN_DOWN)):
                    device.emit(uinput.KEY_S, 1)

            elif(message.startswith(PN_LEFT)):
                if(message.endswith(PN_BTN_UP)):
                    device.emit(uinput.KEY_A, 0)
                elif(message.endswith(PN_BTN_DOWN)):
                    device.emit(uinput.KEY_A, 1)
            elif(message.startswith(PN_RIGHT)):
                if(message.endswith(PN_BTN_UP)):
                    device.emit(uinput.KEY_D, 0)
                elif(message.endswith(PN_BTN_DOWN)):
                    device.emit(uinput.KEY_D, 1)

        elif(self.id == 2):
            if(message.startswith(PN_UP)):
                if(message.endswith(PN_BTN_UP)):
                    device.emit(uinput.KEY_W, 0)
                elif(message.endswith(PN_BTN_DOWN)):
                    device.emit(uinput.KEY_W, 1)

            elif(message.startswith(PN_DOWN)):
                if(message.endswith(PN_BTN_UP)):
                    device.emit(uinput.KEY_S, 0)
                elif(message.endswith(PN_BTN_DOWN)):
                    device.emit(uinput.KEY_S, 1)

            elif(message.startswith(PN_LEFT)):
                if(message.endswith(PN_BTN_UP)):
                    device.emit(uinput.KEY_A, 0)
                elif(message.endswith(PN_BTN_DOWN)):
                    device.emit(uinput.KEY_A, 1)

            elif(message.startswith(PN_RIGHT)):
                if(message.endswith(PN_BTN_UP)):
                    device.emit(uinput.KEY_D, 0)
                elif(message.endswith(PN_BTN_DOWN)):
                    device.emit(uinput.KEY_D, 1)

        elif(self.id == 3):
            if(message.startswith(PN_UP)):
                if(message.endswith(PN_BTN_UP)):
                    device.emit(uinput.KEY_W, 0)
                elif(message.endswith(PN_BTN_DOWN)):
                    device.emit(uinput.KEY_W, 1)

            elif(message.startswith(PN_DOWN)):
                if(message.endswith(PN_BTN_UP)):
                    device.emit(uinput.KEY_S, 0)
                elif(message.endswith(PN_BTN_DOWN)):
                    device.emit(uinput.KEY_S, 1)

            elif(message.startswith(PN_LEFT)):
                if(message.endswith(PN_BTN_UP)):
                    device.emit(uinput.KEY_A, 0)
                elif(message.endswith(PN_BTN_DOWN)):
                    device.emit(uinput.KEY_A, 1)

            elif(message.startswith(PN_RIGHT)):
                if(message.endswith(PN_BTN_UP)):
                    device.emit(uinput.KEY_D, 0)
                elif(message.endswith(PN_BTN_DOWN)):
                    device.emit(uinput.KEY_D, 1)

        elif(self.id == 4):
            if(message.startswith(PN_UP)):
                if(message.endswith(PN_BTN_UP)):
                    device.emit(uinput.KEY_I, 0)
                elif(message.endswith(PN_BTN_DOWN)):
                    device.emit(uinput.KEY_I, 1)

            elif(message.startswith(PN_DOWN)):
                if(message.endswith(PN_BTN_UP)):
                    device.emit(uinput.KEY_K, 0)
                elif(message.endswith(PN_BTN_DOWN)):
                    device.emit(uinput.KEY_K, 1)

            elif(message.startswith(PN_LEFT)):
                if(message.endswith(PN_BTN_UP)):
                    device.emit(uinput.KEY_J, 0)
                elif(message.endswith(PN_BTN_DOWN)):
                    device.emit(uinput.KEY_J, 1)

            elif(message.startswith(PN_RIGHT)):
                if(message.endswith(PN_BTN_UP)):
                    device.emit(uinput.KEY_L, 0)
                elif(message.endswith(PN_BTN_DOWN)):
                    device.emit(uinput.KEY_L, 1)

        return True

    ###########################################################################
    def playerPubNubThread(self):
        """The function that the player Pubnub thread runs in itself."""
        pubnub.subscribe({
            'channel'  : self.player_id,
            'callback' : self.pubNubPlayerThreadCallback
            }) 

    ###########################################################################
    def startPubNubPlayerThread(self):
        """Start the pubnub thread for this player."""
        self.player_thd = threading.Thread(target=self.playerPubNubThread)
        self.player_thd.daemon = True
        self.player_thd.start()

    ###########################################################################
    def notifyAsWinner(self):
        """Notifies this player that they won."""
        if(self.controller == CONTROL_ANDROID):
            sendPubNubMessage("game-winner")

    ###########################################################################
    def notifyAsLoser(self):
        """Notifies this player that they lost."""
        if(self.controller == CONTROL_ANDROID):
            sendPubNubMessage("game-loser")

    ###########################################################################
    def sendPubNubMessage(self, message):
        """Sends +message" over player's private pubNub channel."""
        if(self.controller == CONTROL_ANDROID):
            info = pubnub.publish({
                'channel' : self.player_id,
                'message' : message
                })


###############################################################################
# Obstacle Class
###############################################################################
class Obstacle(game.sprite.Sprite):

    def __init__(self):
        game.sprite.Sprite.__init__(self)

        self.type  = random.randrange(0, MAX_TYPE_COUNT)
        self.image = game.image.load(OBSTACLE_PATH + 'obstacle.jpg').convert()
        self.rect  = self.image.get_rect()

    ###########################################################################
    def setPosition(self, x, y):
        """Set obstacle x,y coordinates"""
        self.rect.x = x
        self.rect.y = y

    ###########################################################################
    def getPosition(self):
        """Get Obstacle x,y coordinates."""
        return (self.rect.x, self.rect.y)


###############################################################################
# Maze Wall Class
###############################################################################
class MazeWall(game.sprite.Sprite):

    def __init__(self):
        game.sprite.Sprite.__init__(self)
        self.image = game.image.load(WALL_PATH + 'brick_tile.png')
        self.rect  = self.image.get_rect() 

    ###########################################################################
    def setPosition(self, x, y):
        """Set the brick x,y coordinates"""
        self.rect.x = x
        self.rect.y = y


###############################################################################
# Maze Class
###############################################################################
class Maze(object):

    def __init__(self, header_height):

        self.maze_width    = 800
        self.maze_height   = 600
        self.cell_size     = 20
        self.header_height = header_height
        self.maze          = None 
        self.wall_pool     = game.sprite.Group()

        if(self.maze_width % self.cell_size != 0):
            raise ValueError ("Error: Maze width is not a multiple of cell size.")

        if(self.maze_height % self.cell_size != 0):
            raise ValueError ("Error: Maze height is not a multiple of cell size.")

        self.cell_width  = int(self.maze_width / self.cell_size)
        self.cell_height = int(self.maze_height / self.cell_size)

        # load maze floor image
        self.loadRandomFloor()

        # generate new maze matrix
        self.generateNewMaze()

    ###########################################################################
    def generateNewMaze(self):
        """
            Returns a randomly generated maze (map).

            Credit:
            Random Maze Generator using Depth-first Search
            http://en.wikipedia.org/wiki/Maze_generation_algorithm
            FB36 - 20130106
            Downloaded From: http://code.activestate.com/recipes/578356-random-maze-generator/
            Code edited to match project needs.
        """

        # reset maze data each level
        if(self.maze != None):
            del self.maze[:]

        mx = self.cell_height
        my = self.cell_width

        maze = [[0 for x in range(mx)] for y in range(my)]
        
        # 4 directions to move in the maze
        dx = [0, 1, 0, -1]
        dy = [-1, 0, 1, 0]

        # start the maze from a random cell
        cx = random.randint(0, mx - 1) 
        cy = random.randint(0, my - 1)
        maze[cy][cx] = 1 
        stack = [(cx, cy, 0)] # stack element: (x, y, direction)

        while len(stack) > 0:
            (cx, cy, cd) = stack[-1]
            # to prevent zigzags:
            # if changed direction in the last move then cannot change again
            if len(stack) > 2:
                if cd != stack[-2][2]: dirRange = [cd]
                else: dirRange = range(4)
            else: dirRange = range(4)

            # find a new cell to add
            nlst = [] # list of available neighbors
            for i in dirRange:
                nx = cx + dx[i]; ny = cy + dy[i]
                if nx >= 0 and nx < mx and ny >= 0 and ny < my:
                    if maze[ny][nx] == 0:
                        ctr = 0 # of occupied neighbors must be 1
                        for j in range(4):
                            ex = nx + dx[j]; ey = ny + dy[j]
                            if ex >= 0 and ex < mx and ey >= 0 and ey < my:
                                if maze[ey][ex] == 1: ctr += 1
                        if ctr == 1: nlst.append(i)

            # if 1 or more neighbors available then randomly select one and move
            if len(nlst) > 0:
                ir = nlst[random.randint(0, len(nlst) - 1)]
                cx += dx[ir]; cy += dy[ir]; maze[cy][cx] = 1
                stack.append((cx, cy, ir))
            else: stack.pop()

        self.maze = maze

        # perform some post processing
        self.prepareMazeArea()

    ###########################################################################
    def getCurrentMaze(self):
        """Returns current maze data."""
        return self.maze[:]

    ###########################################################################
    def prepareMazeArea(self):
        """Prepare Maze Area. Clear finish point and player start points."""
        
        width  = self.cell_width
        height = self.cell_height

        self.wall_pool.empty()

        # clear a 4x4 block region in each corner for player to start in.
        for player in range(1,MAX_GAME_PLAYERS+1):

            # player 1 (x,y) start point
            if(player == PLAYER_1): 
                x_offset = 0
                y_offset = 0

            # player 2 (x,y) start point
            if(player == PLAYER_2):
                x_offset = width - 4
                y_offset = 0

            # player 3 (x,y) start point
            if(player == PLAYER_3):
                x_offset = width - 4
                y_offset = height - 4

            # player 4 (x,y) start point
            if(player == PLAYER_4):
                x_offset = 0
                y_offset = height - 4

            # clear a 4x4 starting region for each player
            for x in range(4):
                for y in range(4):
                    self.maze[x + x_offset][y + y_offset] = 1

        # clear a 4x4 finish point region
        x_offset = int(width / 2) - 2
        y_offset = int(height / 2) - 2

        for x in range(4):
            for y in range(4):
                self.maze[x + x_offset][y + y_offset] = 1

        # clear outside paremeter and generate wall group
        for x in range(width):
            for y in range(height):

                # clear outside maze paremeter
                if((x == 0) or (x == width-1)):
                    self.maze[x][y] = 1
                elif((y == 0) or (y == height-1)):
                    self.maze[x][y] = 1

                # create new brick object and add to group
                if(self.maze[x][y] == 0):
                    new_brick = MazeWall()
                    x_pos = x * self.cell_size
                    y_pos = y * self.cell_size
                    new_brick.setPosition(x_pos, y_pos + self.header_height)
                    self.wall_pool.add(new_brick)

    ###########################################################################
    def draw(self, screen):
        """Draw the maze floor and walls."""

        # first draw the floor
        for x in range(0, self.maze_width, self.cell_size):
            for y in range(0, self.maze_height, self.cell_size):
                screen.blit(self.maze_floor, (x, y + self.header_height))
        
        # next draw the walls
        self.wall_pool.draw(screen)

    ###########################################################################
    def getWindowHeight(self):
        """ Returns the maze window height"""
        return self.maze_height

    ###########################################################################
    def getWindowWidth(self):
        """ Returns the maze window width"""
        return self.maze_width

    ###########################################################################
    def getCellSize(self):
        """ Returns maze cell size"""
        return self.cell_size

    ###########################################################################
    def loadRandomFloor(self):
        """Selects and loads a random floor tile."""
        
        floor_tiles = os.listdir(FLOOR_PATH)
        selection = random.randrange(0, len(floor_tiles))
        tile_name = floor_tiles[selection]
        self.maze_floor = game.image.load(FLOOR_PATH + tile_name)

###############################################################################
# Maze Finish Point
###############################################################################
class FinishPoint(game.sprite.Sprite):

    def __init__(self, width, height, size, offset):
        game.sprite.Sprite.__init__(self)
        self.image = game.image.load(OBSTACLE_PATH + 'finish_point.png')  
        self.rect  = self.image.get_rect() 

        self.rect.x = int(width / 2) - size
        self.rect.y = int((height + offset) / 2)

    ###########################################################################
    def setPosition(self, x, y):
        """Set the finish point x,y coordinates"""
        self.rect.x = x
        self.rect.y = y

    ###########################################################################
    def draw(self, screen):
        """Draw the finish point on the screen."""
        screen.blit(self.image, self.rect)


###############################################################################
# Game Class
###############################################################################
class Game(object):

    def __init__(self):

        self.game_in_progress = False
        
        # header where the score is displayed (FIXME)
        self.header_height = 40

        # score awarded to winning player
        self.award_points = 3

        # current game level
        self.current_level = 1

        # level winner player index
        self.level_winner = 0

        # last player finished tracking
        self.players_finished = 0 

        # obstacle speed change timeout
        self.obstacle_action = 0

        # create new maze object, and get maze attributes
        self.maze        = Maze(self.header_height)
        self.maze_width  = self.maze.getWindowWidth()
        self.maze_height = self.maze.getWindowHeight()
        self.cell_size   = self.maze.getCellSize()

        # initialize the game engine
        game.init()
        self.fps_clock = game.time.Clock()
       
        width  = self.maze_width
        height = self.maze_height + self.header_height
        self.screen = game.display.set_mode( (width, height) )

        # player objects are stored in "player_pool" class
        self.player_color = (CYAN, RED, GREEN, YELLOW)
        self.player_pool  = []
        self.generatePlayers() # create new player objects
        
        # obstacle objects are stored in "obstacle_pool" class
        self.obstacle_count = (5, 10, 15, 20)
        self.obstacle_pool = game.sprite.Group()

        # load game sounds
        self.level_victory     = game.mixer.Sound(SOUND_PATH_1 + 'level_victory.wav')
        self.obstacle_hit      = game.mixer.Sound(SOUND_PATH_1 + 'obstacle_hit.wav')
        self.game_over_sound   = game.mixer.Sound(SOUND_PATH_2 + 'game_over.ogg') 
        self.finish_reached    = game.mixer.Sound(SOUND_PATH_2 + 'winner.ogg') 
        self.sound_round_one   = game.mixer.Sound(SOUND_PATH_2 + 'round1.ogg')
        self.sound_round_two   = game.mixer.Sound(SOUND_PATH_2 + 'round2.ogg')
        self.sound_round_three = game.mixer.Sound(SOUND_PATH_2 + 'round3.ogg')
        self.sound_round_final = game.mixer.Sound(SOUND_PATH_2 + 'roundfinal.ogg')

        # create finish point object
        width  = self.maze_width
        height = self.maze_height
        size   = self.cell_size
        offset = self.header_height
        finish = FinishPoint(width, height, size, offset)
        self.finish_point = game.sprite.Group()
        self.finish_point.add(finish)

        game.display.set_caption("B.Y.O.B")

        # Start up the pubnub lobby thread
        lobbyThread = threading.Thread(target=self.pubNubLobbyThread)
        lobbyThread.daemon = True
        lobbyThread.start()

    ###########################################################################
    def generatePlayers(self):
        """Generate Players."""

        width = self.maze_width
        height = self.maze_height
        cell_size = self.cell_size
        h_offset = self.header_height

        # create new players, and add them to the player_pool
        for player in range(1, MAX_GAME_PLAYERS+1):
            name       = "Player %d" % player
            id         = player
            color      = self.player_color[player-1]
            character  = game.image.load(CHARACTER_PATH + 'player_%d.jpg' % (player-1)).convert()

            if (player == PLAYER_1 or player == PLAYER_2):
                control = CONTROL_KEYBOARD
            else:
                control = CONTROL_AVAILABLE

            new_player = Player(name, id, color, character, control)

            # assign player 1 to Top Left of the maze
            if(player == PLAYER_1):
                x = cell_size * 2
                y = h_offset + (cell_size * 2) 

            # assign player 2 to Top Right of the maze
            if(player == PLAYER_2):
                x = width - (cell_size * 3)
                y = h_offset + (cell_size * 2)
            
            # assign player 3 to Bottom Right of the maze
            if(player == PLAYER_3):
                x = width - (cell_size * 3)
                y = (height + h_offset) - (cell_size * 3)
            
            # assign player 4 to Bottom Left of the maze
            if(player == PLAYER_4):
                x = cell_size * 2
                y = (height + h_offset) - (cell_size * 3)
                
            new_player.setStartPosition(x,y)
            self.player_pool.append(new_player)

    ###########################################################################
    def generateObstacles(self):
        """Generate Obstacles."""

        obstacle_count = self.obstacle_count[self.current_level - 1]
        self.obstacle_pool.empty()

        for obstacle in range(obstacle_count):

            new_obstacle = Obstacle()

            # search for a free spot to place obstacle (allow 100 placement retries)
            while(100):
                maze_width  = self.maze_width - self.cell_size
                maze_height = (self.header_height + self.maze_height) - self.cell_size 

                x = random.randrange(0, maze_width, self.cell_size)
                y = random.randrange(self.header_height, maze_height, self.cell_size)
                
                new_obstacle.setPosition(x, y)
                
                if(game.sprite.spritecollideany(new_obstacle, self.maze.wall_pool) == None):
                    break

            self.obstacle_pool.add(new_obstacle)

    ###########################################################################
    def startGame(self):
        """Start playing the game."""

        # load game music, set the volume to 50%, and start it.
        game.mixer.music.load(SOUND_PATH_3 + 'video-game-7.ogg')
        game.mixer.music.set_volume(0.5)
        game.mixer.music.play(-1)

        while(True):
            self.showGameStartScreen()
            self.showPlayerSelectScreen()

            for level in range(1, MAX_GAME_LEVELS + 1):
                self.showNewLevelScreen(level)
                self.startLevel()
                self.showPlayerVictoryScreen()
                self.showPlayerStatScreen()

            self.showGameOverScreen()

        self.exitGame()
    
    ###########################################################################
    def showGameStartScreen(self):
        """Show Game Start Screen."""

        flash = True

        splash = game.image.load(OTHER_PATH + 'splash.png')
       
        x = self.screen.get_rect().centerx - (splash.get_width() / 2)
        y = self.screen.get_rect().centery - (splash.get_height() / 2) + 15

        offset  = (splash.get_height() / 2)
        message = "B.Y.O.B" 

        for wait in range(10):
            self.screen.fill(BLACK)
            self.screen.blit(splash, (x,y))

            if(flash):
                self.renderTitleMessage(message, WHITE, BLACK, 55, -offset)
                flash = False
            else:
                self.renderTitleMessage(message, LIME, BLACK, 55, -offset)
                flash = True

            self.renderUserDirections(AUTHORS_STRING, GREEN, BLACK, 12, -10)

            if(self.keyPressEventDetected()):
                game.event.get()
                return

            game.display.update()
            self.fps_clock.tick(FPS)

            game.time.wait(485)

    ###########################################################################
    def showPlayerSelectScreen(self):
        """Show Game Player Selection Screen."""

        self.screen.fill(BLACK)

        x = int(self.maze_width / 2)
        y = int(self.maze_height / 2)

        game.draw.line(self.screen, WHITE, (x,0), (x, self.maze_height+self.header_height))
        game.draw.line(self.screen, WHITE, (0,y), (self.maze_width, y))

        game.display.update()
        self.fps_clock.tick(FPS)
        
        game.time.wait(0)

    ###########################################################################
    def showNewLevelScreen(self, level):
        """Show Starting New Level Screen."""

        count = 0
        progress = ""
        message = "LOADING LEVEL %d" % level

        if(level == 1):
            self.sound_round_one.play()
        elif(level == 2):
            self.sound_round_two.play()
        elif(level == 3):
            self.sound_round_three.play()
        elif(level == 4):
            self.sound_round_final.play()

        self.current_level = level
        self.maze.generateNewMaze()
        self.generateObstacles()

        for cycle in range(4):
            self.screen.fill(BLACK)
            self.renderTitleMessage(message+progress, WHITE, BLACK, 25)
            
            if(count < 3): 
                progress += ". "
                count += 1
            else:
                progress = ""
                count = 0

            game.display.update()
            self.fps_clock.tick(FPS)

            game.time.wait(500)

        # reset player state for next level
        for player in self.player_pool:
            player.is_alive = True
            player.resetPosition()

        self.resetScore()

    ###########################################################################
    def startLevel(self):
        """Show Player Victory Screen."""

        self.game_in_progress = True

        while(self.game_in_progress): 

            for event in game.event.get():
               
                if(event.type == QUIT): self.exitGame()

                #####################################################
                # Handle Player 1 Events (UP/DN/LT/RT)
                #####################################################

                if(event.type in [KEYDOWN, KEYUP]):

                    if(event.key == K_LEFT):
                        if(event.type == KEYDOWN):
                            self.player_pool[PLAYER_1-1].setDirection(LEFT)
                        elif(event.type == KEYUP):
                            self.player_pool[PLAYER_1-1].setDirection(STOP)

                    elif(event.key == K_RIGHT):
                        if(event.type == KEYDOWN):
                            self.player_pool[PLAYER_1-1].setDirection(RIGHT)
                        elif(event.type == KEYUP):
                            self.player_pool[PLAYER_1-1].setDirection(STOP)

                    elif(event.key == K_UP):
                        if(event.type == KEYDOWN):
                            self.player_pool[PLAYER_1-1].setDirection(UP)
                        elif(event.type == KEYUP):
                            self.player_pool[PLAYER_1-1].setDirection(STOP)

                    elif(event.key == K_DOWN):
                        if(event.type == KEYDOWN):
                            self.player_pool[PLAYER_1-1].setDirection(DOWN)
                        elif(event.type == KEYUP):
                            self.player_pool[PLAYER_1-1].setDirection(STOP)

                #####################################################
                # Handle Player 2 Events (K8/K2/K4/K6)
                #####################################################

                    if(event.key == K_KP4):
                        if(event.type == KEYDOWN):
                            self.player_pool[PLAYER_2-1].setDirection(LEFT)
                        elif(event.type == KEYUP):
                            self.player_pool[PLAYER_2-1].setDirection(STOP)

                    elif(event.key == K_KP6):
                        if(event.type == KEYDOWN):
                            self.player_pool[PLAYER_2-1].setDirection(RIGHT)
                        elif(event.type == KEYUP):
                            self.player_pool[PLAYER_2-1].setDirection(STOP)

                    elif(event.key == K_KP8):
                        if(event.type == KEYDOWN):
                            self.player_pool[PLAYER_2-1].setDirection(UP)
                        elif(event.type == KEYUP):
                            self.player_pool[PLAYER_2-1].setDirection(STOP)

                    elif(event.key == K_KP2):
                        if(event.type == KEYDOWN):
                            self.player_pool[PLAYER_2-1].setDirection(DOWN)
                        elif(event.type == KEYUP):
                            self.player_pool[PLAYER_2-1].setDirection(STOP)

                #####################################################
                # Handle Player 3 Events (W/A/S/D)
                #####################################################
                # code here
                    if(event.key == K_a):
                        if(event.type == KEYDOWN):
                            self.player_pool[PLAYER_3-1].setDirection(LEFT)
                        elif(event.type == KEYUP):
                            self.player_pool[PLAYER_3-1].setDirection(STOP)

                    elif(event.key == K_d):
                        if(event.type == KEYDOWN):
                            self.player_pool[PLAYER_3-1].setDirection(RIGHT)
                        elif(event.type == KEYUP):
                            self.player_pool[PLAYER_3-1].setDirection(STOP)

                    elif(event.key == K_w):
                        if(event.type == KEYDOWN):
                            self.player_pool[PLAYER_3-1].setDirection(UP)
                        elif(event.type == KEYUP):
                            self.player_pool[PLAYER_3-1].setDirection(STOP)

                    elif(event.key == K_s):
                        if(event.type == KEYDOWN):
                            self.player_pool[PLAYER_3-1].setDirection(DOWN)
                        elif(event.type == KEYUP):
                            self.player_pool[PLAYER_3-1].setDirection(STOP)

                #####################################################
                # Handle Player 4 Events (I/J/K/L)
                #####################################################
                # code here
                    if(event.key == K_j):
                        if(event.type == KEYDOWN):
                            self.player_pool[PLAYER_4-1].setDirection(LEFT)
                        elif(event.type == KEYUP):
                            self.player_pool[PLAYER_4-1].setDirection(STOP)

                    elif(event.key == K_l):
                        if(event.type == KEYDOWN):
                            self.player_pool[PLAYER_4-1].setDirection(RIGHT)
                        elif(event.type == KEYUP):
                            self.player_pool[PLAYER_4-1].setDirection(STOP)

                    elif(event.key == K_i):
                        if(event.type == KEYDOWN):
                            self.player_pool[PLAYER_4-1].setDirection(UP)
                        elif(event.type == KEYUP):
                            self.player_pool[PLAYER_4-1].setDirection(STOP)

                    elif(event.key == K_k):
                        if(event.type == KEYDOWN):
                            self.player_pool[PLAYER_4-1].setDirection(DOWN)
                        elif(event.type == KEYUP):
                            self.player_pool[PLAYER_4-1].setDirection(STOP)

            # Move all players
            for player in self.player_pool:
                self.updatePlayerPosition(player)

            self.renderMaze()
            self.renderExitPoint()
            self.renderPlayers()
            self.renderObstacles()
            self.renderScore()

            game.display.update()
            self.fps_clock.tick(FPS)

    ###########################################################################
    def updatePlayerPosition(self, player):
        """Update player position if no collision is dectected."""

        recover_direction = None

        direction = player.getDirection()

        if(direction == STOP): return

        if(direction == LEFT):    recover_direction = RIGHT
        elif(direction == RIGHT): recover_direction = LEFT
        elif(direction == UP):    recover_direction = DOWN
        elif(direction == DOWN):  recover_direction = UP

        # update the player postion
        player.update(direction)
        
        # check if that results in a collision with wall
        if(game.sprite.spritecollideany(player, self.maze.wall_pool) != None):
            player.update(recover_direction, False) # if collision, restore last position.
            player.setDirection(STOP)

        # check left and right screen limits
        elif(player.rect.x < 0 or (player.rect.x + self.cell_size) > self.maze_width):
            player.update(recover_direction, False)
            player.setDirection(STOP)

        # check top and bottom screen limits
        elif(player.rect.y < self.header_height or \
            (player.rect.y + self.cell_size) > (self.maze_height + self.header_height)):
            player.update(recover_direction, False)
            player.setDirection(STOP)

        # check if finish point is reached
        elif(game.sprite.spritecollideany(player, self.finish_point) != None):
            player.addPoints(self.award_points)
            self.updateScore()
            player.is_alive = False
            self.players_finished +=1
            self.level_winner = player.id

            if(self.players_finished == len(self.player_pool)):
                self.players_finished = 0
                self.resetScore()
                self.game_in_progress = False

            self.finish_reached.play()

            # FIXME - next line is temp code... since we only have one player
            self.game_in_progress = False

        # perform collision detection between players
        elif(len(player.rect.collidelistall(self.player_pool)) > 1):
            player.update(recover_direction, False)
            player.setDirection(STOP)


        # check if obstacle is hit and perform related action
        for hit_obstacle in game.sprite.spritecollide(player, self.obstacle_pool, True):

            self.obstacle_hit.play()

            # type 0 obstacle hit
            if(hit_obstacle.type == 0):
                # freeze all other players for N seconds.
                for freeze_player in self.player_pool:
                    if(player != freeze_player):
                        freeze_player.freeze()

            # type 1 obstacle hit
            elif(hit_obstacle.type == 1):
                # slow down other players for N seconds.
                for slow_player in self.player_pool:
                    if(player != slow_player):
                        slow_player.goSlow()

            # type 2 obstacle hit
            elif(hit_obstacle.type == 2):
                # reset all other players to starting point. hit player slows down for N seconds.
                for reset_player in self.player_pool:
                    if(player != reset_player):
                        reset_player.resetPosition()

                player.goSlow()

            # type 3 obstacle hit
            elif(hit_obstacle.type == 3):
                # shuffle player positions
                pos_save = self.player_pool[0].getPosition()

                for index in range(len(self.player_pool)-1):
                    pos = self.player_pool[index+1].getPosition()
                    self.player_pool[index].setPosition(pos[0], pos[1])

                self.player_pool[-1].setPosition(pos_save[0], pos_save[1])

            # type 4 obstacle hit
            elif(hit_obstacle.type == 4):
                # speed up hit player for N seconds.
                player.goFast()

    ###########################################################################
    def showPlayerVictoryScreen(self):
        """Show Player Victory Screen."""
        
        flash = True
        index = self.level_winner - 1
        winner = self.player_pool[index]
       
        message = "%s is Winner!!!" % winner.name

        # blink winner name
        for wait in range(10):

            # change background to winner color
            self.screen.fill(winner.color)

            if(flash):
                self.renderTitleMessage(message, WHITE, winner.color)
                flash = False
            else:
                self.renderTitleMessage(message, BLACK, winner.color)
                flash = True

            game.display.update()
            self.fps_clock.tick(FPS)

            game.time.wait(250)

        game.time.wait(2000)

    ###########################################################################
    def showPlayerStatScreen(self):
        """Show Player Statistics Screen."""
        
        screen_width  = self.maze_width
        screen_height = self.maze_height + self.header_height
        bar_width = screen_width / 6
        x = bar_width
        unit = screen_height / 2

        self.screen.fill(BLACK)

        # display screen header
        font = game.font.Font('freesansbold.ttf', 45)
        surf = font.render("PLAYER STATISTICS", True, WHITE, BLACK)
        rect = surf.get_rect()
        rect.centerx = self.screen.get_rect().centerx
        rect.centery = 50
        self.screen.blit(surf, rect)

        # collect player statistics
        total_score = 0
        winner_id   = 0
        prev_score  = 0
        for player in self.player_pool:
            if(player.score > prev_score):
                winner_id = player.id
            total_score += player.score

        # draw a bar graph using each players score
        for player in self.player_pool:
            bar_height = ( float(player.score) / float(total_score) ) * unit
            y = screen_height - bar_height
            score_bar = game.Rect(x, y, bar_width, bar_height)
            game.draw.rect(self.screen, player.color, score_bar)
            x += bar_width

            # player score
            font = game.font.Font('freesansbold.ttf', 16)
            surf = font.render(str(player.score), True, WHITE, BLACK)
            rect = surf.get_rect()
            rect.centerx = score_bar.centerx 
            rect.y = y - 25
            self.screen.blit(surf, rect)

            # player name
            font = game.font.Font('freesansbold.ttf', 18)
            surf = font.render(player.name, True, WHITE, BLACK)
            rect = surf.get_rect()
            rect.centerx = score_bar.centerx
            rect.y = y - 50
            self.screen.blit(surf, rect)

            # draw winning star for top score player
            if(player.id == winner_id):
                star = game.image.load(OBSTACLE_PATH + 'finish_point.png')  
                rect = star.get_rect() 
                rect.centerx = score_bar.centerx 
                rect.y = y - (70 + rect.height) 
                self.screen.blit(star, rect)

        game.display.update()
        self.fps_clock.tick(FPS)

        game.time.wait(5500)

    ###########################################################################
    def showGameOverScreen(self):
        """Show Game Over Screen."""

        flash = True

        self.game_over_sound.play()

        # Notify players of game over.
        for player in self.player_pool:
            player.sendPubNubMessage("game-over")

        for wait in range(10):
            self.screen.fill(BLACK)

            if(flash):
                self.renderTitleMessage("GAME OVER", WHITE)
                flash = False
            else:
                self.renderTitleMessage("GAME OVER", RED)
                flash = True

            game.display.update()
            self.fps_clock.tick(FPS)

            game.time.wait(250)

        # reset each players score
        for player in self.player_pool:
            player.resetSettings()

    ###########################################################################
    def renderMaze(self, generate_new_maze = True):
        """Render Game Floor and Maze Walls."""
   
        self.maze.draw(self.screen)

    ###########################################################################
    def renderPlayers(self):
        """Render Game Players."""
       
        for player in self.player_pool:
            if(player.is_alive):
                player.draw(self.screen)

    ###########################################################################
    def renderExitPoint(self):
        """Render Game Exit Point."""

        self.finish_point.draw(self.screen)

    ###########################################################################
    def renderObstacles(self):
        """Render Game Obstacles."""

        self.obstacle_pool.draw(self.screen)

    ###########################################################################
    def renderScore(self):
        """Render Player Score."""
        
        offset = 0
        width  = int(self.maze_width / MAX_GAME_PLAYERS)
        height = self.header_height

        header = game.Rect(0, 0, self.maze_width, height)
        game.draw.rect(self.screen, BLACK, header)

        #for player in range(MAX_GAME_PLAYERS):
        for player in self.player_pool:     

            game.draw.line(self.screen, WHITE, (offset, 0), (offset, height))

            player_info = player.name + ':  %d' % player.score

            font = game.font.Font('freesansbold.ttf', 18)
            surf = font.render(player_info, True, player.color, BLACK)
            rect = surf.get_rect()
            rect.topleft = (offset + 20, 10)
            self.screen.blit(surf, rect)

            offset += width

        game.draw.line(self.screen, WHITE, (0, height), (self.maze_width, height))

    ###########################################################################
    def renderUserDirections(self, message="", f_color=WHITE, b_color=BLACK, size=12, offset=0):
        """Render User Directions."""
        
        font = game.font.Font('freesansbold.ttf', size)
        surf = font.render(message, True, f_color, b_color)
        rect = surf.get_rect()
        rect.centerx = self.screen.get_rect().centerx
        rect.y = self.maze_height + offset
        self.screen.blit(surf, rect)

    ###########################################################################
    def renderTitleMessage(self, message="", f_color=WHITE, b_color=BLACK, size=40, offset=0):
        """Render Title Message."""

        font = game.font.Font('freesansbold.ttf', size)
        surf = font.render(message, True, f_color, b_color)
        rect = surf.get_rect()
        rect.centerx = self.screen.get_rect().centerx
        rect.centery = self.screen.get_rect().centery + offset
        self.screen.blit(surf, rect)

    ###########################################################################
    def updateScore(self):
        """Updates possible points to collect by winner."""

        # possible earn points reduced by 2 each time a player completes
        self.award_points -= 1

    ###########################################################################
    def resetScore(self):
        """Resets game score back to initial value."""

        # possible points = total number of players
        self.award_points = (len(self.player_pool) - 1) * self.current_level

    ###########################################################################
    def exitGame(self):
        """Terminate game."""

        game.quit()
        sys.exit()

    ###########################################################################
    def keyPressEventDetected(self):
        """Check if key press event is detected."""

        if(len(game.event.get(QUIT)) > 0):
            self.exitGame()

        keyUpEvents = game.event.get(KEYUP)

        if(len(keyUpEvents) == 0):
            return None

        if(keyUpEvents[0].key == K_ESCAPE):
            self.exitGame()

        return keyUpEvents[0].key

    ###########################################################################
    def pubNubPlayerReceiveCallback(self, message):
        """Called when a message is received on player channel in pubNub."""
        return True

    ###########################################################################
    def pubNubPlayerThread(self, player_id):
        print "New player thread started"
        # Subscribe to the player thread
        pubnub.subscribe({
            'channel'  : player_id,
            'callback' : self.pubNubPlayerReceiveCallback
            })

    ###########################################################################
    def pubNubLobbyThread(self):
        # Subscribe to the lobby channel for the game
        pubnub.subscribe({
            'channel'  : ('lobby-' + game_pass),
            'callback' : self.pubNubLobbyReceiveCallback
            })

    ###########################################################################
    def pubNubLobbyReceiveCallback(self, message):
        """Called when a message is received on lobby channel in pubNub."""

        print message

        # Determine the type of message received
        if(message.startswith("want-to-join-byob:")):
            # Player is wanting to join the game.
            # If there is room, invite the player to join the game (join-game)
            # and join their private channel for command and control.
            # If game is full, send them "game-is-full" on their private channel.

            # Extract the device ID for the player
            this_player_id  = message.split()[1]

            # Find the first player who has a controller avilable.
            # Setting variables assuming we won't find a spot for the player.
            message           = "game-is-full"

            for player in self.player_pool:
                if(player.controller == CONTROL_AVAILABLE):
                    # Player is available. Mark as Android and set player_id
                    player.controller = CONTROL_ANDROID
                    player.player_id  = this_player_id
                    
                    # Set up a subscription thread for this player.
                    player.startPubNubPlayerThread()

                    # Set message to send player to join game
                    message = "join-game"

                    # Break out of the for loop
                    break

            print "Sending message: " + message
            # Publish a message to the player with results
            info = pubnub.publish({
                'channel'  : player.player_id,
                'message'  : message
                })

        return True


###############################################################################
# Main
###############################################################################
def main():
    """ Main game routine. This will start the game. """

    game_obj = Game()       # create a game class object
    game_obj.startGame()    # start the game


###############################################################################
# Start the Game 
###############################################################################
if __name__ == '__main__':
    main()

