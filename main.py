import midi
import time
from keyboard_input import InstrumentState

if __name__ == '__main__':
    
    midiout = midi.OutputConnection()
    midiout.openPort(midiout.probeMidiPorts()[0])
    
    midiin = midi.InputConnection()
    midiin.openPort(midiin.probeMidiPorts()[0], InstrumentState.midiMessage)
    
    while True:
        #note = 20 if x%2 == 0 else 32
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