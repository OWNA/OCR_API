import math

def rotate(x, y, angle, cx=0, cy=0, rounding=False):
    t = angle * math.pi / 180.
    x2 = cx + math.cos(t) * (x -  cx) - math.sin(t) * (y - cy)
    y2 = cy + math.sin(t) * (x - cx) + math.cos(t) * (y - cy)
    if rounding:
        return int(x2), int(y2)
    else:
        return x2, y2


def revolve(x, y, orientation, W, H):
    if orientation == 'Down':
        return W - x, H - y
    elif orientation == 'Left':
        return y, W - x
    elif orientation == 'Right':
        return H - y, x
    else:
        return x, y


def swap(u, v):
    if v < u:
        tmp = u
        u = v
        v = tmp
    return u, v
