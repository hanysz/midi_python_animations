from __future__ import division # so that a/b for integers evaluates as floating point
import pygame, sys, subprocess, os, time, mido, math
from pygame.locals import *
from pygame import gfxdraw
from moviepy.editor import *
from operator import attrgetter # for sorting the allnotes array by attribute

# Left piano: channel 16=accent, channel 1=normal, channel 2=middle section
# Right piano: channel 13=accent, channel 7=normal, channel 4=middle section
# Note velocities range from 11 to 122

# To do:
#   change "fade to black" for note middles into "fade to background colour"
#   fix glitches in MIDI file (doesn't affect this code but still needs doing)
#   remove anything that says "for testing"

#MODE = 'play' # Display the animation on screen in real time
MODE = 'save' # Save the output to a video file instead of displaying on screen

FPS = 30 # frames per second for saved video output

ONSCREEN_TIME = 12 # number of seconds for a note to cross the screen
INNER_BRIGHTNESS = 0.9 # brightness of the middle of the note when lit up
FADEOUT_TIME = 5 # number of seconds for a note to stop being lit after it's stopped sounding
LINEWIDTH = 1 # thickness of the circle outline in pixels
# nb with width>2 there's obvious cropping at the bottom and right of each note:
# not sure why, maybe a pygame bug??

HEIGHT = 1080 # nb near the end, set fontsize=45 if HEIGHT=1080, or 30 if 720
TEXTSIZE = 45

#HEIGHT=800 # for testing
#TEXTSIZE = 33
WIDTH = int(HEIGHT * 16/9)


# set up some colours
BLACK = (0, 0, 0)

LEFT_COL = (3, 228, 247) # acqua for left channel
RIGHT_COL = (5, 225, 12) # sea-green for right channel
LEFT_HIGHLIGHT = (150, 246, 255) # blue-tinted white for left channel accents
RIGHT_HIGHLIGHT = (180, 255, 200) # green-tinted for right
WHITE = (255, 255, 255)
BACKGROUND = (0, 0, 15) # dark blue for a deep watery K



MIDI_FILE = '/home/alex/midi/K/2021-01-23-K_v04.mid'
WAV_FILE_ORIGINAL = '/home/alex/midi/K/K_v04.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 714 # length of the video file to be generated, in seconds
AUDIO_OFFSET = 8.0 # number of seconds late to start the audio
MIDI_OFFSET = 8.0 # number of seconds to shift midi events by
#AUDIO_OFFSET = 1.0 # for testing
#MIDI_OFFSET = 1.0 # for testing
TRACK_ORDER = [2,1]
BIG_RADIUS = int(WIDTH/70) # accented notes
SMALL_RADIUS = int(WIDTH/120)
OUTPUT_FILE = '/home/alex/midi/python_animations/K_by_Dylan_Crismani.mp4'

titletext = "K for two pianos by Dylan Crismani\n\n" + \
  "Composed 2018\n\n" + \
  "Performed by Alexander Hanysz\n" + \
  "January 2021\n\n" + \
  "Virtual pianos from Pianoteq"


LOWEST_NOTE = -2 # midi note number of the bottom of the screen
HIGHEST_NOTE = 107




def dimmer(colour, brightness):
  return(colour[0]*brightness, colour[1]*brightness, colour[2]*brightness)


class Note(object):
  __slots__ = ['note', 't0', 't1', 'vel', 'track', 'channel', 'shape']
  # note = MIDI note number
  # t0, t1 = start and finish times in seconds
  # vel = MIDI velocity
  # track = track number
  # channel = channel number
  # shape = 1 for round notes, 2-7 for polygons
  
  def __str__(self): # Printable version of note for debugging
    answer = 'Note number ' + str(self.note)
    answer += ' time ' + str(self.t0) + '-' + str(self.t1)
    answer += '; vel ' + str(self.vel) + ', track ' + str(self.track)
    answer += ', ch ' + str(self.channel)
    answer += ', shape ' + str(self.shape)
    return answer

def draw_shape(x, y, radius, shape, incol, outcol, filled):
  # x, y = position
  # shape = 1 for circle, 2+ for polygon
  #   where a digon will actually be a tall thin rectangle
  # incol, outcol = inside and outside colours
  if shape==1:
    if filled:
      gfxdraw.filled_circle(screen, x, y, radius, incol)
    gfxdraw.aacircle(screen, x, y, radius, outcol)
    return
  angles = [2*k*math.pi/shape for k in range(shape)]
  if shape % 2 == 1: # odd shapes look better with a pointy bit at the top!
    angles = [theta - math.pi/2 for theta in angles]
  if shape == 4:
    angles = [theta - math.pi/4 for theta in angles]
  if shape == 2:
    theta = math.pi*0.4
    angles = [theta, math.pi-theta, math.pi+theta, -theta]
  points = [(x+math.cos(theta)*radius, y+math.sin(theta)*radius) for theta in angles]
  if filled:
    gfxdraw.filled_polygon(screen, points, incol)
  gfxdraw.aapolygon(screen, points, outcol)

