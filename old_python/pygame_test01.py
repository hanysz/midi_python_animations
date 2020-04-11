# From https://inventwithpython.com/chapter17.html
# Modified in an attempt to generate 2 seconds of video
#  and save to a file
import pygame, sys, time
from pygame.locals import *
import moviepy.editor as mpy

# set up pygame
pygame.init()

# set up the window
WINDOWWIDTH = 400
WINDOWHEIGHT = 400
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)
pygame.display.set_caption('Animation in progress')

# set up the colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# set up the block data structure
b1 = {'rect':pygame.Rect(300, 80, 50, 100), 'color':RED}
b2 = {'rect':pygame.Rect(200, 200, 20, 20), 'color':GREEN}
b3 = {'rect':pygame.Rect(100, 150, 60, 60), 'color':BLUE}

def make_frame(t):
    # draw the black background onto the surface
    windowSurface.fill(BLACK)

    b1['rect'].left = 200*t
    b2['rect'].top = 150*t
    b3['rect'].left = 300 - 100*t

    # draw the block onto the surface
    pygame.draw.rect(windowSurface, b1['color'], b1['rect'])
    pygame.draw.rect(windowSurface, b2['color'], b2['rect'])
    pygame.draw.rect(windowSurface, b3['color'], b3['rect'])

    # draw the window onto the screen
    # pygame.display.update()
    # not needed as all we're doing is creating a file
    return  pygame.surfarray.array3d(windowSurface)

clip = mpy.VideoClip(make_frame, duration=4) # 4 seconds
#clip.write_gif("testmovie.gif",fps=25)
clip.write_videofile("testmovie.mp4", fps=30)
