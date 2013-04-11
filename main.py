import sys
import time

from ui.keyboard import Keyboard
from instrument.keyboard import keyPressToMusicEventMapper
from instrument import midi
from instrumentstate import InstrumentState

if __name__ == '__main__':

    sys.path.append("/Users/anthonyschmieder/src/pyglet-1.2alpha1")
    
    #keyboard = Keyboard()
    #keymapper = keyPressToMusicEventMapper()
    #keyboard.attach(keymapper)
    #keymapper.attach(InstrumentState)
    
    #keyboard.displayGui()

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