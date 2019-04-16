import math

def wheel(e, r, n):
    e.Begin(gd3.LINE_STRIP)
    for i in range(n + 1):
        th = 2 * math.pi * ((17 * i) % n) / n
        e.Vertex2f(r * math.cos(th), r * math.sin(th))
        
def pinwheel(e):
    e.Clear()
    e.VertexTranslateX(16 * 240)
    e.VertexTranslateY(16 * 136)

    e.ColorRGB(0xc0, 0xff, 0xc0)
    wheel(e, 50, 30)
    e.ColorRGB(0xff, 0xc0, 0xc0)
    wheel(e, 110, 24)
    e.ColorRGB(0xc0, 0xc0, 0xff)
    wheel(e, 230, 52)
    e.swap()

