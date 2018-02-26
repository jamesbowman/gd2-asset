import os
import sys
import array
import struct
import zlib
import textwrap
import wave
import audioop
import xml.etree.ElementTree as ET

import Image, ImageFont, ImageDraw, ImageChops

import gameduino2 as gd2
import gameduino2.convert
import gameduino2.tmxreader
from gameduino2.imbytes import imbytes

def pad4(s):
    while len(s) % 4:
        s += chr(0)
    return s

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
    e = im.resize((w, im.size[1]))
    nch = len(e.mode)
    if nch == 1:
        black = 0
    else:
        black = (0,) * nch
    e.paste(black, (0, 0, e.size[0], e.size[1]))
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

def cname(s):
    """ make name s C-friendly """
    for c in "-+.":
        s = s.replace(c, "_")
    return s.upper()

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

def pma(im):
    im = im.convert("RGBA")
    (r,g,b,a) = im.split()
    (r,g,b) = [ImageChops.multiply(a, c) for c in (r,g,b)]
    return Image.merge("RGBA", (r, g, b, a))

class EVE(gameduino2.base.GD2):
    def __init__(self):
        self.d = ""

    def c(self, s):
        self.d += s

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

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
        self.bitmaps = []

        # Set defaults for FT800. target_810() modifies these
        self.device = 'GD2'
        self.maxram = 256 * 1024
        self.maxhandles = 15
        
    def target_810(self):
        self.device = 'GD3'
        self.maxram = 1024 * 1024
        self.maxhandles = 32

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

    def load_bitmap(self, im, fmt, dither = False):
        (w, h) = im.size

        self.align(2)

        # aw is aligned width
        # For L1, L2, L4 formats the width must be a whole number of bytes
        if fmt == gd2.L1:
            aw = (w + 7) & ~7
        elif fmt == gd2.L2:
            aw = (w + 3) & ~3
        elif fmt == gd2.L4:
            aw = (w + 1) & ~1
        else:
            aw = w

        if aw != w:
            im = setwidth(im, aw)
        if hasattr(im, "imgdata"):
            imgdata = im.imgdata
        else:
            (_, imgdata) = gameduino2.convert.convert(im, dither, fmt = fmt)
        r = len(self.alldata)
        self.alldata += imgdata.tostring()
        return r

    def load_handle(self, name, images, fmt,
                    dither = False,
                    filter = gd2.NEAREST,
                    scale = 1,
                    rotating = False):

        if self.maxhandles <= self.handle:
            print "Error: too many bitmap handles used, limit is %d" % self.maxhandles
            sys.exit(1)

        (w, h) = images[0].size

        self.align(2)

        if name is not None:
            self.define("%s_HANDLE" % name, self.handle)
            name = self.prefix + name
            self.defines.append(("%s_WIDTH" % name, w))
            self.defines.append(("%s_HEIGHT" % name, h))
            self.defines.append(("%s_CELLS" % name, len(images)))
            self.bitmaps.append((name.lower(), w, h, w / 2, h / 2, len(self.alldata), fmt, self.handle))

        self.BitmapHandle(self.handle)
        self.BitmapSource(len(self.alldata))
        if not rotating:
            (vw, vh) = (scale * w, scale * h)
            vsz = 0
        else:
            vsz = int(scale * max(w, h))
            self.define("%s_SIZE" % name, vsz)
            (vw, vh) = (vsz, vsz)
        self.BitmapSize(filter, gd2.BORDER, gd2.BORDER, vw, vh)
        if self.device == 'GD3':
            self.BitmapSizeH(vw >> 9, vh >> 9)
        if name is not None:
            self.inits.append("static const shape_t %s_SHAPE = {%d, %d, %d, %d};" % (name, self.handle, w, h, vsz))

        # aw is aligned width
        # For L1, L2, L4 formats the width must be a whole number of bytes
        if fmt == gd2.L1:
            aw = (w + 7) & ~7
        elif fmt == gd2.L2:
            aw = (w + 3) & ~3
        elif fmt == gd2.L4:
            aw = (w + 1) & ~1
        else:
            aw = w

        bpl = {
            gd2.ARGB1555 : 2 * aw,
            gd2.L1       : aw / 8,
            gd2.L2       : aw / 4,
            gd2.L4       : aw / 2,
            gd2.L8       : aw,
            gd2.RGB332   : aw,
            gd2.ARGB2    : aw,
            gd2.ARGB4    : 2 * aw,
            gd2.RGB565   : 2 * aw,
            gd2.PALETTED : aw}[fmt]
        self.BitmapLayout(fmt, bpl, h)
        if self.device == 'GD3':
            self.BitmapLayoutH(bpl >> 10, h >> 9)

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
        self.BitmapSource(p0 - (onechar * trim0))
        widths = [max(0, w) for w in widths]
        dblock = array.array('B', widths).tostring() + struct.pack("<5i", fmt, 1, sz[0], sz[1], p0 - (onechar * trim0))
        self.alldata += dblock
        self.cmd_setfont(h, p1)

    def load_ttf(self, name, ttfname, size, format, firstchar = 32, topchar = 127, charset = None):
        font = ImageFont.truetype(ttfname, size)
        if charset is not None:
            topchar = firstchar + len(charset)
            rr = [ord(c) for c in charset]
        else:
            rr = range(firstchar, topchar + 1)
        sizes = {c:font.getsize(chr(c)) for c in rr}
        fw = max([w for (w, _) in sizes.values()])
        fh = max([h for (_, h) in sizes.values()])

        # Determine true pixel extents of all characters
        im = Image.new("L", (fw+16, fh+16))
        dr = ImageDraw.Draw(im)
        for i in rr:
            dr.text((8,8), chr(i), font=font, fill=255)
        alle = gd2.prep.extents(im)

        # render and crop the characters to the extents
        ims = [None] * firstchar
        for i in rr:
            im = Image.new("L", (fw+16, fh+16))
            dr = ImageDraw.Draw(im)
            dr.text((8, 8), chr(i), font=font, fill=255)
            ims.append(im.crop(alle))
        widths = [sizes.get(c, (0,0))[0] for c in range(128)]
        if charset is not None:
            for i,c in enumerate(charset):
                widths[firstchar + i] = sizes.get(ord(c), (0,0))[0]
        self.load_font(name, ims, widths, format)

    def load_tiles(self, name, file_name, scale = None, preview = False):
        world_map = gameduino2.tmxreader.TileMapParser().parse_decode(file_name)

        # print("loaded map:", world_map.map_file_name)

        x_pixels = world_map.pixel_width
        y_pixels = world_map.pixel_height
        # print("map size in pixels:", x_pixels, y_pixels)

        # print("tile size used:",  world_map.tilewidth, world_map.tileheight)
        # print("tiles used:", world_map.width, world_map.height)
        # print("found '", len(world_map.layers), "' layers on this map")

        layers = [l for l in world_map.layers if hasattr(l, 'decoded_content')]

        w,h = (world_map.width, world_map.height)

        ts = world_map.tile_sets[0]
        tw = int(ts.tilewidth)
        th = int(ts.tileheight)
        if scale is not None:
            stw,sth = (int(tw * scale), int(th * scale))
        else:
            stw,sth = tw,th

        used = set()
        for layer in layers:
            used |= set(layer.decoded_content)
        # used = sorted(used)
        used = sorted(used - set([0]))

        def reindex(i):
            if i == 0:
                return None
            else:
                return used.index(i)

        def fetchtile(l, i, j):
            if (i < world_map.width) and (j < world_map.height):
                return reindex(l.decoded_content[i + (j * world_map.width)])
            else:
                return None

        eve = EVE()
        # print world_map.width * world_map.height * 4

        for j in range(0, world_map.height, 4):
            for i in range(0, world_map.width, 4):
                for layer in layers:
                    for y in range(4):
                        for x in range(4):
                            t = fetchtile(layer, i + x, j + y)
                            # if i < (480 / 16) and j < (272 / 16): print 16 * (i + x), 16 * (j + y), "tile", t
                            if t is not None:
                                eve.Vertex2ii(stw * x, sth * y, t / 128, t % 128)
                            else:
                                eve.Nop()
        # assert 0
        stride = ((w + 3) / 4)
        self.add(name, struct.pack("6H", w * stw, h * sth, stw * 4, sth * 4, stride, len(layers)) + eve.d)
        self.tile_files = world_map.tile_sets[0].images[0].source

        # print 'Size of tiles: %d (compressed %d)' % (len(eve.d), len(zlib.compress(eve.d)))
        # print 'Tile size', (tw, th)

        im = pma(Image.open(self.tile_files))
        def extract(i):
            if hasattr(ts, 'columns'):
                w = int(ts.columns)
            elif not hasattr(ts, 'spacing'):
                w = im.size[0] / tw
            else:
                w = (im.size[0] + ts.spacing) / (tw + ts.spacing)
            x = ts.margin + (tw + ts.spacing) * (i % w)
            y = ts.margin + (th + ts.spacing) * (i / w)
            r = im.crop((x + 0, y + 0, x + tw, y + th))
            if scale:
                r = r.resize((stw, sth), Image.ANTIALIAS)
            return r
        for i,g128 in enumerate(chunker(used, 128)):
            self.load_handle(None, [extract(t - 1) for t in g128], gd2.ARGB4, dither=0)

        if preview:
            pv = Image.new("RGB", (tw * w, th * h))
            layer = layers[0]
            for y in range(pv.size[1] / th):
                for x in range(pv.size[0] / tw):
                    t = fetchtile(layer, x, y)
                    pv.paste(extract(used[t] - 1), (16 * x, 16 * y))
            return pv

    def load_atlas(self, file_name, scale = None):
        tree = ET.parse(file_name)
        root = tree.getroot()
        if root.tag == 'TextureAtlas':
            imagepath = root.attrib['imagePath']
            im = Image.open(imagepath)
            fmt = gd2.ARGB4
            for child in root.iter('SubTexture'):
                a = child.attrib
                # print a
                (x, y, width, height) = [int(a[n]) for n in ["x", "y", "width", "height"]]
                sub = im.crop((x, y, x + width, y + height))
                if scale is not None:
                    width = int(width * scale)
                    height = int(height * scale)
                    sub = sub.resize((width, height), Image.ANTIALIAS)
                src = self.load_bitmap(sub, fmt)
                nm = a['name']
                nm = nm.replace('.png', '')
                lp = len(self.alldata)
                self.inits.append("#define atlas_%s __fromatlas(%s)" % (nm, ul(lp)))
                self.alldata += struct.pack("HHHHIB", width, height, width / 2, height / 2, src, fmt)
                sub.save("%s.png" % nm)

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
            v = (v | (v >> 1)) & 0x33333333
            v = (v | (v >> 2)) & 0x0F0F0F0F
            v = (v | (v >> 4)) & 0x00FF00FF
            v = (v | (v >> 8)) & 0x0000FFFF
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
    header_intro = ""

    def make(self):
        if self.header is None:
            name = self.__class__.__name__.lower() + "_assets.h"
        else:
            name = self.header
        self.name = name
        self.addall()
        if len(self.alldata) > self.maxram:
            print "Error: The data (%d bytes) is larger the the %s RAM (%d)" % (len(self.alldata), self.device, self.maxram)
            sys.exit(1)
        self.defines.append((self.prefix + "ASSETS_END", ul(len(self.alldata))))
        self.cmd_inflate(0)
        calldata = zlib.compress(self.alldata, 9)
        commandblock = self.commands + pad4(calldata)

        print 'Assets report'
        print '-------------'
        print 'Header file:    %s' % self.header
        print '%s RAM used:   %d' % (self.device, len(self.alldata))
        if not self.asset_file:
            print 'Flash used:     %d' % len(commandblock)
        else:
            print 'Output file:    %s' % self.asset_file
            print 'File size:      %d' % len(calldata)

        hh = open(name, "w")

        hh.write(self.header_intro)

        for (nm,v) in self.defines:
            print >>hh, "#define %s %s" % (nm, v)

        p = self.prefix

        if self.asset_file is None:
            print >>hh, "static const PROGMEM uint8_t %s__assets[%d] = {" % (p, len(commandblock))
            print >>hh, textwrap.fill(", ".join(["%d" % ord(c) for c in commandblock]))
            print >>hh, "};"
            print >>hh, "#define %sLOAD_ASSETS()  (GD.copy(%s__assets, sizeof(%s__assets)), GD.loadptr = %sASSETS_END)" % (p, p, p, p)
        else:
            open(self.asset_file, "wb").write(commandblock)
            print >>hh, '#define %sLOAD_ASSETS()  (GD.safeload("%s"), GD.loadptr = %sASSETS_END)' % (p, self.asset_file, p)
        print >>hh

        for i in self.inits:
            print >>hh, i
        self.dump_bitmaps(hh)
        self.extras(hh)

    def dump_bitmaps(self, hh):
        hh.write("struct {\n")
        hh.write("".join(["  Bitmap %s;\n" % bm[0] for bm in self.bitmaps]))
        hh.write("} bitmaps = {\n")
        fmt = " /* %16s */  {{%3d, %3d}, {%3d, %3d}, %#8xUL, %2d, %2d}"
        hh.write(",\n".join([fmt % bm for bm in self.bitmaps]))
        hh.write("\n};\n")
            
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
        if len(self.alldata) > self.maxram:
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
