MIDI_FILE = '/home/alex/midi/2021-02-suite_bergamasque/suite_bergamasque_v01.mid'
WAV_FILE_ORIGINAL = '/home/alex/midi/2021-02-suite_bergamasque/suite_bergamasque_v02.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 970 # length of the video file to be generated, in seconds
AUDIO_OFFSET = 7 # number of seconds late to start the audio
MIDI_OFFSET = 7 # number of seconds to shift midi events by
#AUDIO_OFFSET = 1 # for testing
#MIDI_OFFSET = 1 # for testing
TRACK_ORDER = [1]
OUTPUT_FILE = '/home/alex/midi/python_animations/suite_bergamasque.mp4'

