# Copyright (c) 2015, Anthony Schmieder
# Use of this source code is governed by the 2-clause BSD license that
# can be found in the LICENSE.txt file.

import logging
import pyglet
from pyglet.window import key

from checktrackssongscore import CheckTracksSongScore

WINDOW_CAPTION = "Keyzer player"
WINDOW_SIZE = (int(0.75 * 1680), int(0.75 * 1050))

class CheckTracksApplicationWindow(object):

    def __init__(self, noteSequence):
        super(CheckTracksApplicationWindow, self).__init__()
        self._log = logging.getLogger("keyzer:CheckTracksApplicationWindow")
        self._window = pyglet.window.Window(WINDOW_SIZE[0], WINDOW_SIZE[1],
                                            caption=WINDOW_CAPTION)
        self._songScore = CheckTracksSongScore(0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1], noteSequence)
        self._fps_display = pyglet.clock.ClockDisplay()

        @self._window.event
        def on_draw():
            self._log.debug("on_draw")
            self._window.clear()
            self._songScore.draw()
            self._fps_display.draw()

        @self._window.event
        def on_key_release(symbol, modifiers):
            if symbol == key.ESCAPE:
                self._window.has_exit = True

    def start(self):
        pyglet.clock.schedule_interval(self.update, 1.0 / 60)
        pyglet.app.run()

    def update(self, dt):
        self._log.debug("update")
        self._songScore.update(dt)
