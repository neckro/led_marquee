#!/usr/bin/env python

# Marquee generator, neckro@gmail.com 2013.
# See README.md for details.

from PIL import Image, ImageFont, ImageDraw
from time import sleep
import string
import argparse

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


def parse_arguments():
    parser = argparse.ArgumentParser(description='Scroll text.')
    parser.add_argument('--debug', action='store_true',
        help='Debug mode (output to screen)')
    parser.add_argument('-t', '--typewriter', action='store_true',
        help='Typewriter mode')
    parser.add_argument('-p', '--port', action='store', default=None, type=str,
        help='Serial port, ex: /dev/ttyUSB0')
    parser.add_argument('-b', '--baud', action='store', default=9600, type=int,
        help='Serial port baud rate (default: %(default)s')
    parser.add_argument('-d', '--delay', action='store', default=30, type=int,
        help='Delay between updates in milliseconds (default: %(default)s ms)')
    parser.add_argument('-w', action='store', default=2, dest='space_width', metavar='width', type=int,
        help='Space width (default: %(default)s)')
    parser.add_argument('-f', '--font', action='store', choices=fonts, default='tinyunicode', help='Choose a predefined font (default: %(default)s)')
    parser.add_argument('files', nargs='?', default=[], help='Text file(s) to output, or stdin if no files specified.')
    args = parser.parse_args()
    args.font = fonts[args.font]
    if args.debug is False and args.port is None:
        print "No serial port specified, turning on debug output."
        args.debug = True
    marquee = Marquee(**vars(args))
    if args.typewriter:
        raise NotImplementedError
    else:
        from fileinput import input
        for line in input(files=args.files):
            marquee.write_line(line, u'\u00b6')  # prefix with pilcrow
        marquee.flush()


class Marquee(object):
    def __init__(self, port, baud, font, delay, space_width, initial_sleep=1.5, bits=8, font_dir='fonts', debug=False, **kwargs):
        self.delay = delay
        self.space_width = space_width
        self.bits = bits
        self.debug = debug
        if port is not None:
            from serial import Serial
            self.serial = Serial(port=port, baudrate=baud)
            # need to wait for arduino to reset
            sleep(initial_sleep)
        else:
            self.serial = None
        self.font_offset = font.pop('offset', 0)
        if font['file'] is not None:
            font['file'] = font_dir + '/' + font['file']
        self.font = ImageFont.truetype(font['file'], font['size'], encoding='unic')

    def output(self, num):
        # zero padded lowercase 8-bit hex
        h = ('%02X' % (num)).lower()
        if self.serial is not None:
            self.serial.write(h + ' ')
        if self.debug:
            # write to console
            print h, '|', bin(int(h, 16))[2:].zfill(self.bits).translate(string.maketrans('01', ' #')), '|'
        sleep(self.delay / 1000.0)

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
    parse_arguments()
