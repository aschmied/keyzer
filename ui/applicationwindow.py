import pyglet
from pyglet.window import key
from pianokeyboard import PianoKeyboard
from songscore import SongScore
from util.attachables import Attachable 

#BOARD_SIZE = (1680, 1050)
BOARD_SIZE = (int(0.75*1680), int(0.75*1050))
WINDOW_CAPTION = "Keezer"

class ApplicationWindow(Attachable):
    
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        
        self._window = pyglet.window.Window(BOARD_SIZE[0], BOARD_SIZE[1],
                                            caption=WINDOW_CAPTION)
        self._fps_display = pyglet.clock.ClockDisplay()
        pyglet.gl.glScalef(0.75, 0.75, 0.75)

        @self._window.event
        def on_draw():
            self._window.clear()
            self._pianoKeyboard.draw()
            self._songScore.draw()
            self._fps_display.draw()
        
        @self._window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.ESCAPE:
                self._window.has_exit = True
            for a in self._getAttached():
                a.onKeyDown(symbol, modifiers)
                
        @self._window.event
        def on_key_release(symbol, modifiers):
            for a in self._getAttached():
                a.onKeyUp(symbol, modifiers)
        
        self.drawScreen()
        #self._window.set_fullscreen(True, width=BOARD_SIZE[0], height=BOARD_SIZE[1])
    
    def drawScreen(self):
        self._pianoKeyboard = PianoKeyboard(0, 0)
        (lowAorigin, lowAsize) = self._pianoKeyboard.getKeyBoundingBox(0)
        (whiteKeyWidth, whiteKeyHeight) = lowAsize
        lowAkeyCentre = lowAorigin[1] + whiteKeyHeight/2.0
        self._songScore = SongScore(whiteKeyWidth, 0, lowAkeyCentre, whiteKeyHeight)

    def start(self):
        pyglet.clock.schedule_interval(self.update, 1/60.)
        pyglet.app.run()

    def update(self, dt):
        self._pianoKeyboard.update(dt)
        self._songScore.update(dt)
    
    def attachToKeyboard(self, objectToAttach):
        '''objectToAttach must implement the keyboard event interface'''
        super(ApplicationWindow, self).attach(objectToAttach)
