MIDI_FILE = '/home/alex/midi/python_animations/midi/schoenberg_op19_2022-03-10-display.mid'
MIDI_BACKGROUND = MIDI_FILE
WAV_FILE_ORIGINAL = '/home/alex/midi/2020-10-schoenberg/schoenberg_op19_2022-03-10.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 393 # length of the video file to be generated, in seconds

AUDIO_OFFSET = 8.65 # number of seconds late to start the audio
MIDI_OFFSET = 8.5 # number of seconds to shift midi events by

# For testing:
#AUDIO_OFFSET = 1.15 # number of seconds late to start the audio
#MIDI_OFFSET = 1 # number of seconds to shift midi events by

OUTPUT_FILE = '/home/alex/midi/python_animations/schoenberg_op19.mp4'

TITLE_TEXT = \
'''Six little piano pieces, opus 19
by Arnold Schoenberg

Performed by Alexander Hanysz
Audio synthesised using Zebra'''

SECTION_STARTS = (-1.5, 97.7, 159.7, 235, 268.9, 306.8, 383, 500) # actual start times from audio
SECTION_STARTS = [x-1.3 for x in SECTION_STARTS] # shift earlier to allow for fade-in

PAGE_STARTS = [x-0.5 for x in SECTION_STARTS]
SCROLL_TIME = 100000000 # never scroll for this one

FADE_TIME = 4 # time in seconds for each page to fade out/in

from pygame.colordict import THECOLORS as COLOURS
# revised tracks 8th March
# 1-3 flute, 4 bells, 5-7 viola, 8 tremolo, 9-11 vln, 12-14 vc, 15-16 bsn,
# 17 marimba, 18-19 horn, 20 gong
# fl, bells, vln, trem in blues
# vc, bsn, horn in greens
# bells, marimba, gong in yellow
#INSTR_COLOURS = [COLOURS[c] for c in
#  ['magenta', 'tan', 'cyan', 'lightskyblue', 'darkcyan', 'steelblue', 'blue', 'springgreen', 'pink', 'orange']]
INSTR_COLOURS = [COLOURS[c] for c in
  ['lightskyblue', 'gold2', 'dodgerblue3', 'orchid3', 'lightgreen',
   'green4', 'royalblue4', 'darkorange2', 'limegreen', 'orangered3']]
#INSTR_COLOURS = [COLOURS[c] for c in
#  ['lightskyblue', 'gold2', 'dodgerblue3', 'darkcyan', 'orchid3',
#   'springgreen4', 'royalblue4', 'darkorange2', 'forestgreen', 'orangered3']]
INST_PER_TRACK = [0, 0,0,0, 1, 2,2,2, 3, 4,4,4, 5,5,5, 6,6, 7, 8,8, 9]
# The first 0 is a placeholder for the tempo track
FG_COLOURS = [INSTR_COLOURS[i] for i in INST_PER_TRACK]

#FG_COLOURS[16] = COLOURS['white']
#FG_COLOURS[15] = COLOURS['white']

LOWEST_NOTE = 25 # midi note number of the bottom of the screen
HIGHEST_NOTE = 95

INNER_BRIGHTNESS=0.5

FPS=30
#FPS=10 # testing


COLOUR_MODE = "track"
BG_COLOUR = (175,231,238)
BACKGROUND = (124,131,132)


