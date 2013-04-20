import time
import midi
from util.attachables import Attachable
import instrument

import logging

_DEFAULT_BEATSPERMIN = 165
_FRAMES_PER_SECOND = 60

class MidiPlayer(Attachable):

    def __init__(self, filename):
        super(MidiPlayer, self).__init__()
        self._filename = filename
        self._pattern = midi.read_midifile(filename)
        self._ticksPerBeat = self._pattern.resolution
        self._pattern.make_ticks_abs()
        self._logging = logging.getLogger("keyzer")

    def attach(self, objectToAttach):
        """objectToAttach must implement the tick update callback interface"""
        super(MidiPlayer, self).attach(objectToAttach)

    def play(self):
        self._initializeMidiOutput()
        
        events = self.getSortedEvents()
        beatsPerMin = _DEFAULT_BEATSPERMIN
        currentTick = 0
        for event in events:
            ticksBeforeNextEvent = event.tick - currentTick
            currentTick = event.tick
            secondsBeforeNextEvent = \
                    self.ticksToSeconds(beatsPerMin, ticksBeforeNextEvent)
            time.sleep(secondsBeforeNextEvent)
            rawMidiEvent = _PyMidiEventToRawMidiEvent.convert(event)
            if rawMidiEvent is not None:
                self._midiout.handleMidiEvent(rawMidiEvent)
            for a in self._getAttached():
                a.onTickUpdate(currentTick)
        
        self._finalizeMidiOutput()

    def getSortedEvents(self):
        events = []
        for track in self._pattern:
            for event in track:
                events.append(event)
        events.sort()
        return events

    def ticksToSeconds(self, beatsPerMin, ticks):
        ticksPerMin = self._ticksPerBeat * beatsPerMin
        ticksPerSec = ticksPerMin / 60.
        return ticks / ticksPerSec

    def _initializeMidiOutput(self):
        self._midiout = instrument.midi.OutputConnection()
        self._midiout.openPort(self._midiout.probeMidiPorts()[0])

    def _finalizeMidiOutput(self):
        self._midiout.closePort()

class _PyMidiEventToRawMidiEvent(object):

    @staticmethod
    def convert(pyMidiEvent):
        log = logging.getLogger("keyzer")
        logging.basicConfig(level=logging.DEBUG)
        
        if isinstance(pyMidiEvent, midi.events.NoteEvent):
            event = [pyMidiEvent.statusmsg + pyMidiEvent.channel,
                     pyMidiEvent.get_pitch(),
                     pyMidiEvent.get_velocity()]
            log.debug("Note: {0}".format(["{0:x}".format(x) for x in event]))
            return event
        elif isinstance(pyMidiEvent, midi.events.ControlChangeEvent):
            event =  [pyMidiEvent.statusmsg + pyMidiEvent.channel,
                      pyMidiEvent.get_control(),
                      pyMidiEvent.get_value()]
            log.debug("ControlChange: {0}".format(["{0:x}".format(x) for x in event]))
            return event
        elif isinstance(pyMidiEvent, midi.events.ProgramChangeEvent):
            event = [pyMidiEvent.statusmsg + pyMidiEvent.channel,
                     pyMidiEvent.get_value()]
            log.debug("ProgramChange: {0}".format(["{0:x}".format(x) for x in event]))
            return event
        elif isinstance(pyMidiEvent, midi.events.PitchWheelEvent):
            event = [pyMidiEvent.statusmsg + pyMidiEvent.channel,
                     pyMidiEvent.data[0],
                     pyMidiEvent.data[1]]
            log.debug("PitchWheel: {0}".format(["{0:x}".format(x) for x in event]))
            return event
        #elif isinstance(pyMidiEvent, midi.events.SetTempoEvent):
            #microsecondsPerSecond = 10**6
            #secondsPerMinute = 60
            #beatsPerMinute = pyMidiEvent.event.bpm
            #microsecondsPerBeat = ((secondsPerMinute * microsecondsPerSecond) / 
                                   #beatsPerMinute)

            #return [pyMidiEvent.statusmsg,
                    #int(microsecondsPerBeat)]
            log.debug("Unknown: {0}".format(["{0:x}".format(x) for x in event]))
        return None
