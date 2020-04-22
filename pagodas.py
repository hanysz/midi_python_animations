from __future__ import division # so that a/b for integers evaluates as floating point
import pygame, sys, subprocess, os, time, mido
from pygame.locals import *
from moviepy.editor import *

#MODE = 'play' # Display the animation on screen in real time
MODE = 'save' # Save the output to a video file instead of displaying on screen

from settings.debussy_pagodas import *

FPS = 25 # frames per second for saved video output

LOWEST_NOTE = 14 # midi note number of the left of the screen
#  nb bottom of piano is 21, choose smaller number so that bass is inside the screen
HIGHEST_NOTE = 104 # top of piano is 108 but we don't need it
MIN_VEL = -5 # velocity of notes at the bottom of the screen: choose a negative number so that velocity=0 isn't actually at the bottom
MAX_VEL = 140 # sim choose something over 128
XDRIFT_SPEED = -18 # how fast the current carries the ripples to the right
YDRIFT_SPEED = -6
RIPPLE_SPEED = 30 # how fast the note ripples outwards, in pixels per second
FADEOUT_TIME = 8 # number of seconds for a note to disappear after it's stopped sounding
SPLASH_RADIUS = 5 # width in pixels of the solid circle when a note first appears
SPLASH_TIME = 1.2 # how long the solid circle persists

HEIGHT = 720
WIDTH = int(HEIGHT * 16/9)


