import time
import midi
from util.attachables import Attachable
import instrument

_DEFAULT_BEATSPERMIN = 165

class MidiPlayer(Attachable):

    def __init__(self, filename):
        super(MidiPlayer, self).__init__()
        self._filename = filename
        self._pattern = midi.read_midifile(filename)
        self._ticksPerBeat = self._pattern.resolution
        self._pattern.make_ticks_abs()

    def attach(self, objectToAttach):
        """objectToAttach must implement the midi event callback interface"""
        super(MidiPlayer, self).attach(objectToAttach)

    def play(self):
        midiout = instrument.midi.OutputConnection()
        midiout.openPort(midiout.probeMidiPorts()[0])
        self.attach(midiout)
        

        events = self.getSortedEvents()
        beatsPerMin = _DEFAULT_BEATSPERMIN
        tick = 0
        for event in events:
            eventTick = event.tick
            ticksDiff = eventTick - tick
            tick = eventTick
            secondsDiff = self.ticksToSeconds(beatsPerMin, ticksDiff)
            time.sleep(secondsDiff)
            rawMidiEvent = _PyMidiEventToRawMidiEvent.convert(event)
            print(event, rawMidiEvent)
            if rawMidiEvent is not None:
                for a in self._getAttached():
                    a.handleMidiEvent(*rawMidiEvent)

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


class _PyMidiEventToRawMidiEvent(object):

    @staticmethod
    def convert(pyMidiEvent):
        if isinstance(pyMidiEvent, midi.events.NoteEvent):
            return [pyMidiEvent.statusmsg,
                    pyMidiEvent.get_pitch(),
                    pyMidiEvent.get_velocity()]
        return None
