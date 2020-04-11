from __future__ import division # so that a/b for integers evaluates as floating point
import pygame, pyglet, sys, subprocess, os, time, mido, copy
from pygame.locals import *
from moviepy.editor import *
import math # we'll need square roots
import bisect # quick way of finding an element of a list, see
# https://docs.python.org/3/library/bisect.html
# and http://stackoverflow.com/questions/7281760/in-python-how-do-you-find-the-index-of-the-first-value-greater-than-a-threshold

#MODE = 'play' # Display the animation on screen in real time
MODE = 'save' # Save the output to a video file instead of displaying on screen

OUTPUT_FILE = '/home/alex/midi/python_animations/scriabin_op74/scriabin_preludes_op74.mp4'

TITLE_TEXT = "Five preludes opus 74 by Alexander Scriabin\n\n" + \
             "Performed by Alexander Hanysz\n" + \
	     "Live recording, Pilgrim Church, Adelaide\n" + \
             "10th November 2013"

FPS = 25 # frames per second for saved video output
#FPS = 10 # for a fast cut of the video
LENGTH = 355 # length of the video file to be generated, in seconds
#LENGTH = 20 # for testing
DELAY = 10 # number of seconds to allow for title screen

HEIGHT = 720
#HEIGHT = 397 # for a fast cut of the video
WIDTH = int(HEIGHT * 16/9)
CENTRE = (WIDTH/2, HEIGHT/2)

# set up some colours
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (0, 255, 255)
MAGENTA = (255, 0, 255)
CYAN = (255, 255, 0)

MIDI_FILES = [
 '/home/alex/midi/python_animations/midi/scriabin_op74/2016-12-Scriabin_op74_no1_v04.mid',
 '/home/alex/midi/python_animations/midi/scriabin_op74/2016-12-Scriabin_op74_no2_v04.mid',
 '/home/alex/midi/python_animations/midi/scriabin_op74/2016-12-Scriabin_op74_no3_v04.mid',
 '/home/alex/midi/python_animations/midi/scriabin_op74/2016-12-Scriabin_op74_no4_v04.mid',
 '/home/alex/midi/python_animations/midi/scriabin_op74/2016-12-Scriabin_op74_no5_v04a.mid'
]
WAV_FILE_ORIGINAL = '/audio/2013-nov-concert/scriabin_all_spaced.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio

# Timing info: six numbers for each movement
# Fade in start and end times
# Playing start and end times (for syncing with MIDI)
# Fade out start and end
TIMES = [[    -6,   4.0,   1.5,  56.0,  49.0,  55.4],
         [ 49.7,  58.7,  56.1, 136.7, 132.0, 138.3],
	 [133.0, 139.8, 138.4, 170.0, 165.0, 172.5],
	 [167.0, 175.2, 173.7, 292.4, 281.1, 293.0],
	 [279.0, 296.0, 293.6, 347.0, 339.0, 347.0]
	]
START_TIMES = [x[0] for x in TIMES]
AUDIO_STARTS = [2.1, 56.7, 139.0, 174.2, 294.3] # start of audio for each movement
AUDIO_OFFSET = 0 # number of seconds late to start the audio
# compensate for playback delay
#AUDIO_OFFSET += 0.3
MIDI_STARTS = [0.2, 1.0, 1.4, 1.7, 1.7] # time of first event in each MIDI track
# nb track 5 is adjusted in code later; actual start time is 3.7
MIDI_OFFSETS = [AUDIO_STARTS[k] - START_TIMES[k] - MIDI_STARTS[k] for k in range(5)]
AUDIO_OFFSET += DELAY
TIMES = [[t+DELAY for t in x] for x in TIMES]
MIDI_OFFSETS = [x+DELAY for x in MIDI_OFFSETS]
TRACK_ORDERS = [
  [2, 3, 4],
  [2, 3, 4, 5, 6],
  [2, 3, 4, 5, 6, 7],
  [2,3,4,5,6,7,8],
  #[2, 3, 4, 5, 6] -- for old version of MIDI file
  [4, 5, 6, 7, 8] # new version has two ignorable tracks at the start
]



