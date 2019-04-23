import gameduino2.gd3registers as gd
from gameduino2.base import align4
import xml.etree.ElementTree as ET

class Drawable:
    def __init__(self, eve, x, y, w, h):
        self.eve = eve
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def draw0(self, x, y):
        eve = self.eve
        eve.BitmapTransformC(self.x << 8)
        eve.BitmapTransformF(self.y << 8)
        eve.BitmapSize(gd.NEAREST, gd.BORDER, gd.BORDER, self.w, self.h)
        eve.BitmapSizeH(self.w >> 9, self.h >> 9)
        eve.Vertex2f(x, y)

    def draw(self, x, y):
        self.draw0(x - self.w // 2, y - self.h // 2)

class NameDict(dict):
    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError

def load(eve, file_name):
    tree = ET.parse(file_name)
    root = tree.getroot()
    if root.tag == 'TextureAtlas':
        imagepath = root.attrib['imagePath']
        eve.cmd_loadimage(0, 0)
        eve.c(align4(open(imagepath, "rb").read()))
        r = NameDict()
        for child in root.iter('SubTexture'):
            a = child.attrib
            nm = a['name']
            (x, y, width, height) = [int(a[n]) // 2 for n in ["x", "y", "width", "height"]]
            # print(nm, x, y, width, height)
            r[nm] = Drawable(eve, x, y, width, height)
        return r
