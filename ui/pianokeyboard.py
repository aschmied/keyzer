import pyglet
from ui.assetmanager import Assets
from instrumentstate import InstrumentState


class PianoKey(pyglet.sprite.Sprite):

    def __init__(self, image, drawingOrigin, noteIndex, batch=None, group=None):
        self._image = image
        self._drawingOrigin = drawingOrigin
        x = drawingOrigin[0]
        y = drawingOrigin[1]
        self._noteIndex = noteIndex
        super(PianoKey, self).__init__(image, x, y, batch=batch, group=group)


class PianoKeyUp(PianoKey):

    def __init__(self, image, drawingOrigin, noteIndex, batch=None, group=None):
        super(PianoKeyUp, self).__init__(image, drawingOrigin, noteIndex,
                                         batch=batch, group=group)

    def update(self, dt):
        velocity = InstrumentState.getNote(self._noteIndex)
        self.visible = (velocity == 0)


class PianoKeyDown(PianoKey):

    def __init__(self, image, drawingOrigin, noteIndex, batch=None, group=None):
        super(PianoKeyDown, self).__init__(image, drawingOrigin, noteIndex,
                                           batch=batch, group=group)
    def update(self, dt):
        velocity = InstrumentState.getNote(self._noteIndex)
        self.visible = (velocity > 0)


class PianoKeyboard(pyglet.graphics.Batch):

    def __init__(self, x, y):
        super(PianoKeyboard, self).__init__()
        self._x = x
        self._y = y
        self._getPianoKeyAssets()
        self._whiteKeyLayer = pyglet.graphics.OrderedGroup(0)
        self._blackKeyLayer = pyglet.graphics.OrderedGroup(1) 
        self._initKeys()

    def _initKeys(self):
        self._keys = []
        drawingCursor = (self._x, self._y)
        for noteIndex in range(0,88):
            if self._noteIndexIsSharp(noteIndex):
                drawingCursor = self._initBlackKey(noteIndex, drawingCursor)
            else:
                drawingCursor = self._initWhiteKey(noteIndex, drawingCursor)

    def _getPianoKeyAssets(self):
        self.bDownImage = Assets.get("black_key_down.png")
        self.wDownImage = Assets.get("white_key_down.png")
        self.bUpImage = Assets.get("black_key_up.png")
        self.wUpImage = Assets.get("white_key_up.png")

    def _noteIndexIsSharp(self, noteIndex):
        sharpKeysInOctave = [1, 4, 6, 9, 11] # 0=A
        return noteIndex % 12 in sharpKeysInOctave and noteIndex < 86

    def _initBlackKey(self, noteIndex, drawingCursor):
        drawingCursorBlackKey = (drawingCursor[0], 
                                 drawingCursor[1] - self.bUpImage.height/2)
        keyup = PianoKeyUp(self.bUpImage, drawingCursorBlackKey, noteIndex,
                           self, self._blackKeyLayer)
        keydown = PianoKeyDown(self.bDownImage, drawingCursorBlackKey,
                               noteIndex, self, self._blackKeyLayer)
        self._keys.append(keyup)
        self._keys.append(keydown)
        return drawingCursor

    def _initWhiteKey(self, noteIndex, drawingCursor):
        keyup = PianoKeyUp(self.wUpImage, drawingCursor, noteIndex,
                           self, self._whiteKeyLayer)
        keydown = PianoKeyDown(self.wDownImage, drawingCursor, noteIndex,
                               self, self._whiteKeyLayer)
        self._keys.append(keyup)
        self._keys.append(keydown)
        return (drawingCursor[0], drawingCursor[1] + keyup.height)

    def update(self, dt):
        for key in self._keys:
            key.update(dt)
    
    def getKeyBoundingBox(self, noteIndex):
        key = self._keys[noteIndex]
        origin = (key._x, key._y)
        size = (key.width, key.height)
        return (origin, size)
