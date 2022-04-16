from __future__ import division # so that a/b for integers evaluates as floating point
import pygame, cairo, sys, subprocess, os, time, mido
import common_functions
from pygame.locals import *
from moviepy.editor import *
import math # we'll need square roots

MODE = 'play' # Display the animation on screen in real time
MODE = 'save' # Save the output to a video file instead of displaying on screen

#from settings.rach_prelude_D import *
#from settings.chopin_op24_2 import *
#from settings.beethoven_op7 import *
#from settings.beethoven_op81a import *
#from settings.scarlatti_K440 import *
#from settings.short import *
#from settings.scriabin_op74_2 import *
from settings.bach_WTC_II_C import *
#from settings.bach_WTC_II_Bflatmin import *


FPS = 30 # frames per second for saved video output
#FPS = 15 # for a fast cut of the video

HEIGHT = 1080
#HEIGHT = 397 # for a fast cut of the video
WIDTH = int(HEIGHT * 16/9)
TITLE_FONT_SIZE = 45 # recommended: 45 if HEIGHT=1080, or 30 if 720


LOWEST_NOTE = 25 # midi note number of the left of the screen
HIGHEST_NOTE = 108
ACCEL = 300 # force of gravity in pixels/sec/sec
KEY_HEIGHT = round(HEIGHT/3) # how far the top of the "keyboard" is from the bottom of the screen
KEY_SPACE = round(HEIGHT/6)  # size of blank space below the "keyboard"
MIN_BOUNCE_HEIGHT = 30 # balls bounce at least this high even for rapid repeated notes
FADEOUT_TIME = 0.13 # time for note to fade to black after note-off


KEY_WIDTH = WIDTH / (HIGHEST_NOTE - LOWEST_NOTE + 1)

# Calculate time for a ball to fall from the very top of the screen to the bottom
T_MAX = math.sqrt(2*(HEIGHT - KEY_HEIGHT)/ACCEL)
# Calculate the duration of a minimum height bounce under normal gravity
T_MIN = math.sqrt(2*MIN_BOUNCE_HEIGHT/ACCEL)


# set up some colours
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (0, 255, 255)
MAGENTA = (255, 0, 255)
CYAN = (255, 255, 0)


def dimmer(colour, brightness):
  return(colour[0]*brightness, colour[1]*brightness, colour[2]*brightness)

def vel_to_colour_old(v):
  # v is a note-on velocity (0 to 127)
  # return the colour we want for that velocity
  red = max(round((v-50)*3.3), 0)
  green = round((128-v)/2)
  blue = round(v*1.8) + 20
  return (red, green, blue)

def vel_to_colour(v):
  brightness = round(v*1.8) + 26
  red = brightness if brightness < 50 else 50 + round((brightness-50)*0.6)
  green = brightness if brightness < 50 else 50 + round((brightness-50)*0.6)
  blue = brightness
  return(red, green, blue)

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

def draw_key(n, t):
  # If note n is playing at time t, then light up the corresponding key
  if t<n.t0 or t>n.t1 + FADEOUT_TIME:
    return
  col = vel_to_colour(n.vel)
  if t>n.t1:
    col = dimmer(col, 1-((t-n.t1)/FADEOUT_TIME))
  ctx.rectangle((n.note - LOWEST_NOTE)*KEY_WIDTH, HEIGHT-KEY_HEIGHT,
                    KEY_WIDTH, KEY_HEIGHT-KEY_SPACE)
  ctx.set_source_rgb(col[2]/255, col[1]/255, col[0]/255)
  ctx.fill()


