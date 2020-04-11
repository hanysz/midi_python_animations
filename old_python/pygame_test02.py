from __future__ import division # so that a/b for integers evaluates as floating point
import pygame, sys, subprocess, time, mido
from pygame.locals import *
import moviepy.editor as mpy

fps = 15

# set up pygame
pygame.init()

# set up the window
WINDOWWIDTH = 600
WINDOWHEIGHT = 1000
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('Animation')

# set up the colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


# Read and parse the MIDI file
mid = mido.MidiFile(sys.argv[1])
ticks_per_second = 384 * 2
# To do: read this from the MIDI file
# Need to look for two message types:
#  set_tempo with tempo in microseconds per crotchet
#  e.g. 500000 is 120bpm
#  time_signature with clocks_per_click

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
    if self.track % 3 == 0:
      col = RED
    elif self.track % 3 == 1:
      col = BLUE
    else:
      col = GREEN
    if t>=self.t0 and t<=self.t1:
      #x = self.vel/128*350 + (t - self.t0)*200
      x = (self.t1 - t) * WINDOWWIDTH / 2
      #y = (self.note/30-1)*350
      y = (127 - self.note)/127*WINDOWHEIGHT
      rect = pygame.Rect(x, y, 100, 5)
      pygame.draw.rect(windowSurface, col, rect)

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
  n.t0 = t/ticks_per_second
  n.vel = e.velocity
  n.track = trk
  n.channel = e.channel
  pending[n.note] = n

def addToNotes(e, t):
  note = e.note
  if note in pending:
    n = pending[note]
    n.t1 = t/ticks_per_second
    allnotes.append(n)
    del pending[note]

tracknum = 0
for t in mid.tracks:
  tracknum+=1
  abstime = 0
  for e in t:
    abstime += e.time
    if isKeyDown(e):
      addToPending(e, abstime, tracknum)
    if isKeyUp(e):
      addToNotes(e, abstime)

# At this point we have an allnotes array and can start to animate it.

midi_play_command = "/usr/bin/timidity " + sys.argv[1]
#subprocess.Popen([sys.executable, midi_play_command])
subprocess.Popen(["timidity", sys.argv[1]])

t = 0
delta_t = 1/fps
running = True
while running:
    # check for the QUIT event
    for event in pygame.event.get():
        if event.type == QUIT:
	    running = False

    # draw the black background onto the surface
    windowSurface.fill(BLACK)
    
    for n in allnotes:
      n.draw(t)
    pygame.display.update()
    time.sleep(delta_t)
    t += delta_t

pygame.display.quit()
pygame.quit()
sys.exit()
