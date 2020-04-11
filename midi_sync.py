from __future__ import division # so that a/b for integers evaluates as floating point
import mido, sys, os

if len(sys.argv) != 5:
  print("Usage: midi_sync infile source dest outfile")
  print("  infile = input MIDI file")
  print("  source = track number of source timing data")
  print("  dest = track number of destination timing data")
  print("  outfile = output MIDI file")
  sys.exit()

# source and dest tracks should each have a series of note-on events at distinct times.
# The mapping source event number n -> dest event number n
# defines a piecewise linear map of time.
# This map is applied to the timing data of all tracks *except* source and dest,
# and the transformed file is saved.

# Use this to sync a MIDI file with audio,
# by syncing selected notes (source track), e.g. the first beat of each bar,
# or anything else that clearly stands out in the audio,
# and then use this script to sync the other notes.

if not os.path.isfile(sys.argv[1]):
  print("Error: input file " + sys.argv[1] + " does not exist")
  # We'll also get an error if the input file exists but is a directory, which is OK
  sys.exit()

if os.path.exists(sys.argv[4]):
  print("Error: output file " + sys.argv[4] + " already exists")
  sys.exit()

mid = mido.MidiFile(sys.argv[1])
source = int(sys.argv[2])
dest = int(sys.argv[3])
outfile = sys.argv[4]
numtracks = len(mid.tracks)

if numtracks-1 < source: # -1 because tracks are numbered from zero
  print("Error: input file has tracks numbered from 0 up to " + str(numtracks-1)
           + ", but source track is number " + str(source))
  sys.exit()

if numtracks < source:
  print("Error: input file has tracks numbered from 0 up to " + str(numtracks-1)
           + ", but destination track is number " + str(dest))
  sys.exit()


def track_to_time_list(t):
# t is a MIDI track
# Return a list of times of all note-on events in t, in ticks
  answer = []
  abstime = 0
  for e in t:
    abstime += e.time
    if e.type == 'note_on' and e.velocity > 0:
      answer.append(abstime)
  return answer

source_times = track_to_time_list(mid.tracks[source])
dest_times = track_to_time_list(mid.tracks[dest])

if len(source_times) != len(dest_times):
  print("Error: source track has " + str(len(source_times)) + " note on events, " +
        "but destination track has " + str(len(dest_times)) + " note on events.")
  sys.exit()

def interpolate(start_time, end_time, ratio):
  return(start_time + int(round((end_time-start_time) * ratio)))

for i in range(numtracks):
  if i != source and i != dest:
    abstime = 0
    index = 0
    prev_time = 0
    for e in mid.tracks[i]:
      abstime += e.time
      while abstime >= source_times[index]:
        index += 1
	if index >= len(source_times):
	  print("Error: track number " + str(i) +
	        " has events after the last source event.")
	  sys.exit()
      if abstime >= source_times[0]: # index will be at least 1
        ratio = (abstime - source_times[index-1]) / \
	          (source_times[index]-source_times[index-1])
	new_abstime = interpolate(dest_times[index-1], dest_times[index], ratio)
	e.time = new_abstime - prev_time
	prev_time = new_abstime
      else:
        prev_time = 0
	e.time = 0

mid.save(outfile)
      
