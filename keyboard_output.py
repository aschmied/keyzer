'''
MIDI keyboard output module
'''

import rtmidi

class InstrumentInterface(object):
    
    @staticmethod
    def send():
        