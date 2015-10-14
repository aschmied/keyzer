# Copyright (c) 2015, Anthony Schmieder
# Use of this source code is governed by the 2-clause BSD license that
# can be found in the LICENSE.txt file.

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
                ('c4B', 4 * colour))
        self._vertexLists.append(vertexList)

    def drawLine(self, x0, y0, x1, y1, colour=(255, 255, 255, 255)):
        vertexList = self.add(2, pyglet.gl.GL_LINES, None,
                ('v2i', [x0, y0, x1, y1]),
                ('c4B', 2 * colour))
        self._vertexLists.append(vertexList)

    def drawBox(self, x0, y0, x1, y1, colour=(255, 255, 255, 255)):
        self.drawLine(x0, y0, x1, y0, colour)
        self.drawLine(x1, y0, x1, y1, colour)
        self.drawLine(x1, y1, x0, y1, colour)
        self.drawLine(x0, y1, x0, y0, colour)

    def drawText(self, text="",
        fontName=None, fontSize=None, bold=False, italic=False,
        colour=(255, 255, 255, 255), x=0, y=0,
        anchorX="left", anchorY="baseline"):
        label = pyglet.text.Label(text, fontName, fontSize, bold, italic,
                                  colour, x, y, anchor_x=anchorX, anchor_y=anchorY,
                                  batch=self)
        self._vertexLists.append(label)

    def clear(self):
        for vertexList in self._vertexLists:
            vertexList.delete()
        del self._vertexLists[:]

class ScreenObject(object):
    """
    An object that may be added to a Layout.
    """

    def __init__(self):
        self._x = 0
        self._y = 0
        self._width = 0
        self._height = 0

    def move(self, x, y):
        self._x = x
        self._y = y

    def resize(self, width, height):
        self._width = width
        self._height = height

    def x(self):
        return self._x

    def y(self):
        return self._y

    def width(self):
        return self._width

    def height(self):
        return self._height

    def update(self, drawingSurface):
        raise RuntimeError("Method not implemented")


class VerticalLayout(ScreenObject):
    """
    Lays out screenObjects from top to bottom.
    """

    def __init__(self):
        super(VerticalLayout, self).__init__()
        self._ycursor = 0
        self._children = []

    def add(self, screenObject):
        self._children.append(screenObject)
        screenObject.move(self._x, self._ycursor)
        self._ycursor += screenObject.height()

    def move(self, x, y):
        dx = x - self._x
        dy = y - self._y
        self._x += dx
        self._y += dy
        for child in self._children:
            child.move(child.x() + dx, child.y() + dy)
        self._ycursor += dy

    def resize(self, width, height):
        self._width = width
        self._height = height
        for child in self._children:
            child.resize(width, child.height())

    def update(self, drawingSurface):
        for child in self._children:
            child.update(drawingSurface)


class HorizontalLayout(ScreenObject):
    """
    Lays out screenObjects from left to right.
    """

    def __init__(self):
        super(HorizontalLayout, self).__init__()
        self._xcursor = 0
        self._children = []

    def add(self, screenObject):
        self._children.append(screenObject)
        screenObject.move(self._xcursor, self._y)
        self._xcursor += screenObject.width()

    def move(self, x, y):
        dx = x - self._x
        dy = y - self._y
        self._x += dx
        self._y += dy
        for child in self._children:
            child.move(child.x() + dx, child.y() + dy)
        self._xcursor += dx

    def resize(self, width, height):
        self._width = width
        self._height = height
        for child in self._children:
            child.resize(child.width(), height)

    def update(self, drawingSurface):
        for child in self._children:
            child.update(drawingSurface)
