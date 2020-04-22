# Fix up bad MIDI files created by PianoTeq: some note-off events may be missing or late

# Assumes we're working on Linux with midicsv command line utility installed,
# see http://www.fourmilab.ch/webtools/midicsv/

# Assumptions: one track only, 960 ticks per beat, 120 beats per minute,
#   all note_off events have velocity=64,
#   note_on with velocity=0 never happens
#   note number zero never happens

rearticulate_time = 192 # ideally, 0.1 sec between letting go of a note and playing it again
staccato_length = 100 # approx 0.05 sec for shortest notes, if possible
min_space = staccato_length + rearticulate_time
# Where a note-off event is missing:
#   if space until the next note-on is >= min-space, then insert the note-off at
#     rearticulate_time ticks before the next note-on
#   else
#     note-off goes at the midpoint between the two consecutive note-ons

args <- commandArgs(trailingOnly = TRUE)

if (length(args)==0) stop("Error: no files specified.  Please list the files to be fixed as command line arguments.")

sectime = function(x) round(x/960/2, digits=2) # convert ticks to seconds

insert_note_off = function(i, t) {
  # n = row number of corresponding note_on, t = time
  # Append the note-off to the new_rows data frame,
  # we'll insert it into the right place in df via the merge_new_notes() function
  x = df[i,]
  x$type = "Note_off_c"
  x$velocity = 64
  x$time = t
  new_rows <<- rbind(new_rows, x)
}

merge_new_notes = function() {
  N = nrow(df)
  answer = rbind(df[1:(N-1),], new_rows) # N-1 because end-of-file marker doesn't have a time but must stay at the end
  answer = answer[order(answer$time),]
  answer = rbind(answer, df[N,])
  return(answer)
}


for (infile in args) {
  cat("Processing", infile, "\n")
  tempfile = paste0(infile, ".csv")
  backupfile = paste0(infile, ".bak")
  
  if (file.exists(tempfile)) {
    cat("Skipping input file", infile, "because CSV file", tempfile, "already exists\n\n")
    next
  }
  if (file.exists(backupfile)) {
    cat("Skipping input file", infile, "because backup file", backupfile, "already exists\n\n")
    next
  }
  
  system(paste("midicsv", infile, tempfile))
  
  df = read.csv(tempfile, header=FALSE)
  names(df)[1:6] = c("track", "time", "type", "channel", "note", "velocity")
  # nb columns 4 and 5 can have different meanings for event types other than notes
  # See documentation at http://www.fourmilab.ch/webtools/midicsv/
  # or man page "man 5 midicsv"
  
  new_rows = df[NULL,]
  
  
  
  playing = rep(FALSE, 127)
  last_on = rep(0,127)
  delete_list = numeric(0)
  for (i in 1:nrow(df)) {
    if (df[i,"type"] == " Note_on_c") {
      n = df[i, "note"]
      t = df[i, "time"]
      if (n == 0) stop("Error: file contains note number zero")
      if (df[i,"velocity"] == 0) stop(paste("Error: found note-on with velocity zero, note number", n))
      if (playing[n]) {
        cat("Double note-on for note number", n, "at time", t, "(", sectime(t), "seconds)")
        delta = t - last_on[n]
        if (delta >= min_space) t2 = t - rearticulate_time
        else t2 = round((t + last_on[n])/2)
        cat(", inserting note-off at time", t2, "(", sectime(t), "seconds)\n")
        insert_note_off(i, t2)
      }
      playing[n]=TRUE
      last_on[n] = t
    }
    
    if (df[i,"type"] == " Note_off_c" ) {
      n = df[i, "note"]
      if (playing[n]) {
        playing[n]=FALSE
        #cat("Stop note number ", n, " at time ", df[i,"time"], "\n")
      }
      else {
        cat("Extra note-off for note number", n, "at time", df[i,"time"], "(", sectime(t), "seconds), deleting\n")
        delete_list = c(delete_list, i)
        # don't delete one row at a time, as it will change the subsequent row numbers,
        # instead keep a list of what to delete, and do it all in one go at the end.
      }
    }
  }
  
  # Now it's safe to delete the rows
  df = df[setdiff(1:nrow(df), delete_list),]
  
  
  output = merge_new_notes()
  write.table(output, tempfile, sep=",", na="", quote=FALSE, row.names=FALSE, col.names=FALSE)
  file.rename(infile, backupfile)
  system(paste("csvmidi", tempfile, infile))
  file.remove(tempfile)
  cat("Finished processing", infile, "\n\n")
}

