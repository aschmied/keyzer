from __future__ import print_function

import argparse
import logging
import sys
import threading

from ui.assetmanager import Assets
from ui.applicationwindow import ApplicationWindow
from instrumentstate import InstrumentState
from instrument import midi
from sequencer.midiplayer import MidiPlayer
from playingsongstate import PlayingSongState


def parseArgs():
    parser = argparse.ArgumentParser(description='Piano sight reading trainer')
    parser.add_argument('--in-port', type=int, default=0,
                        help='Input MIDI port number')
    # output needs to support "none"
    parser.add_argument('--out-port', type=int, default=0,
                        help='Output MIDI port port number')
    parser.add_argument('--list-ports', action='store_true',
                        help='List available MIDI ports and terminate')
    parser.add_argument('--song-path', type=str,
                        help='Input MIDI file')
    parser.add_argument('--list-tracks', action='store_true',
                        help='List tracks, channels, and programs in SONG_PATH')
    parser.add_argument('--track', type=int, default=-1,
                        help='Track number in SONG_PATH')
    parser.add_argument('--channel', type=int, default=-1,
                        help='Channel number in TRACK')
    parser.add_argument('--program', type=int, default=-1,
                        help='Program number in TRACK/CHANNEL')
    args = parser.parse_args()

    if not args.list_ports and not args.song_path:
        parser.error("You must specify one of --song-path or --list-ports")

    if args.list_tracks and not args.song_path:
        parser.error("You must specify a song path to list the tracks")

    if not args.list_ports and not args.list_tracks and not (
            args.track >= 0 and args.channel >= 0 and args.program >= 0):
        parser.error("You must specify a track, channel, and program to learn a song. Use --list-tracks to list them.")

    return args

def probeMidiAndPrint():
    midiin = midi.InputConnection()
    inPorts = midiin.probeMidiPorts()
    midiout = midi.OutputConnection()
    outPorts = midiout.probeMidiPorts()
    printPort = lambda p: print("\t{}: {}".format(p.getNumber(), p.getName()))
    print("Input ports")
    map(printPort, inPorts)
    print("Output ports")
    map(printPort, outPorts)

def extractTracksAndPrint(songPath):
    midiplayer = MidiPlayer(None, songPath)
    noteSequence = midiplayer.getNoteSequence()
    for track in noteSequence:
        for channel in track:
            tix = track._trackIndex
            cix = channel._channelId
            pgms = channel.getPrograms()
            if len(pgms) > 0:
                print("t{}c{}".format(tix, cix))
                for pgm in pgms:
                    notes = sum([1 for note in channel if note.program==pgm])
                    print("  p{}: {} notes".format(pgm, notes))


def main(argv):

    logging.basicConfig(level=logging.WARNING)

    args = parseArgs()

    if args.list_ports:
        probeMidiAndPrint()
        sys.exit(0)

    if args.list_tracks:
        extractTracksAndPrint(args.song_path)
        sys.exit(0)

    midiin = midi.InputConnection()
    inPorts = midiin.probeMidiPorts()
    midiin.attach(InstrumentState)
    midiin.openPort(inPorts[args.in_port])

    midiout = midi.OutputConnection()
    outPorts = midiout.probeMidiPorts()
    midiout.openPort(outPorts[args.out_port])
    midiplayer = MidiPlayer(midiout, args.song_path)
    midiplayer.attach(PlayingSongState)
    noteSequence = midiplayer.getNoteSequence()
    noteSequenceForGui = noteSequence[args.track][args.channel].getNotesForProgram(args.program)
    PlayingSongState.setTicksPerBeat(noteSequence.ticksPerBeat)
    PlayingSongState.setNotes(noteSequenceForGui)

    Assets.loadAssets()
    app = ApplicationWindow()
    playerThread = threading.Thread(target=midiplayer.play)
    playerThread.start()

    app.start()
    midiplayer.stop()
    playerThread.join()
    midiin.closePort()
    midiout.closePort()
    
if __name__ == '__main__':
    main(sys.argv)
    sys.exit(0)

