# Copyright (c) 2015, Anthony Schmieder
# Use of this source code is governed by the 2-clause BSD license that
# can be found in the LICENSE.txt file.

import logging
import pyglet

from ui.components import DrawingSurface
from ui.components import ScreenObject
from ui.components import VerticalLayout
from playingsongstate import PlayingSongState


class CheckTracksSongScore(VerticalLayout):

    def __init__(self, x, y, width, height, sequence):
        super(CheckTracksSongScore, self).__init__()
        self._log = logging.getLogger("keyzer:CheckTracksSongScore")
        self.move(x, y)
        self.resize(width, height)
        self._beatsOnScreen = 24
        self.minVisibleTick = 0
        self.maxVisibleTick = 0
        self._sequence = sequence
        for track in sequence:
            trackIndex = track.trackIndex
            for channel in track:
                channelId = channel.channelId
                for programId in channel.getPrograms():
                    notes = channel.getNotesForProgram(programId)
                    guiProgram = GuiProgram(trackIndex, channelId, programId, notes, self, width)
                    self.add(guiProgram)
        self._drawingSurface = DrawingSurface()

    def update(self, dt):
        self.minVisibleTick = PlayingSongState.getCurrentTick()
        ticksOnScreen = self._beatsOnScreen * self._sequence.ticksPerBeat
        self.maxVisibleTick = self.minVisibleTick + ticksOnScreen

        self._drawingSurface.clear()
        super(CheckTracksSongScore, self).update(self._drawingSurface)

    def draw(self):
        self._drawingSurface.draw()


class GuiProgram(ScreenObject):
    """
    Draws the notes for one program in a particular channel of a MIDI track
    """

    def __init__(self, trackIndex, channelId, programId, notes, visibleTickSource, width):
        """
        visibleTickSource must provide minVisibleTick and maxVisibleTick members
        """
        super(GuiProgram, self).__init__()
        self.resize(width, 130)
        self._trackIndex = trackIndex
        self._channelId = channelId
        self._programId = programId
        self._guiNotes = [GuiNote(self, visibleTickSource, note) for note in notes]

    def update(self, drawingSurface):
        for note in self._guiNotes:
            note.update(drawingSurface)


class GuiNote(object):

    def __init__(self, guiProgram, visibleTickSource, sequenceNote):
        self._log = logging.getLogger("keyzer:GuiNote")
        self._guiProgram = guiProgram
        self._visibleTickSource = visibleTickSource
        self._sequenceNote = sequenceNote

        self._x = 0
        self._y = 0
        self._width = 0
        self._height = 2

    def getXpixelForTick(self, tick):
        minVisibleTick = self._visibleTickSource.minVisibleTick
        maxVisibleTick = self._visibleTickSource.maxVisibleTick
        widthTicks = maxVisibleTick - minVisibleTick
        widthPixels = self._guiProgram._width
        percent = float(tick - minVisibleTick) / widthTicks
        return self._guiProgram.x() + percent * widthPixels

    def getYpixelForNoteIndex(self, noteIndex):
        minY = self._guiProgram.y()
        programHeight = self._guiProgram._height
        maxMidiNoteNumber = 127
        percent = float(noteIndex) / 127
        return minY + percent * programHeight

    def updatePosition(self):
        sequenceNote = self._sequenceNote
        onPixel = self.getXpixelForTick(sequenceNote.onTick)
        offPixel = self.getXpixelForTick(sequenceNote.offTick)
        self._x = onPixel
        self._width = max(5, offPixel - onPixel)
        self._y = self.getYpixelForNoteIndex(sequenceNote.noteIndex)

    def isVisible(self):
        onTick = self._sequenceNote.onTick
        offTick = self._sequenceNote.offTick
        visibleTickSource = self._visibleTickSource
        return onTick <= visibleTickSource.maxVisibleTick and \
                offTick >= visibleTickSource.minVisibleTick

    def _draw(self, drawingSurface):
        left = int(self._x)
        right = int(self._x + self._width)
        top = int(self._y)
        bottom = int(self._y + self._height)
        drawingSurface.drawRect(left, right, top, bottom)

    def update(self, drawingSurface):
        self.updatePosition()
        if self.isVisible():
            self._draw(drawingSurface)
