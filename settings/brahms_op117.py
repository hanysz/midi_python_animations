MIDI_FILE = '/home/alex/midi/2020-12-brahms_op117/brahms-op117_all-multitrack.mid'
WAV_FILE_ORIGINAL = '/home/alex/midi/2020-12-brahms_op117/brahms-op117_all.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 847 # length of the video file to be generated, in seconds
AUDIO_OFFSET = 8.0 # number of seconds late to start the audio
MIDI_OFFSET = 8.0 # number of seconds to shift midi events by
TRACK_ORDER = [4,3,2,1]
OUTPUT_FILE = '/home/alex/midi/python_animations/brahms-intermezzi-op117.mp4'

titletext = "Three intermezzi, opus 117 by Brahms\n\n" + \
  "Performed by Alexander Hanysz\n" + \
  "October 2020\n" + \
  "Virtual Grotrian piano from Pianoteq"

from pygame.colordict import THECOLORS as COLOURS
NOTE_COLOURS = [COLOURS[c] for c in ["white", "cyan", "blue", "magenta", "red"]]

LOWEST_NOTE = -2 # midi note number of the bottom of the screen
HIGHEST_NOTE = 107

INNER_BRIGHTNESS=0.5

FPS=30
