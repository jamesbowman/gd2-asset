import array
import Image
import ImageFilter
import math
import os
import struct
import numpy

import gameduino2 as gd2

class Nightstrike(gd2.prep.AssetBin):

    def addall(self):
        print self.bg
        self.dxt1("../assets/nightstrike/backgrounds/%s.jpg" % self.bg)

        def shrink(im, l):
            factor = float(l) / max(im.size)
            w,h = im.size
            if factor < 0.25:
                im = im.resize((int(w / 2), int(h / 2)), Image.ANTIALIAS)
            return im.resize((int(w * factor), int(h * factor)), Image.ANTIALIAS)

        def rot(im):
            return im.transpose(Image.ROTATE_180)

        def asset(dir, spr, frame):
            return Image.open("../assets/nightstrike/%s/%s%04d.png" % (dir, spr, frame))

        im = shrink(asset("base", "defensor_front", 1), 104)
        (l4, _, _, a) = im.split()
        self.load_handle("DEFENSOR_FRONT", [a, l4], gd2.L4)
        # self.load_handle("DEFENSOR_FRONT", [im], gd2.ARGB4)

        ims = [rot(shrink(asset("base", "defensor_turret", i), 50)) for i in (1, )]
        self.load_handle("DEFENSOR_TURRET", ims, gd2.ARGB4, filter = gd2.BILINEAR, rotating = True)

        ims = [rot(shrink(asset("missles", "missleA", 1), 51))]
        self.load_handle("MISSILE_A", ims, gd2.ARGB4, filter = gd2.BILINEAR, rotating = True)

        ims = [rot(shrink(asset("missles", "missleC", 1), 35))]
        self.load_handle("MISSILE_C", ims, gd2.ARGB4, filter = gd2.BILINEAR, rotating = True)
        # gd2.prep.join(ims).save("out.png")

        heli = [shrink(asset("heli", "copter_fly", i), 100) for i in (1, 2)]
        self.load_handle("HELI", heli, gd2.ARGB4)

        ims = [shrink(asset("heli", "copter_fall", i), 45) for i in (1, 3, 5, 11)]
        self.load_handle("COPTER_FALL", ims, gd2.ARGB4, scale = 2, filter = gd2.BILINEAR)

        ims = [shrink(asset("explosions", "explo_fire", i), 30) for i in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 22, 24)]
        self.load_handle("FIRE", ims, gd2.ARGB2, dither = False)

        ims = [shrink(asset("explosions", "explode_big", i), 100) for i in (1, 2, 3, 4, 5, 6, 8, 10, 12, 14)]
        self.load_handle("EXPLODE_BIG", ims, gd2.ARGB2, dither = False, filter = gd2.BILINEAR, rotating = True)

        ims = [shrink(asset("soldier", "soldier_run", i), 40) for i in (1, 4, 6, 8, 10, 13, 15, 17)]
        self.load_handle("SOLDIER_RUN", ims, gd2.ARGB4)
        gd2.prep.join(ims).save("out0.png")

        # ims = [shrink(asset("soldier", "soldier_shootA", i), 40) for i in (1, 4, 5, 6, 7, 8, 9, 11, 13, 15)]
        # self.load_handle("SOLDIER_SHOOT", ims, gd2.ARGB4)
        # gd2.prep.join(ims).save("out.png")

        self.load_ttf("INFOFONT", "../assets/Hobby-of-night.ttf", 14, gd2.L4)

class NightStrike_welcome(Nightstrike):
    asset_file = "nightw.gd2"
    bg = "welcome"
    prefix = "WELCOME_"

    def addall(self):
        self.dxt1("../assets/nightstrike/backgrounds/%s.jpg" % self.bg)
        self.load_ttf("DISPLAYFONT", "../assets/Hobby-of-night.ttf", 35, gd2.L4)

class Nightstrike_0(Nightstrike):
    asset_file = "night0.gd2"
    bg = "nightfall"

class Nightstrike_1(Nightstrike):
    asset_file = "night1.gd2"
    bg = "redworld"

class Nightstrike_2(Nightstrike):
    asset_file = "night2.gd2"
    bg = "purplesnow"

class Nightstrike_3(Nightstrike):
    asset_file = "night3.gd2"
    bg = "burningwoods"

class Nightstrike_4(Nightstrike):
    asset_file = "night4.gd2"
    bg = "greenland"

if __name__ == '__main__':
    NightStrike_welcome().make()
    Nightstrike_0().make()
    Nightstrike_1().make()
    Nightstrike_2().make()
    Nightstrike_3().make()
    Nightstrike_4().make()
