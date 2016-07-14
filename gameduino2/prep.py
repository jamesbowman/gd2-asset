import os
import sys
import array
import struct
import zlib
import textwrap
import wave
import audioop

import Image
import ImageFont
import ImageDraw

import gameduino2 as gd2
import gameduino2.convert
from gameduino2.imbytes import imbytes

def stretch(im):
    d = imbytes(im)
    # print min(d), max(d)
    r = max(d) - min(d)
    return im.point(lambda x: (x - min(d)) * 255 / r)

def getalpha(im):
    return im.split()[3]

def tile(tw, th, im):
    tiles = []
    for y in range(0, im.size[1], th):
        for x in range(0, im.size[0], tw):
            tiles.append(im.crop((x, y, x + tw, y + th)))
    o = Image.new(im.mode, (tw, th * len(tiles)))
    for i,t in enumerate(tiles):
        o.paste(t, (0, i * th))
    return o

def split(tw, th, im):
    tiles = []
    for y in range(0, im.size[1], th):
        for x in range(0, im.size[0], tw):
            tiles.append(im.crop((x, y, x + tw, y + th)))
    return tiles

def join(tiles):
    (tw, th) = tiles[0].size
    o = Image.new(tiles[0].mode, (tw, th * len(tiles)))
    for i,t in enumerate(tiles):
        o.paste(t, (0, i * th))
    return o

def setwidth(im, w):
    e = Image.new(im.mode, (w, im.size[1]))
    e.paste(im, (0, 0))
    return e

def even(im):
    w = im.size[0]
    if (w % 2) == 0:
        return im
    else:
        return setwidth(im, w + 1)

def extents(im):
    """ find pixel extents of im, as a box """
    w,h = im.size
    cols = [set(imbytes(im.crop((i, 0, i + 1, im.size[1])))) != set([0]) for i in range(w)]
    rows = [set(imbytes(im.crop((0, i, im.size[0], i + 1)))) != set([0]) for i in range(h)]
    if not True in cols:
        return (0, 0, 0, 0)
    else:
        x0 = cols.index(True)
        y0 = rows.index(True)
        while not cols[-1]:
            cols.pop()
        while not rows[-1]:
            rows.pop()
        return (x0, y0, len(cols), len(rows))

def ul(x):
    return str(x) + "UL"

def preview(np, fmt, size, data):

    def chan(x):
        return Image.fromstring("L", size, (255 * x).astype(np.uint8))

    if fmt == gd2.L1:
        r = Image.fromstring("1", size, data)
    elif fmt == gd2.L8:
        r = Image.fromstring("L", size, data)
    else:
        d8 = np.array(data)
        a = np.ones(size[0] * size[1])
        (r, g, b) = (a, a, a)
        if fmt == gd2.ARGB4:
            d16 = np.array(array.array('H', data.tostring()))
            a = (15 & (d16 >> 12)) / 15.
            r = (15 & (d16 >> 8)) / 15.
            g = (15 & (d16 >> 4)) / 15.
            b = (15 & (d16 >> 0)) / 15.
        elif fmt == gd2.RGB565:
            d16 = np.array(array.array('H', data.tostring()))
            r = (31 & (d16 >> 11)) / 31.
            g = (63 & (d16 >> 5)) / 63.
            b = (31 & (d16 >> 0)) / 31.
        elif fmt == gd2.ARGB1555:
            d16 = np.array(array.array('H', data.tostring()))
            a = (1 & (d16 >> 15))
            r = (31 & (d16 >> 10)) / 31.
            g = (31 & (d16 >> 5)) / 31.
            b = (31 & (d16 >> 0)) / 31.
        elif fmt == gd2.ARGB2:
            a = (3 & (d8 >> 6)) / 3.
            r = (3 & (d8 >> 4)) / 3.
            g = (3 & (d8 >> 2)) / 3.
            b = (3 & (d8 >> 0)) / 3.
        elif fmt == gd2.RGB332:
            r = (7 & (d8 >> 5)) / 7.
            g = (7 & (d8 >> 2)) / 7.
            b = (3 & (d8 >> 0)) / 3.
        elif fmt == gd2.L4:
            hi = d8 >> 4
            lo = d8 & 15
            d4 = np.column_stack((hi, lo)).flatten()
            r = d4 / 15.
            g = r
            b = r
        o = Image.merge("RGB", [chan(c) for c in (r, g, b)])
        bg = Image.new("RGB", size, (128, 128, 128))
        r = Image.composite(o, bg, chan(a))

    r = r.resize((r.size[0] * 5, r.size[1] * 5), Image.NEAREST)
    return r

