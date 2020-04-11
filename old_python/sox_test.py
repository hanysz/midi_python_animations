import os


WAV_FILE_ORIGINAL = '/audio/2013-nov-concert/15-rachmaninoff.wav'
WAV_FILE_TEMP = '/tmp/animation_audio.wav' # temporary store for padded version of audio
AUDIO_OFFSET = 3
LENGTH = 60 # length of the video file to be generated, in seconds
os.system('/usr/bin/sox '+ WAV_FILE_ORIGINAL + ' ' + WAV_FILE_TEMP +
	  ' pad '+str(AUDIO_OFFSET) + ' trim 0 ' + str(LENGTH)
	 )
