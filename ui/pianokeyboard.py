import pyglet
from instrumentstate import InstrumentState

class PianoKeyUp(pyglet.sprite.Sprite):
    def __init__(self, image, x, y, noteIndex, batch=None, group=None):
        self._image = image
        self._x = x
        self._y = y
        self._noteIndex = noteIndex
        super(PianoKeyUp, self).__init__(image, x, y, batch=batch, group=group)
    def update(self, dt):
        velocity = InstrumentState.getNote(self._noteIndex)
        self.visible = (velocity == 0)
            
class PianoKeyDown(pyglet.sprite.Sprite):
    def __init__(self, image, x, y, noteIndex, batch=None, group=None):
        self._image = image
        self._x = x
        self._y = y
        self._noteIndex = noteIndex
        super(PianoKeyDown, self).__init__(image, x, y, batch=batch, group=group)
    def update(self, dt):
        velocity = InstrumentState.getNote(self._noteIndex)
        self.visible = (velocity > 0)
    
class PianoKeyboard(pyglet.graphics.Batch):
    def __init__(self, x, y):
        super(PianoKeyboard, self).__init__()
        self._loadImages()
        whiteKeyGroup = pyglet.graphics.OrderedGroup(0)
        blackKeyGroup = pyglet.graphics.OrderedGroup(1) 
        heightWhite = self._images['white_up'].height
        heightBlack = self._images['black_up'] .height
        self._keys = []
        numWhiteKeysInOctave = 7
        haveSharps = [0, 2, 3, 5, 6]
        noteIndex = 0
        for i in range(0,52):
            whiteKeyCoords = (x, y + i*heightWhite)
            blackKeyCoords = (x, whiteKeyCoords[1] + heightWhite - heightBlack/2)
            self._keys.append(PianoKeyUp(self._images['white_up'], whiteKeyCoords[0], whiteKeyCoords[1],
                noteIndex, self, whiteKeyGroup))
            self._keys.append(PianoKeyDown(self._images['white_down'], whiteKeyCoords[0], whiteKeyCoords[1],
                noteIndex, self, whiteKeyGroup))
            noteIndex += 1
            if i%numWhiteKeysInOctave in haveSharps and i<51:
                self._keys.append(PianoKeyUp(self._images['black_up'], blackKeyCoords[0],
                    blackKeyCoords[1], noteIndex, self, blackKeyGroup))
                self._keys.append(PianoKeyDown(self._images['black_down'], blackKeyCoords[0],
                    blackKeyCoords[1], noteIndex, self, blackKeyGroup))
                noteIndex += 1

    def update(self, dt):
        for key in self._keys:
            key.update(dt)
    
    def _loadImages(self):
        pyglet.resource.path.append("res")
        pyglet.resource.reindex()
        self._images = {}
        self._images['white_up'] = pyglet.resource.image("white_up.png")
        self._images['black_up'] = pyglet.resource.image("black_up.png")
        self._images['white_down'] = pyglet.resource.image("white_down.png")
        self._images['black_down'] = pyglet.resource.image("black_down.png")
