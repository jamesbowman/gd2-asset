import array
from PIL import Image, ImageFilter
import math
import os
import struct
import numpy

from gameduino2 import prep, base, gd3registers as GD

class Nightstrike(prep.AssetBin):

    def addall(self):
        self.target_810()

        def shrink(im, l):
            factor = float(l) / max(im.size)
            w,h = im.size
            if factor < 0.25:
                im = im.resize((int(w / 2), int(h / 2)), Image.ANTIALIAS)
            return im.resize((int(w * factor), int(h * factor)), Image.ANTIALIAS)

        def rot(im):
            return im.transpose(Image.ROTATE_180)

        def asset(dir, spr, frame):
            return Image.open("%s/%s%04d.png" % (dir, spr, frame))

        anim = (1, 2, 3, 4, 5, 6, 8, 10, 12, 14)
        ims = [shrink(asset("explosions", "explode_big", i), 245) for i in (1, 2, 3, 4, 5, 6, 8, 10, 12, 14)]

        self.load_handle("EXPLODE_BIG", ims, GD.ASTC_6x6, filter = GD.BILINEAR)
        def inanim(f):
            return max([a for a in anim if a <= f])
        frames = [anim.index(inanim(i)) for i in range(1, 16)]
        self.post = [
            "explode_big.setframes(" + repr(frames) + ")\n"]

        im = shrink(asset("base", "defensor_front", 1), 280)
        self.load_handle("DEFENSOR_FRONT", [im], GD.ASTC_6x6)

        ims = [rot(shrink(asset("base", "defensor_turret", i), 114)) for i in (1, )]
        self.load_handle("DEFENSOR_TURRET", ims, GD.ASTC_6x6, filter = GD.BILINEAR)

        ims = [rot(shrink(asset("missles", "missleA", 1), 125))]
        self.load_handle("MISSILE_A", ims, GD.ASTC_6x6, filter = GD.BILINEAR)

        ims = [rot(shrink(asset("missles", "missleC", 1), 85))]
        self.load_handle("MISSILE_C", ims, GD.ASTC_6x6, filter = GD.BILINEAR)
        # GD.prep.join(ims).save("out.png")

        heli = [shrink(asset("heli", "copter_fly", i), 245) for i in (1, 2)]
        self.load_handle("HELI", heli, GD.ASTC_6x6)

        ims = [shrink(asset("heli", "copter_fall", i), 220) for i in (1, 3, 5, 11)]
        self.load_handle("COPTER_FALL", ims, GD.ASTC_6x6, filter = GD.BILINEAR)

        ims = [shrink(asset("explosions", "explo_fire", i), 73) for i in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 22, 24)]
        self.load_handle("FIRE", ims, GD.ASTC_6x6)

        ims = [shrink(asset("soldier", "soldier_run", i), 98) for i in (1, 4, 6, 8, 10, 13, 15, 17)]
        self.load_handle("SOLDIER_RUN", ims, GD.ASTC_6x6)

        # ims = [shrink(asset("soldier", "soldier_shootA", i), 40) for i in (1, 4, 5, 6, 7, 8, 9, 11, 13, 15)]
        # self.load_handle("SOLDIER_SHOOT", ims, GD.ASTC_6x6)
        # GD.prep.join(ims).save("out.png")

        self.load_ttf("INFOFONT", "Hobby-of-night.ttf", 14, GD.L4)

    def dump_bitmaps(self, hh):
        with open(self.asset_file.replace(".gd3", ".py"), "wt") as hh:
            hh.write("import game\n")
            for bm in self.bm:
                hh.write("{name} = game.Sprite({src}, {fmt}, {w}, {h}, {cells}, {handle})\n".format(**bm))
            hh.write("".join(self.post))

class NightStrike_welcome(Nightstrike):
    asset_file = "nightw.gd3"
    bg = "welcome"
    prefix = "WELCOME_"

    def addall(self):
        self.load_ttf("DISPLAYFONT", "Hobby-of-night.ttf", 35, GD.L4)

class Nightstrike_0(Nightstrike):
    asset_file = "night0.gd3"
    bg = "nightfall"

class Nightstrike_1(Nightstrike):
    asset_file = "night1.gd3"
    bg = "redworld"

class Nightstrike_2(Nightstrike):
    asset_file = "night2.gd3"
    bg = "purplesnow"

class Nightstrike_3(Nightstrike):
    asset_file = "night3.gd3"
    bg = "burningwoods"

class Nightstrike_4(Nightstrike):
    asset_file = "night4.gd3"
    bg = "greenland"

if __name__ == '__main__':
    # NightStrike_welcome().make()
    Nightstrike_0().make()
    # Nightstrike_1().make()
    # Nightstrike_2().make()
    # Nightstrike_3().make()
    # Nightstrike_4().make()
