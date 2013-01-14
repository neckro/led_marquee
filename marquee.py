#!/usr/bin/env python

# Marquee generator, neckro@gmail.com 2013.
# See README.md for details.

from PIL import Image, ImageFont, ImageDraw
from time import sleep
import string


def marquee_stdin():
    from fileinput import input
    marquee = Marquee(**marquee_settings)
    for line in input():
        marquee.write_line(line, u'\u00b6')  # prefix with pilcrow

serial_settings = {'port': '/dev/ttyUSB0', 'baudrate': 9600}

fonts = {
    'tinyunicode': {
        'file': 'TinyUnicode.ttf',
        'size': 16,
        'offset': -5
    },
    'uni05': {
        'file': 'uni05_53.ttf',
        'size': 8,
        'offset': -1
    },
    'millennium': {
        'file': 'Pixel Millennium.ttf',
        'size': 8,
        'offset': 0
    }
}

marquee_settings = {
    'serial': None,
    'font': fonts['tinyunicode'],
    'delay': 0.035,
    'space_width': 2,
    'font_dir': 'fonts'
}


class Marquee(object):
    def __init__(self, serial=None, font=None, delay=0, space_width=3, initial_sleep=1.5, bits=8, font_dir='.'):
        self.delay = delay
        self.space_width = space_width
        self.bits = bits
        if serial is not None:
            from serial import Serial
            self.serial = Serial(**serial)
            # need to wait for arduino to reset
            sleep(initial_sleep)
        else:
            self.serial = None
        if font is not None:
            self.font_offset = font.pop('offset', 0)
            if font['file'] is not None:
                font['file'] = font_dir + '/' + font['file']
            self.font = ImageFont.truetype(font['file'], font['size'], encoding='unic')
        else:
            self.font = None
            self.font_offset = 0

    def output(self, num):
        # zero padded lowercase 8-bit hex
        h = ('%02X' % (num)).lower()
        if self.serial is not None:
            self.serial.write(h + ' ')
        else:
            # write to console for debugging
            print h, '|', bin(int(h, 16))[2:].zfill(self.bits).translate(string.maketrans('01', ' #')), '|'
        sleep(self.delay)

    def scroll(self, w):
        for n in xrange(w):
            self.output(0)

    def flush(self):
        self.scroll(self.bits)

    def image_from_string(self, s):
        size = self.font.getsize(s)
        image = Image.new('1', (size[0], self.bits), (0))
        ImageDraw.Draw(image).text((0, self.font_offset), s, (1), font=self.font)
        return image

    def output_image(self, image):
        pixels = image.load()
        for x in xrange(image.size[0]):
            val = 0
            for y in xrange(image.size[1]):
                val += (1 << y) if pixels[x, y] else 0
            self.output(val)

    # blindly write a string without any splitting or preformatting
    def write(self, s):
        self.output_image(self.image_from_string(s))

    # write a string with a trailing space
    def write_word(self, w):
        if w.__len__ > 0:
            self.write(w)
            self.scroll(self.space_width)

    # write a string word by word
    def write_line(self, s, prefix='', postfix=''):
        s.strip()
        if s.__len__ == 0:
            # flush display on an empty line/string
            self.flush()
        else:
            # output each word individually
            self.write_word(prefix)
            [self.write_word(w) for w in s.split()]
            self.write_word(postfix)

    # write random data
    def led_random(self):
        from random import randint
        self.output(randint(0, 1 << self.bits - 1))

    # iterate all values to display
    def led_interate(self):
        for n in xrange(1 << self.bits):
            self.output(n)


if __name__ == "__main__":
    marquee_stdin()
