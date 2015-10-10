# Copyright (c) 2015, Anthony Schmieder
# Use of this source code is governed by the 2-clause BSD license that
# can be found in the LICENSE.txt file.

"""Loads and manages art assets"""
import pyglet
import os

_ASSET_PATHS = ["res"]
_ASSET_FILE_NAMES = [
    "black_key_down.png",
    "black_key_up.png",
    "white_key_down.png",
    "white_key_up.png",
    "staff_line.png",
]

class Assets(object):

    _loadedAssets = None

    @staticmethod
    def loadAssets():
        Assets._loadedAssets = dict()
        Assets._updateResourcePath()
        for f in _ASSET_FILE_NAMES:
            Assets.loadAsset(f)

    @staticmethod
    def loadAsset(filename):
        Assets._loadedAssets[filename] = pyglet.resource.image(filename)

    @staticmethod
    def _updateResourcePath():
        for p in _ASSET_PATHS:
            pyglet.resource.path.append(os.path.join(os.getcwd(), p))
        pyglet.resource.reindex()

    @staticmethod
    def get(filename):
        if Assets._loadedAssets is None:
            raise RuntimeError("You must initialize the asset manager before "
                               "retrieving assets")
        return Assets._loadedAssets[filename]