# set up some colours
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARKRED = (170, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
LIGHTBLUE = (140, 255, 255)
MAGENTA = (255, 0, 255)
PURPLE = (140, 0, 140)
YELLOW = (255, 255, 0)

BACKGROUND = (80, 160, 200)

# List of colours to be used for different tracks of the MIDI file:
#NOTE_COLOURS = (GREEN, WHITE, YELLOW, BLUE, PURPLE, DARKRED, BLACK)
NOTE_COLOURS = (GREEN, WHITE, YELLOW, LIGHTBLUE, BLUE, DARKRED, BLACK)

NUM_COLOURS = len(NOTE_COLOURS)

def colour_diff(c1, c2):
  # c1 and c2 are triples:
  # return max(c1-c2, 0)
  return (max(c1[0]-c2[0], 0), max(c1[1]-c2[1], 0), max(c1[2]-c2[2], 0))

ADD_COLOURS = [colour_diff(c, BACKGROUND) for c in NOTE_COLOURS]
SUB_COLOURS = [colour_diff(BACKGROUND, c) for c in NOTE_COLOURS]

def dimmer(colour, brightness):
  return(colour[0]*brightness, colour[1]*brightness, colour[2]*brightness)


class Note(object):
  __slots__ = ['note', 't0', 't1', 'vel', 'track', 'channel']
  # note = MIDI note number
  # t0, t1 = start and finish times in seconds
  # vel = MIDI velocity
  # track = track number
  # channel = channel number
  
  def __str__(self): # Printable version of note for debutting
    answer = 'Note number ' + str(self.note)
    answer += ' time ' + str(self.t0) + '-' + str(self.t1)
    answer += '; vel ' + str(self.vel) + ', track ' + str(self.track)
    answer += ', ch' + str(self.channel)
    return answer

def draw_bubble(n, t):
  # Draw the note n at time t as a circle
  fadeout_time = FADEOUT_TIME
  ripple_speed = RIPPLE_SPEED
  splash_radius = SPLASH_RADIUS
  splash_time = SPLASH_TIME
  if n.track == 5: # bass gets special treatment for Debussy
    ripple_speed = 15 # how fast the note ripples outwards, in pixels per second
    fadeout_time = 12 # number of seconds for a note to disappear after it's stopped sounding
    splash_radius = 6 # width in pixels of the solid circle when a note first appears
    splash_time = 3 # how long the solid circle persists
  appear_time = n.t0
  vanish_time = n.t1 + fadeout_time
  outline_fade = 1

  if t<appear_time or t>vanish_time:
    return
  elif t>n.t1:
    outline_fade = (1 - (t-n.t1) / (vanish_time - n.t1))**2
  else:
    outline_fade = 1
  addcol = ADD_COLOURS[n.track]
  addcol = dimmer(addcol, outline_fade)
  subcol = SUB_COLOURS[n.track]
  subcol = dimmer(subcol, outline_fade)


  splash = (t <= appear_time + splash_time)

  x = (n.note - LOWEST_NOTE)/(HIGHEST_NOTE-LOWEST_NOTE)*WIDTH
  y = (MAX_VEL - n.vel)/(MAX_VEL - MIN_VEL)*HEIGHT
  delta = int((t-n.t0)*ripple_speed) 
  radius = delta + splash_radius

  epsilon = x - int(x)
  rect = pygame.Rect(epsilon, epsilon, radius*2, radius*2)
  tempSurface = pygame.Surface((radius*2+1, radius*2+1))
  if splash:
    splash_rect = pygame.Rect(epsilon+delta, epsilon+delta, splash_radius*2,              splash_radius*2)
  xdrift = int((t-n.t0)*XDRIFT_SPEED)
  ydrift = int((t-n.t0)*YDRIFT_SPEED)

  if splash:
    pygame.draw.ellipse(tempSurface, addcol, splash_rect)
  pygame.draw.ellipse(tempSurface, addcol, rect, 1)
  screen.blit(tempSurface, (int(x)-radius+xdrift, int(y)-radius+ydrift), None, pygame.    BLEND_ADD)

  if splash:
    pygame.draw.ellipse(tempSurface, subcol, splash_rect)
  pygame.draw.ellipse(tempSurface, subcol, rect, 1)
  screen.blit(tempSurface, (int(x)-radius+xdrift, int(y)-radius+ydrift), None, pygame.    BLEND_SUB)




# Read and parse the MIDI file
mid = mido.MidiFile(MIDI_FILE)
PPQN = mid.ticks_per_beat

def isKeyDown(e):
  # e is a MIDI event.
  return (e.type == 'note_on' and e.velocity > 0)
  # relying on short circuit evaluation!

def isKeyUp(e):
  return (e.type == 'note_off' or (e.type == 'note_on' and e.velocity == 0))

# Step through the file and create notes
allnotes = []
# Keep a pending list:
pending = {}
# When a note-on event comes up, create a pending note with t0 at current time but no t1
#  key = the note value
# When there's note-off, or note-on with zero velocity
#  look for a matching item in the pending list and move it to allnotes

def addToPending(e, t, trk):
  n = Note()
  n.note = e.note
  n.t0 = t
  n.vel = e.velocity
  n.track = trk
  n.channel = e.channel
  pending[n.note] = n

def addToNotes(e, t):
  note = e.note
  if note in pending:
    n = pending[note]
    n.t1 = t
    allnotes.append(n)
    del pending[note]

# Read the tracks in order from background to foreground.
seconds_per_tick = 0.5 / PPQN # assume tempo of 120 beats per minute until we find out otherwise
for tracknum in [0] + TRACK_ORDER: # always include track 0 because it's the tempo map!
# nb reading the tempo still isn't quite right, as it will only use the last tempo from track 0; it won't handle multiple tempos in one piece.
  t = mid.tracks[tracknum]
  abstime = 0 # reset absolute time at the start of each track.
  # nb abstime is in ticks
  for e in t:
    abstime += e.time
    if e.type == 'set_tempo':
      seconds_per_tick = e.tempo / PPQN / 1000000
    if isKeyDown(e):
      addToPending(e, abstime * seconds_per_tick, tracknum)
    if isKeyUp(e):
      addToNotes(e, abstime * seconds_per_tick)


# At this point we have an allnotes array and can start to animate it.
def make_frame(t, draw_function):
    screen.fill(BACKGROUND)
    for n in allnotes:
      draw_function(n, t-MIDI_OFFSET)
    if MODE == 'save':
      # pymovie swaps the x and y coordinates, so we need to flip the surface back
      return pygame.surfarray.array3d(
        pygame.transform.rotate(
	  pygame.transform.flip(screen, True, False), 90
	)
      )
    #pygame.draw.line(screen, WHITE, (WIDTH/2,0), (WIDTH/2, HEIGHT))
    # Uncomment the line above to get a "now time" line drawn on the animation

# set up pygame
pygame.init()

# set up the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Animation')
background = pygame.Surface(screen.get_size())
background.fill(BLACK)

if MODE == 'play':
  running = True
  audioPlaying = False
  while running:
    for event in pygame.event.get():
      if event.type == QUIT:
	running = False

    t = pygame.time.get_ticks()/1000
    if (not audioPlaying) and t > AUDIO_OFFSET:
      audioplayer = subprocess.Popen(["/usr/bin/aplay", WAV_FILE_ORIGINAL])
      audioPlaying = True
    make_frame(t, draw_bubble)
    pygame.display.update()

  audioplayer.kill()
  pygame.display.quit()
  pygame.quit()
  sys.exit()

else:
  # Edit the audio track: add silence at start and trim to the correct length
  os.system('/usr/bin/sox '+ WAV_FILE_ORIGINAL + ' ' + WAV_FILE_TEMP +
  	    ' pad '+str(AUDIO_OFFSET) + ' trim 0 ' + str(LENGTH)
	   )

  animation_clip = VideoClip(lambda t: make_frame(t, draw_bubble),
                             duration=LENGTH)
  titles = TextClip(
    "Pagodas from Estampes (Engravings) by Debussy\n\n" +
    "Performed by Alexander Hanysz\n" +
    "Recorded in Grainger Studio, Adelaide\n" +
    "May 2008\n" +
    "Audio recorded and produced by Haig Burnell",
    font='Segoe-Script', fontsize = 30, color = 'white'
  )
  titles = titles.set_pos('center').set_duration(7.5).fadein(3, BACKGROUND).fadeout(2.5, BACKGROUND)
  audio = AudioFileClip(WAV_FILE_TEMP)
  audio.set_start(AUDIO_OFFSET)
  animation_clip = animation_clip.set_audio(audio)
  video = CompositeVideoClip([animation_clip, titles])
  video.write_videofile(OUTPUT_FILE, fps=FPS,
    bitrate='2500k', audio_bitrate='320k')
  # clean up:
  os.system('rm '+WAV_FILE_TEMP)

