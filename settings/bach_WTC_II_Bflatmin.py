OUTPUT_FILE = '/home/alex/midi/python_animations/bach_wtc2_Bflatmin.mp4'
#MIDI_FILE = '/home/alex/midi/magenta_transcriptions/13-bach-Bflatmin-II-edited.mid'
#WAV_FILE_ORIGINAL = '/home/alex/midi/magenta_transcriptions/13-bach-Bflatmin-II.wav'
MIDI_FILE = '/home/alex/midi/magenta_transcriptions/13-bach-Bflatmin-II-theme_highlighted.mid'
WAV_FILE_ORIGINAL = '/home/alex/midi/magenta_transcriptions/13-bach-Bflatmin-II_noise_reduced.wav'
LENGTH = 415 # length of the video file to be generated, in seconds

AUDIO_OFFSET = 8 # number of seconds late to start the audio
MIDI_OFFSET = 7.92 # number of seconds to shift midi events by
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio

TRACK_ORDER = [1,2,3,4]

from pygame.colordict import THECOLORS as COLOURS

BALL_COLOURS_HEX = ['FFFFFF', 'FF83FA', 'EE1289', '8B20AB', '551AEB']
# 'FFFFFF' is a dummy value: track 0 never gets drawn
# sop, alto, tenor, bass are tracks 1, 4, 6, 9
# other tracks are extra voices
BALL_COLOURS = [tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) for h in BALL_COLOURS_HEX]

BACKGROUND = COLOURS['black']

TITLE_TEXT = \
'''J.S. Bach: Prelude and Fugue in B flat minor
From book 2 of The Well-Tempered Clavier

Performed by Alexander Hanysz
Recorded live in Elder Hall, The University of Adelaide

August 2011'''
