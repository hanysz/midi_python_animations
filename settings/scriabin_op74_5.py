import pygame
MIDI_FILE = '/home/alex/midi/python_animations/midi/scriabin_op74/2016-12-Scriabin_op74_no5_v04.mid'
WAV_FILE_ORIGINAL = '/audio/2013-nov-concert/10-scriabin.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 58 # length of the video file to be generated, in seconds
AUDIO_OFFSET = 0 # number of seconds late to start the audio
MIDI_OFFSET = 0 # number of seconds to shift midi events by
TRACK_ORDER = [2, 3, 4, 5, 6]
OUTPUT_FILE = '/home/alex/midi/python_animations/scriabin_prelude_op74no5.mp4'

TITLE_TEXT = "Scriabin prelude opus 74 number 5"
