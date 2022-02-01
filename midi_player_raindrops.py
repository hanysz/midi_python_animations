# Jan 2022: update to cairo graphics; use python3 only, not python 2
# To do: 
# - map different tracks/channels to different colours/shapes more flexibly
# - implement LINEWIDTH seeting
# - add a setting for amount of parallax
# - add a setting for title font height


import datetime # for testing

import pygame, sys, subprocess, os, time, mido, cairo, math
from pygame.colordict import THECOLORS as COLOURS
from cairo_utility_functions import * # my raindrop-drawing code and other bits
import numpy as np
from pygame.locals import *
from moviepy.editor import *

#MODE = 'play' # Display the animation on screen in real time
MODE = 'save' # Save the output to a video file instead of displaying on screen

FPS = 25 # frames per second for saved video output

LOWEST_NOTE = 21 # midi note number of the bottom of the screen
HIGHEST_NOTE = 108
ONSCREEN_TIME = 12 # max number of seconds for a note to cross the screen
  # (with parallax, time will be less for the foreground notes)
INNER_BRIGHTNESS = 0.4 # brightness of the middle of the note when lit up
FADEOUT_TIME = 1 # number of seconds for a note to stop being lit after it's stopped sounding
LINEWIDTH = 1 # thickness of the circle outline in pixels
# currently not used with cairo version: need to fix this
# nb with width>2 there's obvious cropping at the bottom and right of each note:
# not sure why, maybe a pygame bug??

HEIGHT = 1080 # nb near the end, set fontsize=45 if HEIGHT=1080, or 30 if 720
#HEIGHT = 720
TITLE_FONT_SIZE = 45 # recommended: 45 if HEIGHT=1080, or 30 if 720
WIDTH = int(HEIGHT * 16/9)


# List of colours to be used for different tracks of the MIDI file:
NOTE_COLOURS = dict([
  (1, COLOURS["white"]),
  (2, COLOURS["green"]),
  (3, COLOURS["blue"]),
  (4, COLOURS["yellow"]),
  (5, COLOURS["magenta"]),
  (6, COLOURS["cyan"]),
  (7, COLOURS["red"])
])

BACKGROUND = COLOURS["black"]
# may be overridden by the import below

#from settings.testing import *
from settings.szymanowski_op4 import *
#from settings.szymanowski3 import *
# For testing:
#HEIGHT = 600
WIDTH = int(HEIGHT * 16/9)
#FPS=10

NOTEWIDTH  = WIDTH / (HIGHEST_NOTE - LOWEST_NOTE + 1)


def dimmer(colour, brightness):
  return(colour[0]*brightness, colour[1]*brightness, colour[2]*brightness)

def blend(colour1, colour2, mix):
  return([x*(1-mix) + y*mix for x, y in zip(colour1, colour2)])

def colour_from_time(collist, nowtime, interpolate=True):
  # collist is a list [[t1, c1], [t2, c2], ...]
  #   with 0=t1<t2< ...
  # With interpolate=True, blend the colours from before and after nowtime
  # otherwise, just return the "before" colour
  #  (in the latter case, we can be a bit naughty with types:
  #    the "colour" can actually be a dictionary of colours per track/channel)
  found = False
  for t, c in collist:
    if t > nowtime:
      t_after = t
      c_after = c
      found = True
      break # At this point t_before <= nowtime < t_after
    else:
      t_before = t
      c_before = c
  if not interpolate:
    return c_before
  if found:
    mix = (nowtime - t_before)/(t_after-t_before)
    return(blend(c_before, c_after, mix))
  else:
    return(c_before)


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


