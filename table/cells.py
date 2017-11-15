from utils.geometry import rotate, swap, revolve
from utils.files import SimpleWord
from utils.constants import *

CELL_NUMBER = 1
CELL_DESCRIPTION = 2
CELL_OTHER = 3
CELL_POSSIBLE_NUMBER = 4


class Cell:

    def __init__(self, l, r, t, b, content, cell_type):
        self.l = l
        self.r = r
        self.t = t
        self.b = b
        self.content = content
        self.cell_type = cell_type

    def is_number(self):
        return self.cell_type == CELL_NUMBER

    def is_possible_number(self):
        return self.cell_type == CELL_POSSIBLE_NUMBER

    def is_description(self):
        return self.cell_type == CELL_DESCRIPTION

    def is_other(self):
        return self.cell_type == CELL_OTHER

    def copy(self, cell):
        self.l = cell.l
        self.r = cell.r
        self.t = cell.t
        self.b = cell.b
        self.cell_type = cell.cell_type
        self.content = cell.content

    def rotate(self, angle):
        l = self.l
        r = self.r
        b = self.b
        t = self.t
        l, t = rotate(l, t, angle, rounding=True)
        r, b = rotate(r, b, angle, rounding=True)
        l, r = swap(l, r)
        t, b = swap(t, b)
        return Cell(l, r, t, b, self.content, self.cell_type)

    def intersect(self, cell_or_word):
        l1 = self.l
        r1 = self.r
        t1 = self.t
        b1 = self.b
        if type(cell_or_word) == SimpleWord:
            w = cell_or_word
            l2 = w.xL
            r2 = w.xR
            t2 = w.yT
            b2 = w.yB
        else:
            cell = cell_or_word
            l2 = cell.l
            r2 = cell.r
            t2 = cell.t
            b2 = cell.b
        x_intersect_1 = l2 >= l1 and l2 <= r1
        x_intersect_2 = l1 >= l2 and l1 <= r2
        y_intersect_1 = t2 >= t1 and t2 <= b1
        y_intersect_2 = t1 >= t2 and t1 <= b2
        if ((x_intersect_1 or x_intersect_2) and
            (y_intersect_1 or y_intersect_2)):
            intersect = (min(r1, r2) - max(l1, l2)) * (min(b1, b2) - max(t1, t2))
            union = (r1 - l1) * (b1 - t1) + (r2 - l2) * (b2 - t2)
            return float(intersect) / float(union)
        else:
            return 0

    def correct_exif(self, exif_orientation, width, height):
        if exif_orientation == 3:
            orientation = DOWN
        elif exif_orientation == 6:
            orientation = RIGHT
        elif exif_orientation == 8:
            orientation = LEFT
        else:
            return self
        l = self.l
        r = self.r
        b = self.b
        t = self.t
        l, t = revolve(l, t, orientation, width, height)
        r, b = revolve(r, b, orientation, width, height)
        l, r = swap(l, r)
        t, b = swap(t, b)
        return Cell(l, r, t, b, self.content, self.cell_type)

    def __str__(self):
        return ','.join([self.content.encode('utf-8'),
                         str(int(self.l)),
                         str(int(self.r)),
                         str(int(self.t)),
                         str(int(self.b))])
