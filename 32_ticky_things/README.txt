To create a rendition of "32 Ticky Things after Ligeti":

Prerequisites: a Linux system with python3, csound and the python libraries pygame, soundfile, cairo, json and pandas; some audio samples of percussion sounds that you'd like to use.

Step 1: Create a folder containing some .wav files of samples (can be either mono or stereo; if stereo, only the left channel will be used)

Step 2: Create a text file containing a list of colour names from the pygame dictionary pygame.colordict.THECOLORS.  The script list_good_colours.py will list all the colours that are bright enough to show well against a black background.  Or you can make your own list if you prefer.

Step 3: Create a json file with overall parameters (use parameters.json as a template)

Step 4: Run metadata_to_csv.py to create a note list (.csv file)

Step 5: Run csv_to_csound.py to create a Csound score (.csd file)

Step 6: Edit csd_to_video.py as needed (look at variable names in all caps).  Then run csd_to_video.py to convert the score plus Csound output to a video

Step 7: Watch the video and decide if you want to change anything.  Go back to a previous step and edit one or more of the input files as appropriate.  (Most promising is to play with the csv file and re-run steps 5 and 6.)  Hint: if you're having trouble identifying which sound goes with which row of the csv file, run show_colours.py
