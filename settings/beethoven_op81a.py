MIDI_FILE = '/home/alex/midi/python_animations/midi/beethoven_LesAdieuxIII_v03.mid'
WAV_FILE_ORIGINAL = '/audio/2008-anpa_audition/LesAdieuxIII-edited.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 378 # length of the video file to be generated, in seconds
AUDIO_OFFSET = 0.43 # number of seconds late to start the audio
MIDI_OFFSET = -4.7 # number of seconds to shift midi events by
TRACK_ORDER = [3]
OUTPUT_FILE = '/home/alex/midi/python_animations/LesAdieuxIII.mp4'

TITLE_TEXT = \
  "Beethoven sonata in E flat, op 81a, 'Les Adieux\n" + \
  "Movement 3: The Return\n\n" + \
  "Performed by Alexander Hanysz\nRecorded in Grainger Studio, Adelaide\n" + \
  "May 2008"