def draw_shape(n, t, background):
  # Draw the note n at time t, using colour determined by channel, and shape by track
  # Need to pass the background colour so that we can fade to non-black colours
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
  if 'COLOUR_CHANGES' in globals():
    colour_dict = colour_from_time(COLOUR_CHANGES, n.t0, interpolate=False)
  else:
    colour_dict = NOTE_COLOURS
  outcol = colour_dict[n.track]
  outcol = dimmer(outcol, outline_fade)

  filled = True
  if t<n.t0 or t>n.t1+FADEOUT_TIME:
    filled = False
  elif t<n.t1:
    #incol = dimmer(outcol, INNER_BRIGHTNESS)
    incol = blend(background, outcol, INNER_BRIGHTNESS)
  else:
    fade_fraction = 1-(t-n.t1)/FADEOUT_TIME
    #incol = dimmer(outcol, INNER_BRIGHTNESS * fade_fraction)
    incol = blend(background, outcol, INNER_BRIGHTNESS * fade_fraction)
  if t>=n.t0-ONSCREEN_TIME/2 and t<=n.t1+ONSCREEN_TIME/2:
    y = HEIGHT - ((n.t0-t)/ONSCREEN_TIME + 0.5) * HEIGHT
    x = WIDTH - (HIGHEST_NOTE - n.note)*NOTEWIDTH
    radius = n.vel/2

    # parallax: adjust y so that larger drops move faster
    offset = y - HEIGHT/2
    offset = offset * (1+n.vel/127) # max value is 2
    y = HEIGHT/2 + offset

    shape = NOTE_SHAPES[n.channel]
    if shape=="raindrop":
      ctx.raindrop(x, y, radius*0.45)
    elif shape=="star":
      ctx.star(x, y, 7, radius*0.6, radius*0.27)
    else:
      ctx.arc(x, y, radius*0.7, 0, math.pi*2)

    if filled:
      #ctx.set_operator(cairo.OPERATOR_ADD) # blend colours for overlapping circles
      incol = [c/255 for c in incol] # cairo colours are 0-1, pygame 0.255
      ctx.set_source_rgb(incol[2], incol[1], incol[0])
      ctx.fill_preserve()
    #ctx.set_operator(cairo.OPERATOR_OVER)
    outcol = [c/255 for c in outcol]
    ctx.set_source_rgb(outcol[2], outcol[1], outcol[0])
    ctx.stroke()



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
for tracknum in [0] + TRACK_ORDER: # always include track 0 because it's the tempo map!
# nb reading the tempo still isn't quite right:
# for a standard midi file, the tempos only appear in track 0
# At the moment I'm preprocessing the midi using a different script
# to copy tempo changes into all the other tracks
  t = mid.tracks[tracknum]
  seconds_per_tick = 0.5 / PPQN # assume tempo of 120 beats per minute until we find out otherwise
  abstime = 0 # reset absolute time at the start of each track.
  # nb abstime is in seconds
  for e in t:
    #print(e.time/PPQN)
    abstime += e.time * seconds_per_tick
    # increment abstime *before* changing seconds_per_tick for the next tempo!
    if e.type == 'set_tempo':
      seconds_per_tick = e.tempo / PPQN / 1000000
    if isKeyDown(e):
      addToPending(e, abstime, tracknum)
    if isKeyUp(e):
      addToNotes(e, abstime)


# At this point we have an allnotes array and can start to animate it.
def make_frame(t, draw_function):
    if 'BACKGROUND_CHANGES' in globals():
      # if true, then background colour varies over time
      background = colour_from_time(BACKGROUND_CHANGES, t-MIDI_OFFSET)
    else:
      background = BACKGROUND
    ctx.set_source_rgb(background[2]/255.0, background[1]/255.0, background[0]/255.0)
    ctx.paint()

    for n in allnotes:
      draw_function(n, t-MIDI_OFFSET, background)

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
    #pygame.draw.line(screen, COLOURS["white"], (0,HEIGHT/2), (WIDTH, HEIGHT/2))
    # Uncomment the line above to get a "now time" line drawn on the animation

# set up pygame and cairo
pygame.init()
window = pygame.display.set_mode( (WIDTH, HEIGHT) )
screen = pygame.display.get_surface()
surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = CustomContext(surface) # cairo context with some extra functions
ctx.set_operator(cairo.OPERATOR_OVER)

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
    make_frame(t, draw_shape)
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

  animation_clip = VideoClip(lambda t: make_frame(t, draw_shape),
                             duration=LENGTH)
  titles = TextClip(
     titletext, # from settings import
    font='Segoe-Script', fontsize = TITLE_FONT_SIZE, color = 'white'
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

