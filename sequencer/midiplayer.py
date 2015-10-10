import midi
import time

from util.attachables import Attachable
import logging
import util.music

_DEFAULT_BEATSPERMIN = 120.0
_SECONDS_PER_FRAME = 1.0/60

_MAX_MIDI_CHANNELS = 15
_DEFAULT_MIDI_PROGRAM = 0


class Note(object):

    def __init__(self, onTick, offTick, program, noteIndex, velocity):
        """Member of a Channel. Notes are sorted by offTick within onTick."""
        self.onTick = onTick
        self.offTick = offTick
        self.program = program
        self.noteIndex = noteIndex
        self.velocity = velocity

    def __lt__(self, other):
        if self.onTick < other.onTick:
            return True
        elif self.onTick > other.onTick:
            return False
        else:
            return self.offTick < other.offTick
    
    def __repr__(self):
        return "{}--{}: {} {} {}".format(
            self.onTick, self.offTick, self.program, self.noteIndex, self.velocity)


class Channel(list):
    """A sorted list of Notes"""

    def __init__(self, pyMidiTrack, channelId):
        super(Channel, self).__init__()
        self._channelId = channelId

        program = _DEFAULT_MIDI_PROGRAM
        noteOnEvents = 88*[None]
        for event in pyMidiTrack:
            if not isinstance(event, midi.events.Event):
                continue

            if not event.channel == self._channelId:
                continue

            if isinstance(event, midi.events.ProgramChangeEvent):
                program = event.get_value()

            if isinstance(event, midi.events.NoteOnEvent):
                pitch = event.get_pitch()
                index = util.music.midiPitchToNoteIndex(pitch)
                if noteOnEvents[index] is None:
                    velocity = event.get_velocity()
                    tick = event.tick
                    noteOnEvents[index] = Note(tick, -1, program, index, velocity)

            elif isinstance(event, midi.events.NoteOffEvent):
                pitch = event.get_pitch()
                index = util.music.midiPitchToNoteIndex(pitch)
                if not noteOnEvents[index] is None:
                    note = noteOnEvents[index]
                    note.offTick = event.tick
                    self.append(note)
                    noteOnEvents[index] = None
            else:
                pass

        self.sort()

    def getNotesForProgram(self, program):
        return [note for note in self if note.program == program]

    def getPrograms(self):
        programs = set([note.program for note in self])
        return sorted(programs)


class Track(list):
    """A list of Channels indexed by channelId"""
    
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
        self.ticksPerBeat = pyMidiPattern.resolution
        for (trackIndex, track) in enumerate(pyMidiPattern):
            self.append(Track(trackIndex, track))


