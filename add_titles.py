from __future__ import division # so that a/b for integers evaluates as floating point

# Add title text to an existing video file
# At the moment, moviepy only seems to work for me with python3 not python2

from moviepy.editor import *

INPUT_FILE = 'temp.mp4'
OUTPUT_FILE = 'andulko_test.mp4'

TITLE_TEXT = "Variations on a Czech Folksong\n'Andulko'\n" + \
             'Composed by John Polglase\n' + \
	     '\nPerformed by Alexander Hanysz\n' + \
	     '\nVirtual Steinway D piano by Pianoteq 6'
BACKGROUND = (0, 0, 0) # black background

main_clip = VideoFileClip(INPUT_FILE)
title_text = TextClip(TITLE_TEXT, font='Segoe-Script', fontsize = 30, color = 'white')
title_text = title_text.set_pos('center').set_duration(8.5).fadein(3, BACKGROUND).fadeout(2.5, BACKGROUND)
title_background = ColorClip(size = main_clip.size, color = BACKGROUND, duration = 8.5)
titles = CompositeVideoClip([title_background, title_text])
#main_clip = main_clip.subclip(0,10) # for quick testing
video = concatenate_videoclips([titles, main_clip])
video.write_videofile(OUTPUT_FILE)
