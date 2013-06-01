import pygame, sys
from pygame.locals import*

pygame.init()
pygame.mixer.init()

fpsClock = pygame.time.Clock()
enlarge_factor = 8

white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0,)
green = pygame.Color(0, 255, 0) 
blue = pygame.Color(0, 0, 255)
black = pygame.Color(0, 0, 0)

windowSurfaceObj = pygame.display.set_mode((800, 800))
pygame.display.set_caption('Worst Map Ever')

soundObj = pygame.mixer.Sound("E:\\Embedded_System\\Python\\maze_trial\\ting.wav")

f = open("E:\\Embedded_System\\Python\\maze_trial\\test.txt", "r")
a = f.readlines()
f.close()

def enlarge_pixel(color):
   for p in range(0,enlarge_factor):
               for q in range (0,enlarge_factor):
                  pixArr[(enlarge_factor*y-p), (enlarge_factor*x-q)] = color

while True:

   windowSurfaceObj.fill(black)
   
   pixArr = pygame.PixelArray(windowSurfaceObj)

   for x in range(0,100):
      for y in range (0,95):
         if a[x][y] == "0":
            enlarge_pixel(white)
         elif a[x][y] == "1":
            enlarge_pixel(red)
         elif a[x][y] == " ":
            enlarge_pixel(black)
         elif a[x][y] == "2":
            enlarge_pixel(green)
   del pixArr

   for event in pygame.event.get():
      if event.type == QUIT:
         pygame.quit()
         sys.exit()
      elif event.type == MOUSEBUTTONUP:
         if event.button == 1:
            soundObj.play()
            print ("left mouse button click")

   pygame.display.update()
   fpsClock.tick(30)
