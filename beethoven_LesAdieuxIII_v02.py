from __future__ import division # so that a/b for integers evaluates as floating point
import pygame, pyglet, sys, subprocess, os, time, mido
from pygame.locals import *
from moviepy.editor import *
import math # we'll need square roots


MODE = 'play' # Display the animation on screen in real time
#MODE = 'save' # Save the output to a video file instead of displaying on screen


MIDI_FILE = '/home/alex/midi/python_animations/midi/beethoven_LesAdieuxIII_v04.mid'
WAV_FILE_ORIGINAL = '/audio/2008-anpa_audition/LesAdieuxIII-edited.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 383 # length of the video file to be generated, in seconds
AUDIO_OFFSET = 6.43 # number of seconds late to start the audio
MIDI_OFFSET = 1.3 # number of seconds to shift midi events by
TRACK_ORDER = [1]
OUTPUT_FILE = '/home/alex/midi/python_animations/LesAdieuxIII.mp4'

TITLE_TEXT = \
  "Beethoven sonata in E flat, op 81a, 'Les Adieux'\n" + \
  "Movement 3: The Return\n\n" + \
  "Performed by Alexander Hanysz\nRecorded in Grainger Studio, Adelaide\n" + \
  "May 2008"

# Adjust offsets to sync with the midi file
#AUDIO_OFFSET = 6.63 # number of seconds late to start the audio
#MIDI_OFFSET = 1.5 # number of seconds to shift midi events by
#AUDIO_OFFSET -= 0.15 # to compensate for delay in playback starting
#LENGTH = LENGTH + 5

# For testing a short range
#START_TIME = 315 # start of slow section
#START_TIME = 365 # just before end of slow section
START_TIME = 10
AUDIO_OFFSET -= START_TIME
MIDI_OFFSET -= START_TIME

FPS = 25 # frames per second for saved video output
#FPS = 15 # for a fast cut of the video

LOWEST_NOTE = 25 # midi note number of the left of the screen
HIGHEST_NOTE = 108
ACCEL_DEFAULT = 400 # force of gravity in pixels/sec/sec
ACCEL_SLOW = 80 # for the Andante
ACCEL_CODA = 2000
ANDANTE_TIME = 325
CODA_TIME = 372

KEY_HEIGHT = 50 # how far the "keyboard" is from the bottom of the screen
MIN_BOUNCE_HEIGHT = 30 # balls bounce at least this high even for rapid repeated notes

HEIGHT = 720
#HEIGHT = 397 # for a fast cut of the video
WIDTH = int(HEIGHT * 16/9)

KEY_WIDTH = WIDTH / (HIGHEST_NOTE - LOWEST_NOTE + 1)

T_MAX_DEFAULT = math.sqrt(2*(HEIGHT - KEY_HEIGHT)/ACCEL_DEFAULT)
T_MAX_SLOW = math.sqrt(2*(HEIGHT - KEY_HEIGHT)/ACCEL_SLOW)
T_MAX_CODA = math.sqrt(2*(HEIGHT - KEY_HEIGHT)/ACCEL_CODA)

#def accel(t, t_prev, t_next):
def accel(t):
  if t > CODA_TIME:
    return ACCEL_CODA
  if t > ANDANTE_TIME:
    return ACCEL_SLOW
  return ACCEL_DEFAULT

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


# Some variables to control display and changing of current time in "play" mode
show_osd = False
paused = False
seek_offset = 0
osd_font = pygame.font.SysFont(None, 48)
OSD_COLOUR = WHITE



def dimmer(colour, brightness):
  return(colour[0]*brightness, colour[1]*brightness, colour[2]*brightness)

def vel_to_colour(v):
  # v is a note-on velocity (0 to 127)
  # return the colour we want for that velocity
  red = max(round((v-50)*3.3), 0)
  green = round((128-v)/2)
  blue = round(v*1.8) + 20
  return (red, green, blue)

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
  if t<n.t0 or t>n.t1:
    return
  key = pygame.Rect((n.note - LOWEST_NOTE)*KEY_WIDTH, HEIGHT-KEY_HEIGHT,
                    KEY_WIDTH, KEY_HEIGHT)
  #col = dimmer(NOTE_COLOURS[n.track % NUM_COLOURS], n.vel/127)
  col = vel_to_colour(n.vel)
  pygame.draw.rect(screen, col, key)


