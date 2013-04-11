
class Attachable(object):

    def __init__(self):
        self._attached = []
    
    def attach(self, attached):
        if attached not in self._attached:
            self._attached.append(attached)
    
    def detach(self, attached):
        if attached in self._attached:
            self._attached.remove(attached)
    
    def _getAttached(self):
        return self._attached
