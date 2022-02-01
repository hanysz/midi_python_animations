# Take tempo events from track 0 and copy them into other tracks
# so that my python scripts can read them without a lot of extra work!

# Assumes we're working on Linux with midicsv command line utility installed,
# see http://www.fourmilab.ch/webtools/midicsv/

infile = "/home/alex/midi/2021-szymanowski_studies_op4/szymanowski_op4_all-channel_is_motif.mid"
outfile = "/home/alex/midi/2021-szymanowski_studies_op4/szymanowski_op4_all-channel_is_motif_fixed.mid"
tempfile = "/tmp/deleteme.csv"

if (file.exists(tempfile)) {
  cat("CSV file", tempfile, "already exists\n")
  stop()
}

sectime = function(x) round(x/960/2, digits=3) # convert ticks to seconds

minsectime = function(x) paste0(floor(x/60),":",round(x%%60, digits=3))

notenames = c("B#", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
notename = function(n) {
  # n is a MIDI note number, 60 = C5 = middle C
  paste0(notenames[n%%12 + 1], floor(n/12))
}

system(paste("midicsv", infile, tempfile))
df = read.csv(tempfile, header=FALSE, stringsAsFactors = FALSE)
file.remove(tempfile)
names(df)[1:6] = c("track", "tick", "type", "channel", "note", "velocity")
# nb columns 4 and 5 can have different meanings for event types other than notes
# See documentation at http://www.fourmilab.ch/webtools/midicsv/
# or man page "man 5 midicsv"


merge_new_events = function(midifile, new_rows, target_track) {
  new_rows$track = target_track
  t = subset(midifile, track==target_track)
  N = nrow(t)
  newtrack = rbind(t[1:(N-1),], new_rows) # N-1 because end-of-file marker doesn't have a time but must stay at the end
  newtrack = newtrack[order(newtrack$tick),]
  newtrack = rbind(newtrack, t[N,])
  
  track_start = min(which(midifile$track==target_track))
  track_end   = max(which(midifile$track==target_track))
  
  before=head(midifile, track_start-1)
  after = tail(midifile, nrow(midifile)-track_end)
  
  return(rbind(before, newtrack, after))
}

tempos = subset(df, type==" Tempo")
N = nrow(tempos)
for (t in 2:max(df$track)) df = merge_new_events(df, tempos, t)

write.table(df, tempfile, sep=",", na="", quote=FALSE, row.names=FALSE, col.names=FALSE)
system(paste("csvmidi", tempfile, outfile))
file.remove(tempfile)

