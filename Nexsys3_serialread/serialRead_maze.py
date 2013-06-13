##Created By: Tejashree
##This code receives dat through UART. According to the data
##particular events are posted

#!/usr/bin/python
import pygame as game
import serial
import thread
import time

#Initialize
game.init()

#Configure the serial port
port = serial.Serial("COM19", baudrate=9600, timeout=1)

#create two events names KEYUP and KEYDOWN
KEYDOWN = game.USEREVENT+2
KEYUP = game.USEREVENT+3

#create events with key as the button names
NEX3_UP = game.event.Event(KEYDOWN,key="NEX_UP")
NEX3_UR = game.event.Event(KEYUP, key="NEX_UP")

NEX3_DP = game.event.Event(KEYDOWN, key="NEX_DOWN")
NEX3_DR = game.event.Event(KEYUP, key="NEX_DOWN")

NEX3_RP = game.event.Event(KEYDOWN, key="NEX_RIGHT")
NEX3_RR = game.event.Event(KEYUP, key="NEX_RIGHT")

NEX3_LP = game.event.Event(KEYDOWN, key="NEX_LEFT")
NEX3_LR = game.event.Event(KEYUP, key="NEX_LEFT")

def read_keys():
  while True:
      #receive data from UART
      receive = port.read(2)
      #According to the data received post corresponding event
      if receive == "01":
        game.event.post(NEX3_UP)  #UP button pressed
      elif receive == "11":
        game.event.post(NEX3_UR)  #UP button released
      elif receive == "04":
        game.event.post(NEX3_DP)  #DOWN button pressed
      elif receive == "14":
        game.event.post(NEX3_DR)  #DOWN button released
      elif receive == "02":
        game.event.post(NEX3_LP)  #LEFT button pressed
      elif receive == "12":
        game.event.post(NEX3_LR)  #LEFT button released
      elif receive == "08":
        game.event.post(NEX3_RP)  #RIGHT button pressed
      elif receive == "18":
        game.event.post(NEX3_RR)  #RIGHT button released

#start the thread
thread.start_new_thread(read_keys, ())
