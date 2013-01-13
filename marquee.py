#!/usr/bin/env python

from serial import Serial
from time import sleep
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from fileinput import input

led = Serial("/dev/ttyUSB0", 9600)
delay = 0.035
font = "TinyUnicode.ttf"
# need to wait for arduino to reset
sleep(1.5)
space_width = 3


def led_output(n):
    # zero padded lowercase 8-bit hex
    h = ('%02X' % (n)).lower()
    led.write(h)
    #print(h)
    sleep(delay)


def random_blink():
    from random import randint
    while False:
        led_output(randint(0, 255))


def iterate_binary():
    while False:
        for n in xrange(256):
            led_output(n)


def get_string_image(s, typeface):
    font = ImageFont.truetype(typeface, 16, encoding="unic")
    size = font.getsize(s)
    image = Image.new("1", (size[0], 8), (0))
    ImageDraw.Draw(image).text((0, -5), s, (1), font=font)
    return image


def parse_image(image, func):
    pixels = image.load()
    for x in xrange(image.size[0]):
        val = 0
        for y in xrange(image.size[1]):
            val += (1 << y) if pixels[x, y] else 0
        func(val)


# scroll past edge of display
def led_flush():
    led_scroll(8)


def led_scroll(w):
    for n in xrange(w):
        led_output(0)


def led_string(s):
    image = get_string_image(s, font)
    parse_image(image, led_output)


def led_word(w):
    led_string(w)
    led_scroll(space_width)


if __name__ == "__main__":
    for line in input():
        line = ' '.join(line.split())
        if line.__len__() == 0:
            led_flush()
        else:
            led_word(u'\u00b6')
            [led_word(w) for w in line.split()]
    led_flush()
