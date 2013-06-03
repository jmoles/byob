#!/usr/bin/python
################################################################################
# Portland State University
# ECE-540: Embedded Design with FPGA's 
# 
# Project Members: Tejashree Chaudhari
#                  Dimitriy A. Labunsky
#                  Josh Moles
#                  Tejas Tapsale
#
# Date: May 24th 2013 (Spring Term)
# Description:
################################################################################

import pygame as game
from pygame.locals import *
import random
import sys

# refresh rate: frame per second
FPS = 15                
MAX_GAME_LEVELS = 4
MAX_GAME_PLAYERS = 4

# define color encodings (RGB)
#             R    G    B
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
UP    = "up"
DOWN  = "down"
LEFT  = "left"
RIGHT = "right"

IMAGE_PATH = './/image//'
SOUND_PATH = './/sound//'

CHARACTER_PATH = IMAGE_PATH + 'character//'
FLOOR_PATH     = IMAGE_PATH + 'floor//'
OBSTACLE_PATH  = IMAGE_PATH + 'obstacle//'
WALL_PATH      = IMAGE_PATH + 'wall//'
OTHER_PATH     = IMAGE_PATH + 'other//'

################################################################################
# Controller Class
################################################################################
class Controller(object):
   
    # This is just a template for now

    def __init__(self, type):
        self.control_type = type

    ###########################################################################
    def getType(self):
        """Get Controller Type"""
        return self.control_type

################################################################################
# Player Class
################################################################################
class Player(game.sprite.Sprite):

    def __init__(self, name, color, character, control):
        game.sprite.Sprite.__init__(self)

        self.name       = name                  # player name
        self.color      = color                 # player color
        self.image      = character             # player character
        self.rect       = character.get_rect()  # player position data (x,y)      
        self.score      = 0                     # player score 
        self.controller = Controller(control)   # controller object ptr
        self.direction  = None                  # move direction
        self.speed      = 20                    # object move speed
        self.is_alive   = True                  # is player alive
        self.default_x  = 0                     # default player x coord
        self.default_y  = 0                     # default player y coord

    ###########################################################################
    def update(self, direction):
        """Player update class -- used by base class"""

        self.direction = direction

        # check for wall collisions
        if(direction == UP):      self.rect.y -= self.speed
        elif(direction == RIGHT): self.rect.x += self.speed
        elif(direction == DOWN):  self.rect.y += self.speed
        elif(direction == LEFT):  self.rect.x -= self.speed

    ###########################################################################
    def getPosition(self):
        """Get players x,y coordinates."""
        return (self.rect.x, self.rect.y)

    ###########################################################################
    def setPosition(self, x, y):
        """Set player x,y coordinates"""
        self.rect.x = x; self.default_x = x
        self.rect.y = y; self.default_y = y

    ###########################################################################
    def resetPosition(self):
        """Reset player x,y coordinates"""
        self.rect.x = self.default_x
        self.rect.y = self.default_y

    ###########################################################################
    def getPlayerScore(self):
        """Get Players Score."""
        return self.score

    ###########################################################################
    def setPlayerScore(self, score):
        """Set Players Score"""
        self.score += score

    ###########################################################################
    def getPlayerControlType(self):
        """Get Player Controller Type"""
        return self.controller.getType()

    ###########################################################################
    def draw(self, screen):
        """Render player on screen."""
        screen.blit(self.image, self.rect)

###############################################################################
# Obstacle Class
###############################################################################
class Obstacle(game.sprite.Sprite):

    def __init__(self):
        game.sprite.Sprite.__init__(self)

        self.type  = random.rand_range()
        self.image = game.image.load(OBSTACLE_PATH + 'object_type_%d.jpg' % self.type)
        self.rect  = self.image.get_rect()

        random_position = self.getRandomPosition()

        self.rect.x = random_position[0]    # x-coordiante
        self.rand.y = random_position[1]    # y-coordinate

    ###########################################################################
    def getRandomPosition(self):
        """Get Obstacles Initial Position."""
        x = 0
        y = 0
        
        # Add Code Here

        return [x, y]

    ###########################################################################
    def getObstaclePosition(self):
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

        # load game images
        self.maze_floor = game.image.load(FLOOR_PATH + 'grass_tile.png')

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
        for player in range(MAX_GAME_PLAYERS):

            # player 0 (x,y) start point
            if(player == 0): 
                x_offset = 0
                y_offset = 0

            # player 1 (x,y) start point
            if(player == 1):
                x_offset = width - 4
                y_offset = 0

            # player 2 (x,y) start point
            if(player == 2):
                x_offset = width - 4
                y_offset = height - 4

            # player 3 (x,y) start point
            if(player == 3):
                x_offset = 0
                y_offset = height - 4

            # clear a 4x4 starting region for each player
            for x in range(4):
                for y in range(4):
                    self.maze[x + x_offset][y + y_offset] = 1

        # clear a 4x4 finish point region
        x_offset = (width / 2) - 2
        y_offset = (height / 2) - 2

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


