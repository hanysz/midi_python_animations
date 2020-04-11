from __future__ import division # so that a/b for integers evaluates as floating point
import mido
import sys


mid = mido.MidiFile(sys.argv[1])
ticks_per_second = 48
# To do: read this from the MIDI file
# Need to look for two message types:
#  set_tempo with tempo in microseconds per crotchet
#  e.g. 500000 is 120bpm
#  time_signature with clocks_per_click

class Note(object):
  #def _init_(self, note, t0, t1, vel, track, channel):
  __slots__ = ['note', 't0', 't1', 'vel', 'track', 'channel']
  # add a __str__(self) method for debugging?
  def __str__(self):
    answer = 'Note number ' + str(self.note)
    answer += ' time ' + str(self.t0) + '-' + str(self.t1)
    answer += '; vel ' + str(self.vel) + ', track ' + str(self.track)
    answer += ', ch' + str(self.channel)
    return answer

def isKeyDown(e):
  # e is a MIDI event.
  return (e.type == 'note_on' and e.velocity > 0)
  # relying on short circuit evaluation!

def isKeyUp(e):
  return (e.type == 'note_off' or (e.type == 'note_on' and e.velocity == 0))

# Step through the file and create notes
allnotes = []
# Keep a pending list:
pending = {}
# When a note-on event comes up, create a pending note with t0 at current time but no t1
#  key = the note value
# When there's note-off, or note-on with zero velocity
#  look for a matching item in the pending list and move it to allnotes
# use del(pending[N]) to delete something

def addToPending(e, t, trk):
  n = Note()
  n.note = e.note
  n.t0 = t/ticks_per_second
  n.vel = e.velocity
  n.track = trk
  n.channel = e.channel
  pending[n.note] = n

def addToNotes(e, t):
  note = e.note
  if note in pending:
    n = pending[note]
    n.t1 = t/ticks_per_second
    allnotes.append(n)
    del pending[note]

tracknum = 0
for t in mid.tracks:
  tracknum+=1
  abstime = 0
  for e in t:
    abstime += e.time
    if isKeyDown(e):
      addToPending(e, abstime, tracknum)
    if isKeyUp(e):
      addToNotes(e, abstime)

for n in allnotes:
  print(n)
