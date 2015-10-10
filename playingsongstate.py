# Copyright (c) 2015, Anthony Schmieder
# Use of this source code is governed by the 2-clause BSD license that
# can be found in the LICENSE.txt file.

import logging
import Queue

class PlayingSongState():

    _ticksPerBeat = 0
    _notes = None
    _currentTick = 0
    _attached = []
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
        return PlayingSongState._currentTick

    @staticmethod
    def onTickUpdate(tick):
        PlayingSongState._log.debug("onTickUpdate(tick={})".format(tick))
        PlayingSongState._currentTick = tick
