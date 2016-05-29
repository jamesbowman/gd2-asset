import Image
import array
import random

from gameduino2.registers import *
from gameduino2.imbytes import imbytes

def convert(im, dither = False, fmt = ARGB1555):
    """ Convert PIL image to GD2 format, optionally dithering"""
    im = im.convert({
        ARGB1555 : "RGBA",
        L1 : "L",
        L4 : "L",
        L8 : "L",
        RGB332 : "RGB",
        ARGB2 : "RGBA",
        ARGB4 : "RGBA",
        RGB565 : "RGB",
        PALETTED : "RGB"}[fmt])
    imdata = []
    colorfmts = {
        ARGB1555 : (1, 5, 5, 5),
        RGB332 :   (0, 3, 3, 2),
        ARGB2 :    (2, 2, 2, 2),
        ARGB4 :    (4, 4, 4, 4),
        RGB565 :   (0, 5, 6, 5)}
    if dither:
        rnd = random.Random()
        rnd.seed(0)
    if fmt in colorfmts:
        im = im.convert("RGBA")
        (asz,rsz,gsz,bsz) = colorfmts[fmt]
        totalsz = sum((asz,rsz,gsz,bsz))
        assert totalsz in (8,16)
        for y in range(im.size[1]):
            for x in range(im.size[0]):
                (r,g,b,a) = im.getpixel((x,y))
                if dither:
                    a = min(255, a + rnd.randrange(256>>asz))
                    r = min(255, r + rnd.randrange(256>>rsz))
                    g = min(255, g + rnd.randrange(256>>gsz))
                    b = min(255, b + rnd.randrange(256>>bsz))
                binary = ((a >> (8-asz)) << (bsz+gsz+rsz)) | ((r >> (8-rsz)) << (gsz+bsz)) | ((g >> (8-gsz)) << (bsz)) | (b >> (8-bsz))
                imdata.append(binary)
        fmtchr = {8:'B',16:'H'}[totalsz]
        data = array.array('B', array.array(fmtchr, imdata).tostring())
    elif fmt == PALETTED:
        im = im.convert("P", palette = Image.ADAPTIVE)
        lut = im.resize((256, 1))
        lut.putdata(range(256))
        palstr = lut.convert("RGBA").tobytes()
        rgba = zip(*(array.array('B', palstr[i::4]) for i in range(4)))
        data = imbytes(im)
        totalsz = 8
    elif fmt == L8:
        data = imbytes(im)
        totalsz = 8
    elif fmt == L4:
        b0 = imbytes(im)[::2]
        b1 = imbytes(im)[1::2]
        def to15(c):
            if dither:
                dc = min(255, c + rnd.randrange(16))
            else:
                dc = c
            return int((15. * dc / 255))
                
        data = array.array('B', [(16 * to15(l) + to15(r)) for (l,r) in zip(b0, b1)])
        totalsz = 4
    elif fmt == L1:
        if dither:
            im = im.convert("1", dither=Image.FLOYDSTEINBERG)
        else:
            im = im.convert("1", dither=Image.NONE)
        data = imbytes(im)
        totalsz = 1
    return (im.size, data)
