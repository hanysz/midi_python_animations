from __future__ import division # so that a/b for integers evaluates as floating point
import pygame, pyglet, sys, subprocess, os, time, mido
from pygame.locals import *
from moviepy.editor import *
import math # we'll need square roots


MODE = 'play' # Display the animation on screen in real time
#MODE = 'save' # Save the output to a video file instead of displaying on screen

#from settings.rach_prelude_D import *
from settings.chopin_op24_2 import *
#from settings.beethoven_op7 import *
#from settings.beethoven_op81a import *
#from settings.scarlatti_K440 import *

# For testing a short range
START_TIME = 0
AUDIO_OFFSET -= START_TIME
MIDI_OFFSET -= START_TIME

# compensate for playback delay
AUDIO_OFFSET += 0.3

FPS = 25 # frames per second for saved video output
#FPS = 15 # for a fast cut of the video

HEIGHT = 720
#HEIGHT = 397 # for a fast cut of the video
WIDTH = int(HEIGHT * 16/9)
CENTRE = (WIDTH/2, HEIGHT/2)

LOWEST_NOTE = 25 # midi note number of the bottom of the screen
HIGHEST_NOTE = 108
NOTE_HEIGHT = HEIGHT / (HIGHEST_NOTE - LOWEST_NOTE + 1)

# set up some colours
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (0, 255, 255)
MAGENTA = (255, 0, 255)
CYAN = (255, 255, 0)
# The above is unnecessary,
#e.g. use pygame.Color('black') instead of BLACK
#Colour chart at https://sites.google.com/site/meticulosslacker/pygame-thecolors

# List of colours to be used for different tracks of the MIDI file:
NOTE_COLOURS = (WHITE, GREEN, BLUE, YELLOW, MAGENTA, CYAN, RED)
NUM_COLOURS = len(NOTE_COLOURS)

BG_COLOUR = pygame.Color('darkgray')
FG_COLOUR = pygame.Color('orange')
#BACKGROUND = pygame.Color('indigo') # name not recognised
BACKGROUND = pygame.Color('#4b0082')



# Some variables to control display and changing of current time in "play" mode
show_osd = False
paused = False
seek_offset = 0
osd_font = pygame.font.SysFont(None, 48)
OSD_COLOUR = WHITE



def dimmer(colour, brightness):
  return(colour[0]*brightness, colour[1]*brightness, colour[2]*brightness)


class Note(object):
  __slots__ = ['note', 't0', 't1', 'vel', 'track', 'channel']
  # note = MIDI note number
  # t0, t1 = start and finish times in seconds
  # vel = MIDI velocity
  # track = track number
  # channel = channel number
  
  def __str__(self): # Printable version of note for debugging
    answer = 'Note number ' + str(self.note)
    answer += ' time ' + str(self.t0) + '-' + str(self.t1)
    answer += '; vel ' + str(self.vel) + ', track ' + str(self.track)
    answer += ', ch' + str(self.channel)
    return answer

def rescale (r, z):
  # r is a rectangle in the plane of the screen
  # rescale so that it's z units away
  # The vanishing point is the centre of the screen: global variable CENTRE
  scale = (5-z) / z # Not quite right, needs to be fixed...
  r.width = r.width * scale
  r.height = r.height * scale
  return r

def draw_note(n, t):
  # Draw the rectangle for note n at time t.
  # If n is actually playing at time t, draw in the foreground,
  # else background.
  #if t<n.t0 or t>n.t1:
    #return
  x0 = n.t0/LENGTH*WIDTH
  x1 = n.t1/LENGTH*WIDTH
  y0 = (HIGHEST_NOTE - n.note) / (HIGHEST_NOTE - LOWEST_NOTE + 1) * HEIGHT
  scale = 1
  note = pygame.Rect(x0, y0, x1-x0, NOTE_HEIGHT)
 
  BIG = 30
  GROW_TIME = 0.6
  GPS = (BIG-1)/GROW_TIME # GPS = growth per second
  col = BG_COLOUR
  if t>n.t0 and t<n.t1:
    col = FG_COLOUR
    scale = BIG
  elif t < n.t0 and t > n.t0-GROW_TIME:
    scale = (t - n.t0)*GPS + BIG
  elif t > n.t1 and t < n.t1+GROW_TIME:
    scale = BIG - (t - n.t1)*GPS
  #pygame.draw.rect(screen, col, rescale(note, z))
  #s = (1-z) * 4 + 1
  pygame.draw.rect(screen, col, note.inflate(scale, scale))





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

key_times = [[] for _ in range(128)]
# This is a list of 128 empty lists, one for each MIDI note number.
# As we parse the files, we'll store the note-on times for each note in the corresponding list.
key_indices = [0]*128
# This is for playback: each key_indices element will be updated to point to the most recent key_times element

def addToPending(e, t, trk):
  n = Note()
  n.note = e.note
  n.t0 = t
  n.vel = e.velocity
  n.track = trk
  n.channel = e.channel
  pending[n.note] = n
  key_times[n.note].append(t)

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

for l in key_times:
  l.sort()

# At this point we have an allnotes array and can start to animate it.
def make_frame(t):
    screen.fill(BLACK)
    for n in allnotes:
      draw_note(n, t-MIDI_OFFSET)
    if show_osd:
      timetext = osd_font.render("%.1f" % (t-MIDI_OFFSET), True, OSD_COLOUR)
      textrect = timetext.get_rect()
      textrect.x = 0
      textrect.y = 0
      screen.blit(timetext, textrect)
    if MODE == 'save':
      # pymovie swaps the x and y coordinates, so we need to flip the surface back
      return pygame.surfarray.array3d(
        pygame.transform.rotate(
	  pygame.transform.flip(screen, True, False), 90
	)
      )

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
  if seek_time < 0:
    global key_indices
    key_indices = [0]*128
  global paused
  paused = False


if MODE == 'play':
  running = True
  audioPlaying = False
  soundtrack = pyglet.media.Player()
  soundtrack.queue(pyglet.media.load(WAV_FILE_ORIGINAL, streaming=False))
  while running:
    for event in pygame.event.get():
      if event.type == QUIT:
	running = False
      if event.type == KEYDOWN:
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
      soundtrack.play()
      audioPlaying = True
    if paused:
      make_frame(pause_time)
    else:
      make_frame(t)
    pygame.display.flip()

  pygame.display.quit()
  pygame.quit()
  sys.exit()

else:
  # Edit the audio track: add silence at start and trim to the correct length
  os.system('/usr/bin/sox '+ WAV_FILE_ORIGINAL + ' ' + WAV_FILE_TEMP +
  	    ' pad '+str(AUDIO_OFFSET) + ' trim 0 ' + str(LENGTH)
	   )

  animation_clip = VideoClip(make_frame, duration=LENGTH)
  titles = TextClip(TITLE_TEXT,
    font='Segoe-Script-Regular', fontsize = 30, color = 'white'
    #font='Segoe-Script-Regular', fontsize = 20, color = 'white'
  )
  titles = titles.set_pos('center').set_duration(8.5).fadein(3).fadeout(2.5)
  #titles = titles.set_pos('center').set_duration(5).fadein(1).fadeout(1)
  audio = AudioFileClip(WAV_FILE_TEMP)
  audio.set_start(AUDIO_OFFSET)
  animation_clip = animation_clip.set_audio(audio)
  video = CompositeVideoClip([animation_clip, titles])
  video.write_videofile(OUTPUT_FILE, fps=FPS,
    bitrate='2500k', audio_bitrate='320k')
  # clean up:
  os.system('rm '+WAV_FILE_TEMP)