def draw_bubble(n, t):
  # Draw the note n at time t
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
  #outcol = NOTE_COLOURS[n.track % NUM_COLOURS]
  if n.channel in [12,15]: #accented notes
    if n.track==1: # left piano
      outcol = LEFT_HIGHLIGHT
    else:
      outcol = RIGHT_HIGHLIGHT
  elif n.track==1: #left piano
    outcol = LEFT_COL
  else:
    outcol = RIGHT_COL
  outcol = dimmer(outcol, outline_fade)

  filled = True
  if t<n.t0 or t>n.t1+FADEOUT_TIME:
    filled = False
    incol = outcol # dummy value since this gets passed to draw_shape anyway
  elif t<n.t1:
    incol = dimmer(outcol, INNER_BRIGHTNESS)
  else:
    fade_fraction = 1-(t-n.t1)/FADEOUT_TIME
    incol = dimmer(outcol, INNER_BRIGHTNESS * fade_fraction)
  if t>=n.t0-ONSCREEN_TIME/2 and t<=n.t1+ONSCREEN_TIME/2:
    x = (n.vel+30)*WIDTH/320
    if n.track == 2: # right piano
      x = WIDTH - x # mirror image
    y = ((n.t0-t)/ONSCREEN_TIME + 0.5) * HEIGHT
    if n.channel in [1,3]: # middle section, reverse direction
      y = HEIGHT - y

    if n.channel in [12,15]: #accented notes
      radius = BIG_RADIUS
    else:
      radius = SMALL_RADIUS
    #centre = (int(x), int(y))
    #pygame.draw.circle(screen, incol, centre, radius)
    #pygame.draw.circle(screen, outcol, centre, radius, 1)
    # Circles don't work well: integer rounding means they wobble!

    #rect = pygame.Rect(x-radius/2, y-radius/2, radius, radius)
    #if filled:
      #pygame.draw.ellipse(screen, incol, rect)
    #pygame.draw.ellipse(screen, outcol, rect, LINEWIDTH)

    x = int(x)
    y = int(y)
    #epsilon = x - int(x)
    #rect = pygame.Rect(epsilon+LINEWIDTH, epsilon+LINEWIDTH, radius*2+(LINEWIDTH-1)*2, radius*2+(LINEWIDTH-1)*2)
    #tempSurface = pygame.Surface((radius*2+LINEWIDTH*2-1, radius*2+LINEWIDTH*2-1))
    #if filled:
      #pygame.draw.ellipse(tempSurface, incol, rect)
    #pygame.draw.ellipse(tempSurface, outcol, rect, min(LINEWIDTH, radius))
    #screen.blit(tempSurface, (int(x)-radius-LINEWIDTH, int(y)-radius-LINEWIDTH), None, pygame.BLEND_ADD)
    draw_shape(x, y, radius, n.shape, incol, outcol, filled)



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
  n.shape = 1
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
  #seconds_per_tick = 0.5 / PPQN *120/168
  for e in t:
    abstime += e.time
    if e.type == 'set_tempo':
      seconds_per_tick = e.tempo / PPQN / 1000000
    if isKeyDown(e):
      addToPending(e, abstime * seconds_per_tick, tracknum)
    if isKeyUp(e):
      addToNotes(e, abstime * seconds_per_tick)

# At this stage, notes are sorted by track then by *end* time
# To assign shapes for K, we need them sorted by start time
allnotes.sort(key=attrgetter('track', 't0'))

# Assign shapes to accented notes, i.e. channels 13 and 16
# Shape = number of notes between accented notes
#  e.g. where every 5th note is accented, we want shape=5
gap = 1
for n in allnotes:
  if n.channel in [12, 15]:
    if gap>7: # first accent of the recap
      if n.track==1:
        n.shape=3
      else:
        n.shape=2
    else:
      n.shape=gap
    gap = 1 # reset counter each time we assign a shape
    #print(n) # for debugging
  else:
    gap += 1
    #print(str(n.t0) + ' ' + str(n.vel) + ' ' + str(n.channel)) # for debugging


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
background.fill(BACKGROUND)

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
     titletext,
    font='Segoe-Script', fontsize = TEXTSIZE, color = 'white'
  )
  titles = titles.set_pos('center').set_duration(7.5)\
                 .fadein(3, initial_color=BACKGROUND).fadeout(2.5, final_color=BACKGROUND)
  audio = AudioFileClip(WAV_FILE_TEMP)
  audio.set_start(AUDIO_OFFSET)
  animation_clip = animation_clip.set_audio(audio)
  video = CompositeVideoClip([animation_clip, titles])
  video.write_videofile(OUTPUT_FILE, fps=FPS,
    bitrate='2500k', audio_bitrate='320k')
  # clean up:
  os.system('rm '+WAV_FILE_TEMP)

