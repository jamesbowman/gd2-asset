import array

def imbytes(im):
    try:
        bb = im.tobytes()
    except AttributeError:
        bb = im.tostring()
    return array.array('B', bb)

