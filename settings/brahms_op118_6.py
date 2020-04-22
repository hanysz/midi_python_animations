MIDI_FILE = 'midi/brahms-split_tracks_v3.mid'
WAV_FILE_ORIGINAL = '/audio/2008-anpa_audition/Brahms.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 327 # length of the video file to be generated, in seconds
AUDIO_OFFSET = 8.0 # number of seconds late to start the audio
MIDI_OFFSET = 8.0 # number of seconds to shift midi events by
TRACK_ORDER = [3,4,2,1]
OUTPUT_FILE = '/home/alex/midi/python_animations/brahms-intermezzo-op118no6.mp4'

titletext = "Intermezzo in E flat minor, opus 116 no. 6 by Brahms\n\n" + \
  "Performed by Alexander Hanysz\n" + \
  "Recorded in Grainger Studio, Adelaide\n" + \
  "May 2008\n" + \
  "Audio recorded and produced by Haig Burnell"

NOTE_COLOURS = (WHITE, CYAN, BLUE, MAGENTA, RED)

LOWEST_NOTE = 11 # midi note number of the bottom of the screen
HIGHEST_NOTE = 100

INNER_BRIGHTNESS=0.5
