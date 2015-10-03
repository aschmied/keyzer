# Introduction

Keyzer is a sight reading trainer for piano.


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
* Install with `pip install midi`

### Pyglet

* Sprite and animation toolkit
* Tested on 1.2alpha1
* Install with `pip install pyglet`

### The USB Driver for Your Keyboard

# Helpful Tools

### Midi Keys

* Generate MIDI events using your PC's keyboard
* http://www.manyetas.com/creed/midikeys.html


# Usage

### Same MIDI device for input and output (e.g. a keyboard with builtin speakers)

* Connect the MIDI device to your computer via USB
* Probe the MIDI ports: `./keyzer --list-ports`
* Probe the song tracks: `./keyzer --song-path ./beatles-imagine.mid --list-tracks`
* Start Keyzer: `./keyzer --in-port 0 --out-port 0 --song-path ./beatles-imagine.mid --track 0 --channel 0 --program 0`
