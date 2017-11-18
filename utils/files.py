import xml
import numpy as np
from .geometry import rotate, revolve, swap
from flags import WORD_SPLIT_DISTANCE
from skimage.transform import AffineTransform, ProjectiveTransform
from skimage.transform import SimilarityTransform, warp
from sklearn.metrics import mean_squared_error
from skimage.measure import ransac
from scipy.interpolate import griddata
from xml.etree import ElementTree
import math
import json


SCHEMA = '{http://www.abbyy.com/FineReader_xml/FineReader10-schema-v1.xml}'
RECEIPT_SCHEMA = '{http://www.abbyy.com/ReceiptCaptureSDK_xml/ReceiptCapture-1.0.xsd}'

def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) **2 + (y1 - y2)**2)


class Box(object):

    def __init__(self, l, t, r, b):
        self.l = l
        self.r = r
        self.b = b
        self.t = t

    @property
    def center(self):
        return [(self.l + self.r) / 2, (self.t + self.b) / 2]


class Word(object):

    def __init__(self, content, xL, xR, yT, yB, page_index=0):
        self.content = content
        self.xL = xL
        self.xR = xR
        self.yT = yT
        self.yB = yB
        self.page_index = page_index

    def x(self, offset):
        return (self.xL[offset] + self.xR[offset]) / 2.

    def meanYT(self, start, end):
        return np.mean(self.yT[start:end])

    def meanYB(self, start, end):
        return np.mean(self.yB[start:end])

    def minYT(self, start, end):
        return min(self.yT[start:end])

    def maxYB(self, start, end):
        return max(self.yB[start:end])

    @property
    def box(self):
        return Box(self.xL[0], self.yT[0], self.xR[-1],  self.yB[-1])

    def __str__(self):
        return ','.join([self.content.encode('utf-8'),
                         str(int(self.xL[0])),
                         str(int(self.xR[-1])),
                         str(int(self.yT[0])),
                         str(int(self.yB[-1]))])


class SimpleWord(Word):

    def __init__(self, content, xL, xR, yT, yB, page_index=0):
        super(SimpleWord, self).__init__(content, xL, xR, yT, yB, page_index)

    def x(self, offset):
        return self.xL + (self.xR - self.xL) * (offset + 1) / (len(self.content))

    def meanYT(self, start, end):
        return self.yT

    def meanYB(self, start, end):
        return self.yB

    def __str__(self):
        return ','.join([self.content.encode('utf-8'),
                         str(int(self.xL)),
                         str(int(self.xR)),
                         str(int(self.yT)),
                         str(int(self.yB))])


class JSONFile(object):

    def __init__(self, filename):
        self.filename = filename
        self.words = []


    def parse(self, W, H):
        j = json.load(open(self.filename))
        orientation = j.get('orientation')
        angle = j.get('textAngle')
        tx = 0
        ty = 0
        index = 0
        if orientation in ('Left', 'Right'):
            W, H = H, W
        for region in j.get('regions'):
            for line in region.get('lines'):
                words = []
                L = None
                T = None
                R = None
                B = None
                for word in line.get('words'):
                    index += 1
                    bb = word.get('boundingBox')
                    l, t, w, h = bb.split(',')
                    text = word.get('text')
                    l = int(l)
                    t = int(t)
                    r = l + int(w)
                    b = t + int(h)
                    l, t = revolve(l, t, orientation, W, H)
                    r, b = revolve(r, b, orientation, W, H)
                    l, t = rotate(
                        l,
                        t,
                        angle,
                        W / 2.,
                        H / 2.,
                        rounding=True)
                    r, b = rotate(
                        r,
                        b,
                        angle,
                        W / 2.,
                        H / 2.,
                        rounding=True)
                    l, r = swap(l, r)
                    t, b = swap(t, b)
                    if not L:
                        L = l
                        R = r
                        T = t
                        B = b
                    else:
                        L = min(L, l)
                        R = max(R, r)
                        T = min(T, t)
                        B = max(B, b)
                    words.append(word.get('text'))
                self.words.append(SimpleWord(' '.join(words), L, R, T, B))


