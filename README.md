*As of October 2023, I am no longer updating this repository.  Check https://hanysz.net/software.html to see if there are any more recent versions.*

Messy python code that makes the animations for [my YouTube channel](https://www.youtube.com/channel/UCVtiLYoo1dCpG3xOdt4y6SQ).

Created for personal use only but I don't mind if people borrow ideas from this code.  Shared here without warranty.

Update February 2022: currently in quite a messy state, as I'm in the middle of migrating from Python 2 to Python 3, and from pygame to cairo for the graphics backend!  I might tidy up one day.  Or then again, I might prefer to spend that time playing the piano.

OK, I'm not going to offer *much* technical support with this, but since someone asked so nicely: I've put a test file in the repository, including the audio and midi that you need as inputs.  (Generally, I'm not going to upload audio here, it's just for code.  This one is the exception.) So if you're working on a Linux system, you should be able to clone the entire repository, cd to the top level, and run `python3 test.py` to get 30 seconds of animated Szymanowski on your screen.  Edit line 12 of test.py to render the output as an mp4 video file.

Right now I'm on Python version 3.6.9, pygame version 1.9.6 and cairo version 1.16.2.  I haven't tested whether this works on other versions.
