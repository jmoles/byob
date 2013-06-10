#!/usr/bin/python
import pygame as game
import serial
import thread
import time


game.init()

port = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=0)

UP = game.USEREVENT+2
NEXSYS3_UP = game.event.Event(UP)

DOWN = game.USEREVENT+3
NEXSYS3_DOWN = game.event.Event(DOWN)

LEFT = game.USEREVENT+4
NEXSYS3_LEFT = game.event.Event(LEFT)

RIGHT = game.USEREVENT+5
NEXSYS3_RIGHT = game.event.Event(RIGHT)

def read_keys():
  while True:
      receive = port.read(256)
      if receive == "1":
        game.event.post(NEXSYS3_UP)
#        print "Posted up", receive
      elif receive == "4":
        game.event.post(NEXSYS3_DOWN)
#        print "Posted down", receive
      elif receive == "8":
        game.event.post(NEXSYS3_RIGHT)
#        print "Posted right", receive
      elif receive == "2":
        game.event.post(NEXSYS3_LEFT)
#        print "Posted lft", receive

thread.start_new_thread(read_keys, ())

