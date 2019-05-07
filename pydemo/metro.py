print('===== START =====')

import time
import struct
import board
import busio
import digitalio
import random
import math
import sys

from micropython import const
import gc

class CircuitSPI:
    def __init__(self):
        self.cs = digitalio.DigitalInOut(board.D2)
        self.cs.direction = digitalio.Direction.OUTPUT
        self.unsel()

        self.sp = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
        while not self.sp.try_lock():
            pass
        self.sp.configure(baudrate=10000000, phase=0, polarity=0)

    def sel(self):
        self.cs.value = False

    def unsel(self):
        self.cs.value = True

    def write(self, bb):
        self.sp.write(bb)

    def read(self, n):
        r = bytearray(n)
        self.sp.readinto(r)
        # print(list(r))
        return r

import base
import gd3registers as gd3

class CoprocessorException(Exception):
    pass

class GD(base.GD2):
    def __init__(self):
        self.spi = CircuitSPI()
        self.coldstart()

        self.getspace()
        self.stream()

    def coldstart(self):
        self.host_cmd(0x00)   # Wake up
        self.host_cmd(0x48)   # int clock
        self.host_cmd(0x68)   # Core reset
        time.sleep(.25)

    def host_cmd(self, a, b = 0, c = 0):
        self.spi.sel()
        self.spi.write(bytes([a, b, c]))
        self.spi.unsel()

    def start(self, a):
        self.spi.sel()
        self.spi.write(bytes([
            0xff & (a >> 16),
            0xff & (a >> 8),
            0xff & a]))

    def _rd(self, a, n):
        self.start(a)
        r = self.spi.read(1 + n)
        self.spi.unsel()
        return r[1:]

    def _rd32(self, a):
        return struct.unpack("<I", self._rd(a, 4))[0]

    def _wr32(self, a, v):
        self.start(0x800000 | a)
        self.spi.write(struct.pack("I", v))
        self.spi.unsel()

    def getspace(self):
        self.space = self._rd32(gd3.REG_CMDB_SPACE)
        if self.space & 1:
            raise CoprocessorException

    def stream(self):
        self.start(0x800000 | gd3.REG_CMDB_WRITE)

    def unstream(self):
        self.spi.unsel()

    def reserve(self, n):
        if self.space < n:
            self.unstream()
            while self.space < n:
                self.getspace()
            self.stream()

    def c4(self, v):
        '''
        Write 32-bit value v to the command FIFO
        '''
        self.reserve(4)
        self.spi.write(struct.pack("I", v))
        self.space -= 4

    def c(self, ss):
        '''
        Write s to the command FIFO
        '''
        if len(ss) <= 256:
            self.reserve(len(ss))
            self.spi.write(ss)
            self.space -= len(ss)
        else:
            for i in range(0, len(ss), 256):
                self.c(ss[i:i + 256])

    def load(self, f):
        while True:
            s = f.read(512)
            if not s:
                return
            s = base.align4(s)
            self.reserve(len(s))
            self.spi.write(s)
            self.space -= len(s)

    def finish(self):
        self.reserve(4092)

    def is_idle(self):
        self.unstream()
        self.getspace()
        self.stream()
        return self.space == 4092

    def rd32(self, a):
        self.unstream()
        r = self._rd32(a)
        self.stream()
        return r

    def rd(self, a, n):
        self.unstream()
        r = self._rd(a, n)
        self.stream()
        return r

    def result(self, n=1):
        # Return the result field of the preceding command
        self.finish()
        self.unstream()
        wp = self._rd32(gd3.REG_CMD_READ)
        r = self._rd32(gd3.RAM_CMD + (4095 & (wp - 4 * n)))
        self.stream()
        return r

    def setup_480_272(self):
        b = 6
        setup = [
            (gd3.REG_OUTBITS, b * 73),
            (gd3.REG_DITHER, 1),
            (gd3.REG_GPIO, 0x83),
            (gd3.REG_PCLK_POL, 1),
            (gd3.REG_ROTATE, 1),
            (gd3.REG_SWIZZLE, 3),
        ]
        for (a, v) in setup:
            self.cmd_regwrite(a, v)

        self.Clear()
        self.swap()
        self.finish()

        self.cmd_regwrite(gd3.REG_PCLK, 5)  # Enable display

        self.w = 480
        self.h = 272

    def calibrate(self):
        self.Clear()
        self.cmd_text(240, 135, 29, gd3.OPT_CENTER, "Tap the dot")
        self.cmd_calibrate(0)
        self.cmd_dlstart()

    def screenshot(self, dest):
        REG_SCREENSHOT_EN    = 0x302010 # Set to enable screenshot mode
        REG_SCREENSHOT_Y     = 0x302014 # Y line register
        REG_SCREENSHOT_START = 0x302018 # Screenshot start trigger
        REG_SCREENSHOT_BUSY  = 0x3020e8 # Screenshot ready flags
        REG_SCREENSHOT_READ  = 0x302174 # Set to enable readout
        RAM_SCREENSHOT       = 0x3c2000 # Screenshot readout buffer

        self.cmd_regwrite(gd3.REG_PCLK, 0)  # Enable display
        self.finish()
        self.unstream()

        self._wr32(REG_SCREENSHOT_EN, 1)
        self._wr32(0x0030201c, 32)

        self._wr32(REG_SCREENSHOT_READ, 1)

        for ly in range(self.h):
            self._wr32(REG_SCREENSHOT_Y, ly)
            self._wr32(REG_SCREENSHOT_START, 1)
            time.sleep(.002)
            # while (self.raw_read(REG_SCREENSHOT_BUSY) | self.raw_read(REG_SCREENSHOT_BUSY + 4)): pass
            while self._rd(REG_SCREENSHOT_BUSY, 8) != bytes(8):
                pass
            self._wr32(REG_SCREENSHOT_READ, 1)
            bgra = self._rd(RAM_SCREENSHOT, 4 * self.w)
            # (b,g,r,a) = [bgra[i::4] for i in range(4)]
            # line = bytes(sum(zip(r,g,b), ()))
            dest(bgra)
            self._wr32(REG_SCREENSHOT_READ, 0)
        self._wr32(REG_SCREENSHOT_EN, 0)
        self.stream()
        self.cmd_regwrite(gd3.REG_PCLK, 5)  # Enable display

    def screenshot_im(self):
        self.ssbytes = b""
        def appender(s):
            self.ssbytes += s
        self.screenshot(appender)
        from PIL import Image
        return Image.frombytes("RGB", (self.w, self.h), self.ssbytes)

    def screenshot_serial(self):
        sys.stdout.write(b'\xa5')
        def safe(bb):
            return [(c | 1) for c in bb]
        def rgb(bgra):
            return [safe(bgra[i:i + 3]) for i in range(0, len(bgra), 4)]

        def line(bgra):
            for i in range(0, len(bgra), 4 * 8):
                o = rgb(bgra[i:i + 32])
                difference = 1
                for b in range(1, 8):
                    difference |= (o[b-1] != o[b]) << b
                sys.stdout.write(bytes([difference]))
                for b in range(8):
                    if (difference >> b) & 1:
                        sys.stdout.write(bytes(o[b]))

        self.screenshot(line)

