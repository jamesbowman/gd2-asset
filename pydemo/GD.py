import time
import struct

import gameduino2.gd3registers as gd3
import gameduino2.base
from spidriver import SPIDriver
from gameduino2.gd3registers import *

class CoprocessorException(Exception):
    pass

class GD(gameduino2.base.GD2):
    def __init__(self, dev):
        self.spi = SPIDriver(dev)

        self.spi.setb(1)
        if False:
            self.spi.setb(0)
            time.sleep(1)
            self.spi.setb(1)
            time.sleep(1)

        self.coldstart()

        t0 = time.time()
        while self._rd32(gd3.REG_ID) != 0x7c:
            assert (time.time() - t0) < 1.0, "No response - is GD attached?"

        if 0:
            time.sleep(1)
            print("ID        %8x" % self._rd32(gd3.REG_ID))
            print("CMD_READ  %8x" % self._rd32(gd3.REG_CMD_READ))
            print("CMD_WRITE %8x" % self._rd32(gd3.REG_CMD_WRITE))
            print("CMD_SPACE %8x" % self._rd32(gd3.REG_CMDB_SPACE))

        while self._rd32(gd3.REG_ID) != 0x7c:
            time.sleep(.1)
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

    def _wr(self, a, v):
        self.start(0x800000 | a)
        self.spi.write(v)
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
        for i in range(0, len(ss), 64):
            s = ss[i:i + 64]
            self.reserve(len(s))
            self.spi.write(s)
            self.space -= len(s)

    def flush(self):
        pass

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

    def wr(self, a, v):
        self.unstream()
        r = self._wr(a, v)
        self.stream()

    def result(self, n=1):
        # Return the result field of the preceding command
        self.finish()
        self.unstream()
        wp = self._rd32(gd3.REG_CMD_READ)
        r = self._rd32(gd3.RAM_CMD + (4095 & (wp - 4 * n)))
        self.stream()
        return r

    def setup_480x272(self):
        b = 6
        setup = [
            (gd3.REG_OUTBITS, b * 73),
            (gd3.REG_DITHER, 1),
            (gd3.REG_GPIO, 0x83),
            (gd3.REG_PCLK_POL, 1),
            (gd3.REG_ROTATE, 0),
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

    def setup_800x480(self):
        b = 6
        setup = [
            (gd3.REG_OUTBITS, b * 73),
            (gd3.REG_DITHER, 1),
            (gd3.REG_GPIO, 0x83),
            (gd3.REG_ROTATE, 0),
            (gd3.REG_SWIZZLE, 3),
            (gd3.REG_HCYCLE, 928),
            (gd3.REG_HOFFSET, 88),
            (gd3.REG_HSIZE, 800),
            (gd3.REG_HSYNC0, 0),
            (gd3.REG_HSYNC1, 48),
            (gd3.REG_VCYCLE, 525),
            (gd3.REG_VOFFSET, 32),
            (gd3.REG_VSIZE, 480),
            (gd3.REG_VSYNC0, 0),
            (gd3.REG_VSYNC1, 3),
            (gd3.REG_CSPREAD, 0),
            (gd3.REG_PCLK_POL, 0),
        ]
        for (a, v) in setup:
            self.cmd_regwrite(a, v)

        self.Clear()
        self.swap()
        self.finish()

        self.cmd_regwrite(gd3.REG_PCLK, 2)  # Enable display

        self.w = 800
        self.h = 480


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
            (b,g,r,a) = [bgra[i::4] for i in range(4)]
            line = bytes(sum(zip(r,g,b), ()))
            dest(line)
            self._wr32(REG_SCREENSHOT_READ, 0)
        self._wr32(REG_SCREENSHOT_EN, 0)
        self.stream()

    def screenshot_im(self):
        self.ssbytes = b""
        def appender(s):
            self.ssbytes += s
        self.screenshot(appender)
        from PIL import Image
        return Image.frombytes("RGB", (self.w, self.h), self.ssbytes)
