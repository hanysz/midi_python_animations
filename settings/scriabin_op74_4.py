import pygame
MIDI_FILE = '/home/alex/midi/python_animations/midi/2016-12-Scriabin_op74_no4_v03.mid'
WAV_FILE_ORIGINAL = '/audio/2013-nov-concert/09-scriabin.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 118 # length of the video file to be generated, in seconds
AUDIO_OFFSET = 0 # number of seconds late to start the audio
MIDI_OFFSET = 0 # number of seconds to shift midi events by
#TRACK_ORDER = [1, 2, 3]
TRACK_ORDER = [6]
OUTPUT_FILE = '/home/alex/midi/python_animations/scriabin_prelude_op74no4.mp4'

TITLE_TEXT = "Scriabin prelude opus 74 number 4"

# Settings specific to piano_roll_3D
TRACK_PLANES = [0,0,0,0,0,0, 1] # indexed by track number
BG_COLOUR = pygame.Color('darkgray')
FG_COLOURS = [0,0,0,0,0,0, pygame.Color('blue')]
BACKGROUND = pygame.Color('black')



MIDI_FILE = '/home/alex/midi/python_animations/midi/2016-12-Scriabin_op74_no4_v04.mid'
WAV_FILE_ORIGINAL = '/audio/2013-nov-concert/09-scriabin.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 118 # length of the video file to be generated, in seconds
AUDIO_OFFSET = 0 # number of seconds late to start the audio
MIDI_OFFSET = 0 # number of seconds to shift midi events by
#TRACK_ORDER = [1, 2, 3]
TRACK_ORDER = [4,5,6,7,8,9,10]
OUTPUT_FILE = '/home/alex/midi/python_animations/scriabin_prelude_op74no4.mp4'

TITLE_TEXT = "Scriabin prelude opus 74 number 4"

# Settings specific to piano_roll_3D
TRACK_PLANES = [0,0,0,0,.1,.1,.1,.1,.7,1.5,.4] # indexed by track number
BG_COLOUR = pygame.Color('darkgray')
FG_COLOURS = [pygame.Color(x) for x in [
              'red','red','red','red','yellow','yellow','yellow','yellow','green','red','blue']]
BACKGROUND = pygame.Color('black')

