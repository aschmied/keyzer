import pyglet

class Sprite(pyglet.sprite.Sprite):

    def __init__(self, image, drawingOrigin, drawingSurface=None):
        self._image = image
        self._drawingOrigin = drawingOrigin
        x = drawingOrigin[0]
        y = drawingOrigin[1]
        super(Sprite, self).__init__(image, x, y, batch=drawingSurface, group=None)


class DrawingSurface(pyglet.graphics.Batch):

    def __init__(self):
        super(DrawingSurface, self).__init__()
        self._vertexLists = []

    def drawRect(self, pixLeft, pixRight, pixTop, pixBottom,
            colour=(255, 255, 255, 255)):
        vertexList = self.add(4, pyglet.gl.GL_QUADS, None,
                ('v2i', [pixLeft, pixTop,
                         pixRight, pixTop,
                         pixRight, pixBottom,
                         pixLeft, pixBottom]),
                ('c4B', 4*colour))
        self._vertexLists.append(vertexList)

    def clear(self):
        for vertexList in self._vertexLists:
            vertexList.delete()
        del self._vertexLists[:]
