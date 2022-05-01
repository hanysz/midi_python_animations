import sys
if not (4 <= len(sys.argv) <= 5):
  sys.exit("Usage: python csv_to_csound.py score.csd notelist.csv audio.wav [output.mp4]")
import pygame, cairo, subprocess, os, time, pandas
from pygame.locals import *
from moviepy.editor import *
from math import pi, sqrt

infilename = sys.argv[1]
metadatafilename = sys.argv[2]
soundfilename = sys.argv[3]
if len(sys.argv) == 5:
  outfilename = sys.argv[4]

MODE = 'play' # Display the animation on screen in real time
if len(sys.argv) == 5:
  MODE = 'save' # Save the output to a video file instead of displaying on screen

if MODE=='save' and os.path.exists(outfilename):
  sys.exit(f"Error: output file {outfilename} already exists")

if not os.path.exists(metadatafilename):
  sys.exit(f"Error: input file {metadatafilename} does not exist")

if not os.path.exists(infilename):
  sys.exit(f"Error: input file {infilename} does not exist")

if not os.path.exists(soundfilename):
  sys.exit(f"Error: audio file {soundfilename} does not exist")

metadata = pandas.read_csv(metadatafilename)
LENGTH = max(metadata['stop_time']) + 14

TITLE_TIME = 8 if MODE=='save' else 0
# number of seconds for titles before the sound starts

WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio

from pygame.colordict import THECOLORS as COLOURS
#TICK_COLOURS = [COLOURS[c] for c in
#  ['white', 'orchid1', 'olivedrab4',
#  'chartreuse3', 'cadetblue3', 'hotpink1', 'violetred1', 'deeppink2', 'deeppink2',
#   'magenta4', 'magenta4', 'purple4', 'purple4']
#]

colour_list = metadata['colour']
TICK_COLOURS = [COLOURS[c] for c in colour_list]

DURATION_MULTIPLIERS = [1]*32
# if durations of wave files don't seem to match the visuals,

RADII = metadata['radius']
RING_WIDTH = 5
MARGIN = max(RADII)*2
BACKGROUND = COLOURS['black']
TEMPI = metadata['bpm']
MAX_TEMPO = max(TEMPI)
MIN_TEMPO = min(TEMPI)

DURATIONS = metadata['duration']

TITLE_TEXT = \
'''32 Ticky Things after Ligeti

Created by Alexander Hanysz
using Csound, Python and
percussion samples from The Sound Site

May 2022'''

FPS = 30 # frames per second for saved video output
#FPS = 15 # for a fast cut of the video

HEIGHT = 1080
#HEIGHT=900
#HEIGHT=600
#HEIGHT = 397 # for a fast cut of the video
WIDTH = int(HEIGHT * 16/9)
MIN_DURATION = 0.5 # shortest visual note
TITLE_FONT_SIZE = 45 # recommended: 45 if HEIGHT=1080, or 30 if 720

class Note(object):
  __slots__ = ['t0', 't1', 'voice', 'pan', 'predelay']
  # t0, t1 = start and finish times in seconds
  # voice = instrument number: use this to choose a colour
  # pan = stereo position: use this to choose x coordinate on the screen
  # predelay = reverb setting: use this to choose y coordinate
  
  def __str__(self): # Printable version of note for debugging
    return(f'time {self.t0} to {self.t1}, voice {self.voice} with pan {self.pan} and predelay {self.predelay}')


allnotes = []
with open(infilename) as infile:
  for line in infile:
    tokens = line.split()
    if len(tokens)==9 and tokens[0]=='i' and tokens[1]=='"playwave"':
      n=Note()
      n.t0=float(tokens[2])
      n.voice = int(tokens[4])-1 # csound counts from 1, python from 0
      duration = DURATIONS[n.voice]
      n.t1 = n.t0 + max(duration, MIN_DURATION)
      n.pan = float(tokens[6])
      n.predelay = float(tokens[8])*1000
      allnotes.append(n)

print(f"Got {len(allnotes)} notes")



def draw_note(n, t):
  if t<n.t0 or t>n.t1:
    return
  x = round(n.pan * WIDTH)
  #y = round((n.predelay+5)/80*HEIGHT)
  y = round((MAX_TEMPO - TEMPI[n.voice])/(MAX_TEMPO-MIN_TEMPO)*(HEIGHT-2*MARGIN)) + MARGIN
  r = (n.t1-t)/(n.t1-n.t0)*RADII[n.voice]
  ctx.arc(x, y, r, 0, pi*2)
  incol = [x/255 for x in TICK_COLOURS[n.voice]]
  ctx.set_source_rgb(incol[2], incol[1], incol[0])
  ctx.fill()

  if r>RING_WIDTH:
    ctx.arc(x, y, r-RING_WIDTH, 0, pi*2)
    ctx.set_source_rgb(0, 0, 0)
    ctx.fill()


def make_frame(t):
    ctx.set_source_rgb(BACKGROUND[2]/255.0, BACKGROUND[1]/255.0, BACKGROUND[0]/255.0)
    ctx.paint()
    for n in allnotes:
      draw_note(n, t-TITLE_TIME)

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
    if (not audioPlaying) and t > TITLE_TIME:
      audioplayer = subprocess.Popen(["/usr/bin/aplay", soundfilename])
      audioPlaying = True
    make_frame(t)
    pygame.display.update()

  audioplayer.kill()
  pygame.display.quit()
  pygame.quit()
  sys.exit()

else:
  # Edit the audio track: add silence at start and trim to the correct length
  os.system('/usr/bin/sox '+ soundfilename + ' ' + WAV_FILE_TEMP +
              ' pad '+str(TITLE_TIME) + ' trim 0 ' + str(LENGTH)
           )

  animation_clip = VideoClip(make_frame, duration=LENGTH)
  titles = TextClip(TITLE_TEXT,
    font='Segoe-Script', fontsize = TITLE_FONT_SIZE, color = 'white'
  )
  #titles = titles.set_pos('center').set_duration(7.5).fadein(3).fadeout(2.5)
  titles = titles.set_pos('center').set_duration(5).fadein(1).fadeout(1)
  audio = AudioFileClip(WAV_FILE_TEMP)
  audio.set_start(TITLE_TIME)
  animation_clip = animation_clip.set_audio(audio)
  video = CompositeVideoClip([animation_clip, titles])
  video.write_videofile(outfilename, fps=FPS,
    bitrate='2500k', audio_bitrate='320k')
  # clean up:
  os.system('rm '+WAV_FILE_TEMP)

