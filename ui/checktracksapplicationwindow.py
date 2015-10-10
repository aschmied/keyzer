# Copyright (c) 2015, Anthony Schmieder
# Use of this source code is governed by the 2-clause BSD license that
# can be found in the LICENSE.txt file.

import pyglet
from pyglet.window import key

WINDOW_CAPTION = "Keyzer player"
WINDOW_SIZE = (100, 100)

class CheckTracksApplicationWindow(object):

    def __init__(self):
        super(CheckTracksApplicationWindow, self).__init__()
        self._window = pyglet.window.Window(WINDOW_SIZE[0], WINDOW_SIZE[1],
                                            caption=WINDOW_CAPTION)
        self._fps_display = pyglet.clock.ClockDisplay()

        @self._window.event
        def on_key_release(symbol, modifiers):
            if symbol == key.ESCAPE:
                self._window.has_exit = True

    def start(self):
        pyglet.app.run()