def draw_ball(n, t):
  # Draw the note n at time t as a circle
  # In this case, n is a MIDI note number
  # to be used as an index into the arrays key_times and key_indices

  #if n != 46: # test: just look at one note
    #return
  times = key_times[n]
  num_notes = len(times)
  if num_notes==0: # MIDI note number n is never sounded
    return
  # advance the index until it points to the earliest note-on event that's later than time t
  while key_indices[n]<num_notes-1 and times[key_indices[n]] < t:
    key_indices[n] += 1

  # Now we calculate three parameters:
  #  d = the duration of the bounce as a whole
  #  eps = how far into the bounce we are at point t
  #  t_note = the time of the latest note_on event that's not before t
  #  t_next = the note after t_note, or a very large number if t_note is the last one
  #  We'll use t_note and t_next to fetch the correct ACCEL value
  if t < times[0]:
    eps = times[0] - t
    t_note = times[0]
    if num_notes > 1:
      t_next = times[1]
    else:
      t_next = 1000000
  elif t > times[-1]: # remember that [-1] is the last element of a list
    eps = t - times[-1]
    t_note = times[-1]
    t_next = 1000000
  else:
    i = key_indices[n]
    t_mid = (times[i-1] + times[i])/2
    t_note = times[i-1]
    t_next = times[i]
    if t < t_mid:
      eps = t - times[i-1]
    else:
      eps = times[i] - t

  ACCEL = accel(t_note)
  ACCEL_next = accel(t_next)
  # Calculate time for a ball to fall from the very top of the screen to the bottom
  T_MAX = math.sqrt(2*(HEIGHT - KEY_HEIGHT)/ACCEL)
  # Calculate the duration of a minimum height bounce under normal gravity
  T_MIN = math.sqrt(2*MIN_BOUNCE_HEIGHT/ACCEL)

  # If the last note was a long time ago, then we actually want a more current ACCEL value:
  T_MAX_next = math.sqrt(2*(HEIGHT - KEY_HEIGHT)/ACCEL_next)
  T_between = max(T_MAX+T_MAX_next, 2*T_MAX)
  #print t, t_note, t_next, T_MAX, T_MAX_next
  if t - t_note > max(T_MAX, T_MAX_next) and t_next - t_note > T_between:
  # It's important to get the above condition right, otherwise balls will teleport when the tempo changes!
  # First part: max(T_MAX, T_MAX_next) says the previous note is finished, and will stay finished even if the tempo slows down.
  # Second part: there's enough time between notes for the ball to get off the screen and back on.
  # This is for a change from slow to fast tempo:
  # If t_next - t_note is greater than T_between and less than 2*max(T_MAX, T_MAX_next), 
  # then it's possible for the ball to go up and down at the slow tempo and stay on the screen throughout,
  # and it's also possible for the ball to leave the screen at the slow tempo and come back on in the fast tempo.
  # We want the latter.
    ACCEL = accel(t_next)
    T_MAX = math.sqrt(2*(HEIGHT - KEY_HEIGHT)/ACCEL)
    T_MIN = math.sqrt(2*MIN_BOUNCE_HEIGHT/ACCEL)

  if t < times[0] or t > times[-1]:
    d = T_MAX
  else:
    d = min(t_mid - times[i-1], T_MAX)


  if eps >= T_MAX: # the ball is off the top of the screen
    return

  x = (n - LOWEST_NOTE)*KEY_WIDTH
  if d >= T_MIN: # the "normal" bounce will go above MIN_BOUNCE_HEIGHT
    y = HEIGHT - KEY_HEIGHT - KEY_WIDTH - ACCEL * eps * (2*d - eps)/2
  else:
    y = HEIGHT - KEY_HEIGHT - KEY_WIDTH - MIN_BOUNCE_HEIGHT * (1 - ((d-eps) / d)**2)

  ball = pygame.Rect(x, y, KEY_WIDTH, KEY_WIDTH)
  pygame.draw.ellipse(screen, WHITE, ball)




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
      draw_key(n, t-MIDI_OFFSET)
    for i in range(128):
      draw_ball(i, t-MIDI_OFFSET)
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
    pygame.display.update()

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

