MIDI_FILE = '/win10/midi/2020-04-debussy+brahms_sync+vis/Brahms-synced-v1.mid'
WAV_FILE_ORIGINAL = '/audio/2008-anpa_audition/Brahms.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 327 # length of the video file to be generated, in seconds
AUDIO_OFFSET = 8.0 # number of seconds late to start the audio
MIDI_OFFSET = 8.0 # number of seconds to shift midi events by
TRACK_ORDER = [1]
#TRACK_ORDER = [3, 5, 4]
# For the Rachmaninoff MIDI, I want to draw bass then descant then melody in that order
OUTPUT_FILE = '/home/alex/midi/python_animations/brahms-intermezzo-op118no6.mp4'

titletext = "Intermezzo in E flat minor, opus 116 no. 6 by Brahms\n\n" + \
  "Performed by Alexander Hanysz\n" + \
  "Recorded in Grainger Studio, Adelaide\n" + \
  "March 2008\n" + \
  "Audio recorded and produced by Haig Burnell"

NOTE_COLOURS = (WHITE, CYAN, GREEN, BLUE, YELLOW, MAGENTA, CYAN, RED)

LOWEST_NOTE = 16 # midi note number of the bottom of the screen
HIGHEST_NOTE = 108

