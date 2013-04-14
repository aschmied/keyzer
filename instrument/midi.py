'''
RTMIDI interfacing details. Handles input/output connections and raw MIDI
events.
'''
import rtmidi
import sys

from util.attachables import Attachable

class MidiPort(object):
    
    def __init__(self, number, name):
        self._number = number
        self._name = name
    
    def getNumber(self):
        return self._number
            
    def getName(self):
        return self._name


class InputConnection(Attachable):
    
    def __init__(self):
        super(InputConnection, self).__init__()
        self._midiInput = rtmidi.MidiIn()
        self._connectedPort = None
        self._availablePorts = []

    def probeMidiPorts(self):
        self._availablePorts = []
        portNames = self._midiInput.get_ports(
            encoding=('latin1' if sys.platform.startswith('win') else 'utf-8'))
        if not portNames:
            raise Exception("No midi input ports found")
        ports = [MidiPort(number, name) for number, name in enumerate(portNames)]
        self._availablePorts.extend(ports)
        return self._availablePorts
        
    def getAvailablePorts(self):
        return self._availablePorts
    
    def attach(self, objectToAttach):
        '''object must implement instrument event callback interface'''
        super(InputConnection, self).attach(objectToAttach)
    
    def openPort(self, port):
        self._midiInput.open_port(port.getNumber())
        self._connectedPort = port
        self._midiInput.set_callback(self._midiEventCallback)
        
    def _midiEventCallback(self, event, data=None):
        message, _deltatime = event
        note, velocity = MessageDecoder.decode(message)
        if note is None: return
        for a in super(InputConnection, self)._getAttached():
            a.onInstrumentEvent(note, velocity)
    
    def closePort(self):
        self._midiInput.close_port()
        del self._midiInput


class MessageDecoder(object):
    statuses = {'noteonc1': 144,
                'noteoffc1': 128,
                'noteon': 153,
                'noteoff': 137,
                'bank_select': 176}
    
    @staticmethod
    def _midiNoteToNoteIndex(midiNote):
        return midiNote - 21
    
    @staticmethod
    def decode(message):
        status = message[0]
        noteIndex = MessageDecoder._midiNoteToNoteIndex(message[1])
        if status == MessageDecoder.statuses['noteonc1']:
            velocity = message[2]
            return noteIndex, velocity
        elif status == MessageDecoder.statuses['noteoffc1']:
            return noteIndex, 0
        return None, None
    

class OutputConnection(object):
    
    def __init__(self):
        self._midiOutput = rtmidi.MidiOut()
        self._connectedPort = None
        self._availablePorts = []

    def probeMidiPorts(self):
        self._availablePorts = []
        portNames = self._midiOutput.get_ports(
            encoding=('latin1' if sys.platform.startswith('win') else 'utf-8'))
        if not portNames:
            raise Exception("No midi output ports found")
        ports = [MidiPort(number, name) for number, name in enumerate(portNames)]
        self._availablePorts.extend(ports)
        return self._availablePorts
        
    def getAvailablePorts(self):
        return self._availablePorts
    
    def openPort(self, port):
        self._midiOutput.open_port(port.getNumber())
        
    def closePort(self):
        self._midiOutput.close_port()
        del self._midiOutput
    
    def handleMidiEvent(self, status, midiNote, velocity):
        self._midiOutput.send_message([status, midiNote, velocity])

    def sendNoteOnEvent(self, midiNote, velocity):
        self.sendMidiEvent(MessageDecoder.statuses['noteon'], midiNote, velocity)
    
    def sendNoteOffEvent(self, midiNote, velocity):
        self.sendMidiEvent(MessageDecoder.statuses['noteoff'], midiNote, velocity)

