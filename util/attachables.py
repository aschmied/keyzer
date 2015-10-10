# Copyright (c) 2015, Anthony Schmieder
# Use of this source code is governed by the 2-clause BSD license that
# can be found in the LICENSE.txt file.

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