###############################################################################
# Maze Finish Point
###############################################################################
class FinishPoint(game.sprite.Sprite):

    def __init__(self, width, height, size, offset):
        game.sprite.Sprite.__init__(self)
        self.image = game.image.load(OBSTACLE_PATH + 'finish_point.png')  
        self.rect  = self.image.get_rect() 

        self.rect.x = (width / 2) - size
        self.rect.y = (height + offset) / 2

    ###########################################################################
    def setPosition(self, x, y):
        """Set the finish point x,y coordinates"""
        self.rect.x = x
        self.rect.y = y

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
        self.award_points = 100

        # current game level
        self.current_level = 0

        # last player finished tracking
        self.players_finished = 0 

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
        self.screen.convert() 

        # player objects are stored in "player_pool" class
        self.player_color = (CYAN, RED, GREEN, YELLOW)
        self.player_pool  = []
        self.generatePlayers() # create new player objects

        # obstacle objects are stored in "obstacle_pool" class
        self.obstacle_pool = game.sprite.Group()
        self.generateObstacles() # create new obstacles

        # load game sounds
        self.game_start_sound    = game.mixer.Sound(SOUND_PATH + 'game_start.wav') 
        self.next_level_sound    = game.mixer.Sound(SOUND_PATH + 'next_level.wav') 
        self.level_victory_sound = game.mixer.Sound(SOUND_PATH + 'level_victory.wav') 
        self.game_over_sound     = game.mixer.Sound(SOUND_PATH + 'game_over.wav') 
        self.finish_reached      = game.mixer.Sound(SOUND_PATH + 'finish_reached.wav') 

        # create finish point object
        width  = self.maze_width
        height = self.maze_height
        size   = self.cell_size
        offset = self.header_height
        finish = FinishPoint(width, height, size, offset)
        self.finish_point = game.sprite.Group()
        self.finish_point.add(finish)

        game.display.set_caption("Maze Madeness")
        
    ###########################################################################
    def generatePlayers(self):
        """Generate Players."""

        width = self.maze_width
        height = self.maze_height
        cell_size = self.cell_size
        h_offset = self.header_height

        # create new players, and add them to the player_pool
        for player in range(MAX_GAME_PLAYERS):
            name       = "Player %d" % player
            color      = self.player_color[player]
            character  = game.image.load(CHARACTER_PATH + 'player_%d.jpg' % player)
            control    = None
            new_player = Player(name, color, character, control)

            # assign player 0 to Top Left of the maze
            if(player == 0):
                x = cell_size * 2
                y = h_offset + (cell_size * 2) 

            # assign player 1 to Top Right of the maze
            if(player == 1):
                x = width - (cell_size * 3)
                y = h_offset + (cell_size * 2)
            
            # assign player 2 to Bottom Right of the maze
            if(player == 2):
                x = width - (cell_size * 3)
                y = (height + h_offset) - (cell_size * 3)
            
            # assign player 3 to Bottom Left of the maze
            if(player == 3):
                x = cell_size * 2
                y = (height + h_offset) - (cell_size * 3)
                
            new_player.setPosition(x,y)
            self.player_pool.append(new_player)

    ###########################################################################
    def generateObstacles(self):
        """Generate Obstacles."""
        pass

    ###########################################################################
    def startGame(self):
        """Start playing the game."""

        self.showGameStartScreen()
        self.showPlayerSelectScreen()

        for level in range(MAX_GAME_LEVELS):
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

        self.game_start_sound.play()
        #splash = game.image.load(OTHER_PATH + 'monkey.jpg') <-- load custom image here
        
        for wait in range(10):
            self.screen.fill(BLACK)
            #self.screen.blit(splash, (450, 350))

            if(flash):
                self.renderTitleMessage("- * - * MAZE MADNESS * - * -", WHITE, BLACK)
                flash = False
            else:
                self.renderTitleMessage("- * - * MAZE MADNESS * - * -", LIME, BLACK)
                flash = True

            self.renderUserDirections("Portland State University", GREEN, BLACK, 14)

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

        x = self.maze_width / 2
        y = self.maze_height / 2

        game.draw.line(self.screen, WHITE, (x,0), (x, self.maze_height+self.header_height))
        game.draw.line(self.screen, WHITE, (0,y), (self.maze_width, y))

        game.display.update()
        self.fps_clock.tick(FPS)
        
        game.time.wait(5000)

    ###########################################################################
    def showNewLevelScreen(self, level):
        """Show Starting New Level Screen."""

        count = 0
        progress = ""
        message = "LOADING LEVEL %d" % level

        self.current_level = level

        self.maze.generateNewMaze()

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
       
        # reset player state for next level
        for player in self.player_pool:
            player.is_alive = True
            player.resetPosition()

            game.time.wait(500)

    ###########################################################################
    def startLevel(self):
        """Show Player Victory Screen."""

        redraw_screen = True
        self.game_in_progress = True

        while(self.game_in_progress): 

            for event in game.event.get():
               
                if(event.type == QUIT): self.exitGame()

                # FIXME - support only for player 0
                if(event.type == KEYDOWN):
                    redraw_screen = True

                    if(event.key == K_LEFT):    direction = LEFT
                    elif(event.key == K_RIGHT): direction = RIGHT
                    elif(event.key == K_UP):    direction = UP
                    elif(event.key == K_DOWN):  direction = DOWN
                    
                    self.updatePlayerPosition(self.player_pool[0], direction)


            if(redraw_screen):
                self.renderMaze()
                self.renderExitPoint()
                self.renderPlayers()
                self.renderObstacles()
                self.renderScore()

                game.display.update()
                self.fps_clock.tick(FPS)

                redraw_screen = False
        
    ###########################################################################
    def updatePlayerPosition(self, player, direction):
        """Update player position if no collision is dectected."""

        recover_direction = None

        if(direction == LEFT):    recover_direction = RIGHT
        elif(direction == RIGHT): recover_direction = LEFT
        elif(direction == UP):    recover_direction = DOWN
        elif(direction == DOWN):  recover_direction = UP

        # update the player postion
        player.update(direction)
        
        # check if that results in a collision with wall
        if(game.sprite.spritecollideany(player, self.maze.wall_pool) != None):
            player.update(recover_direction) # if collision, restore last position.

        # check left and right screen limits
        elif(player.rect.x < 0 or (player.rect.x + self.cell_size) > self.maze_width):
            player.update(recover_direction)

        # check top and bottom screen limits
        elif(player.rect.y < self.header_height or \
            (player.rect.y + self.cell_size) > (self.maze_height + self.header_height)):
            player.update(recover_direction)

        # check if finish point is reached
        elif(game.sprite.spritecollideany(player, self.finish_point) != None):
            player.setPlayerScore(self.award_points)
            self.updateScore()
            player.is_alive = False
            self.players_finished +=1

            if(self.players_finished == len(self.player_pool)):
                self.players_finished = 0
                self.resetScore()
                self.game_in_progress = False

            self.finish_reached.play()


            # this is temp code... since we only have one player FIXME
            self.game_in_progress = False

    ###########################################################################
    def showPlayerVictoryScreen(self):
        """Show Player Victory Screen."""
        
        flash      = True
        winner     = 0
        last_score = 0

        # play victory sound
        self.level_victory_sound.play()

        for player in self.player_pool:
            if(player.score > last_score):
                winner = player
       
        message = "%s is Winner!!!" % winner.name

        # blank winner name
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
        pass

    ###########################################################################
    def showGameOverScreen(self):
        """Show Game Over Screen."""

        flash = True

        self.game_over_sound.play()

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
        width  = self.maze_width / MAX_GAME_PLAYERS
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
    def renderUserDirections(self, message="", f_color=WHITE, b_color=BLACK, size=12):
        """Render User Directions."""
        
        font = game.font.Font('freesansbold.ttf', size)
        surf = font.render(message, True, f_color, b_color)
        rect = surf.get_rect()
        rect.centerx = self.screen.get_rect().centerx
        rect.y = self.maze_height - 15
        self.screen.blit(surf, rect)

    ###########################################################################
    def renderTitleMessage(self, message="", f_color=WHITE, b_color=BLACK, size=40):
        """Render Title Message."""

        font = game.font.Font('freesansbold.ttf', size)
        surf = font.render(message, True, f_color, b_color)
        rect = surf.get_rect()
        rect.centerx = self.screen.get_rect().centerx
        rect.centery = self.screen.get_rect().centery
        self.screen.blit(surf, rect)

    ###########################################################################
    def updateScore(self):
        """Updates possible points to collect by winner."""

        # possible earn points reduced by 2 each time a player completes
        self.award_points /= 2

    ###########################################################################
    def resetScore(self):
        """Resets game score back to initial value."""

        self.award_points = 100 * (1 + self.current_level)

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

