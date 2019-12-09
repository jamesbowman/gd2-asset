import sys
import struct
import random
from PIL import Image
import numpy as np
from scipy import spatial

def OnLine(a, b, p):
    ap = p-a
    ab = b-a
    if np.dot(ab, ab) == 0:
        return 0
    return np.clip(np.dot(ap,ab)/np.dot(ab,ab), 0, 1)

if __name__ == '__main__':
    im = Image.open(sys.argv[1]).convert("RGB")
    im = im.crop((500, 200, 600, 400))
    op = open("out.astc", "wb")
    op.write(struct.pack("<IBBBHBHBHB", 0x5ca1ab13, 10, 6, 1, im.size[0], 0, im.size[1], 0, 1, 0))

    dith = np.array(
        ([0.00, 0.50] * 5 +
         [0.75, 0.25] * 5) * 3) + 0.125
    print(dith)
    for y in range(0, im.size[1], 6):
        print(y)
        for x in range(0, im.size[0], 10):
            tile = im.crop((x, y, x + 10, y + 6))
            d = np.asarray(tile)
            (r, g, b) = d[0][0]
            d = d.reshape(60, 3).astype(float)
            dist_mat = spatial.distance_matrix(d, d)
            i, j = np.unravel_index(dist_mat.argmax(), dist_mat.shape)
            c0 = d[i]
            c1 = d[j]
            # c0 = np.array((0, 0, 0))
            # c1 = np.array((255, 255, 255))
            wf = [OnLine(c0, c1, p) for p in d]
            if sum(c0) > sum(c1):
                (c1, c0) = (c0, c1)
                wf = [1-w for w in wf]
            # print(wf)
            assert all([wf[i] < 1.0001 for i in range(60)])
            if 0:
                q = 0xfffffffffffffdfc
                q |= int(r) << 0x48
                q |= int(g) << 0x58
                q |= int(b) << 0x68
                q |= int(255) << 0x78
            else:
                blockmode = 0b10101000100       # 8x8
                blockmode = 0b00110100100
                cem = 8
                q = blockmode | (cem << 13)
                q |= int(c0[0]) << (17 + 0*8)
                q |= int(c0[1]) << (17 + 2*8)
                q |= int(c0[2]) << (17 + 4*8)
                q |= int(c1[0]) << (17 + 1*8)
                q |= int(c1[1]) << (17 + 3*8)
                q |= int(c1[2]) << (17 + 5*8)
                q |= sum([(int(wf[i] > d) << (127 - i)) for i,d in enumerate(dith)])

            op.write(struct.pack("<QQ", q & (2**64-1), (q >> 64)))

    op.close()
