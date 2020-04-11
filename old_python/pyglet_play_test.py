from __future__ import division # so that a/b for integers evaluates as floating point
import pygame, pyglet, sys, subprocess, os, time, mido
from pygame.locals import *
from moviepy.editor import *
import math # we'll need square roots



#from settings.rach_prelude_D import *
#from settings.chopin_op24_2 import *
#from settings.beethoven_op7 import *
from settings.beethoven_op81a import *
#from settings.scarlatti_K440 import *

# For testing a short range
#START_TIME = 10
#AUDIO_OFFSET -= START_TIME
#MIDI_OFFSET -= START_TIME

HEIGHT = 720
#HEIGHT = 397 # for a fast cut of the video
WIDTH = int(HEIGHT * 16/9)

# set up some colours
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (0, 255, 255)
MAGENTA = (255, 0, 255)
CYAN = (255, 255, 0)



# Some variables to control display and changing of current time in "play" mode
show_osd = False
paused = False
seek_offset = 0
osd_font = pygame.font.SysFont(None, 48)
OSD_COLOUR = WHITE

# At this point we have an allnotes array and can start to animate it.
def make_frame(t):
    screen.fill(BLACK)
    if paused:
      pausetext = osd_font.render("I am paused!", True, OSD_COLOUR)
      pauserect = pausetext.get_rect()
      pauserect.x = 50
      pauserect.y = 100
      screen.blit(pausetext, pauserect)
    if show_osd:
      timetext = osd_font.render("%.1f" % (t-MIDI_OFFSET), True, OSD_COLOUR)
      textrect = timetext.get_rect()
      textrect.x = 0
      textrect.y = 0
      screen.blit(timetext, textrect)

# set up pygame
pygame.init()

# set up the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Animation')
background = pygame.Surface(screen.get_size())
background.fill(BLACK)

def seek(seek_time):
  global seek_offset
  seek_offset += seek_time
  global audioPlaying
  audioPlaying = False
  soundtrack.pause()
  global paused
  paused = False


running = True
audioPlaying = False
soundtrack = pyglet.media.Player()
soundtrack.queue(pyglet.media.load(WAV_FILE_ORIGINAL, streaming=False))
while running:
  for event in pygame.event.get():
    if event.type == QUIT:
      running = False
    if event.type == KEYDOWN:
      print("A key was pressed!")
      if event.key == pygame.K_q: # quit
	running = False
      if event.key == pygame.K_o: # toggle on-screen display
	show_osd =  not show_osd
      if event.key == pygame.K_RIGHT:
	seek(10)
      if event.key == pygame.K_LEFT:
	seek(-10)
      if event.key == pygame.K_UP:
	seek(60)
      if event.key == pygame.K_DOWN:
	seek(-60)
      if event.key == pygame.K_SPACE:
	paused = not paused
	if paused:
	  pause_time = t
	  audioPlaying = False
	  soundtrack.pause()
	else:
	  seek_offset -= t - pause_time
      if event.key == pygame.K_PERIOD and paused:
	# advance to next frame
	pause_time += 1/FPS


  t = pygame.time.get_ticks()/1000 + seek_offset
  if (not audioPlaying) and (not paused) and t > AUDIO_OFFSET:
    soundtrack.seek(t-AUDIO_OFFSET)
    print("Starting playback")
    soundtrack.play()
    audioPlaying = True
  if paused:
    make_frame(pause_time)
  else:
    make_frame(t)
  pygame.display.update()

pygame.display.quit()
pygame.quit()
sys.exit()
