from pyglet.window import key

from util.attachables import Attachable 


class KeyPressToMusicEventMapper(Attachable):
    '''
    Maps computer keyboard events to music events.
    Useful for testing and debugging without a MIDI device.
    '''
    _keyToNote={key.Q: 30, 
                key.W: 31,
                key.E: 32,
                key.R: 33,
                key.T: 34,
                key.Y: 35,
                key.U: 36,
                key.I: 37,
                key.O: 38,
                key.P: 39,
                key.A: 40,
                key.S: 41,
                key.D: 42,
                key.F: 43,
                key.G: 44,
                key.H: 45,
                key.J: 46,
                key.K: 47,
                key.L: 48,
                key.SEMICOLON: 49,
                key.Z: 50,
                key.X: 51,
                key.C: 52,
                key.V: 53,
                key.B: 54,
                key.N: 55,
                key.M: 56,
                key.COMMA: 57,
                key.PERIOD: 58,
                key.SLASH: 59
    }
    
    def __init__(self):
        super(KeyPressToMusicEventMapper, self).__init__()
    
    def attach(self, objectToAttach):
        '''objectToAttach must implement the music event handler interface'''
        super(KeyPressToMusicEventMapper, self).attach(objectToAttach)
        
    def onKeyDown(self, symbol, modifiers):
        note = self._keyToNote.get(symbol)
        if note is None: return
        for a in super(KeyPressToMusicEventMapper, self)._getAttached():
            a.onInstrumentEvent(note, 100)
    
    def onKeyUp(self, symbol, modifiers):
        note = self._keyToNote.get(symbol)
        if note is None: return
        for a in super(KeyPressToMusicEventMapper, self)._getAttached():
            a.onInstrumentEvent(note, 0)
    
