import sys
import time
import threading

from ui.assetmanager import Assets
from ui.applicationwindow import ApplicationWindow
from instrument.keyboard import KeyPressToMusicEventMapper
from instrument import midi
from instrumentstate import InstrumentState
from sequencer.midiplayer import MidiPlayer
from playingsongstate import PlayingSongState

def usage():
    print("Usage: keyzer runType songPath trackNumber")

def parseArgs(argv):
    if len(argv) != 4:
        print(argv)
        usage()
        sys.exit(1)
    runType = argv[1]
    songPath = argv[2]
    trackToLearn = argv[3]
    return (runType, songPath, trackToLearn)

def main(argv):

    (runType, songPath, trackToLearn) = parseArgs(argv)

    midiin = None
    Assets.loadAssets()
    app = ApplicationWindow()
    if runType == "k":
        keyPressToMusicEventMapper = KeyPressToMusicEventMapper()
        app.attachToKeyboard(keyPressToMusicEventMapper)
        keyPressToMusicEventMapper.attach(InstrumentState)
    else:
        midiin = midi.InputConnection()
        midiin.attach(InstrumentState)
        midiin.openPort(midiin.probeMidiPorts()[0])

        midiplayer = MidiPlayer(songPath)
        midiplayer.attach(PlayingSongState)
        threading.Thread(target=midiplayer.play).start()

    app.start()
    if midiin is not None:
        midiin.closePort()
    
if __name__ == '__main__':
    main(sys.argv)
    sys.exit(0)

