import sys
import GD

if __name__ == '__main__':
    eve = GD.GD(sys.argv[1])
    eve.setup_480x272()

    eve.ClearColorRGB(0x00, 0x40, 0x00)
    eve.Clear()
    eve.cmd_text(20, 20, 31, 0, "Hello from Python")
    eve.swap()