def draw_ball(trk, t):
  # Draw the note for track trk at time t as a circle

  # First, find the notes immediately before and after time t in track trk
  # edge cases:
  #   if t is before the first note, then we want n_before is None, n_after = 1st note
  #   if t is after the last note, then n_before = last note, n_after is None
  n_before, n_after = None, None
  found = False
  for n in allnotes[trk]:
    if n.t0 >= t:
      n_after = n
      # previous iteration got the note before, so it's OK to stop now
      break
    n_before = n
  if n_before is None:
    n_after = allnotes[trk][0]
  # I'm sure there's a more elegant way to do this

  # Now we calculate two parameters:
  #  d = the duration of the bounce as a whole
  #  eps = how far into the bounce we are at point t: for calculating the y position
  #  delta = proportion of elapsed time from note before to after, for x position
  if n_before is None:
    d = T_MAX
    eps = n_after.t0 - t
    delta = 0
  elif n_after is None:
    d = T_MAX
    eps = t - n_before.t0
    delta = 0
  else:
    delta = (t - n_before.t0) / (n_after.t0 - n_before.t0)
    t_mid = (n_before.t0 + n_after.t0)/2
    d = min(t_mid - n_before.t0, T_MAX)
    if t < t_mid:
      eps = t - n_before.t0
    else:
      eps = n_after.t0 - t

  if eps >= T_MAX: # the ball is off the top of the screen
    return

  n1 = n_before if n_before is not None else n_after
  n2 = n_after if n_after is not None else n_before
  x1 = (n1.note - LOWEST_NOTE)*KEY_WIDTH
  x2 = (n2.note - LOWEST_NOTE)*KEY_WIDTH
  x = x1 + (x2-x1)*delta + KEY_WIDTH/2
  if d >= T_MIN: # the "normal" bounce will go above MIN_BOUNCE_HEIGHT
    y = HEIGHT - KEY_HEIGHT - KEY_WIDTH - ACCEL * eps * (2*d - eps)/2
  else:
    y = HEIGHT - KEY_HEIGHT - KEY_WIDTH - MIN_BOUNCE_HEIGHT * (1 - ((d-eps) / d)**2)

  ctx.arc(x, y, KEY_WIDTH/2, 0, math.pi*2)
  incol = [x/255 for x in BALL_COLOURS[trk]]
  ctx.set_source_rgb(incol[2], incol[1], incol[0])
  ctx.fill()




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
allnotes = dict() # each key will be a track number
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
    if n.track in allnotes:
      allnotes[n.track].append(n)
    else:
      allnotes[n.track] = [n]
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

# Sort each track: if notes overlap, they'll be in order of end time,
# and we want them ordered by start time instead
for trk in allnotes:
  allnotes[trk].sort(key = lambda n: n.t0)

# At this point we have an allnotes array and can start to animate it.
def make_frame(t):
    ctx.set_source_rgb(BACKGROUND[2]/255.0, BACKGROUND[1]/255.0, BACKGROUND[0]/255.0)
    ctx.paint()
    for trk in allnotes:
      draw_ball(trk, t-MIDI_OFFSET)
      for n in allnotes[trk]:
        draw_key(n, t-MIDI_OFFSET)

    data = surface.get_data()
    image = pygame.image.frombuffer(data, (WIDTH, HEIGHT),"RGBA",)
    # nb pygame bug: surface is created as ARGB but we must write to it as RGBA
    # see https://github.com/pygobject/pycairo/issues/247
    screen.blit(image, (0,0))

    if MODE == 'save':
      # pymovie swaps the x and y coordinates, so we need to flip the surface back
      return pygame.surfarray.array3d(
        pygame.transform.rotate(
          pygame.transform.flip(screen, True, False), 90
        )
      )

# set up pygame and cairo
pygame.init()
window = pygame.display.set_mode( (WIDTH, HEIGHT) )
screen = pygame.display.get_surface()
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)
ctx.set_operator(cairo.OPERATOR_OVER)

pygame.display.set_caption('Animation')

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
  titles = TextClip(TITLE_TEXT,
    font='Segoe-Script', fontsize = TITLE_FONT_SIZE, color = 'white'
  )
  #titles = titles.set_pos('center').set_duration(7.5).fadein(3).fadeout(2.5)
  titles = titles.set_pos('center').set_duration(5).fadein(1).fadeout(1)
  audio = AudioFileClip(WAV_FILE_TEMP)
  audio.set_start(AUDIO_OFFSET)
  animation_clip = animation_clip.set_audio(audio)
  video = CompositeVideoClip([animation_clip, titles])
  video.write_videofile(OUTPUT_FILE, fps=FPS,
    bitrate='2500k', audio_bitrate='320k')
  # clean up:
  os.system('rm '+WAV_FILE_TEMP)

