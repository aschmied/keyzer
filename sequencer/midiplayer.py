import midi
import time

from util.attachables import Attachable
import logging

_DEFAULT_BEATSPERMIN = 165.0
_SECONDS_PER_FRAME = 1.0/60

class Note(object):

    def __init__(self, channel, onTick, offTick, velocity):
        self.channel = channel
        self.onTick = onTick
        self.offTick = offTick
        self.velocity = velocity

    def __lt__(self, other):
        return self.onTick < other.onTick


class NoteSequence(object):
    """
    A representation of a sequence of notes for consumption by other components
    in the application.
    """

    def __init__(self, pyMidiPattern):
        self._tracks = []
        for track in pyMidiPattern:
            noteOnEvents = {}
            notesForTrack = []
            for event in track:
                if isinstance(event, midi.events.NoteOnEvent):
                    channel = event.channel
                    pitch = event.get_pitch()
                    key = str(channel) + "-" + str(pitch)
                    if not key in noteOnEvents:
                        velocity = event.get_velocity()
                        tick = event.tick
                        noteOnEvents[key] = Note(channel, tick, -1, velocity)
                elif isinstance(event, midi.events.NoteOffEvent):
                    channel = event.channel
                    pitch = event.get_pitch()
                    key = str(channel) + "-" + str(pitch)
                    if key in noteOnEvents:
                        note = noteOnEvents[key]
                        note.offTick = event.tick
                        notesForTrack.append(note)
                        del noteOnEvents[key]
                else:
                    pass
            notesForTrack.sort()
            self._tracks.append(notesForTrack)

    def getTrack(self, trackIndex):
        return self._tracks[trackIndex]


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
        return NoteSequence(self._pattern)

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