TRACK_PLANES_LIST = [
  [0,0, 0.4 ,0.5, 0.3],
  [0,0, 0.1, 0, 0, 0, 0],
  [0,0, 0.2, 0.5, 0.3, 0.7, 0.1, 0.2],
  [0,0,.1,.1,.1,.1, .4, .6, .2],
  #[0,0, 1, 0.2, 0.2, 1.5, 0.1]
  [0, 0, 0,0, 0.6, 0.4, 0.2, 1.5, 0.1]
]

BG_COLOURS_LIST = [
  pygame.Color('darkgray'),
  WHITE,
  pygame.Color('darkgray'),
  pygame.Color('darkgray'),
  (50,50,50)
]

FG_COLOURS_LIST = [
  [pygame.Color(x) for x in
               ['black', 'black', 'magenta', '#8000B3', '#4B00C2']],
  [pygame.Color(x) for x in
             ['black', 'black', 'cyan', 'lightskyblue', 'darkcyan', 'steelblue', 'blue']],
  [pygame.Color(x) for x in
             ['black', 'black', 'white', 'springgreen',
	      'green', 'yellow', 'darkcyan', 'white']],
  [pygame.Color(x) for x in [
                'black','black', 'tan','tan','tan','tan', 'gold','orange','orangered']],
  [pygame.Color(x) for x in [
                #'black','black', 'magenta','red','pink','yellow', 'magenta']]
                'black','black','black','black',
		'magenta','red','pink','yellow', 'magenta']]
]

BACKGROUND = BLACK




# For testing a short range
#START_TIME = -5
#AUDIO_OFFSET -= START_TIME
#MIDI_OFFSETS = [x - START_TIME for x in MIDI_OFFSETS]


EYE_COORDS = (WIDTH/2, HEIGHT/2, 20)
#PICTURE_PLANE = 5
GROW_TIMES = [0.6, 0.6, 0.4, 0.6, 0.3] # how many seconds it takes for notes to grow to full size before they sound
GROWTH_FACTOR = 30 # Enhanced growth as the notes get closer

LOWEST_NOTES = [30, 15, 25, 30, 18] # midi note number of the bottom of the screen, for each file
HIGHEST_NOTES = [90, 90, 85, 100, 95]
NOTE_HEIGHTS = [0,0,0,0,0]
NOTE_HEIGHTS = [HEIGHT / (HIGHEST_NOTES[i] - LOWEST_NOTES[i] + 1) for i in range(5)]



# Some variables to control display and changing of current time in "play" mode
show_osd = False
paused = False
seek_offset = 0
osd_font = pygame.font.SysFont(None, 48)
OSD_COLOUR = WHITE



def dimmer(colour, brightness):
  return(colour[0]*brightness, colour[1]*brightness, colour[2]*brightness)


class Note(object):
  __slots__ = ['note', 't0', 't1', 'vel', 'track', 'channel', 'z', 'col']
  # note = MIDI note number
  # t0, t1 = start and finish times in seconds
  # vel = MIDI velocity
  # track = track number
  # channel = channel number
  #  Added for the piano roll 3D version:
  # z: z-coordinate (updated during playing)
  # col: colour, ditto
  
  def __str__(self): # Printable version of note for debugging
    answer = 'Note number ' + str(self.note)
    answer += ' time ' + str(self.t0) + '-' + str(self.t1)
    answer += '; vel ' + str(self.vel) + ', track ' + str(self.track)
    answer += ', ch' + str(self.channel)
    answer += ', z=' + str(self.z)
    answer += ', col=' + str(self.col)
    return answer

