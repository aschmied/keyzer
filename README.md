# Introduction

Keyzer is a sight reading trainer for piano.


# Dependencies

### Python

* Tested on version 2.7.6

### python-rtmidi

* Interface to the MIDI system. Handles port selection and sending and receiving of events
* Tested on version 0.3.1a
* Installing with pip you might need `--pre` to allow installation of pre-release software

### Python MIDI

* Toolkit for loading and iterating over MIDI sequences
* https://github.com/vishnubob/python-midi/
* Python 2 only. `2to3` works

### Pyglet

* Sprite and animation toolkit
* Tested on 1.2alpha1
* pyglet seems not to like running in 64-bit mode, so you have to install a universal python binary and run like `arch -32 python`

### The Driver for Your MIDI device

# Helpful Tools

### Midi Keys

* Generate MIDI events using your PC's keyboard
* http://www.manyetas.com/creed/midikeys.html