import sys
import GD
import gameduino2.gd3registers as gd3
import math
import random

from gameduino2.base import align4

if __name__ == '__main__':
    eve = GD.GD(sys.argv[1])
    eve.setup_480x272()
    eve.cmd_regwrite(gd3.REG_ROTATE, 1)

    # Load the "jet" color LUT into memory. 512 bytes startig at address 0
    # Use it as a color palette

    eve.cmd_loadimage(0, 0)
    eve.c(align4(open("jet.png", "rb").read()))
    eve.PaletteSource(0)

    # Initialize a 256x256 image at address 512
    a = 512
    eve.cmd_loadimage(a, gd3.OPT_MONO)
    eve.c(align4(open("turing.jpg", "rb").read()))

    eve.cmd_setbitmap(a, gd3.PALETTED565, 256, 256)
    eve.BitmapSize(gd3.NEAREST, gd3.BORDER, gd3.REPEAT, 256, 255)

    def update(y, linedata):
        eve.Clear()
        eve.Begin(gd3.BITMAPS)

        eve.BitmapTransformF(256 * ((y - 254) & 0xff))

        eve.Vertex2f(112, 10)

        eve.swap()
        eve.cmd_memwrite(a + 256 * y, len(linedata))
        eve.c(linedata)

    for y in range(154):
        bias = 128 + 20 * math.sin(y * .1)
        signal = [max(0, math.cos(.03 * (i - bias))) for i in range(256)]
        print(signal)
        update(y, bytes([int(255*s) for s in signal]))

    if 0:
        for x in range(256):
            for y in range(256):
                v = int(255 * math.sqrt((x / 256) ** 2 + (y / 256) ** 2) / math.sqrt(2))
                eve.wr(a + 256 * y + x, bytes([v]))


    eve.screenshot_im().save("specgram_5.png")
