import unittest
import Image
import gameduino2 as gd2


class TestPreptools(unittest.TestCase):
    def test_tile_magicland(self):
        class Tiledemo(gd2.prep.AssetBin):
            asset_file = "tiledemo.gd2"
            def addall(self):
                self.target_810()

                if 0:
                    self.load_tiles("TILEMAP", "gameart2d-desert.tmx", 0.5)
                    desert = Image.open("desert-bg.png").resize((480, 272), Image.ANTIALIAS)
                    self.load_handle("BACKGROUND", [desert], gd2.RGB565)
                else:
                    self.preview = self.load_tiles("TILEMAP", "testdata/MagicLand.tmx", preview = True)
        td = Tiledemo()
        td.make()
        p = td.preview
        self.assertEqual(p.mode, "RGB")
        self.assertEqual(p.size, (7360, 1200))
        self.assert_(p.tostring() == Image.open("testdata/golden-tiledemo.png").tostring())

if __name__ == '__main__':
    unittest.main()
