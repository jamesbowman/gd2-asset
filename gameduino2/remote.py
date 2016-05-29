import array
import StringIO
import zlib
import Image
import struct
import time

import convert

def pad4(s):
    while len(s) % 4:
        s += chr(0)
    return s

import gameduino2.registers as reg
import gameduino2.base

class GD2Exception(Exception):
    pass

class GD2(gameduino2.base.GD2):

    def __init__(self, transport):
        self.ramptr = 0
        self.wp = 0

        self.cc = StringIO.StringIO()
        self.transport = transport

        self.transport.reset()

        self.wr(reg.REG_GPIO, 0xff)

        self.wr32(reg.REG_HCYCLE, 525)
        self.wr32(reg.REG_HOFFSET, 43)
        self.wr32(reg.REG_HSIZE, 480)
        self.wr32(reg.REG_HSYNC0, 0)
        self.wr32(reg.REG_HSYNC1, 41)
        self.wr32(reg.REG_VCYCLE, 286)
        self.wr32(reg.REG_VOFFSET, 12)
        self.wr32(reg.REG_VSIZE, 272)
        self.wr32(reg.REG_VSYNC0, 0)
        self.wr32(reg.REG_VSYNC1, 10)
        self.wr32(reg.REG_CSPREAD, 1)
        self.wr32(reg.REG_DITHER, 1)
        self.wr32(reg.REG_PCLK_POL, 1)

        self.cmd_dlstart()
        self.Clear(1,1,1)
        self.Display()
        self.cmd_swap()
        self.cmd_regwrite(reg.REG_PCLK, 5)
        self.finish()

    def rdstr(self, a, n):
        return self.transport.rdstr(a, n)

    def wrstr(self, a, s):
        return self.transport.wrstr(a, s)

    def wr(self, a, v):
        """ Write a single byte ``v`` to address ``a``. """
        self.wrstr(a, chr(v))

    def rd(self, a):
        """ Read byte at address ``a`` """
        return struct.unpack("<B", self.rdstr(a, 1))[0]

    def rd16(self, a):
        return struct.unpack("<H", self.rdstr(a, 2))[0]

    def rd32(self, a):
        return struct.unpack("<L", self.rdstr(a, 4))[0]

    def wr16(self, a, v):
        """ Write 16-bit value ``v`` at to address ``a`` """
        self.wrstr(a, struct.pack("<H", v))

    def wr32(self, a, v):
        """ Write 32-bit value ``v`` at to address ``a`` """
        self.wrstr(a, struct.pack("<L", v))

    def command(self, cmd):
        assert (len(cmd) % 4) == 0
        while True:
            rp = self.rd16(reg.REG_CMD_READ)
            if rp & 3:
                raise GD2Exception, "At address %04X" % self.rd32(reg.RAM_CMD)
            fullness = (self.wp - rp) & 4095
            available = 4096 - 4 - fullness
            if min(1000, len(cmd)) <= available:
                break
        canwrite = min(available, len(cmd))
        if canwrite != len(cmd):
            self.command(cmd[:canwrite])
            return self.command(cmd[canwrite:])
        if (self.wp + len(cmd)) < 4096:
            self.wrstr(reg.RAM_CMD + self.wp, cmd)
            self.wp += len(cmd)
        else:
            rem = 4096 - self.wp
            self.wrstr(reg.RAM_CMD + self.wp, cmd[:rem])
            self.wrstr(reg.RAM_CMD, cmd[rem:])
            self.wp = len(cmd) - rem
        assert (self.wp % 4) == 0
        assert 0 <= self.wp < 4096
        self.wr16(reg.REG_CMD_WRITE, self.wp)

    def finish(self):
        c = self.cc.getvalue()
        self.cc = StringIO.StringIO()
        for i in range(0, len(c), 4096):
            res = self.command(c[i:i+4096])
        # self.v.waitidle()

    def c(self, cmdstr):
        self.cc.write(pad4(cmdstr))

    def load_image(self, im, dither = False, fmt = reg.ARGB1555, sampling = reg.NEAREST, zoom = 1):
        strides = {
            reg.L1 :       lambda w: w / 8,
            reg.L4 :       lambda w: w / 2,
            reg.L8 :       lambda w: w,
            reg.RGB332 :   lambda w: w,
            reg.ARGB2 :    lambda w: w,
            reg.PALETTED : lambda w: w,
        }
        if fmt == reg.L1:
            i = Image.new(im.mode, ((im.size[0] + 7) & ~7, im.size[1]))
            i.paste(im, (0,0))
            im = i
        stride = strides.get(fmt, lambda w: 2 * w)(im.size[0])
        (_,da) = convert.convert(im, dither = dither, fmt = fmt)
        self.ramptr = (self.ramptr + 1) & ~1
        self.zload(self.ramptr, da.tostring())
        self.BitmapSize(sampling, reg.BORDER, reg.BORDER, min(511, zoom * im.size[0]), min(511, zoom * im.size[1]))
        self.BitmapSource(self.ramptr)
        self.BitmapLayout(fmt, stride, im.size[1])
        self.ramptr += len(da.tostring())

    def zload(self, dst, data):
        self.cmd_inflate(dst)
        c = zlib.compress(data)
        print len(data), len(c)
        self.c(pad4(c))

