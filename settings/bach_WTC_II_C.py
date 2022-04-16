OUTPUT_FILE = '/home/alex/midi/python_animations/bach_wtc2_C.mp4'
MIDI_FILE = '/home/alex/midi/magenta_transcriptions/01-bach-Cmaj-II-theme_highlighted.mid'
WAV_FILE_ORIGINAL = '/home/alex/midi/magenta_transcriptions/01-bach-Cmaj-II_noise_reduced.wav'
LENGTH = 244 # length of the video file to be generated, in seconds

AUDIO_OFFSET = 8 # number of seconds late to start the audio
MIDI_OFFSET = 7.92 # number of seconds to shift midi events by
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio

TRACK_ORDER = [1,2,3,4,5,6,7,8,9]

from pygame.colordict import THECOLORS as COLOURS
BALL_COLOURS = [COLOURS[c] for c in
  ['white', 'orchid1', 'hotpink1', 'violetred1', 'deeppink2', 'deeppink2',
   'magenta4', 'magenta4', 'purple4', 'purple4']
]

BALL_COLOURS_HEX = ['FFFFFF', 'FF83FA', 'FF6EB4', 'FF3E96', 'EE1289', 'EE1289',
   '8B20AB', '8B20AB', '551AEB', '551AEB']
# 'FFFFFF' is a dummy value: track 0 never gets drawn
# sop, alto, tenor, bass are tracks 1, 4, 6, 9
# other tracks are extra voices
BALL_COLOURS = [tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) for h in BALL_COLOURS_HEX]

BACKGROUND = COLOURS['black']

TITLE_TEXT = \
'''J.S. Bach: Prelude and Fugue in C major
From book 2 of The Well-Tempered Clavier

Performed by Alexander Hanysz
Recorded live in Elder Hall, The University of Adelaide

August 2011'''
