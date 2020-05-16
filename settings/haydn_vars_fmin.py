MIDI_FILE = '/home/alex/midi/2020-polglase+haydn/2020-05-16-haydn_edited.mid'
MIDI_BACKGROUND = '/home/alex/midi/2020-polglase+haydn/2020-05-16-haydn_background_synced.mid'
WAV_FILE_ORIGINAL = '/home/alex/midi/2020-polglase+haydn/2020-05-14-haydn_variations.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
LENGTH = 13*60+10 # length of the video file to be generated, in seconds
#LENGTH = 20 # for testing
AUDIO_OFFSET = 8.65 # number of seconds late to start the audio
MIDI_OFFSET = 8.5 # number of seconds to shift midi events by

# For testing:
#AUDIO_OFFSET = 1.15 # number of seconds late to start the audio
#MIDI_OFFSET = 1 # number of seconds to shift midi events by

OUTPUT_FILE = '/home/alex/midi/python_animations/haydn_vars_fmin.mp4'

TITLE_TEXT = 'Variations in F minor "Un piccolo divertimento"\n' + \
             "by Haydn\n\n" + \
	     "Performed by Alexander Hanysz\n" + \
	     "April 2020\n\n" + \
	     "Virtual Bechstein piano (1899) from Pianoteq"

SECTION_STARTS = (1.165, 25.372, 49.566, 60+24.744,
               2*60+0.272, 2*60+21.165, 2*60+42.090, 3*60+2.886,
	       3*60+24.256, 3*60+47.754, 4*60+10.914, 4*60+44.866,
	       5*60+19.157, 5*60+39.620, 5*60+59.945, 6*60+19.849,
	       6*60+40.843, 7*60+4.463, 7*60+27.804, 8*60+1.490,
	       8*60+37.079, 8*60+52.907, 9*60+8.989, 9*60+28.473,
	       9*60+49.297, 10*60+13)
PAGE_STARTS = [x-0.5 for x in SECTION_STARTS]
SCROLL_TIME = 10*60+1

# silly little variations for testing
#MIDI_FILE = '/home/alex/midi/python_animations/midi/stupid_variations.mid'
#MIDI_BACKGROUND = '/home/alex/midi/python_animations/midi/stupid_variations-background.mid'
#WAV_FILE_ORIGINAL = '/home/alex/midi/python_animations/midi/stupid_variations.wav'
#PAGE_STARTS = (0, 6.257, 12.5, 18.6, 24.8)
#SCROLL_TIME = 21.3
#LENGTH = 32
#MIDI_OFFSET = 1
#AUDIO_OFFSET = 1.2

LOWEST_NOTE = 25
HIGHEST_NOTE = 94

COLOUR_MODE = "channel"
#BG_COLOUR = (138,225,54) # light green
BG_COLOUR = (175,231,238)
#FG_COLOURS = [(38,87,255), 0, 0, 0, 0, 0, (250,238,40)]
FG_COLOURS = [(49,80,84), 0, 0, 0, 0, 0, (72,187,201)]
  # channels 0 and 7 in blue and yellow
#BACKGROUND = (70,141,40) # mid green
BACKGROUND = (124,131,132)


