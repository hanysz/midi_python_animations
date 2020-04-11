MIDI_FILE = '/home/alex/midi/python_animations/midi/chopin.mid'
WAV_FILE_ORIGINAL = '/home/alex/midi/python_animations/chopin.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 190 # length of the video file to be generated, in seconds
AUDIO_OFFSET = 0 # number of seconds late to start the audio
MIDI_OFFSET = 0.2 # number of seconds to shift midi events by
TRACK_ORDER = [1, 2, 3]
OUTPUT_FILE = '/home/alex/midi/python_animations/chopin_mazurka_op24_no2.mp4'

TITLE_TEXT = "Chopin Mazurka in A minor, opus 24 no. 2"

TRACK_PLANES = [0, 0.5, 2, 1] # for the piano_roll_3D view; indexed by track number
