import pyglet
from ui.assetmanager import Assets
#from playingsongstate import PlayingSongState

class StaffLine(pyglet.sprite.Sprite):

    def __init__(self, image, drawingOrigin, batch=None, group=None):
        self._image = image
        self._drawingOrigin = drawingOrigin
        x = drawingOrigin[0]
        y = drawingOrigin[1]
        super(StaffLine, self).__init__(image, x, y, batch=batch, group=group)


class SongScore(pyglet.graphics.Batch):

    def __init__(self, x, y, lowAkeyCentreY, whiteKeyHeight):
        super(SongScore, self).__init__()
        self._x = x
        self._y = y
        #self._noteheadOrigins = 88 * [-1]
        whiteKeyIndexes = range(0, 52)
        self._noteheadOrigins = [(x, lowAkeyCentreY + i*whiteKeyHeight)
                                 for i in whiteKeyIndexes]
        self._getScoreAssets()
        self._drawStaff()

    def _getScoreAssets(self):
        self._staffLineImage = Assets.get("staff_line.png")
        #self.middleCLineImage = Assets.get("staff_middle_c_line.png")

    def _drawStaff(self):
        self._staffLines = []
        for (x, y) in self._noteheadOrigins[1::2]:
            self._staffLines.append(StaffLine(self._staffLineImage, (x, y), self))
        
    def update(self, dt):
        pass
