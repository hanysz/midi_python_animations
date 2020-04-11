from __future__ import division # so that a/b for integers evaluates as floating point
import pyglet, sys, subprocess, os, time, mido
from moviepy.editor import *
import math # we'll need square roots
import pygame.display
from pygame.locals import *



#from settings.rach_prelude_D import *
from settings.chopin_op24_2 import *
#from settings.beethoven_op7 import *
#from settings.beethoven_op81a import *
#from settings.scarlatti_K440 import *

pygame.init()
screen = pygame.display.set_mode((200, 200))
pygame.display.set_caption('Animation')
#background = pygame.Surface(screen.get_size())
#background.fill((255, 0, 0))


soundtrack = pyglet.media.Player()
soundtrack.queue(pyglet.media.load(WAV_FILE_ORIGINAL, streaming=False))
#soundtrack.play()

running = True
playing = False
while running:
    x = 1
    for event in pygame.event.get():
	if event.type == KEYDOWN:
	  running = False
    screen.fill((125,0,37))
    pygame.display.flip()
    if not playing:
      soundtrack.play()
      playing = True
  
#pygame.display.quit()
#pygame.quit()
sys.exit()

