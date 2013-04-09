
class Attachable(object):

    def __init__(self):
        self.attached = []
    
    def attach(self, attached):
        if attached not in self.attached:
            self.attached.append(attached)
    
    def detach(self, attached):
        if attached in self.attached:
            self.attached.remove(attached)
