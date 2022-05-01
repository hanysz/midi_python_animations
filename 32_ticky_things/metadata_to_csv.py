# Create CSV file with columns for:
#  sample (full pathname of a *.wav file)
#  start_time (time of first playback of that sample, in seconds)
#  bpm (rate of playback in beats per minute)
#  slowdown_time (time in seconds at which it starts to slow down)
#  slowdown_ratio (number >1, ratio between successive tick times after slowdown_time)
#  stop_time (last tick is shortly before this time)
#  amplitude (playback volume for this sample 0-1)
#  pan (stereo position from 0=left to 1=right)
#  predelay (reverb predelay time in milliseconds)
#  colour (pygame colours name for video: randomly chosen)
#  duration

# Inspect each .wav file to get suggested amplitude and duration
# Scale amplitude according to perceived loudness as measured by RMS of first 0.1 sec
# (may need to edit this by hand after listening to the results)

import sys
if len(sys.argv) != 3:
  sys.exit("Usage: python csv_to_csound.py input.json output.csv")
import sys, os, pandas, soundfile, json, random, re, math, numpy

infilename = sys.argv[1]
outfilename = sys.argv[2]

if os.path.exists(outfilename):
  sys.exit(f"Error: output file {outfilename} already exists")

if not os.path.exists(infilename):
  sys.exit(f"Error: input file {infilename} does not exist")

with open(infilename) as f:
  metadata = json.load(f)

random.seed(metadata['random_seed'])

colours = []
with open(metadata['colour_list']) as f:
  for c in f.readlines():
    colours.append(c)

N = metadata['num_samples']
samples = os.listdir(metadata['sample_dir'])
waves_only = re.compile("wav$")
samples = list(filter(waves_only.search, samples))

if N > len(samples):
  sys.exit(f"Metadata ask for {N} samples, but there are only {len(samples)} *.wav files in {metadata['sample_dir']}")
samples = random.sample(samples, N)
colours = random.sample(colours, N)


# For each of start times, slowdown times, stop times
# we want to generate a list that's *approximately* equally spaced
# Start with a regular spacing and perturb it.
def perturbed_list(first, last, N):
  length = last-first
  delta = length/N/2 * 0.8
  regular_spacing = [first + i/(N-1)*length for i in range(1, N-1)]
  offsets = [random.uniform(-delta*0.8, delta*0.8) for i in range(1,N-1)]
  random_spacing = [s+o for s, o in zip(regular_spacing, offsets)]
  random_spacing = random_spacing + [first, last]
  random.shuffle(random_spacing) # this shuffles the list in place
  return(random_spacing)


start_rampdown = metadata['length'] - metadata['rampdown']
end_rampdown = (start_rampdown + metadata['length'])/2
earliest_stop = (end_rampdown + 3*metadata['length'])/4

start_times = perturbed_list(0, metadata['rampup'], N)
slowdown_times = perturbed_list(start_rampdown, end_rampdown, N)
stop_times = perturbed_list(earliest_stop, metadata['length'], N)

pans = perturbed_list(0.15, 0.85, N)
predelays = perturbed_list(3, 65, N)

# Placeholder values: we'll change these below based on the contents of the .wav file
amplitudes = [2/N]*N
bpms = perturbed_list(metadata['min_speed'], metadata['max_speed'], N)
durations = [100]*N


def RMS(x, k):
  # root mean square value of first k samples of x
  # where x is 1- or 2-channel audio data
  if len(x.shape)>1:
    x = x[:,0]
  return(math.sqrt(sum(x[0:(k-1)]**2)/k))


for i, s in enumerate(samples):
  print(f"Inspecting sound file {s}")
  data, samplerate = soundfile.read(metadata['sample_dir'] + '/' + s)
  numchannels  = 1 if len(data.shape)==1 else data.shape[1]
  numsamples = data.shape[0]
  print(f"Got {numsamples} samples with {numchannels} channel{'s' if numchannels>1 else ''}")
  loudest = numpy.max(abs(data))
  n_start = min(4410, data.shape[0])
  average = RMS(data, n_start)
  amplitudes[i] = (0.5/N) / average
  durations[i] = data.shape[0] / 44100
  max_bpm = 60/durations[i]
  if max_bpm < metadata['min_speed']:
    bpms[i] = random.uniform(max_bpm*0.7, max_bpm)
  else:
    bpms[i] = random.uniform(metadata['min_speed'],
      min(metadata['max_speed'], max_bpm))
  radii = [round(math.sqrt(60/b)*12) + 5 for b in bpms]


with open(outfilename, "w") as f:
  f.write("sample,start_time,bpm,slowdown_time,slowdown_ratio,")
  f.write("stop_time,amplitude,pan,predelay,radius,duration,colour\n")
  for sample, start_time, bpm, slowdown_time,\
      stop_time, amplitude, pan, predelay, radius, duration, colour in\
    zip(samples, start_times, bpms, slowdown_times,
        stop_times, amplitudes, pans, predelays, radii, durations, colours):
      f.write(metadata['sample_dir'])
      f.write("/")
      f.write(f'{sample},{start_time},{bpm},{slowdown_time},')
      f.write("1.1,") # slowdown ratio same for all sounds
      f.write(f'{stop_time},{amplitude},{pan},{predelay},{radius},{duration},{colour}')
      # No \n needed because the colour names have \n on the end
# I'm sure there was more elegant way to do all that, but I'm being lazy
    

print(f"Finished.  Wrote voice list to file {outfilename}")
