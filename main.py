from __future__ import print_function

import argparse
import sys
import time
import threading

from ui.assetmanager import Assets
from ui.applicationwindow import ApplicationWindow
from instrumentstate import InstrumentState
from instrument.keyboard import KeyPressToMusicEventMapper
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
    parser.add_argument('-l', '--list', action='store_true',
                        help='List available MIDI ports and terminate')
    parser.add_argument('--song-path', type=str,
                        help='Input MIDI file')
    parser.add_argument('--track', type=int,
                        help='MIDI track number to learn')
    args = parser.parse_args()

    if not args.list and not args.song_path:
        parser.error("You must specify one of --song-path or --list")

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

def main(argv):

    args = parseArgs()

    if args.list:
        probeMidiAndPrint()
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

