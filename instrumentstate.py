import logging

class InstrumentState(object):
    
    _log = logging.getLogger("keyzer:InstrumentState")
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
        InstrumentState._log.debug("{}, {}".format(note, velocity))

