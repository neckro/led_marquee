# Marquee scroller

This is a silly thing I wrote for Raspberry Pi and Arduino.  There are two
parts, an Arduino sketch and a Python module.

## led_marquee.ino

Requires [LedControl library](http://playground.arduino.cc/Main/LedControl).

A simple Arduino sketch that reads data from the serial port and scrolls
columns on an attached LED matrix using the LedControl library for Maxim LED
controllers. It's currently hardcoded for an 8x8 pixel display but could easily
be modified for other controllers or sizes.

The data format is currently pairs of (lowercase) hexadecimal digits.  If any
invalid character is received, it is ignored and value reading is aborted
(for example 'a 4 b 8 7' would do nothing because of the spaces).  This is to
avoid possible desynchronization.

## marquee.py

This Python module writes data to the serial port for use with led_marquee.ino.
Intended for use with the Raspberry Pi but should work anywhere.

Parameter 'serial' is a dict of parameters for a pySerial object.  If it is set
to None it will output to stdout instead, for testing/amusement purposes.
If the module is run directly it reads files specified on the command line
or text piped via stdin.

I've had a tricky time finding TrueType pixel fonts that look good at 8px
height without being so wide that they take forever to scroll.  Here are the
ones I found that worked reasonably well:

* [TinyUnicode](http://www.dafont.com/tinyunicode.font)
* [Uni-05](http://www.dafont.com/uni-05-x.font)
* [Pixel Millennium](http://www.dafont.com/pixel-millennium.font)

Requires the Python Imaging Library (PIL) with FreeType support compiled.

---
Copyright © 2013 neckro@gmail.com

This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.