class XMLFile(object):


    def __init__(self, filename, page_index=0):

        self.filename = filename
        self.words = []
        self.page_index = page_index


    def parseWithVariants(self, split=False):
        e = ElementTree.parse(self.filename).getroot()
        # page/block/text/par/formatting/line/charParams
        self.text = ''
        self.words = []
        page = e.findall('.//{}page'.format(SCHEMA))[0]
        rotation = None
        if 'rotation' in page.attrib:
            rotation = page.attrib['rotation']
        width = int(page.attrib['width'])
        height = int(page.attrib['height'])
        original = 'originalCoords' in page.attrib
        self.original = original
        self.width = width
        self.height = height
        if (rotation == 'RotatedUpsidedown'):
            self.rotation = 180
        elif (rotation == 'RotatedClockwise'):
            self.rotation = 90
        elif (rotation == 'RotatedCounterclockwise'):
            self.rotation = -90
        else:
            self.rotation = 0
        for par in e.findall('.//{}par'.format(SCHEMA)):
            for line in par.findall('.//{}line'.format(SCHEMA)):
                word = ''
                xL = []
                xR = []
                yT = []
                yB = []
                lp, rp, tp, bp = [None] * 4
                spaces = 0
                for charParams in line.findall('.//{}charParams'.format(SCHEMA)):
                    char = ''
                    for charRecVariants in charParams.findall(
                            './/{}charRecVariants'.format(SCHEMA)):
                        char = charRecVariants.tail
                    attrib = charParams.attrib
                    l = float(attrib['l'])
                    r = float(attrib['r'])
                    t = float(attrib['t'])
                    b = float(attrib['b'])
                    if not l or not r or not t or not b:
                        continue
                    if original:
                        l, t = rotate(l, t, self.rotation)
                        r, b = rotate(r, b, self.rotation)
                        if l > r:
                            tmp = l
                            l = r
                            r = tmp
                        if b < t:
                            tmp = b
                            b = t
                            t = tmp
                    if (lp and rp <= l and
                        distance(rp, tp, l, t) > WORD_SPLIT_DISTANCE and
                        distance(rp, bp, l, b) > WORD_SPLIT_DISTANCE and
                        split):
                        N = len(word)
                        self.words.append(Word(word[0:N - spaces],
                                               xL[0:N - spaces],
                                               xR[0:N - spaces],
                                               yT[0:N - spaces],
                                               yB[0:N - spaces],
                                               self.page_index))
                        word = ''
                        spaces = 0
                        xL = []
                        xR = []
                        yT = []
                        yB = []
                        lp, rp, tp, bp = [None] * 4
                    elif char != ' ':
                        spaces = 0
                        lp, rp, tp, bp = l, r, t, b
                    if not char.isspace() or (not word.isspace() and word):
                        word += char
                        xL.append(l)
                        xR.append(r)
                        yT.append(t)
                        yB.append(b)
                        if char.isspace():
                            spaces += 1
                N = len(word)
                if N != spaces:
                    self.words.append(Word(word[0:N - spaces],
                                           xL[0:N - spaces],
                                           xR[0:N - spaces],
                                           yT[0:N - spaces],
                                           yB[0:N - spaces],
                                           self.page_index))

    def parse(self):

        e = ElementTree.parse(self.filename).getroot()
        # page/block/text/par/formatting/line/charParams
        self.text = ''
        self.words = []
        for par in e.findall('.//{}par'.format(SCHEMA)):
            for line in par.findall('.//{}line'.format(SCHEMA)):
                word = ''
                xL = []
                xR = []
                yt = []
                yB = []
                for charParams in line.findall('.//{}charParams'.format(SCHEMA)):
                    attrib = charParams.attrib
                    l1 = float(attrib['l'])
                    r1 = float(attrib['r'])
                    t1 = float(attrib['t'])
                    b1 = float(attrib['b'])
                    xL.append(l1)
                    xR.append(r1)
                    yT.append(t1)
                    yB.append(b1)
                    word += charParams.text
                self.words.append(Word(word, xL, xR, yT, yB, self.page_index))

    def transform(self, xml_file, words, image):
        src = []
        dst = []
        if len(self.words) != len(xml_file.words):
            return None
        for w1, w2 in zip(self.words, xml_file.words):
            if w2.content != w1.content:
                return None
            points = zip(w1.xL, w1.yT, w2.xL, w2.yT) + \
                     zip(w1.xR, w1.yB, w2.xR, w2.yB)
            for x1, y1, x2, y2 in points:
                src.append([x1, y1])
                dst.append([x2, y2])
        src = np.array(src)
        dst = np.array(dst)
        # A model for transforming coordinates
        # This requires being able to convert from the current coordinates
        # to the destination coordinates.
        modelC = ProjectiveTransform()
        modelC.estimate(dst, src)
        dst2 = modelC.inverse(src)
        error = mean_squared_error(dst, dst2)
        print "Fitting MSE: {} on {}".format(error, self.filename)
        left_points = []
        right_points = []
        for w in words:
            left_points.append([w.xL, w.yT])
            right_points.append([w.xR, w.yB])
        left_points = modelC.inverse(left_points)
        right_points = modelC.inverse(right_points)
        for w, (xL, yT), (xR, yB) in zip(words, left_points, right_points):
            w.xL = xL
            w.xR = xR
            w.yT = yT
            w.yB = yB
        # A model for warping images
        # This requires being able to convert from the destination coordinates
        # to the original coordinates (prior to their rotation in the
        # parseWithVariants code).
        modelI = ProjectiveTransform()
        fix = SimilarityTransform(rotation=self.rotation * math.pi / 180.)
        srcO = fix.inverse(src)
        modelI.estimate(srcO, dst)
        w, h, _ = image.shape
        image_transformed = warp(
            image, modelI.inverse,
            output_shape=(xml_file.height, xml_file.width, 3))
        return image_transformed * 255

    def debug(self):
        for word in self.words:
            print word


class ProcessReceiptXMLItem(object):

    def __init__(self, name, price, count, total):

        self.name = name
        self.price = price
        self.count = count
        self.total = total


class ProcessReceiptXMLFile(object):


    def __init__(self, filename):

        self.filename = filename
        self.items = []


    def parseWithVariants(self):

        e = ElementTree.parse(self.filename).getroot()
        print self.filename
        # page/block/text/par/formatting/line/charParams
        self.text = ''
        self.words = []
        sc = RECEIPT_SCHEMA
        for items in e.findall('.//{}recognizedItems'.format(sc)):
            for item in items.findall('.//{}item'.format(sc)):
                name = item.find('.//{}name/{}text'.format(sc, sc))
                price = item.find('.//{}price/{}normalizeValue'.format(sc, sc))
                count = item.find('.//{}count/{}normalizedValue'.format(sc, sc))
                total = item.find('.//{}total/{}normalizedValue'.format(sc, sc))
                name = name.text if name is not None else ""
                price = price.text if price is not None else 0
                count = count.text if count is not None else 0
                total = total.text if total is not None else 0
                item = ProcessReceiptXMLItem(name, price, count, total)
                self.items.append(item)


    def parse(self):

        raise NotImplemented()
