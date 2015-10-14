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
        """
        GuiProgram determines its own height based on the range of notes used.
        """
        super(GuiProgram, self).__init__()

        controlsWidth = 70

        notesWidth = width - controlsWidth
        self._notes = GuiProgramNotes(notes, notesWidth)
        # GuiProgramNotes determines the height of GuiProgramControls and
        # GuiProgram.
        height = self._notes.height()

        self._controls = GuiProgramControls(trackIndex, channelId, programId,
                                            controlsWidth, height)

        self.resize(width, height)

        self.add(self._controls)
        self.add(self._notes)


class GuiProgramControls(ScreenObject):
    """
    Draws controls and metadata.
    """

    def __init__(self, trackIndex, channelId, programId, width, height):
        super(GuiProgramControls, self).__init__()
        self.resize(width, height)
        self._trackIndex = trackIndex
        self._channelId = channelId
        self._programId = programId

    def update(self, drawingSurface):
        text = "t{} c{} p{}".format(self._trackIndex, self._channelId, self._programId)
        textX = self._x
        textY = self._y + (self._height / 2)
        drawingSurface.drawText(text=text, fontName="Arial", fontSize=10,
                                x=textX, y=textY, anchorY="center")
        drawingSurface.drawBox(self._x, self._y,
                               self._x + self._width, self._y + self._height,
                               colour=(128, 128, 128, 255))


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

        self._beatsOnScreen = 24
        self.minVisibleTick = 0
        self.maxVisibleTick = 0
        
        minNoteId = 99999999
        maxNoteId = -1
        for note in notes:
            if note.noteIndex < minNoteId:
                minNoteId = note.noteIndex
            if note.noteIndex > maxNoteId:
                maxNoteId = note.noteIndex
        self._minNoteId = minNoteId
        self._maxNoteId = maxNoteId
        heightPerNote = 2
        height = heightPerNote * (maxNoteId - minNoteId + 1)

        self.resize(width, height)

        self._guiNotes = [GuiNote(self, self, note) for note in notes]

    def update(self, drawingSurface):
        # TODO: this is computed for each track/channel/program tuple. It should
        # be done once per frame.
        self.minVisibleTick = PlayingSongState.getCurrentTick()
        ticksOnScreen = self._beatsOnScreen * PlayingSongState.getTicksPerBeat()
        self.maxVisibleTick = self.minVisibleTick + ticksOnScreen

        drawingSurface.drawBox(self._x, self._y,
                               self._x + self._width, self._y + self._height,
                               colour=(128, 128, 128, 255))

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
        minY = self._guiProgramNotes._y
        programHeight = self._guiProgramNotes._height
        minNoteId = self._guiProgramNotes._minNoteId
        maxNoteId = self._guiProgramNotes._maxNoteId
        percent = float(noteIndex - minNoteId) / (maxNoteId - minNoteId)
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
