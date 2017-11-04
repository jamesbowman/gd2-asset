import sys
import struct
from fractions import Fraction

def pp4(fourcc):
    (a,b,c,d) = struct.unpack("4B", fourcc)
    return "%02x%02x%02x%02x" % (d, c, b, a)

class Avi:
    def __init__(self, filename):
        self.f = open(filename, "r+b")
        self.atime = 0
        self.vtime = 0

    def get(self, n):
        return self.f.read(n)

    def unpack(self, fmt):
        sz = struct.calcsize(fmt)
        return struct.unpack(fmt, self.get(sz))

    def parse(self, level = 0):
        fourcc = self.get(4)
        (size, ) = self.unpack("I")
        if fourcc in ('RIFF', 'LIST'):
            print ("    " * level)+ fourcc, pp4(fourcc), size
            if fourcc == 'RIFF':
                self.remainder = size - 4
            else:
                self.remainder -= 12
            _ = self.get(4)
            sz = size - 4
            while sz:
                sz -= self.parse(level + 1)
                assert 0 <= sz
        else:
            if fourcc == 'avih':
                (
                    _,_,_,
                    dwFlags,dwTotalFrames,_,dwStreams,_,
                    dwWidth,dwHeight,
                    _,_,_,_
                ) = self.unpack("IIIIIIIIIIIIII")
                print ("    " * level)+'flags', '%04x' % dwFlags, dwTotalFrames,dwStreams,dwWidth,dwHeight
            elif fourcc == 'strh':
                o = self.f.tell()
                (
                    fccType, fccHandler,
                    dwFlags, wPriority,
                    wLanguage, dwInitialFrames,
                    dwScale, dwRate,
                    dwStart, dwLength,
                    dwSuggestedBufferSize,
                    dwQuality,
                    dwSampleSize,
                    _,_,_,_) = self.unpack("4s4sIHHIIIIIIII4H")
                if fccType == 'vids':
                    print 'offset', o
                    self.rate_offset = o + 20
                print (
                    fccType, fccHandler,
                    dwFlags,
                    wPriority, wLanguage,
                    dwInitialFrames,
                    dwScale, dwRate,
                    dwStart, dwLength,
                    dwSuggestedBufferSize,
                    dwQuality,
                    dwSampleSize)
                print float(dwRate) / dwScale, 'samples/s'
            elif fourcc == 'strf':
                d = self.get(size)
                if 0:
                    if size == 16:
                        print struct.unpack("HHIIHH", d)
                    if size == 18:
                        print struct.unpack("HHIIHHH", d)
            elif fourcc == '01dc':
                d = self.get(size)
                if d:
                    self.vtime += 1 / 30.
            elif fourcc == '01wb':
                self.samples.write(self.get(size)[4:])
                self.atime += (size - 0) / 44100.
            else:
                self.get(size)
            # "A=%7.3f V=%7.3f  %7.3f" % (self.atime, self.vtime, self.atime - self.vtime)
            # print ("    " * level) + 'chunk', fourcc, pp4(fourcc), size, "%08x" % (self.remainder)
            self.remainder -= ((9 + size) & -2)
        if size & 1:
            self.get(1)
        # return 8 + ((size + 1) & -2)
        return (9 + size) & -2

if __name__ == '__main__':
    rate = Fraction(sys.argv[1])
    print repr(rate)

    a = Avi(sys.argv[2])
    a.parse()
    a.f.seek(a.rate_offset)
    a.f.write(struct.pack("II", rate.denominator, rate.numerator))
