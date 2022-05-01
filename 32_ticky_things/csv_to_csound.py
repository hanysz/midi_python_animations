# Read CSV file with columns for:
#  sample (full pathname of a *.wav file)
#  start_time (time of first playback of that sample, in seconds)
#  bpm (rate of playback in beats per minute)
#  slowdown_time (time in seconds at which it starts to slow down)
#  slowdown_ratio (number >1, ratio between successive tick times after slowdown_time)
#  stop_time (last tick is shortly before this time)
#  amplitude (playback volume for this sample 0-1)
#  pan (stereo position from 0=left to 1=right)
#  predelay (reverb predelay time in milliseconds)

# Inspect each .wav file to get max amplitude and duration
# Create a csound file to play the samples

import sys, os, pandas, soundfile, numpy
from math import log2, ceil

if len(sys.argv) != 3:
  sys.exit("Usage: python csv_to_csound.py input.csv output.csd")
infilename = sys.argv[1]
outfilename = sys.argv[2]

if os.path.exists(outfilename):
  sys.exit(f"Error: output file {outfilename} already exists")

if not os.path.exists(infilename):
  sys.exit(f"Error: input file {infilename} does not exist")

metadata = pandas.read_csv(infilename)
outfile = open(outfilename, "w")

outfile.write(
'''<CsoundSynthesizer>
<CsOptions>
;-odac ; for testing.  Later on we'll save
</CsOptions>
; ==============================================
<CsInstruments>

sr      =       44100
ksmps   =       40 ; shouldn't be using modulation, so a big number here is OK
nchnls  =       2
0dbfs   =       1

garvbl   init    0
garvbr   init    0

instr playwave
iwavnum = p4
iamp = p5
ipan = p6 ;0=hard left 0.5=centre, 1=hard right
irvbsend = p7 ; reverb send amount
idelay = p8 ; reverb pre-delay in seconds; 0.001 to 0.06 works well

a1  oscil iamp, sr/ftlen(iwavnum), iwavnum

aleft, aright pan2 a1, ipan
out aleft, aright
if idelay>0 then ; delay time of zero will raise an error
  ald = delay(aleft, idelay)
  ard = delay(aright, idelay)
else
  ald=aleft
  ard=aright
endif

garvbl = garvbl + ald * irvbsend
garvbr = garvbr + ard * irvbsend
endin

instr reverb_bus
idur    =       p3
irvbtim =       p4
ihiatn  =       p5
arvbl, arvbr    freeverb garvbl, garvbr, irvbtim, ihiatn
        outs    arvbl, arvbr
garvbl   =       0
garvbr   =       0
        endin


</CsInstruments>
; ==============================================
<CsScore>
''')

metadata['fnum'] = range(1, metadata.shape[0]+1)
# dummy values, fix later
metadata['duration'] = 2.1
metadata['amp_adjusted'] = 1.1

for i, s in enumerate(metadata["sample"]):
  print(f"Inspecting sound file {s}")
  data, samplerate = soundfile.read(s)
  numchannels  = 1 if len(data.shape)==1 else data.shape[1]
  numsamples = data.shape[0]
  print(f"Got {numsamples} samples with {numchannels} channel{'s' if numchannels>1 else ''}")
  loudest = numpy.max(abs(data))
  metadata.at[i,'amp_adjusted'] = metadata.at[i,'amplitude']/loudest
  metadata.at[i,'duration'] = numsamples/samplerate
  tablesize = 2**ceil(log2(numsamples)) # csound table sizes must be a power of 2
  outfile.write(f'f {i+1} 0 {tablesize} 1 "{s}" 0 4 1\n')
  # the 0, 1, 0, 4 1 represent
  #  load wave at time zero, use GEN1 to load wave, skip nothing
  #  format code 4 = 16-bit, read only left channel if stereo


end_time = max(metadata['stop_time'])+14
outfile.write(f'\ni "reverb_bus" 0 {end_time} 0.9 .7')
outfile.write(
''' ; start, duration, size(0-1), high freq rolloff (0-1)

;               time    dur     fn      amp     pan     rvbsend predelay
''')


print(metadata)


reverbsend = 0.5 # may need to adjust this if I change the reverb algorithm
for row in metadata.itertuples(index=True, name='Pandas'):
  #outfile.write(f"sample {row.sample} ticks at {row.bpm} beats per minute\n")
  ticktime = row.start_time
  interval = 60/row.bpm
  while ticktime < row.stop_time:
    outfile.write(f'i "playwave"\t{ticktime}\t{row.duration}\t{row.fnum}\t')
    outfile.write(f'{row.amp_adjusted}\t{row.pan}\t{reverbsend}\t')
    outfile.write(f'{row.predelay/1000}\n')
    if ticktime > row.slowdown_time:
      interval *= row.slowdown_ratio
    ticktime += interval

outfile.write(
'''
</CsScore>
</CsoundSynthesizer>
''')

outfile.close()
print(f"Finished.  Wrote csound score to file {outfilename}")