import gameduino2.base

class AssetBin(gameduino2.base.GD2):

    asset_file = None
    prefix = ""
    previews = False

    def __init__(self):
        self.alldata = ""
        self.commands = ""
        self.defines = []
        self.inits = []
        self.handle = 0
        self.np = None

    def define(self, n, v):
        self.defines.append((self.prefix + n, v))

    def add(self, name, s):
        if name:
            self.defines.append((name, ul(len(self.alldata))))
        self.alldata += s

    def c(self, s):
        self.commands += s

    def addim(self, name, im, fmt, dither = False):
        (_, imgdata) = gameduino2.convert.convert(im, dither, fmt = fmt)
        self.add(name, imgdata.tostring())
        (w, h) = im.size
        if name:
            self.defines.append(("%s_WIDTH" % name, w))
            self.defines.append(("%s_HEIGHT" % name, h))

    def align(self, n):
        while (len(self.alldata) % n) != 0:
            self.alldata += chr(0)

    def load_handle(self, name, images, fmt,
                    dither = False,
                    filter = gd2.NEAREST,
                    scale = 1,
                    rotating = False):

        if 15 <= self.handle:
            print "Error: too many bitmap handles used, limit is 15"
            sys.exit(1)

        (w, h) = images[0].size

        self.define("%s_HANDLE" % name, self.handle)
        name = self.prefix + name
        self.defines.append(("%s_WIDTH" % name, w))
        self.defines.append(("%s_HEIGHT" % name, h))
        self.defines.append(("%s_CELLS" % name, len(images)))

        self.align(2)

        self.BitmapHandle(self.handle);
        self.BitmapSource(len(self.alldata));
        if not rotating:
            (vw, vh) = (scale * w, scale * h)
            vsz = 0
        else:
            vsz = int(scale * max(w, h))
            self.define("%s_SIZE" % name, vsz)
            (vw, vh) = (vsz, vsz)
        self.BitmapSize(filter, gd2.BORDER, gd2.BORDER, vw, vh);
        self.inits.append("static const shape_t %s_SHAPE = {%d, %d, %d, %d};" % (name, self.handle, w, h, vsz))

        # aw is aligned width
        if fmt == gd2.L1:
            aw = (w + 7) & ~7
        elif fmt == gd2.L4:
            aw = (w + 1) & ~1
        else:
            aw = w

        # print self.name, name, (filter, gd2.BORDER, gd2.BORDER, vw, vh)
        bpl = {
            gd2.ARGB1555 : 2 * aw,
            gd2.L1       : aw / 8,
            gd2.L4       : aw / 2,
            gd2.L8       : aw,
            gd2.RGB332   : aw,
            gd2.ARGB2    : aw,
            gd2.ARGB4    : 2 * aw,
            gd2.RGB565   : 2 * aw,
            gd2.PALETTED : aw}[fmt]
        self.BitmapLayout(fmt, bpl, h);

        for i,im in enumerate(images):
            if aw != w:
                im = setwidth(im, aw)
            if hasattr(im, "imgdata"):
                imgdata = im.imgdata
            else:
                (_, imgdata) = gameduino2.convert.convert(im, dither, fmt = fmt)
            """
            if self.previews:
                if not self.np:
                    import numpy
                    self.np = numpy
                preview(self.np, fmt, im.size, imgdata).save("previews/%s-%s-%02d.png" % (self.name, name, i))
            """
            self.alldata += imgdata.tostring()

        self.handle += 1

    def load_font(self, name, ims, widths, fmt, **args):
        trim0 = 0
        while ims[trim0] is None:
            trim0 += 1
        p0 = len(self.alldata)
        h = self.handle
        tims = ims[trim0:]
        self.load_handle(name, tims, fmt, **args)

        self.align(4)
        p1 = len(self.alldata)
        # Compute memory required by one char
        onechar = (p1 - p0) / len(tims)
        # print name, 'font requires', (p1 - p0), 'bytes'
        sz = ims[trim0].size
        self.BitmapSource(p0 - (onechar * trim0));
        widths = [max(0, w) for w in widths]
        dblock = array.array('B', widths).tostring() + struct.pack("<5i", fmt, 1, sz[0], sz[1], p0 - (onechar * trim0))
        self.alldata += dblock
        self.cmd_setfont(h, p1);

    def load_ttf(self, name, ttfname, size, format):
        font = ImageFont.truetype(ttfname, size)
        sizes = [font.getsize(chr(c)) for c in range(32, 128)]
        fw = max([w for (w, _) in sizes])
        fh = max([h for (_, h) in sizes])
        # print fw, fh
        alle = {}
        for i in range(1, 96):
            im = Image.new("L", (fw+8, fh))
            dr = ImageDraw.Draw(im)
            dr.text((8,0), chr(32 + i), font=font, fill=255)
            alle[i] = gd2.prep.extents(im)

        fw = max([(x1 - x0) for (x0, y0, x1, y1) in alle.values()])
        ims = ([None] * 32) + [Image.new("L", (fw, fh)) for i in range(32, 128)]
        for i in range(33, 127):
            dr = ImageDraw.Draw(ims[i])
            (x0, y0, x1, y1) = alle[i - 32]
            x = max(0, 8 - x0)
            if x > 0:
                sizes[i - 32] = (sizes[i - 32][0] - x, sizes[i - 32][1])
            dr.text((x, 0), chr(i), font=font, fill=255)
        # imgtools.view(im)
        widths = ([0] * 32) + [w for (w, _) in sizes]
        self.load_font(name, ims, widths, format)

    """
    def dxt1(self, imagefile):
        import numpy

        im = Image.open(imagefile).resize((480,272), Image.ANTIALIAS)
        dxt = "%s.dxt" % imagefile
        if not os.access(dxt, os.R_OK):
            im.save("tmp.png")
            assert os.system("squishpng tmp.png %s" % dxt) == 0

        sz = (480 / 4, 272 / 4)

        def rgb(cs):
            r = (cs >> 11) << 3
            g = 0xff & ((cs >> 5) << 2)
            b = 0xff & (cs << 3)
            return (r,g,b)
        def rgbim(cs):
            return Image.merge("RGB", [Image.fromarray(c.astype(numpy.uint8).reshape(*sz)) for c in rgb(cs)])
        def morton1(x):
            v = x & 0x55555555
            v = (v | (v >> 1)) & 0x33333333;
            v = (v | (v >> 2)) & 0x0F0F0F0F;
            v = (v | (v >> 4)) & 0x00FF00FF;
            v = (v | (v >> 8)) & 0x0000FFFF;
            return v.astype(numpy.uint16)

        h = open(dxt)
        h.read(8)

        c0s = []
        c1s = []
        bits = []
        for i in range(sz[0] * sz[1]):
            tile = h.read(8)
            c0,c1,bit = struct.unpack("2HI", tile)
            b0 = bit & 0x55555555
            b1 = (bit >> 1) & 0x55555555
            is0 = ~b1 & ~b0
            is1 = ~b1 & b0
            is2 = b1 & ~b0
            is3 = b1 & b0
            if c0<=c1:
                if bit == 0xaaaaaaaa:
                    # print c0<c1,hex(bit)
                    r0,g0,b0 = rgb(c0)
                    r1,g1,b1 = rgb(c1)
                    r = (r0 + r1) / 2
                    g = (g0 + g1) / 2
                    b = (b0 + b1) / 2
                    # r,g,b = (255,0,255)
                    c0 = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
                    c1 = c0
                    bit = 0
                else:
                    if 0:
                        for i in range(0, 32, 2):
                            fld = (3 & (bit >> i))
                            if 3 == fld:
                                print c0, c1, hex(bit), i
                                assert 0
                    # Map as follows:
                    # 0 -> 0
                    # 1 -> 3
                    # 2 -> 1
                    bit = (is1 * 3) + (is2 * 1)
                    assert is3 == 0
            else:
                # 0 -> 0
                # 1 -> 3
                # 2 -> 1
                # 3 -> 2
                bit = (is1 * 3) + (is2 * 1) + (is3 * 2)

            if 0:
                c0 = 63 << 5 # green
                c1 = 31 << 11 # red
                bit = 0x0f0f0f0f

            c0s.append(c0)
            c1s.append(c1)
            bits.append(bit)
        c0s = numpy.array(c0s, numpy.uint16)
        c1s = numpy.array(c1s, numpy.uint16)
        bits = numpy.array(bits, numpy.uint32)
        bits0 = morton1(bits)
        bits1 = morton1(bits >> 1)

        if 1:
            def im44(v):
                im = Image.new("1", (4,4))
                pix = im.load()
                for i in range(4):
                    for j in range(4):
                        if v & (1 << (4 * i + j)):
                            pix[j,i] = 255
                return im
            ims = [im44(i) for i in range(65536)]

        b0im = Image.new("1", (480, 272))
        b1im = Image.new("1", (480, 272))
        xys = [(x,y) for y in range(0, 272, 4) for x in range(0, 480, 4)]
        for i,(x,y) in enumerate(xys):
            b0im.paste(ims[bits0[i]], (x, y))
            b1im.paste(ims[bits1[i]], (x, y))

        class MockImage:
            def __init__(self, s, size):
                self.imgdata = s
                self.size = size

        self.load_handle("BACKGROUND_COLOR", [MockImage(c0s, sz), MockImage(c1s, sz)], gd2.RGB565, scale = 4)
        self.load_handle("BACKGROUND_BITS", [b0im, b1im], gd2.L1)
    """

    def load_sample(self, name, filename):
        f = wave.open(filename, "rb")
        if f.getnchannels() != 1:
            print "Sorry - .wav file must be mono"
            sys.exit(1)
        if f.getsampwidth() != 2:
            print "Sorry - .wav file must be 16-bit"
            sys.exit(1)
        freq = f.getframerate()
        pcm16 = f.readframes(f.getnframes())
        (adpcm, _) = audioop.lin2adpcm(pcm16, f.getsampwidth(), (0,0))
        adpcm = adpcm[:len(adpcm) & ~7]
        da = array.array('B', [((ord(c) >> 4) | ((15 & ord(c)) << 4)) for c in adpcm])
        self.align(8)
        self.add(name, da.tostring())
        self.define(name + "_LENGTH", len(da))
        self.define(name + "_FREQ", freq)

    header = None
    def make(self):
        if self.header is None:
            name = self.__class__.__name__.lower() + "_assets.h"
        else:
            name = self.header
        self.name = name
        self.addall()
        if len(self.alldata) > 0x40000:
            print "Error: The data (%d bytes) is larger the the GD2 RAM" % len(self.alldata)
            sys.exit(1)
        self.defines.append((self.prefix + "ASSETS_END", ul(len(self.alldata))))
        self.cmd_inflate(0)
        calldata = zlib.compress(self.alldata)
        print 'Assets report'
        print '-------------'
        print 'Header file:    %s' % self.header
        print 'GD2 RAM used:   %d' % len(self.alldata)
        if not self.asset_file:
            print 'Flash used:     %d' % len(calldata)
        else:
            print 'Output file:    %s' % self.asset_file
            print 'File size:      %d' % len(calldata)

        commandblock = self.commands + calldata

        hh = open(name, "w")
        if self.asset_file is None:
            print >>hh, "static const PROGMEM uint8_t %s__assets[%d] = {" % (self.prefix, len(commandblock))
            print >>hh, textwrap.fill(", ".join(["%d" % ord(c) for c in commandblock]))
            print >>hh, "};"
            print >>hh, "#define %sLOAD_ASSETS()  GD.copy(%s__assets, sizeof(%s__assets))" % (self.prefix, self.prefix, self.prefix)
        else:
            open(self.asset_file, "wb").write(commandblock)
            print >>hh, '#define %sLOAD_ASSETS()  GD.safeload("%s");' % (self.prefix, self.asset_file)
        for (nm,v) in self.defines:
            print >>hh, "#define %s %s" % (nm, v)
        for i in self.inits:
            print >>hh, i
        self.extras(hh)

    def addall(self):
        pass
    def extras(self, hh):
        pass

