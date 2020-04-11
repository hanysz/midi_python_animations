from __future__ import division # so that a/b for integers evaluates as floating point
import pygame, sys, subprocess, os, time, mido
from pygame.locals import *
from moviepy.editor import *

MODE = 'play' # Display the animation on screen in real time
#MODE = 'save' # Save the output to a video file instead of displaying on screen

MIDI_FILE = '/home/alex/midi/python_animations/2016-11-Rachmaninoff_prelude_D_v3.mid'
WAV_FILE_ORIGINAL = '/audio/2013-nov-concert/15-rachmaninoff.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 263 # length of the video file to be generated, in seconds
AUDIO_OFFSET = 6.9 # number of seconds late to start the audio
MIDI_OFFSET = -1.1 # number of seconds to shift midi events by
TRACK_ORDER = [3, 5, 4]
# For the Rachmaninoff MIDI, I want to draw bass then descant then melody in that order

MIDI_FILE = '/home/alex/midi/python_animations/Beethoven_op_7_I.mid'
WAV_FILE_ORIGINAL = '/home/alex/midi/python_animations/Beethoven_op_7_I.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 30 # length of the video file to be generated, in seconds
AUDIO_OFFSET = 0
MIDI_OFFSET = 0.3
TRACK_ORDER = [0]

MIDI_FILE = '/home/alex/midi/python_animations/chopin.mid'
WAV_FILE_ORIGINAL = '/home/alex/midi/python_animations/chopin.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 263 # length of the video file to be generated, in seconds
AUDIO_OFFSET = 0 # number of seconds late to start the audio
MIDI_OFFSET = 0.2 # number of seconds to shift midi events by
TRACK_ORDER = [1, 2, 3]


OUTPUT_FILE = '/home/alex/midi/python_animations/rachmaninoff-prelude-D-Nov2016.mp4'
FPS = 25 # frames per second for saved video output

LOWEST_NOTE = 21 # midi note number of the bottom of the screen
HIGHEST_NOTE = 108
ONSCREEN_TIME = 12 # number of seconds for a note to cross the screen
INNER_BRIGHTNESS = 0.4 # brightness of the middle of the note when lit up
FADEOUT_TIME = 1 # number of seconds for a note to stop being lit after it's stopped sounding
LINEWIDTH = 1 # thickness of the circle outline in pixels
# nb with width>2 there's obvious cropping at the bottom and right of each note:
# not sure why, maybe a pygame bug??

HEIGHT = 720
WIDTH = int(HEIGHT * 16/9)
NOTEHEIGHT  = HEIGHT / (HIGHEST_NOTE - LOWEST_NOTE + 1)


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
  appear_time = n.t0 - ONSCREEN_TIME/2
  vanish_time = n.t0 + ONSCREEN_TIME/2
  outline_fade = 1

  if t<appear_time or t>vanish_time:
    return
  if t<n.t0:
    outline_fade = (t-appear_time) / (n.t0-appear_time)
  elif t>n.t1:
    outline_fade = 1 - (t-n.t1) / (vanish_time - n.t1)
  else:
    outline_fade = 1
  outcol = NOTE_COLOURS[n.track % NUM_COLOURS]
  outcol = dimmer(outcol, outline_fade)

  filled = True
  if t<n.t0 or t>n.t1+FADEOUT_TIME:
    filled = False
  elif t<n.t1:
    incol = dimmer(outcol, INNER_BRIGHTNESS)
  else:
    fade_fraction = 1-(t-n.t1)/FADEOUT_TIME
    incol = dimmer(outcol, INNER_BRIGHTNESS * fade_fraction)
  if t>=n.t0-ONSCREEN_TIME/2 and t<=n.t1+ONSCREEN_TIME/2:
    x = ((n.t0-t)/ONSCREEN_TIME + 0.5) * WIDTH
    y = (HIGHEST_NOTE - n.note)*NOTEHEIGHT
    radius = int(n.vel/2)
    #centre = (int(x), int(y))
    #pygame.draw.circle(screen, incol, centre, radius)
    #pygame.draw.circle(screen, outcol, centre, radius, 1)
    # Circles don't work well: integer rounding means they wobble!

    #rect = pygame.Rect(x-radius/2, y-radius/2, radius, radius)
    #if filled:
      #pygame.draw.ellipse(screen, incol, rect)
    #pygame.draw.ellipse(screen, outcol, rect, LINEWIDTH)

    epsilon = x - int(x)
    rect = pygame.Rect(epsilon+LINEWIDTH, epsilon+LINEWIDTH, radius*2+(LINEWIDTH-1)*2, radius*2+(LINEWIDTH-1)*2)
    tempSurface = pygame.Surface((radius*2+LINEWIDTH*2-1, radius*2+LINEWIDTH*2-1))
    if filled:
      pygame.draw.ellipse(tempSurface, incol, rect)
    pygame.draw.ellipse(tempSurface, outcol, rect, min(LINEWIDTH, radius))
    screen.blit(tempSurface, (int(x)-radius-LINEWIDTH, int(y)-radius-LINEWIDTH), None, pygame.BLEND_ADD)



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
for tracknum in TRACK_ORDER:
  t = mid.tracks[tracknum]
  abstime = 0 # reset absolute time at the start of each track.
  # nb abstime is in ticks
  seconds_per_tick = 0.5 / PPQN # assume tempo of 120 beats per minute until we find out otherwise
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
    screen.fill(BLACK)
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

