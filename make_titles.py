# Create a few seconds of title screen (for splicing onto other videos)

from moviepy.editor import *

VIDEO_SIZE = (1920,1280)
#VIDEO_SIZE = (1280,720)
LENGTH = 10 # seconds
TEXT_SIZE = 45  # 30 works well for 1280x1720, or 45 for 1920x1280
FPS = 29.97
OUTPUT_FILE = 'titles.mp4'

#TITLE_TEXT = "Variations on a Czech Folksong\n'Andulko'\n" + \
#             'Composed by John Polglase\n' + \
#	     '\nPerformed by Alexander Hanysz\n' + \
#	     '\nVirtual Steinway D piano by Pianoteq 6'

TITLE_TEXT  = \
"""Sonata quasi una fantasia, op.27 no.2
"Moonlight Sonata"

Composed by Ludwig van Beethoven

Performed by Alexander Hanysz


Virtual Grimaldi harpsichord by Pianoteq 7
Wah and distortion effects by Zebrify

Images by Celestia"""

BACKGROUND = (0, 0, 0) # black background

title_text = TextClip(TITLE_TEXT, font='Segoe-Script', fontsize = TEXT_SIZE, color = 'white')
title_text = title_text.set_pos('center').set_duration(LENGTH).fadein(3, BACKGROUND).fadeout(2.5, BACKGROUND)
title_background = ColorClip(size = VIDEO_SIZE, color = BACKGROUND, duration = 8.5)
titles = CompositeVideoClip([title_background, title_text])
#main_clip = main_clip.subclip(0,10) # for quick testing
#video = concatenate_videoclips([titles, main_clip])
titles.write_videofile(OUTPUT_FILE, fps=FPS)
