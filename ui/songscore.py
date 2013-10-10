import pyglet

from ui.assetmanager import Assets
from playingsongstate import PlayingSongState
import util.music


class StaffLine(pyglet.sprite.Sprite):

    def __init__(self, image, drawingOrigin, batch=None, group=None):
        self._image = image
        self._drawingOrigin = drawingOrigin
        x = drawingOrigin[0]
        y = drawingOrigin[1]
        super(StaffLine, self).__init__(image, x, y, batch=batch, group=group)


class SongScore(pyglet.graphics.Batch):

    notesWithStaffline = [22, 26, 29, 32, 36, 43, 46, 50, 53, 56]

    def __init__(self, x, y, lowAkeyCentreY, whiteKeyHeight):
        super(SongScore, self).__init__()
        self._x = x
        self._y = y
        self._computeNoteheadOrigins(lowAkeyCentreY, whiteKeyHeight)
        self._getScoreAssets()
        self._drawStaff()

    def _computeNoteheadOrigins(self, lowAkeyCentreY, whiteKeyHeight):
        self._naturalNoteheadOrigins = [(self._x, lowAkeyCentreY)] + 87*[None]
        noteheadYorigin = lowAkeyCentreY
        for i in range(1, 88):
            if not util.music.noteIndexIsSharp(i):
                noteheadYorigin += whiteKeyHeight
                self._naturalNoteheadOrigins[i] = (self._x, noteheadYorigin)

    def _getScoreAssets(self):
        self._staffLineImage = Assets.get("staff_line.png")
        #self.middleCLineImage = Assets.get("staff_middle_c_line.png")

    def _drawStaff(self):
        self._staffLines = []
        for noteIndex in SongScore.notesWithStaffline:
            (x, y) = self._naturalNoteheadOrigins[noteIndex]
            self._staffLines.append(StaffLine(self._staffLineImage, (x, y), self))
        
    def update(self, dt):
        print "Tick: {}".format(PlayingSongState.getCurrentTick())

