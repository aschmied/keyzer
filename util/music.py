def noteIndexIsSharp(noteIndex):
    """x->boolean where x in 0, 1, ..., 87. True if note index x is sharp"""
    sharpKeysInOctave = [1, 4, 6, 9, 11] # 0=low A
    return noteIndex % 12 in sharpKeysInOctave and noteIndex < 86


