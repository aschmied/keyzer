import logging
import pyglet

from ui.assetmanager import Assets
from playingsongstate import PlayingSongState
import util.music


class StaffLine(pyglet.sprite.Sprite):

    def __init__(self, image, drawingOrigin, batch=None, group=None):
        # stafflines in a batch below noteheads
        self._image = image
        self._drawingOrigin = drawingOrigin
        x = drawingOrigin[0]
        y = drawingOrigin[1]
        super(StaffLine, self).__init__(image, x, y, batch=batch, group=group)


class ScoreNote(object):

    def __init__(self, sequenceNote):
        self._log = logging.getLogger("keyzer:ScoreNote")
        self._sequenceNote = sequenceNote

        self._x = 0
        self._y = 0
        self._width = 0
        self._height = 10
        # TODO: This line was removed in my local repo, but the change uncommitted.
        # Don't remember why. Look into it when the project is resurrected
        # self.visible = False

    def isVisible(self, score):
        self._log.debug("isVisible()")
        onTick = self._sequenceNote.onTick
        offTick = self._sequenceNote.offTick
        return onTick <= score._windowTickMax and offTick >= score._windowTickMin

    def updateState(self, score):
        self._log.debug("updateState()")
        onPix = score.getXpixelForTick(self._sequenceNote.onTick)
        offPix = score.getXpixelForTick(self._sequenceNote.offTick)
        self._x = onPix
        self._width = max(10, offPix - onPix)
        yCentre = score.getYpixelForNoteIndex(self._sequenceNote.noteIndex)
        self._y = yCentre - self._height

    def _draw(self, score):
        self._log.debug("_draw()")
        left = int(self._x)
        right = int(self._x + self._width)
        top = int(self._y)
        bottom = int(self._y + self._height)
        score.drawRect(left, right, top, bottom)

    def update(self, score):
        self._log.debug("update()")
        self.updateState(score)
        if self.isVisible(score):
            self._draw(score)

class SongScore(pyglet.graphics.Batch):

    notesWithStaffline = [22, 26, 29, 32, 36, 43, 46, 50, 53, 56]

    def __init__(self, x, y, lowAkeyCentreY, whiteKeyHeight):
        super(SongScore, self).__init__()
        self._log = logging.getLogger("keyzer:SongScore")
        self._x = x
        self._y = y
        self._whiteKeyHeight = whiteKeyHeight
        self._beatsOnScreen = 12
        self._sharpKey = True
        self._computeNoteheadOrigins(lowAkeyCentreY)

        self._initializeScoreNotes()
        self._getScoreAssets()
        self._drawStaff()
        self._computePixBounds()

    def _computeNoteheadOrigins(self, lowAkeyCentreY):
        self._naturalNoteheadOrigins = [(self._x, lowAkeyCentreY)] + 87*[None]
        noteheadYorigin = lowAkeyCentreY
        for i in range(1, 88):
            if not util.music.noteIndexIsSharp(i):
                noteheadYorigin += self._whiteKeyHeight
                self._naturalNoteheadOrigins[i] = (self._x, noteheadYorigin)

    def _getScoreAssets(self):
        self._staffLineImage = Assets.get("staff_line.png")

    def _drawStaff(self):
        self._staffLines = []
        for noteIndex in SongScore.notesWithStaffline:
            (x, y) = self._naturalNoteheadOrigins[noteIndex]
            self._staffLines.append(StaffLine(self._staffLineImage, (x, y), self))
        
    def _initializeScoreNotes(self):
        self._notes = [ScoreNote(note)
                       for note in PlayingSongState.getNotes()]

    def _computePixBounds(self):
        self._windowPixMin = self._x
        self._windowPixMax = self._x + self._staffLines[0].width

    def getXpixelForTick(self, tick):
        widthTicks = self._windowTickMax - self._windowTickMin
        widthPix = self._windowPixMax - self._windowPixMin
        percent = float(tick-self._windowTickMin) / widthTicks
        pix = self._windowPixMin + percent * widthPix
        return min(max(pix, self._windowPixMin), self._windowPixMax)

    def getYpixelForNoteIndex(self, noteIndex):
        if util.music.noteIndexIsSharp(noteIndex):
            if self._sharpKey:
                noteCentreIndex = noteIndex - 1
            else:
                noteCentreIndex = noteIndex + 1
        else:
            noteCentreIndex = noteIndex
        return self._naturalNoteheadOrigins[noteCentreIndex][1]

    def drawRect(self, pixLeft, pixRight, pixTop, pixBot,
            colour=(255, 255, 255, 255)):
        self._log.debug("_drawRect({}, {}, {}, {})".format(
                pixLeft, pixRight, pixTop, pixBot))

        self.add(4, pyglet.gl.GL_QUADS, None,
                ('v2i', [pixLeft, pixTop,
                         pixRight, pixTop,
                         pixRight, pixBot,
                         pixLeft, pixBot]),
                ('c4B', 4*colour))

    def _updateState(self):
        self._log.debug("_updateState()")
        self._windowTickMin = PlayingSongState.getCurrentTick()
        ticksOnScreen = self._beatsOnScreen * PlayingSongState.getTicksPerBeat()
        self._windowTickMax = self._windowTickMin + ticksOnScreen
        self._log.debug("windowTickMin={} windowTickMax={} ticksOnScreen={}".format(self._windowTickMin, self._windowTickMax, ticksOnScreen))

    def _updateScreen(self):
        self._log.debug("_updateScreen()")
        #for staffLine in self._staffLines:
            #staffLine.update(dt)
        self.drawRect(self._x, self._x + 2000, self._y, self._y + 1000, (0, 0, 0, 255))
        for note in self._notes:
            note.update(self)
        
    def update(self, dt):
        self._updateState()
        self._updateScreen()

