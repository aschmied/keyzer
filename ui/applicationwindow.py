import pyglet
from pyglet.window import key
from pianokeyboard import PianoKeyboard
from util.attachables import Attachable 

BOARD_SIZE = (1680, 1050)
WINDOW_CAPTION = "Keezer"

class ApplicationWindow(Attachable):
    
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        
        self._window = pyglet.window.Window(BOARD_SIZE[0], BOARD_SIZE[1],
                                            caption=WINDOW_CAPTION)

        @self._window.event
        def on_draw():
            self._window.clear()
            self._pianoKeyboard.draw()
        
        @self._window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.ESCAPE:
                self._window.has_exit = True
            for a in super(ApplicationWindow, self)._getAttached():
                a.onKeyDown(symbol, modifiers)
                
        @self._window.event
        def on_key_release(symbol, modifiers):
            for a in super(ApplicationWindow, self)._getAttached():
                a.onKeyUp(symbol, modifiers)
        
        self.drawScreen()
        self._window.set_fullscreen(True, width=BOARD_SIZE[0], height=BOARD_SIZE[1])
    
    def drawScreen(self):
        self._pianoKeyboard = PianoKeyboard(0, 0)

    def start(self):
        pyglet.clock.schedule_interval(self.update, 1/60.)
        pyglet.app.run()

    def update(self, dt):
        self._pianoKeyboard.update(dt)
    
    def attachToKeyboard(self, objectToAttach):
        '''objectToAttach must implement the keyboard event interface'''
        super(ApplicationWindow, self).attach(objectToAttach)
        
    
    
    
    