def rescale(r, z):
  # r is a rectangle in the z = 0 plane
  # transform so that it's z units away
  # This is a combination of perspective view plus the note actually moving as it's played.
  # The maths is a bit of a kludge...
  alpha = 1-z/EYE_COORDS[2]
  scale = (EYE_COORDS[2] / (EYE_COORDS[2]-z))
  scale = (scale-1)*GROWTH_FACTOR + scale
  r.left = alpha*r.left + (alpha - scale)*r.height/2 + (1-alpha)*EYE_COORDS[0]
  r.top = alpha*r.top + (alpha - scale)*r.height/2 + (1-alpha)*EYE_COORDS[1]
  r.width = r.width * scale
  r.height = r.height * scale
  return r


def set_note_properties(n, t):
  # For note n at time t, set the z value (foreground/background position) and colour
  z = 0
  z_target = TRACK_PLANES[n.track]
  GPS = z_target/GROW_TIME # GPS = growth per second
  #col = copy.deepcopy(BG_COLOUR)
  col = [rgb for rgb in BG_COLOUR] # copy BG_COLOUR and make it mutable so we can fade it out
  if t>n.t0 and t<n.t1:
    z = z_target
    FGcol = FG_COLOURS[n.track]
    col_intensity = (n.t1-t/3 - 2*n.t0/3)/(n.t1-n.t0)
    col_intensity = (n.t1-t/2 - n.t0/2)/(n.t1-n.t0)
    for i in range(3):
      col[i] = int(col_intensity*FGcol[i] + (1-col_intensity)*col[i])
  elif t < n.t0 and t > n.t0-GROW_TIME:
    z = (t - n.t0)*GPS + z_target
  elif t > n.t1 and t < n.t1+GROW_TIME:
    z = z_target - (t - n.t1)*GPS
  n.z = z
  n.col = col



def draw_note(n):
  # Draw the rectangle for note n at time t.
  # If n is actually playing at time t, draw in the foreground,
  # else background.
  # Actually, t isn't passed as a parameter, because the t-related calculations
  # are done in the set_note_properties function above.
  x0 = n.t0/ITEM_LENGTH*WIDTH
  x1 = n.t1/ITEM_LENGTH*WIDTH
  y0 = (HIGHEST_NOTE - n.note) / (HIGHEST_NOTE - LOWEST_NOTE + 1) * HEIGHT
  noterect = pygame.Rect(x0, y0, x1-x0, NOTE_HEIGHT)
  pygame.draw.rect(frame, dimmer(n.col, FADE_OUT**2), rescale(noterect, n.z))


# Read and parse the MIDI file
def isKeyDown(e):
  # e is a MIDI event.
  return (e.type == 'note_on' and e.velocity > 0)
  # relying on short circuit evaluation!

def isKeyUp(e):
  return (e.type == 'note_off' or (e.type == 'note_on' and e.velocity == 0))

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

note_arrays = []
for i in range(5):
  mid = mido.MidiFile(MIDI_FILES[i])
  PPQN = mid.ticks_per_beat

  # Step through the file and create notes
  allnotes = []
  # Keep a pending list:
  pending = {}
  # When a note-on event comes up, create a pending note with t0 at current time but no t1
  #  key = the note value
  # When there's note-off, or note-on with zero velocity
  #  look for a matching item in the pending list and move it to allnotes

  # Read the tracks in order from background to foreground.
  seconds_per_tick = 0.5 / PPQN # assume tempo of 120 beats per minute until we find out otherwise
  for tracknum in [0] + TRACK_ORDERS[i]: # always include track 0 because it's the tempo map!
  # nb reading the tempo still isn't quite right, as it will only use the last tempo from track 0; it won't handle multiple tempos in one piece.
    t = mid.tracks[tracknum]
    abstime = 0 # reset absolute time at the start of each track.
    if i==4:
      abstime = -2/seconds_per_tick # shift movement 5 back two seconds
    # nb abstime is in ticks
    for e in t:
      abstime += e.time
      if e.type == 'set_tempo':
	seconds_per_tick = e.tempo / PPQN / 1000000
      if isKeyDown(e):
	addToPending(e, abstime * seconds_per_tick, tracknum)
      if isKeyUp(e):
	addToNotes(e, abstime * seconds_per_tick)
  note_arrays.append(allnotes)