class MidiPlayer(Attachable):

    def __init__(self, midioutConnection, filename):
        super(MidiPlayer, self).__init__()
        self._log = logging.getLogger("keyzer:MidiPlayer")
        self._midiout = midioutConnection
        self._filename = filename
        self._pattern = midi.read_midifile(filename)
        self._beatsPerMin = _DEFAULT_BEATSPERMIN
        self._ticksPerBeat = self._pattern.resolution
        self._pattern.make_ticks_abs()
        self._log = logging.getLogger("keyzer:MidiPlayer")
        self._playing = False

    def attach(self, objectToAttach):
        """objectToAttach must implement onTickUpdate(currentTick)"""
        super(MidiPlayer, self).attach(objectToAttach)

    def onTempoChange(self, beatsPerMinute):
        self._log.debug("onTempoChange({})".format(beatsPerMinute))
        self._beatsPerMin = float(beatsPerMinute)
        self._ticksPerFrame = self.secondsToTicks(self._beatsPerMin, _SECONDS_PER_FRAME)

    def play(self):
        self.onTempoChange(_DEFAULT_BEATSPERMIN)
        self._playing = True
        pyMidiEventToRawMidiEvent = _PyMidiEventToRawMidiEvent()
        pyMidiEventToRawMidiEvent.setTempChangeListener(self)
        events = self.getSortedEvents()
        secsPerFrame = _SECONDS_PER_FRAME

        currentTick = 0
        eventIter = iter(events)
        try:
            event = eventIter.next()
            while self._playing:
                # dispatch overdue events
                while event.tick <= currentTick:
                    rawMidiEvent = pyMidiEventToRawMidiEvent.convert(event)
                    if rawMidiEvent is not None:
                        self._midiout.handleMidiEvent(rawMidiEvent)
                    event = eventIter.next()

                # sleep and update GUI until next event
                ticksBeforeNextEvent = event.tick - currentTick
                assert ticksBeforeNextEvent > 0
                numWaits = int(ticksBeforeNextEvent / self._ticksPerFrame)
                self._log.debug("next MIDI event is {0} ticks and {1} GUI frames away".format(
                                ticksBeforeNextEvent, numWaits))

                for i in range(numWaits):
                    time.sleep(secsPerFrame)
                    currentTick += self._ticksPerFrame
                    ticksBeforeNextEvent -= self._ticksPerFrame
                    for a in self._getAttached():
                        a.onTickUpdate(currentTick)
                secondsBeforeNextEvent = \
                        self.ticksToSeconds(self._beatsPerMin, ticksBeforeNextEvent)
                time.sleep(secondsBeforeNextEvent)
                currentTick = event.tick
                for a in self._getAttached():
                    a.onTickUpdate(currentTick)

        except StopIteration:
            pass

    def stop(self):
        for channel in xrange(_MAX_MIDI_CHANNELS):
            allNotesOffEvent = [0xB0 + channel, 0x7B, 0]
            self._midiout.handleMidiEvent(allNotesOffEvent)
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
        self._log.debug("ticksToSeconds()")
        ticksPerMin = self._ticksPerBeat * beatsPerMin
        ticksPerSec = ticksPerMin / 60.
        self._log.debug("beatsPerMin={}, ticks={}, ticksPerMin={}, ticksPerSec={}, seconds={}".format(beatsPerMin, ticks, ticksPerMin, ticksPerSec, ticks/ticksPerSec))
        seconds = ticks / ticksPerSec
        assert seconds >= 0
        return seconds

    def secondsToTicks(self, beatsPerMin, seconds):
        beatsPerSec = beatsPerMin / 60.
        ticksPerSec = self._ticksPerBeat * beatsPerSec
        return int(seconds * ticksPerSec)


class _PyMidiEventToRawMidiEvent(object):

    def __init__(self):
        self.tempoChangeListener = None
        self._log = logging.getLogger("keyzer:_PyMidiEventToRawMidiEvent")
    
    def setTempChangeListener(self, listener):
        """listener must implement onTempoChange(beatsPerMinute)"""
        self.tempoChangeListener = listener

    def convert(self, pyMidiEvent):
        tick = pyMidiEvent.tick
        if isinstance(pyMidiEvent, midi.events.NoteEvent):
            event = [pyMidiEvent.statusmsg + pyMidiEvent.channel,
                     pyMidiEvent.get_pitch(),
                     pyMidiEvent.get_velocity()]
            self._log.debug("{0}: Note: {1}".format(tick, ["{0:x}".format(x) for x in event]))
            return event
        elif isinstance(pyMidiEvent, midi.events.ControlChangeEvent):
            event =  [pyMidiEvent.statusmsg + pyMidiEvent.channel,
                      pyMidiEvent.get_control(),
                      pyMidiEvent.get_value()]
            self._log.debug("{0}: ControlChange: {1}".format(tick, ["{0:x}".format(x) for x in event]))
            return event
        elif isinstance(pyMidiEvent, midi.events.ProgramChangeEvent):
            event = [pyMidiEvent.statusmsg + pyMidiEvent.channel,
                     pyMidiEvent.get_value()]
            self._log.debug("{0}: ProgramChange: {1}".format(tick, ["{0:x}".format(x) for x in event]))
            return event
        elif isinstance(pyMidiEvent, midi.events.PitchWheelEvent):
            event = [pyMidiEvent.statusmsg + pyMidiEvent.channel,
                     pyMidiEvent.data[0],
                     pyMidiEvent.data[1]]
            self._log.debug("{0}: PitchWheel: {1}".format(tick, ["{0:x}".format(x) for x in event]))
            return event
        elif isinstance(pyMidiEvent, midi.events.SetTempoEvent):
            if self.tempoChangeListener:
                self.tempoChangeListener.onTempoChange(pyMidiEvent.bpm)
            self._log.debug("{0}: SetTempo: {1}".format(tick, pyMidiEvent.bpm))
            return None
        self._log.warning("{0}: Unknown: {1}".format(tick, pyMidiEvent))
        return None
