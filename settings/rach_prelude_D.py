MIDI_FILE = '/home/alex/midi/python_animations/midi/2016-11-Rachmaninoff_prelude_D_v3.mid'
WAV_FILE_ORIGINAL = '/audio/2013-nov-concert/15-rachmaninoff.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 263 # length of the video file to be generated, in seconds
AUDIO_OFFSET = 6.9 # number of seconds late to start the audio
MIDI_OFFSET = -1.1 # number of seconds to shift midi events by
TRACK_ORDER = [3, 5, 4]
# For the Rachmaninoff MIDI, I want to draw bass then descant then melody in that order
OUTPUT_FILE = '/home/alex/midi/python_animations/rachmaninoff-prelude-D-Nov2016.mp4'

titletext = "Prelude in D major by Sergei Rachmaninoff\n\n" + \
    "Performed by Alexander Hanysz\nLive recording, Pilgrim Church, Adelaide\n" + \
    "10th November 2013"

