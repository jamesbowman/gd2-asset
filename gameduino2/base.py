import struct

def align4(s):
    return s + chr(0) * (-len(s) & 3)

def f16(v):
    return int(round(65536 * v))

class GD2:
    def c4(self, i):
        """Send a 32-bit value to the GD2."""
        self.c(struct.pack("I", i))
    def ac(self, s):
        self.c(align4(s))

    # The basic graphics instructions

    def AlphaFunc(self, func,ref):
        self.c4((9 << 24) | ((func & 7) << 8) | ((ref & 255) << 0))
    def Begin(self, prim):
        self.c4((31 << 24) | ((prim & 15) << 0))
    def BitmapHandle(self, handle):
        self.c4((5 << 24) | ((handle & 31) << 0))
    def BitmapLayout(self, format,linestride,height):
        self.c4((7 << 24) | ((format & 31) << 19) | ((linestride & 1023) << 9) | ((height & 511) << 0))
    def BitmapSize(self, filter,wrapx,wrapy,width,height):
        self.c4((8 << 24) | ((filter & 1) << 20) | ((wrapx & 1) << 19) | ((wrapy & 1) << 18) | ((width & 511) << 9) | ((height & 511) << 0))
    def BitmapSource(self, addr):
        self.c4((1 << 24) | ((addr & 1048575) << 0))
    def BitmapTransformA(self, a):
        self.c4((21 << 24) | ((a & 131071) << 0))
    def BitmapTransformB(self, b):
        self.c4((22 << 24) | ((b & 131071) << 0))
    def BitmapTransformC(self, c):
        self.c4((23 << 24) | ((c & 16777215) << 0))
    def BitmapTransformD(self, d):
        self.c4((24 << 24) | ((d & 131071) << 0))
    def BitmapTransformE(self, e):
        self.c4((25 << 24) | ((e & 131071) << 0))
    def BitmapTransformF(self, f):
        self.c4((26 << 24) | ((f & 16777215) << 0))
    def BlendFunc(self, src,dst):
        self.c4((11 << 24) | ((src & 7) << 3) | ((dst & 7) << 0))
    def Call(self, dest):
        self.c4((29 << 24) | ((dest & 65535) << 0))
    def Cell(self, cell):
        self.c4((6 << 24) | ((cell & 127) << 0))
    def ClearColorA(self, alpha):
        self.c4((15 << 24) | ((alpha & 255) << 0))
    def ClearColorRGB(self, red,green,blue):
        self.c4((2 << 24) | ((red & 255) << 16) | ((green & 255) << 8) | ((blue & 255) << 0))
    def Clear(self, c = 1,s = 1,t = 1):
        self.c4((38 << 24) | ((c & 1) << 2) | ((s & 1) << 1) | ((t & 1) << 0))
    def ClearStencil(self, s):
        self.c4((17 << 24) | ((s & 255) << 0))
    def ClearTag(self, s):
        self.c4((18 << 24) | ((s & 255) << 0))
    def ColorA(self, alpha):
        self.c4((16 << 24) | ((alpha & 255) << 0))
    def ColorMask(self, r,g,b,a):
        self.c4((32 << 24) | ((r & 1) << 3) | ((g & 1) << 2) | ((b & 1) << 1) | ((a & 1) << 0))
    def ColorRGB(self, red,green,blue):
        self.c4((4 << 24) | ((red & 255) << 16) | ((green & 255) << 8) | ((blue & 255) << 0))
    def Display(self):
        self.c4((0 << 24))
    def End(self):
        self.c4((33 << 24))
    def Jump(self, dest):
        self.c4((30 << 24) | ((dest & 65535) << 0))
    def LineWidth(self, width):
        self.c4((14 << 24) | ((width & 4095) << 0))
    def Macro(self, m):
        self.c4((37 << 24) | ((m & 1) << 0))
    def PointSize(self, size):
        self.c4((13 << 24) | ((size & 8191) << 0))
    def RestoreContext(self):
        self.c4((35 << 24))
    def Return(self):
        self.c4((36 << 24))
    def SaveContext(self):
        self.c4((34 << 24))
    def ScissorSize(self, width,height):
        self.c4((28 << 24) | ((width & 1023) << 10) | ((height & 1023) << 0))
    def ScissorXY(self, x,y):
        self.c4((27 << 24) | ((x & 511) << 9) | ((y & 511) << 0))
    def StencilFunc(self, func,ref,mask):
        self.c4((10 << 24) | ((func & 7) << 16) | ((ref & 255) << 8) | ((mask & 255) << 0))
    def StencilMask(self, mask):
        self.c4((19 << 24) | ((mask & 255) << 0))
    def StencilOp(self, sfail,spass):
        self.c4((12 << 24) | ((sfail & 7) << 3) | ((spass & 7) << 0))
    def TagMask(self, mask):
        self.c4((20 << 24) | ((mask & 1) << 0))
    def Tag(self, s):
        self.c4((3 << 24) | ((s & 255) << 0))
    def Vertex2f(self, x, y):
        x = int(16 * x)
        y = int(16 * y)
        self.c4((1 << 30) | ((x & 32767) << 15) | ((y & 32767) << 0))
    def Vertex2ii(self, x,y,handle,cell):
        self.c4((2 << 30) | ((x & 511) << 21) | ((y & 511) << 12) | ((handle & 31) << 7) | ((cell & 127) << 0))

    # Higher-level graphics commands

    def cmd_append(self, ptr, num):
        self.c(struct.pack("III", 0xffffff1e, ptr, num))

    def cmd_bgcolor(self, c):
        self.c(struct.pack("II", 0xffffff09, c))

    def cmd_bitmap_transform(self, x0, y0, x1, y1, x2, y2, tx0, ty0, tx1, ty1, tx2, ty2, result):
        self.c(struct.pack("IiiiiiiiiiiiiH", 0xffffff21, x0, y0, x1, y1, x2, y2, tx0, ty0, tx1, ty1, tx2, ty2, result))

    def cmd_button(self, x, y, w, h, font, options, s):
        self.c(struct.pack("IhhhhhH", 0xffffff0d, x, y, w, h, font, options) + s + chr(0))

    def cmd_calibrate(self, result):
        self.c(struct.pack("II", 0xffffff15, result))

    def cmd_clock(self, x, y, r, options, h, m, s, ms):
        self.c(struct.pack("IhhhHHHHH", 0xffffff14, x, y, r, options, h, m, s, ms))

    def cmd_coldstart(self):
        self.c(struct.pack("I", 0xffffff32))

    def cmd_dial(self, x, y, r, options, val):
        self.c(struct.pack("IhhhHH", 0xffffff2d, x, y, r, options, val))

    def cmd_dlstart(self):
        self.c(struct.pack("I", 0xffffff00))

    def cmd_fgcolor(self, c):
        self.c(struct.pack("II", 0xffffff0a, c))

    def cmd_gauge(self, x, y, r, options, major, minor, val, range):
        self.c(struct.pack("IhhhHHHHH", 0xffffff13, x, y, r, options, major, minor, val, range))

    def cmd_getmatrix(self, a, b, c, d, e, f):
        self.c(struct.pack("Iiiiiii", 0xffffff33, a, b, c, d, e, f))

    def cmd_getprops(self, ptr, w, h):
        self.c(struct.pack("IIII", 0xffffff25, ptr, w, h))

    def cmd_getptr(self, result):
        self.c(struct.pack("II", 0xffffff23, result))

    def cmd_gradcolor(self, c):
        self.c(struct.pack("II", 0xffffff34, c))

    def cmd_gradient(self, x0, y0, rgb0, x1, y1, rgb1):
        self.c(struct.pack("IhhIhhI", 0xffffff0b, x0, y0, rgb0, x1, y1, rgb1))

    def cmd_inflate(self, ptr):
        self.c(struct.pack("II", 0xffffff22, ptr))

    def cmd_interrupt(self, ms):
        self.c(struct.pack("II", 0xffffff02, ms))

    def cmd_keys(self, x, y, w, h, font, options, s):
        self.c(struct.pack("IhhhhhH", 0xffffff0e, x, y, w, h, font, options) + s + chr(0))

    def cmd_loadidentity(self):
        self.c(struct.pack("I", 0xffffff26))

    def cmd_loadimage(self, ptr, options):
        self.c(struct.pack("III", 0xffffff24, ptr, options))

    def cmd_logo(self):
        self.c(struct.pack("I", 0xffffff31))

    def cmd_memcpy(self, dest, src, num):
        self.c(struct.pack("IIII", 0xffffff1d, dest, src, num))

    def cmd_memcrc(self, ptr, num, result):
        self.c(struct.pack("IIII", 0xffffff18, ptr, num, result))

    def cmd_memset(self, ptr, value, num):
        self.c(struct.pack("IIII", 0xffffff1b, ptr, value, num))

    def cmd_memwrite(self, ptr, num):
        self.c(struct.pack("III", 0xffffff1a, ptr, num))

    def cmd_regwrite(self, ptr, val):
        self.memwrite(ptr, 4)
        self.c4(val)

    def cmd_regwrite(self, ptr, val):
        self.c(struct.pack("IIII", 0xffffff1a, ptr, 4, val))

    def cmd_memzero(self, ptr, num):
        self.c(struct.pack("III", 0xffffff1c, ptr, num))

    def cmd_number(self, x, y, font, options, n):
        self.c(struct.pack("IhhhHi", 0xffffff2e, x, y, font, options, n))

    def cmd_progress(self, x, y, w, h, options, val, range):
        self.c(struct.pack("IhhhhHHH", 0xffffff0f, x, y, w, h, options, val, range))

    def cmd_regread(self, ptr, result):
        self.c(struct.pack("III", 0xffffff19, ptr, result))

    def cmd_rotate(self, a):
        self.c(struct.pack("Ii", 0xffffff29, a))

    def cmd_scale(self, sx, sy):
        self.c(struct.pack("Iii", 0xffffff28, f16(sx), f16(sy)))

    def cmd_screensaver(self):
        self.c(struct.pack("I", 0xffffff2f))

    def cmd_scrollbar(self, x, y, w, h, options, val, size, range):
        self.c(struct.pack("IhhhhHHHH", 0xffffff11, x, y, w, h, options, val, size, range))

    def cmd_setfont(self, font, ptr):
        self.c(struct.pack("III", 0xffffff2b, font, ptr))

    def cmd_setmatrix(self):
        self.c(struct.pack("I", 0xffffff2a))

    def cmd_sketch(self, x, y, w, h, ptr, format):
        self.c(struct.pack("IhhHHIH", 0xffffff30, x, y, w, h, ptr, format))

    def cmd_slider(self, x, y, w, h, options, val, range):
        self.c(struct.pack("IhhhhHHH", 0xffffff10, x, y, w, h, options, val, range))

    def cmd_snapshot(self, ptr):
        self.c(struct.pack("II", 0xffffff1f, ptr))

    def cmd_spinner(self, x, y, style, scale):
        self.c(struct.pack("IhhHH", 0xffffff16, x, y, style, scale))

    def cmd_stop(self):
        self.c(struct.pack("I", 0xffffff17))

    def cmd_swap(self):
        self.c(struct.pack("I", 0xffffff01))

    def cmd_text(self, x, y, font, options, s):
        self.c(align4(struct.pack("IhhhH", 0xffffff0c, x, y, font, options) + s + chr(0)))

    def cmd_toggle(self, x, y, w, font, options, state, s):
        self.c(struct.pack("IhhhhHH", 0xffffff12, x, y, w, font, options, state) + s + chr(0))

    def cmd_touch_transform(self, x0, y0, x1, y1, x2, y2, tx0, ty0, tx1, ty1, tx2, ty2, result):
        self.c(struct.pack("IiiiiiiiiiiiiH", 0xffffff20, x0, y0, x1, y1, x2, y2, tx0, ty0, tx1, ty1, tx2, ty2, result))

    def cmd_track(self, x, y, w, h, tag):
        self.c(struct.pack("Ihhhhh", 0xffffff2c, x, y, w, h, tag))

    def cmd_translate(self, tx, ty):
        self.c(struct.pack("Iii", 0xffffff27, f16(tx), f16(ty)))

    # Converting versions, *f

    def cmd_translatef(self, tx, ty):
        self.cmd_translate(int(65536 * tx), int(65536 * ty))
