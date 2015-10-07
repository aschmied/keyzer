# Introduction

Keyzer is a sight reading trainer for piano.


# Project Status

This is currently a prototype. Only basic functionality has been implemented and the code has only been tested on my 2010 MacBook Pro running Mavericks. See TODO.txt for a list of features that I would like to implement.


# Dependencies

### Python

* Tested on version 2.7.6

### python-rtmidi

* Interface to the MIDI system. Handles port selection and sending and receiving of events
* Tested on version 0.3.1a
* Install with `pip install python-rtmidi`

### Python MIDI

* Toolkit for loading and iterating over MIDI sequences
* https://github.com/vishnubob/python-midi/
* Python 2 only. `2to3` works
* Install with `pip install midi` (you might need `--pre` to allow installation of pre-release software)


### Pyglet

* Sprite and animation toolkit
* Tested on 1.2.4
* Install with `pip install pyglet`
* pyglet does not run in 64-bit mode, so you have to install a universal python binary and edit `keyzer` to run like `arch -32 python main.py $*`

### The USB Driver for Your MIDI Keyboard

# Helpful Tools

### Midi Keys (Mac OSX)

* Generate MIDI events using your computer's keyboard
* http://www.manyetas.com/creed/midikeys.html


# Usage

### Same MIDI device for input and output (e.g. a MIDI keyboard with builtin speakers)

* Connect the MIDI device to your computer via USB
* Probe the MIDI ports: `./keyzer --list-ports`
* Probe the song tracks: `./keyzer --song-path ./beatles-imagine.mid --list-tracks`
* Start Keyzer: `./keyzer --in-port 0 --out-port 0 --song-path ./beatles-imagine.mid --track 0 --channel 0 --program 0`
