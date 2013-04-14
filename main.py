import sys
import time

from ui.assetmanager import Assets
from ui.keyboard import Keyboard
from ui.applicationwindow import ApplicationWindow
from instrument.keyboard import KeyPressToMusicEventMapper
from instrument import midi
from instrumentstate import InstrumentState
from sequencer import midiplayer

if __name__ == '__main__':

    #Assets.loadAssets()
    #app = ApplicationWindow()

    runType = ""
    if runType == "k":
        keyPressToMusicEventMapper = KeyPressToMusicEventMapper()
        app.attachToKeyboard(keyPressToMusicEventMapper)
        keyPressToMusicEventMapper.attach(InstrumentState)
    else:
        #midiin = midi.InputConnection()
        #midiin.attach(InstrumentState)
        #midiin.openPort(midiin.probeMidiPorts()[0])

        midiout = midi.OutputConnection()
        midiout.openPort(midiout.probeMidiPorts()[0])
        midiplayer = midiplayer.MidiPlayer("/Users/anthonyschmieder/Dropbox/"
                                  "music/midi/chet_atkins_windy_and_warm.mid")
        midiplayer.attach(midiout)
        midiplayer.play()


        #midiin.closePort()
        midiout.closePort()

    #app.start()
    
    if False:
    
        midiout = midi.OutputConnection()
        midiout.openPort(midiout.probeMidiPorts()[0])
            
        midiin = midi.InputConnection()
        midiin.attach(InstrumentState)
        midiin.openPort(midiin.probeMidiPorts()[0])    
        
        
        while True:
            midiout.sendNoteOnEvent(59, 80)
            midiout.sendNoteOnEvent(41, 80)
            time.sleep(.33)
            midiout.sendNoteOffEvent(59, 0)
            midiout.sendNoteOffEvent(41, 0)
            time.sleep(.33)
            midiout.sendNoteOnEvent(59, 80)
            midiout.sendNoteOnEvent(40, 80)
            time.sleep(.33)
            midiout.sendNoteOffEvent(59, 0)
            midiout.sendNoteOffEvent(40, 0)
            time.sleep(.33)
    
        midiin.closePort()
        midiout.closePort()
