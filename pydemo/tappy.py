import atlas

import GD

if __name__ == '__main__':
    eve = GD.GD()
    eve.setup_480_272()

    a = atlas.load(eve, "sheet.xml")

    score = 1230

    eve.ClearColorRGB(0x97, 0x71, 0x4a)
    eve.Clear()
    eve.Begin(GD.BITMAPS)

    a.background   .draw0(0, 0)
    a.background   .draw0(400, 0)

    a.rockGrassDown.draw0(220, 0)
    a.rockGrass    .draw0(300, 120)
    a.rockGrassDown.draw0(400, 0)
    a.planeRed1    .draw(100, 136)
    a.textGetReady .draw(300, 136)

    a.groundGrass  .draw0(0, 205)
    a.groundGrass  .draw0(400, 205)

    for i,digit in enumerate("%06d" % score):
        x = 290 + 32 * i
        a["number" + str(digit)].draw(x, 252)

    eve.ColorRGB(128, 128, 128)
    a.planeRed1.draw(40, 252)
    a.planeRed1.draw(90, 252)

    eve.swap()
    eve.finish()
