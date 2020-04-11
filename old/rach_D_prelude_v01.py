from __future__ import division # so that a/b for integers evaluates as floating point
import pygame, sys, subprocess, time, mido
from pygame.locals import *
import moviepy.editor as mpy

MIDI_FILE = '/home/alex/midi/python_animations/midi/d.mid'
WAV_FILE = '/audio/2013-nov-concert/15-rachmaninoff.wav'
OUTPUT_FILE = '/home/alex/midi/python_animations/rachmaninoff-prelude-D-Nov2016.mp4'
AUDIO_OFFSET = 8 # number of seconds late to start the audio
MIDI_OFFSET = -4.1 # number of seconds to shift midi events by
TICKS_PER_SECOND = 960*2
# To do: read this from the MIDI file
# Need to look for two message types:
#  set_tempo with tempo in microseconds per crotchet
#  e.g. 500000 is 120bpm
#  time_signature with clocks_per_click
# Except that the "divisions" shown by Timidity don't agree with those numbers...
#fps = 25  # Not used here, try delta time via system clock instead

LOWEST_NOTE = 21 # midi note number of the bottom of the screen
HIGHEST_NOTE = 108
ONSCREEN_TIME = 12 # number of seconds for a note to cross the screen
INNER_BRIGHTNESS = 0.4 # brightness of the middle of the note when lit up
FADEOUT_TIME = 1 # number of seconds for a note to stop being lit after it's stopped sounding

WINDOWWIDTH = 1600
WINDOWHEIGHT = 900

NOTEHEIGHT  = WINDOWHEIGHT / (HIGHEST_NOTE - LOWEST_NOTE + 1)

# set up pygame
pygame.init()

# set up the window
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('Animation')

# set up the colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (0, 255, 255)
MAGENTA = (255, 0, 255)
CYAN = (255, 255, 0)

NOTE_COLOURS = (WHITE, GREEN, BLUE, YELLOW, MAGENTA, CYAN, RED)
NUM_COLOURS = len(NOTE_COLOURS)

def dimmer(colour, brightness):
  return(colour[0]*brightness, colour[1]*brightness, colour[2]*brightness)


class Note(object):
  #def _init_(self, note, t0, t1, vel, track, channel):
  __slots__ = ['note', 't0', 't1', 'vel', 'track', 'channel']
  
  def __str__(self):
    answer = 'Note number ' + str(self.note)
    answer += ' time ' + str(self.t0) + '-' + str(self.t1)
    answer += '; vel ' + str(self.vel) + ', track ' + str(self.track)
    answer += ', ch' + str(self.channel)
    return answer

  def draw(self, t):
    # Draw the note at time t
    appear_time = self.t0 - ONSCREEN_TIME/2
    vanish_time = self.t0 + ONSCREEN_TIME/2
    outline_fade = 1

    if t<appear_time or t>vanish_time:
      return
    if t<self.t0:
      outline_fade = (t-appear_time) / (self.t0-appear_time)
    elif t>self.t1:
      outline_fade = 1 - (t-self.t1) / (vanish_time - self.t1)
    else:
      outline_fade = 1
    outcol = NOTE_COLOURS[self.track % NUM_COLOURS]
    outcol = dimmer(outcol, outline_fade)

    filled = True
    if t<self.t0 or t>self.t1+FADEOUT_TIME:
      #incol = BLACK
      filled = False
    elif t<self.t1:
      incol = dimmer(outcol, INNER_BRIGHTNESS)
    else:
      fade_fraction = 1-(t-self.t1)/FADEOUT_TIME
      incol = dimmer(outcol, INNER_BRIGHTNESS * fade_fraction)
    if t>=self.t0-ONSCREEN_TIME/2 and t<=self.t1+ONSCREEN_TIME/2:
      x = ((self.t0-t)/ONSCREEN_TIME + 0.5) * WINDOWWIDTH
      y = (HIGHEST_NOTE - self.note)*NOTEHEIGHT
      #rect = pygame.Rect(x, y, WINDOWWIDTH*(self.t1-self.t0)/ONSCREEN_TIME, NOTEHEIGHT)
      #pygame.draw.rect(windowSurface, incol, rect)
      #pygame.draw.rect(windowSurface, outcol, rect, 1)
      #pygame.gfxdraw.rectangle(windowSurface, rect, outcol)
      #pygame.gfxdraw.box(windowSurface, rect, incol)
      radius = self.vel
      #centre = (int(x), int(y))
      #pygame.draw.circle(windowSurface, incol, centre, radius)
      #pygame.draw.circle(windowSurface, outcol, centre, radius, 1)
      # Circles don't work well: integer rounding means they wobble!
      rect = pygame.Rect(x-radius/2, y-radius/2, radius, radius)
      if filled:
	pygame.draw.ellipse(windowSurface, incol, rect)
      pygame.draw.ellipse(windowSurface, outcol, rect, 1)


# Read and parse the MIDI file
mid = mido.MidiFile(MIDI_FILE)

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
# use del(pending[N]) to delete something

def addToPending(e, t, trk):
  n = Note()
  n.note = e.note
  n.t0 = t/TICKS_PER_SECOND
  n.vel = e.velocity
  n.track = trk
  n.channel = e.channel
  pending[n.note] = n

def addToNotes(e, t):
  note = e.note
  if note in pending:
    n = pending[note]
    n.t1 = t/TICKS_PER_SECOND
    allnotes.append(n)
    del pending[note]

tracknum = 0
#for t in mid.tracks:
for tracknum in [3, 5, 4]:
# For the Rachmaninoff MIDI, want to draw bass then descant then melody in that order
  t = mid.tracks[tracknum]
  #tracknum+=1
  abstime = 0
  for e in t:
    abstime += e.time
    if isKeyDown(e):
      addToPending(e, abstime, tracknum)
    if isKeyUp(e):
      addToNotes(e, abstime)

# At this point we have an allnotes array and can start to animate it.

#midi_play_command = "/usr/bin/timidity " + sys.argv[1]
#subprocess.Popen([sys.executable, midi_play_command])
#midiplayer = subprocess.Popen(["timidity", sys.argv[1]])

#t = 0
#delta_t = 1/fps
running = True
audioPlaying = False
while running:
    # check for the QUIT event
    for event in pygame.event.get():
        if event.type == QUIT:
	    running = False

    # draw the black background onto the surface
    windowSurface.fill(BLACK)
    
    #pygame.draw.line(windowSurface, WHITE, (WINDOWWIDTH/2,0), (WINDOWWIDTH/2, WINDOWHEIGHT))
    t = pygame.time.get_ticks()/1000 - MIDI_OFFSET
    if (not audioPlaying) and t > AUDIO_OFFSET:
      audioplayer = subprocess.Popen(["/usr/bin/aplay", WAV_FILE])
      audioPlaying = True
    for n in allnotes:
      n.draw(t)
    pygame.display.update()
    #time.sleep(delta_t)
    #t += delta_t

audioplayer.kill()
pygame.display.quit()
pygame.quit()
sys.exit()
