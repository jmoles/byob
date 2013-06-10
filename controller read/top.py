import sys
import pygame as game
import serialRead_maze as Read
from pygame.locals import*
import time

game.init()

fpsClock = game.time.Clock()

def my_events():
  
  while True:
#    time.sleep(1)
    for event in game.event.get():
        print event.type
        #if event.type == QUIT:
        #    game.quit()
        if event.type == Read.UP:
            print("UP")
        elif event.type == Read.DOWN:
            print("DOWN")
        elif event.type == Read.RIGHT:
            print("RIGHT")
        elif event.type == Read.LEFT:
            print("LEFT")
            
my_events()
game.display.update()
fpsClock.tick(30)
