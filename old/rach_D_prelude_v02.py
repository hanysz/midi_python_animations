from __future__ import division # so that a/b for integers evaluates as floating point
import pygame, sys, subprocess, os, time, mido
from pygame.locals import *
from moviepy.editor import *

MODE = 'play' # Display the animation on screen in real time
#MODE = 'save' # Save the output to a video file instead of displaying on screen

MIDI_FILE = '/home/alex/midi/python_animations/midi/2016-11-Rachmaninoff_prelude_D_v3.mid'
WAV_FILE_ORIGINAL = '/audio/2013-nov-concert/15-rachmaninoff.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 263 # length of the video file to be generated, in seconds

OUTPUT_FILE = '/home/alex/midi/python_animations/rachmaninoff-prelude-D-Nov2016.mp4'
FPS = 25 # frames per second for saved video output
AUDIO_OFFSET = 6.9 # number of seconds late to start the audio
MIDI_OFFSET = -1.1 # number of seconds to shift midi events by
TICKS_PER_SECOND = 960*2
# To do: figure out how to read this from the MIDI file!

LOWEST_NOTE = 21 # midi note number of the bottom of the screen
HIGHEST_NOTE = 108
ONSCREEN_TIME = 12 # number of seconds for a note to cross the screen
INNER_BRIGHTNESS = 0.4 # brightness of the middle of the note when lit up
FADEOUT_TIME = 1 # number of seconds for a note to stop being lit after it's stopped sounding

HEIGHT = 720
WIDTH = int(HEIGHT * 16/9)
NOTEHEIGHT  = HEIGHT / (HIGHEST_NOTE - LOWEST_NOTE + 1)

# set up pygame
pygame.init()

# set up the window
windowSurface = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
pygame.display.set_caption('Animation')

# set up some colours
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (0, 255, 255)
MAGENTA = (255, 0, 255)
CYAN = (255, 255, 0)

# List of colours to be used for different tracks of the MIDI file:
NOTE_COLOURS = (WHITE, GREEN, BLUE, YELLOW, MAGENTA, CYAN, RED)

NUM_COLOURS = len(NOTE_COLOURS)

def dimmer(colour, brightness):
  return(colour[0]*brightness, colour[1]*brightness, colour[2]*brightness)


class Note(object):
  __slots__ = ['note', 't0', 't1', 'vel', 'track', 'channel']
  
  def __str__(self): # Printable version of note for debutting
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
      filled = False
    elif t<self.t1:
      incol = dimmer(outcol, INNER_BRIGHTNESS)
    else:
      fade_fraction = 1-(t-self.t1)/FADEOUT_TIME
      incol = dimmer(outcol, INNER_BRIGHTNESS * fade_fraction)
    if t>=self.t0-ONSCREEN_TIME/2 and t<=self.t1+ONSCREEN_TIME/2:
      x = ((self.t0-t)/ONSCREEN_TIME + 0.5) * WIDTH
      y = (HIGHEST_NOTE - self.note)*NOTEHEIGHT
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

# Read the tracks in order from background to foreground.
# For the Rachmaninoff MIDI, I want to draw bass then descant then melody in that order
for tracknum in [3, 5, 4]:
  t = mid.tracks[tracknum]
  abstime = 0 # reset absolute time at the start of each track.
  # nb abstime is in ticks; we'll convert to seconds within the addTo... functions
  for e in t:
    abstime += e.time
    if isKeyDown(e):
      addToPending(e, abstime, tracknum)
    if isKeyUp(e):
      addToNotes(e, abstime)


# At this point we have an allnotes array and can start to animate it.
def make_frame(t):
    windowSurface.fill(BLACK)
    for n in allnotes:
      n.draw(t-MIDI_OFFSET)
    if MODE == 'save':
      # pymovie swaps the x and y coordinates, so we need to flip the surface back
      return pygame.surfarray.array3d(
        pygame.transform.rotate(
	  pygame.transform.flip(windowSurface, True, False), 90
	)
      )


if MODE == 'play':
  running = True
  audioPlaying = False
  while running:
    for event in pygame.event.get():
      if event.type == QUIT:
	running = False

    #pygame.draw.line(windowSurface, WHITE, (WIDTH/2,0), (WIDTH/2, HEIGHT))
    # Uncomment the line above to get a "now time" line drawn on the animation
    t = pygame.time.get_ticks()/1000
    if (not audioPlaying) and t > AUDIO_OFFSET:
      audioplayer = subprocess.Popen(["/usr/bin/aplay", WAV_FILE_ORIGINAL])
      audioPlaying = True
    make_frame(t)
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

  animation_clip = VideoClip(make_frame, duration=LENGTH)
  titles = TextClip(
    "Prelude in D major by Sergei Rachmaninoff\n\n" +
    "Performed by Alexander Hanysz\nLive recording, Pilgrim Church, Adelaide\n" +
    "10th November 2013",
    font='Segoe-Script-Regular', fontsize = 30, color = 'white'
  )
  titles = titles.set_pos('center').set_duration(7.5).fadein(3).fadeout(2.5)
  audio = AudioFileClip(WAV_FILE_TEMP)
  audio.set_start(AUDIO_OFFSET)
  animation_clip = animation_clip.set_audio(audio)
  video = CompositeVideoClip([animation_clip, titles])
  video.write_videofile(OUTPUT_FILE, fps=FPS,
    bitrate='2500k', audio_bitrate='320k')
  # clean up:
  os.system('rm '+WAV_FILE_TEMP)