def helloworld(eve):
    eve.ClearColorRGB(0x00, 0x20, 0x20)
    eve.Clear()
    eve.cmd_text(20, 20, 30, 0, "Hello from CircuitPython")
    eve.swap()

def fizz(eve):
    gc.collect()
    while True:
        eve.Clear()
        eve.Begin(gd3.POINTS)
        random.seed(7)
        rr = random.randrange
        b = bytearray(100 * 3 * 4)
        eve.finish()
        _p = struct.pack_into

        t0 = eve.rd32(gd3.REG_CLOCK)
        if 1:
            for i in range(100):
                eve.ColorRGB(rr(256), rr(256), rr(256))
                eve.PointSize(100 + rr(900))
                eve.Vertex2f(rr(480), rr(272))
        elif 1:
            for i in range(100):
                _p("BBBB", b, 12 * i, rr(256), rr(256), rr(256), 0x04)
                _p("I",  b, 12 * i + 4, 0x0d000000 | (100 + rr(900)))
                x = rr(480) * 16
                y = rr(272) * 16
                _p("I", b, 12 * i + 8, 0x40000000 | ((x & 32767) << 15) | (y & 32767))
            eve.c(b)

        t1 = eve.rd32(gd3.REG_CLOCK)
        print('took', 1000 * (0xffffffff & (t1 - t0)) / 60e6, 'ms')
        eve.swap()
        break

def blinka(eve):
    eve.BitmapHandle(0)
    eve.cmd_loadimage(0, 0)
    eve.load(open("circuitpython.png", "rb"))

    eve.BitmapHandle(1)
    eve.cmd_loadimage(-1, 0)
    eve.load(open("blinka100.png", "rb"))
    eve.BitmapSize(gd3.BILINEAR, gd3.BORDER, gd3.BORDER, 100, 100)

    r = 100                                 # radius for circle of Blinkas

    for t in range(0, 3600, 2):
        eve.Begin(gd3.BITMAPS)
        eve.BitmapHandle(0)                 # Draw the background
        eve.Vertex2f(0, 0)

        eve.BitmapHandle(1)                 # Ten Blinkas, 36 degrees apart
        for i in range(10):
            angle = 36 * i + t
            eve.cmd_loadidentity()
            eve.cmd_rotate_around(50, 50, angle)
            eve.cmd_setmatrix()
            th = math.radians(-angle)
            x = r * math.sin(th)
            y = r * math.cos(th)
            eve.Vertex2f(240 - 50 + x, 136 - 50 + y)
        eve.swap()

s = GD()
REG_ID = 0x302000
print('ID register:', s.rd32(REG_ID))
s.setup_480_272()

# helloworld(s)
# fizz(s)
blinka(s)

print('%H%')
while 1:
    pass
