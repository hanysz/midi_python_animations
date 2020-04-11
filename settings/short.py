# Use midi file b as it's very short
# but we don't have corresponding audio, so this will look and sound weird
MIDI_FILE = '/home/alex/midi/python_animations/midi/b.mid'
WAV_FILE_ORIGINAL = '/audio/2013-nov-concert/scarlatti-K440.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 190 # length of the video file to be generated, in seconds
AUDIO_OFFSET = 0 # number of seconds late to start the audio
MIDI_OFFSET = -7.0 # number of seconds to shift midi events by
MIDI_OFFSET = -2.5 # number of seconds to shift midi events by
TRACK_ORDER = [1, 2]
OUTPUT_FILE = '/home/alex/midi/python_animations/scarlatti_K440.mp4'