class ForthAssetBin(AssetBin):
    def make(self):
        if self.header is None:
            name = self.__class__.__name__.lower() + "_assets.fs"
        else:
            name = self.header
        self.name = name
        self.addall()
        if len(self.alldata) > 0x40000:
            print "Error: The data (%d bytes) is larger the the GD2 RAM" % len(self.alldata)
            sys.exit(1)
        self.defines.append((self.prefix + "ASSETS_END", ul(len(self.alldata))))
        self.cmd_inflate(0)
        calldata = zlib.compress(self.alldata)
        print 'Assets report'
        print '-------------'
        print 'Header file:    %s' % self.header
        print 'GD2 RAM used:   %d' % len(self.alldata)
        if not self.asset_file:
            print 'Flash used:     %d' % len(calldata)
        else:
            print 'Output file:    %s' % self.asset_file
            print 'File size:      %d' % len(calldata)

        commandblock = self.commands + calldata
        commandblock += chr(0) * ((-len(commandblock)) & 3)
        commandblock32 = array.array('I', commandblock)

        hh = open(name, "w")
        print >>hh, "base @"
        print >>hh, "hex"
        if self.asset_file is None:
            print >>hh, textwrap.fill(" ".join(["%08x GD.c" % c for c in commandblock32]))
        else:
            open(self.asset_file, "wb").write(commandblock)
        print >>hh, "decimal"
        for (nm,v) in self.defines:
            print >>hh, "%-8s constant %s" % (str(v).replace('UL', ''), nm)
        print >>hh, "base !"
        self.extras(hh)
