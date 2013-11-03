import logging
import Queue

class PlayingSongState():

    _ticksPerBeat = 0
    _notes = None
    _currentTick = 0
    _attached = []
    _tickUpdateQueue = Queue.Queue()
    _log = logging.getLogger("keyzer:PlayingSongState")

    @staticmethod
    def setTicksPerBeat(ticksPerBeat):
        PlayingSongState._ticksPerBeat = ticksPerBeat

    @staticmethod
    def getTicksPerBeat():
        return PlayingSongState._ticksPerBeat

    @staticmethod
    def setNotes(notes):
        """notes is a list of midiplayer.Notes sorted by offTick within onTick"""
        PlayingSongState._notes = notes
        PlayingSongState._currentTick = 0

    @staticmethod
    def getNotes():
        """returns a list of midiplayer.Notes sorted by offTick within onTick"""
        return PlayingSongState._notes

    @staticmethod
    def getCurrentTick():
        PlayingSongState._log.debug("getCurrentTick()")
        # The tick is the current time point in the playing song so when >1
        # are in the queue the most recent is the most correct. Discard others.
        try:
            tick = None
            while True:
                tick = PlayingSongState._tickUpdateQueue.get_nowait()
        except Queue.Empty:
            if tick:
                PlayingSongState._currentTick = tick
        return PlayingSongState._currentTick

    @staticmethod
    def onTickUpdate(tick):
        PlayingSongState._log.debug("onTickUpdate(tick={})".format(tick))
        # Tick updates received from the song player. If consumers get so behind
        # that the queue gets full then something is seriously wrong. Just 
        # discard the events in that case.
        try:
            PlayingSongState._tickUpdateQueue.put_nowait(tick)
        except Queue.Full:
            PlayingSongState._log.warning("_tickUpdateQueue is full")