def draw_notes(t, k):
  # Draw movement k at time t
  if t<TIMES[k][0] or t>TIMES[k][5]:
    return
  global allnotes, ITEM_LENGTH, TRACK_ORDER, TRACK_PLANES, BG_COLOUR, \
	 FG_COLOURS, LOWEST_NOTE, HIGHEST_NOTE, NOTE_HEIGHT, MIDI_OFFSET, \
	 GROW_TIME, FADE_OUT
  allnotes = note_arrays[k]
  ITEM_LENGTH = TIMES[k][3] - TIMES[k][2]
  if t < TIMES[k][1]:
    FADE_OUT = (t - TIMES[k][0]) / (TIMES[k][1] - TIMES[k][0])
  elif t > TIMES[k][4]:
    FADE_OUT = (TIMES[k][5] - t) / (TIMES[k][5] - TIMES[k][4])
  else:
    FADE_OUT = 1
  TRACK_ORDER = TRACK_ORDERS[k]
  TRACK_PLANES = TRACK_PLANES_LIST[k]
  BG_COLOUR = BG_COLOURS_LIST[k]
  FG_COLOURS = FG_COLOURS_LIST[k]
  LOWEST_NOTE = LOWEST_NOTES[k]
  HIGHEST_NOTE = HIGHEST_NOTES[k]
  NOTE_HEIGHT = NOTE_HEIGHTS[k]
  MIDI_OFFSET = MIDI_OFFSETS[k]
  GROW_TIME = GROW_TIMES[k]
  for n in allnotes:
    set_note_properties(n, t-MIDI_OFFSET-START_TIMES[k])
  allnotes.sort(key = lambda n: n.z)
  frame.fill(BLACK)
  for n in allnotes:
    draw_note(n)
    # nb draw_note doesn't actually refer to t, as the time has been used in set_note_properties instead
  screen.blit(frame, (0,0), None, pygame.BLEND_ADD)
  # The BLEND_ADD parameter allows us to cross-fade nicely from one movement to the next


def make_frame(t):
    # First, figure out which MIDI file we're using, and set variables as appropriate
    k=max(bisect.bisect(START_TIMES, t)-1, 0)
    # This returns k=0 if k< START_TIMES[1], k=1 if START_TIMES[1]<=k<START_TIMES[2], etc
    screen.fill(BACKGROUND)
    if k >= 1 and t < TIMES[k-1][5]: # previous track is still fading out
      draw_notes(t, k-1)
    draw_notes(t, k)
    if show_osd:
      timetext = osd_font.render("%.1f" % t, True, OSD_COLOUR)
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
frame = pygame.Surface(screen.get_size()) # draw on to the frame then blit the frame on to the surface, so we can use different blending modes

def seek(seek_time):
  global seek_offset
  seek_offset += seek_time
  global audioPlaying
  audioPlaying = False
  soundtrack.pause()
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
  titles = titles.set_pos('center').set_duration(9.0).fadein(3).fadeout(2.5)
  #titles = titles.set_pos('center').set_duration(5).fadein(1).fadeout(1)
  audio = AudioFileClip(WAV_FILE_TEMP)
  audio.set_start(AUDIO_OFFSET)
  animation_clip = animation_clip.set_audio(audio)
  video = CompositeVideoClip([animation_clip, titles])
  video.write_videofile(OUTPUT_FILE, fps=FPS,
    bitrate='2500k', audio_bitrate='320k')
  # clean up:
  os.system('rm '+WAV_FILE_TEMP)

