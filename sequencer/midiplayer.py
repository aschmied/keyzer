import midi
import time

from util.attachables import Attachable
import logging

_DEFAULT_BEATSPERMIN = 165.0
_SECONDS_PER_FRAME = 1.0/60

_MAX_MIDI_CHANNELS = 15
_DEFAULT_MIDI_PROGRAM = 0

class Note(object):

    def __init__(self, onTick, offTick, program, pitch, velocity):
        """Member of a Channel"""
        self.onTick = onTick
        self.offTick = offTick
        self.program = program
        self.pitch = pitch
        self.velocity = velocity

    def __lt__(self, other):
        return self.onTick < other.onTick
    
    def __repr__(self):
        return "{}--{}: {} {} {}".format(
            self.onTick, self.offTick, self.program, self.pitch, self.velocity)


class Channel(list):
    """A list of Notes"""

    def __init__(self, pyMidiTrack, channelIndex):
        super(Channel, self).__init__()
        self._channelIndex = channelIndex

        program = _DEFAULT_MIDI_PROGRAM
        noteOnEvents = {}
        for event in pyMidiTrack:
            if not isinstance(event, midi.events.Event):
                continue

            if not event.channel == self._channelIndex:
                continue

            if isinstance(event, midi.events.ProgramChangeEvent):
                program = event.get_value()

            if isinstance(event, midi.events.NoteOnEvent):
                pitch = event.get_pitch()
                if not pitch in noteOnEvents:
                    velocity = event.get_velocity()
                    tick = event.tick
                    noteOnEvents[pitch] = Note(tick, -1, program, pitch, velocity)

            elif isinstance(event, midi.events.NoteOffEvent):
                pitch = event.get_pitch()
                if pitch in noteOnEvents:
                    note = noteOnEvents[pitch]
                    note.offTick = event.tick
                    self.append(note)
                    del noteOnEvents[pitch]
            else:
                pass

        self.sort()

    def getNotesForProgram(self, program):
        return [note for note in self if note.program == program]

    def getPrograms(self):
        programs = set([note.program for note in self])
        return sorted(programs)


class Track(list):
    """A list of Channels"""
    
    def __init__(self, trackIndex, pyMidiTrack):
        super(Track, self).__init__()
        self._trackIndex = trackIndex
        for channelId in range(_MAX_MIDI_CHANNELS):
            self.append(Channel(pyMidiTrack, channelId))


class Sequence(list):
    """
    A representation of a sequence of notes for consumption by other components
    in the application. A Sequence is a list of Tracks.
    """

    def __init__(self, pyMidiPattern):
        super(Sequence, self).__init__()
        for (trackIndex, track) in enumerate(pyMidiPattern):
            self.append(Track(trackIndex, track))


class MidiPlayer(Attachable):

    def __init__(self, midioutConnection, filename):
        super(MidiPlayer, self).__init__()
        self._midiout = midioutConnection
        self._filename = filename
        self._pattern = midi.read_midifile(filename)
        self._ticksPerBeat = self._pattern.resolution
        self._pattern.make_ticks_abs()
        self._logging = logging.getLogger("keyzer")
        self._playing = False

    def attach(self, objectToAttach):
        """objectToAttach must implement onTickUpdate(currentTick)"""
        super(MidiPlayer, self).attach(objectToAttach)

    def play(self):
        self._playing = True
        events = self.getSortedEvents()
        beatsPerMin = _DEFAULT_BEATSPERMIN
        ticksPerFrame = self.secondsToTicks(beatsPerMin, _SECONDS_PER_FRAME)

        currentTick = 0
        eventIter = iter(events)
        event = eventIter.next()
        try:
            while self._playing:
                # dispatch overdue events
                while event.tick <= currentTick:
                    rawMidiEvent = _PyMidiEventToRawMidiEvent.convert(event)
                    if rawMidiEvent is not None:
                        self._midiout.handleMidiEvent(rawMidiEvent)
                    event = eventIter.next()

                # sleep and update GUI until next event
                ticksBeforeNextEvent = event.tick - currentTick
                secondsBeforeNextEvent = \
                        self.ticksToSeconds(beatsPerMin, ticksBeforeNextEvent)
                numWaits = int(secondsBeforeNextEvent / _SECONDS_PER_FRAME)
                for i in range(numWaits):
                    time.sleep(_SECONDS_PER_FRAME)
                    currentTick += ticksPerFrame
                    ticksBeforeNextEvent -= ticksPerFrame
                    for a in self._getAttached():
                        a.onTickUpdate(currentTick)
                secondsBeforeNextEvent = \
                        self.ticksToSeconds(beatsPerMin, ticksBeforeNextEvent)
                time.sleep(secondsBeforeNextEvent)
                currentTick = event.tick
                for a in self._getAttached():
                    a.onTickUpdate(currentTick)

        except StopIteration:
            pass

    def stop(self):
        self._playing = False
        
    def getSortedEvents(self):
        events = []
        for track in self._pattern:
            for event in track:
                events.append(event)
        events.sort()
        return events
    
    def getNoteSequence(self):
        return Sequence(self._pattern)

    def ticksToSeconds(self, beatsPerMin, ticks):
        ticksPerMin = self._ticksPerBeat * beatsPerMin
        ticksPerSec = ticksPerMin / 60.
        return ticks / ticksPerSec

    def secondsToTicks(self, beatsPerMin, seconds):
        beatsPerSec = beatsPerMin / 60.
        ticksPerSec = self._ticksPerBeat * beatsPerSec
        return seconds * ticksPerSec


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
