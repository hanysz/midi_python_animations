MIDI_FILE = '/home/alex/midi/2021-szymanowski_studies_op4/szymanowski_op4_all-channel_is_motif_fixed.mid'
WAV_FILE_ORIGINAL = '/home/alex/midi/2021-szymanowski_studies_op4/szymanowski_op4_all.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 853 # length of the video file to be generated, in seconds
AUDIO_OFFSET = 8.2 # number of seconds late to start the audio
MIDI_OFFSET = 8.2 # number of seconds to shift midi events by
TRACK_ORDER = [4,3,2,1]
OUTPUT_FILE = '/home/alex/midi/python_animations/szymanowski_op4.mp4'


titletext = '''Four studies, op 4 by Karol Szymanowski

Performed by Alexander Hanysz
April 2021
Virtual Grotrian piano from Pianoteq '''
#titletext = " "

from pygame.colordict import THECOLORS as COLOURS
NOTE_COLOURS_1 = dict([
  (1, COLOURS["turquoise3"]),
  (2, COLOURS["slateblue3"]),
  (3, COLOURS["darkorchid2"]),
  (4, COLOURS["deeppink1"])
])

NOTE_COLOURS_2 = dict([
  (1, COLOURS["blue"]),
  (2, COLOURS["deepskyblue2"]),
  (3, COLOURS["white"]),
  (4, (128, 0, 30))
])

NOTE_COLOURS_3 = dict([
  (1, COLOURS["grey88"]),
  (2, (0, 83, 255)),   # formerly "blue"
  (3, COLOURS["seagreen1"]),
  (4, COLOURS["gold1"])
])

NOTE_COLOURS_4 = dict([
  (1, COLOURS["violet"]),
  (2, COLOURS["lavenderblush2"]),
  (3, COLOURS["mediumslateblue"]),
  (4, COLOURS["dodgerblue3"])
])

NOTE_COLOURS = NOTE_COLOURS_1

NOTE_SHAPES = dict([
  (0, "circle"),
  (6, "raindrop"),
  (12, "star")
])

COLOUR_CHANGES = [
  [-1000, NOTE_COLOURS_1],
  [231, NOTE_COLOURS_2],
  [359, NOTE_COLOURS_3],
  [628, NOTE_COLOURS_4]
]


BACKGROUND_CHANGES = [
  [-1000, COLOURS["black"]],
  [223, COLOURS["black"]],
  [234, COLOURS["skyblue1"]],
  [350, COLOURS["skyblue1"]],
  [361, COLOURS["darkblue"]],
  [598, COLOURS["darkblue"]],
  [628, COLOURS["black"]]
]

LOWEST_NOTE = 18 # midi note number of the left of the screen
HIGHEST_NOTE = 107

INNER_BRIGHTNESS=0.7

FPS=30
