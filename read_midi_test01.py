import mido
mid = mido.MidiFile('midi/sync_test.mid')
mid = mido.MidiFile('/home/alex/xxx.mid')
#mid = mido.MidiFile('midi/2016-12-Scriabin_op74_no4_v02.mid')

for i, track in enumerate(mid.tracks):
    print('Track {}: {}'.format(i, track.name))
    for message in track:
	    print(message)
