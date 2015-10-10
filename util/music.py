# Copyright (c) 2015, Anthony Schmieder
# Use of this source code is governed by the 2-clause BSD license that
# can be found in the LICENSE.txt file.

def noteIndexIsSharp(noteIndex):
    """x->boolean where x in 0, 1, ..., 87. True if note index x is sharp"""
    sharpKeysInOctave = [1, 4, 6, 9, 11] # 0=low A
    return noteIndex % 12 in sharpKeysInOctave and noteIndex < 86

def midiPitchToNoteIndex(pitch):
    """TODO: this is also hardcoded in instrument/midi.py"""
    return pitch - 21
