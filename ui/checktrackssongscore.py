# Copyright (c) 2015, Anthony Schmieder
# Use of this source code is governed by the 2-clause BSD license that
# can be found in the LICENSE.txt file.

import logging
import pyglet

from ui.components import DrawingSurface
from ui.components import HorizontalLayout
from ui.components import ScreenObject
from ui.components import VerticalLayout
from playingsongstate import PlayingSongState


class CheckTracksSongScore(VerticalLayout):

    def __init__(self, x, y, width, height, sequence):
        super(CheckTracksSongScore, self).__init__()
        self._log = logging.getLogger("keyzer:CheckTracksSongScore")
        self.move(x, y)
        self.resize(width, height)
        self._sequence = sequence
        for track in sequence:
            trackIndex = track.trackIndex
            for channel in track:
                channelId = channel.channelId
                for programId in channel.getPrograms():
                    notes = channel.getNotesForProgram(programId)
                    guiProgram = GuiProgram(trackIndex, channelId, programId, notes, width)
                    self.add(guiProgram)
        self._drawingSurface = DrawingSurface()

    def update(self, dt):
        self._drawingSurface.clear()
        super(CheckTracksSongScore, self).update(self._drawingSurface)

    def draw(self):
        self._drawingSurface.draw()


class GuiProgram(HorizontalLayout):
    """
    Draws controls, metadata, and notes for one program in a particular channel 
    of a MIDI track.
    """

    def __init__(self, trackIndex, channelId, programId, notes, width):
        super(GuiProgram, self).__init__()
        self.resize(width, 130)

        controlsWidth = 30

        notesWidth = width - controlsWidth
        self._notes = GuiProgramNotes(notes, notesWidth)
        
        controlsHeight = self._notes.height()
        self._controls = GuiProgramControls(trackIndex, channelId, programId,
                                            controlsWidth, controlsHeight)

        self.add(self._controls)
        self.add(self._notes)


class GuiProgramControls(ScreenObject):
    """
    Draws controls and metadata.
    """

    def __init__(self, trackIndex, channelId, programId, width, height):
        super(GuiProgramControls, self).__init__()
        self.resize(width, height)

    def update(self, drawingSurface):
        pass
        # drawingSurface.drawRect(self._x, self._x + self._width,
        #                         self._y, self._y + self._height)


class GuiProgramNotes(ScreenObject):
    """
    Draws notes.
    """

    def __init__(self, notes, width):
        """
        visibleTickSource must provide minVisibleTick and maxVisibleTick members
        """
        super(GuiProgramNotes, self).__init__()
        self._log = logging.getLogger("keyzer:GuiProgramNotes")
        self.resize(width, 130)

        self._beatsOnScreen = 24
        self.minVisibleTick = 0
        self.maxVisibleTick = 0
        
        self._guiNotes = [GuiNote(self, self, note) for note in notes]

    def update(self, drawingSurface):
        # TODO: this is computed for each track/channel/program tuple. It should
        # be done once per frame.
        self.minVisibleTick = PlayingSongState.getCurrentTick()
        ticksOnScreen = self._beatsOnScreen * PlayingSongState.getTicksPerBeat()
        self.maxVisibleTick = self.minVisibleTick + ticksOnScreen

        for note in self._guiNotes:
            note.update(drawingSurface)


class GuiNote(object):

    def __init__(self, guiProgramNotes, visibleTickSource, sequenceNote):
        self._log = logging.getLogger("keyzer:GuiNote")
        self._guiProgramNotes = guiProgramNotes
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
        widthPixels = self._guiProgramNotes._width
        percent = float(tick - minVisibleTick) / widthTicks
        return self._guiProgramNotes.x() + percent * widthPixels

    def getYpixelForNoteIndex(self, noteIndex):
        minY = self._guiProgramNotes.y()
        programHeight = self._guiProgramNotes._height
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
        left = max(self._guiProgramNotes._x, int(self._x))
        right = int(self._x + self._width)
        top = int(self._y)
        bottom = int(self._y + self._height)
        drawingSurface.drawRect(left, right, top, bottom)

    def update(self, drawingSurface):
        self.updatePosition()
        if self.isVisible():
            self._draw(drawingSurface)
