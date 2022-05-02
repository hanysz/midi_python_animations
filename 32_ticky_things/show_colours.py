# display the colour of each voice, from left to right
# This file is much longer than it really needs to be,
# because hacking csd_to_video.py is quicker than making a standalone colour chart!

import sys
if len(sys.argv) != 3:
  sys.exit("Usage: python show_colours.py score.csd notelist.csv")
import pygame, cairo, subprocess, os, time, pandas
from pygame.locals import *
from moviepy.editor import *
from math import pi, sqrt

infilename = sys.argv[1]
metadatafilename = sys.argv[2]
if len(sys.argv) == 5:
  outfilename = sys.argv[4]

if not os.path.exists(metadatafilename):
  sys.exit(f"Error: input file {metadatafilename} does not exist")

if not os.path.exists(infilename):
  sys.exit(f"Error: input file {infilename} does not exist")

metadata = pandas.read_csv(metadatafilename)

from pygame.colordict import THECOLORS as COLOURS
colour_list = metadata['colour']
TICK_COLOURS = [COLOURS[c] for c in colour_list]

RADII = metadata['radius']
RING_WIDTH = 5
MARGIN = max(RADII)*2
BACKGROUND = COLOURS['black']
TEMPI = metadata['bpm']
MAX_TEMPO = max(TEMPI)
MIN_TEMPO = min(TEMPI)

HEIGHT=900
HEIGHT=600
WIDTH = int(HEIGHT * 16/9)
MIN_DURATION = 0.5 # shortest visual note

class Note(object):
  __slots__ = ['t0', 't1', 'voice', 'pan', 'predelay']
  # t0, t1 = start and finish times in seconds
  # voice = instrument number: use this to choose a colour
  # pan = stereo position: use this to choose x coordinate on the screen
  # predelay = reverb setting: use this to choose y coordinate
  
  def __str__(self): # Printable version of note for debugging
    return(f'time {self.t0} to {self.t1}, voice {self.voice} with pan {self.pan} and predelay {self.predelay}')


allnotes = []
with open(infilename) as infile:
  for line in infile:
    tokens = line.split()
    if len(tokens)==9 and tokens[0]=='i' and tokens[1]=='"playwave"':
      n=Note()
      n.t0=float(tokens[2])
      n.voice = int(tokens[4])-1 # csound counts from 1, python from 0
      duration = float(tokens[3])
      n.t1 = n.t0 + max(duration, MIN_DURATION)
      n.pan = float(tokens[6])
      n.predelay = float(tokens[8])*1000
      allnotes.append(n)


def draw_note(n, t):
  x = round((n.voice+0.5)/33*WIDTH)
  x = round(n.pan * WIDTH)
  y = round((MAX_TEMPO - TEMPI[n.voice])/(MAX_TEMPO-MIN_TEMPO)*(HEIGHT-2*MARGIN)) + MARGIN
  r = RADII[n.voice]
  ctx.arc(x, y, r, 0, pi*2)
  incol = [x/255 for x in TICK_COLOURS[n.voice]]
  ctx.set_source_rgb(incol[2], incol[1], incol[0])
  ctx.fill()

  ctx.select_font_face("Courier New")
  ctx.set_font_size(30)
  ctx.move_to(x+r,y)
  ctx.show_text(str(n.voice+1))

  if r>RING_WIDTH:
    ctx.arc(x, y, r-RING_WIDTH, 0, pi*2)
    ctx.set_source_rgb(0, 0, 0)
    ctx.fill()



def make_frame(t):
    ctx.set_source_rgb(BACKGROUND[2]/255.0, BACKGROUND[1]/255.0, BACKGROUND[0]/255.0)
    ctx.paint()
    for n in allnotes:
      draw_note(n, t)

    data = surface.get_data()
    image = pygame.image.frombuffer(data, (WIDTH, HEIGHT),"RGBA",)
    # nb pygame bug: surface is created as ARGB but we must write to it as RGBA
    # see https://github.com/pygobject/pycairo/issues/247
    screen.blit(image, (0,0))


# set up pygame and cairo
pygame.init()
window = pygame.display.set_mode( (WIDTH, HEIGHT) )
screen = pygame.display.get_surface()
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)
ctx.set_operator(cairo.OPERATOR_OVER)

pygame.display.set_caption('Animation')

running = True
while running:
  for event in pygame.event.get():
    if event.type == QUIT:
      running = False

  t = pygame.time.get_ticks()/1000
  make_frame(t)
  pygame.display.update()

pygame.display.quit()
pygame.quit()
sys.exit()

