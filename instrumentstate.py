class InstrumentState(object):
    
    _notes = 88 * [0]
    
    @staticmethod
    def getNote(noteIndex):
        return InstrumentState._notes[noteIndex]
    
    @staticmethod
    def setNote(noteIndex, velocity):
        InstrumentState._notes[noteIndex] = velocity
    
    @staticmethod
    def unsetNote(noteIndex):
        InstrumentState.setNote(noteIndex, 0)
    
    @staticmethod
    def onInstrumentEvent(note, velocity):
        InstrumentState._notes[note] = velocity
        print(note, velocity)
        
        
if __name__ == "__main__":
    print(InstrumentState._notes)
    InstrumentState.midiMessage(0, 50)
    print(InstrumentState._notes)