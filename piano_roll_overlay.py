from __future__ import division # so that a/b for integers evaluates as floating point

# Piano roll, overlay mode: for variation form or other weird effects
# Background and foreground from two different files
# (typically the background file would be the theme repeated,
#   and the foreground file has the variations)

import pygame, sys, subprocess, os, time, mido
from pygame.locals import *
from moviepy.editor import *
from bisect import bisect_left

MODE = 'play' # Display the animation on screen in real time
MODE = 'save' # Save the output to a video file instead of displaying on screen

LOWEST_NOTE = 25 # midi note number of the bottom of the screen
HIGHEST_NOTE = 108
#COLOUR_MODE = "track" # assign colours based on track number
COLOUR_MODE = "channel"

FPS = 25 # frames per second for saved video output
#FPS = 15 # for a fast cut of the video

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
# The above is unnecessary,
#e.g. use pygame.Color('black') instead of BLACK
#Colour chart at https://sites.google.com/site/meticulosslacker/pygame-thecolors

# List of colours to be used for different tracks or channels of the MIDI file:
BG_COLOUR = pygame.Color('darkgray')
FG_COLOURS = [RED, WHITE, pygame.Color('orange'), GREEN, BLUE]
BACKGROUND = BLACK

#from settings.rach_prelude_D import *
#from settings.beethoven_op81a import *
#from settings.scarlatti_K440 import *
#execfile("settings/scarlatti_K440.py")

# Python3 no longer has "execfile":
settings_file = "settings/haydn_vars_fmin.py"
exec(compile(open(settings_file).read(), settings_file, 'exec'))

SCROLL_OFFSET = SCROLL_TIME - PAGE_STARTS[-2]
# time from start of last page to start of scrolling

NOTE_HEIGHT = HEIGHT / (HIGHEST_NOTE - LOWEST_NOTE + 1)

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


def draw_note(n, t, foreground):
  # Draw the rectangles for note n at time t.
  # For the overlay effect, we'll draw both a background rectangle
  #  and a foreground rectangle for each note.
  # One or both of those rectangles may be off the screen
  # If n is actually playing at time t, draw in the foreground colour,
  # else background.
  page_num = bisect_left(PAGE_STARTS, t) - 1
  if page_num < 0: # can happen if t<=0
    #page_num = 0
    return
  if page_num >= len(PAGE_STARTS)-1: # scrolling takes us past the last page
    page_num = len(PAGE_STARTS)-2

  page_times = (PAGE_STARTS[page_num], PAGE_STARTS[page_num+1])
  page_width  = page_times[1]-page_times[0]
  # to do: adjust for if time > SCROLL_TIME
  if t > SCROLL_TIME:
    page_times = (t-SCROLL_OFFSET, t-SCROLL_OFFSET+page_width)

  if not foreground:
    x0_bg = (n.t0-page_times[0])/page_width*WIDTH
    x1_bg = (n.t1-page_times[0])/page_width*WIDTH
    y0 = (HIGHEST_NOTE - n.note) / (HIGHEST_NOTE - LOWEST_NOTE + 1) * HEIGHT
    note_bg = pygame.Rect(x0_bg, y0, x1_bg-x0_bg, NOTE_HEIGHT)
   
    col = BG_COLOUR
    pygame.draw.rect(screen, col, note_bg)

  if foreground and t>n.t0:

    x0_fg = (n.t0-page_times[0])/page_width*WIDTH
    x1_fg = (n.t1-page_times[0])/page_width*WIDTH
    x_current = (t-page_times[0])/page_width*WIDTH
    x1_fg = min(x1_fg, x_current) # draw only the part of the note up to the current time
    y0 = (HIGHEST_NOTE - n.note) / (HIGHEST_NOTE - LOWEST_NOTE + 1) * HEIGHT
    note_fg = pygame.Rect(x0_fg, y0, x1_fg-x0_fg, NOTE_HEIGHT)
    if COLOUR_MODE == "track":
      col = FG_COLOURS[n.track]
    else:
      col = FG_COLOURS[n.channel]
    pygame.draw.rect(screen, col, note_fg)



# Read and parse the MIDI file
def parse_midi(filename):
  mid = mido.MidiFile(filename)
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
  seconds_per_tick = 0.5 / PPQN # assume tempo of 120 beats per minute until we find out otherwise
  tracknum = 0
  for t in mid.tracks:
  # nb reading the tempo still isn't quite right, as it will only use the last tempo from track 0; it won't handle multiple tempos in one piece.
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
    tracknum += 1
  return(allnotes)

fg_notes = parse_midi(MIDI_FILE)
bg_notes = parse_midi(MIDI_BACKGROUND)

# At this point we have an allnotes array and can start to animate it.
def make_frame(t):
    screen.fill(BACKGROUND)
    for n in bg_notes:
      draw_note(n, t-MIDI_OFFSET, foreground = False)
    for n in fg_notes:
      draw_note(n, t-MIDI_OFFSET, foreground = True)
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
    font='Segoe-Script', fontsize = 30, color = 'white'
  )
  titles = titles.set_pos('center').set_duration(8.5).fadein(3, BACKGROUND).fadeout(2.5, BACKGROUND)
  #titles = titles.set_pos('center').set_duration(5).fadein(1).fadeout(1)
  audio = AudioFileClip(WAV_FILE_TEMP)
  audio.set_start(AUDIO_OFFSET)
  animation_clip = animation_clip.set_audio(audio)
  video = CompositeVideoClip([animation_clip, titles])
  video.write_videofile(OUTPUT_FILE, fps=FPS,
    bitrate='2500k', audio_bitrate='320k')
  # clean up:
  os.system('rm '+WAV_FILE_TEMP)

