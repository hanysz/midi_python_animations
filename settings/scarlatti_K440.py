MIDI_FILE = '/home/alex/midi/python_animations/midi/scarlatti-K440.mid'
WAV_FILE_ORIGINAL = '/audio/2013-nov-concert/scarlatti-K440.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 190 # length of the video file to be generated, in seconds
AUDIO_OFFSET = 0 # number of seconds late to start the audio
MIDI_OFFSET = -7.0 # number of seconds to shift midi events by
TRACK_ORDER = [2, 3]
OUTPUT_FILE = '/home/alex/midi/python_animations/scarlatti_K440.mp4'

TRACK_PLANES = [0, 0, 1, 2] # for piano_roll_3D version
