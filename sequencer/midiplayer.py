import time
import midi
from util.attachables import Attachable
import instrument

_DEFAULT_BEATSPERMIN = 165
_FRAMES_PER_SECOND = 60

class MidiPlayer(Attachable):

    def __init__(self, filename):
        super(MidiPlayer, self).__init__()
        self._filename = filename
        self._pattern = midi.read_midifile(filename)
        self._ticksPerBeat = self._pattern.resolution
        self._pattern.make_ticks_abs()

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
                self._midiout.handleMidiEvent(*rawMidiEvent)
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
        if isinstance(pyMidiEvent, midi.events.NoteEvent):
            return [pyMidiEvent.statusmsg,
                    pyMidiEvent.get_pitch(),
                    pyMidiEvent.get_velocity()]
        return None
