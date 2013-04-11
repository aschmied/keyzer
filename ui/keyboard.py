import pyglet
from util.attachables import Attachable 

class Keyboard(Attachable):
    def __init__(self):
        super(Keyboard, self).__init__()
        self._window = pyglet.window.Window()
    
        @self._window.event
        def on_key_press(symbol, modifiers):
            for a in super(Keyboard, self)._getAttached():
                a.onKeyDown(symbol, modifiers)
            
        @self._window.event
        def on_key_release(symbol, modifiers):
            for a in super(Keyboard, self)._getAttached():
                a.onKeyUp(symbol, modifiers)
      
    '''
    objectToAttach must implement the keyboard callback interface
    '''
    def attach(self, objectToAttach):
        super(Keyboard, self).attach(objectToAttach)
    
    def displayGui(self):
        pyglet.app.run()