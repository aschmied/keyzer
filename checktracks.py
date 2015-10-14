# Copyright (c) 2015, Anthony Schmieder
# Use of this source code is governed by the 2-clause BSD license that
# can be found in the LICENSE.txt file.

from __future__ import print_function

import argparse
import logging
import sys
import threading

from ui.checktracksapplicationwindow import CheckTracksApplicationWindow
from instrument import midi
from instrumentstate import InstrumentState
from sequencer.midiplayer import MidiPlayer
from playingsongstate import PlayingSongState

def parseArgs():
    parser = argparse.ArgumentParser(description='Keyzer track selection')
    parser.add_argument('--out-port', type=int, default=0,
                        help='Output MIDI port port number')
    parser.add_argument('--list-ports', action='store_true',
                        help='List available MIDI ports and terminate')
    parser.add_argument('--song-path', type=str,
                        help='Input MIDI file')
    parser.add_argument('--debug', action='store_true',
                        help='Print debug messages')
    args = parser.parse_args()

    if not args.list_ports and not args.song_path:
        parser.error("You must specify one of --song-path or --list-ports")

    return args

def probeMidiAndPrint():
    midiout = midi.OutputConnection()
    outPorts = midiout.probeMidiPorts()
    printPort = lambda p: print("\t{}: {}".format(p.getNumber(), p.getName()))
    print("Output ports")
    map(printPort, outPorts)

def main(argv):
    args = parseArgs()

    level = logging.DEBUG if args.debug  else logging.WARNING
    logging.basicConfig(level=level)

    if args.list_ports:
        probeMidiAndPrint()
        sys.exit(0)

    midiout = midi.OutputConnection()
    outPorts = midiout.probeMidiPorts()
    midiout.openPort(outPorts[args.out_port])

    midiplayer = MidiPlayer(midiout, args.song_path)
    midiplayer.attach(PlayingSongState)

    noteSequence = midiplayer.getNoteSequence()
    app = CheckTracksApplicationWindow(noteSequence)

    playerThread = threading.Thread(target=midiplayer.play)
    playerThread.start()

    app.start()

    midiplayer.stop()
    playerThread.join()
    midiout.closePort()

if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)
