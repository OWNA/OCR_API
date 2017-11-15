import re
import numpy as np
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity


def contain_header_words(text):
    words = ["quantity", "price", "gst", "value", "code",
             "description", "qty", "details"]
    for w in words:
        if w in text.lower():
            return True
    return False


class TableLine(object):
    def __init__(self, cells):
        self.cells = cells
        self.features = []
        self.__compute_features()

    def __compute_features(self):
        for cell in self.cells:
            cell_features = [0] * 3
            cell_features[0] = len(cell)
            cell_features[1] = is_digit(cell)
            cell_features[2] = cell.startswith('$')
            self.features += cell_features
        self.features = np.array(self.features)

    def get_normalized(self, means):
        normalized = []
        for (f, m) in zip(self.features, means):
            if m:
                normalized.append(f / m)
            else:
                normalized.append(f)
        return np.array(normalized).reshape(1, -1)


def remove_outliers(lines):
    lines = [line for line in lines if len(''.join(line))]

    max_length = np.max([len(line) for line in lines])
    for line in lines:
        for k in range(len(line), max_length):
            line.append('')

    table_lines = [TableLine(line) for line in lines]
    lines = []

    samples = []
    for l in table_lines:
        samples.append(l.features)
    samples = np.array(samples)
    samples_mean = np.mean(samples, axis=0)

    for l1 in table_lines:
        S = []
        f1 = l1.get_normalized(samples_mean)
        for l2 in table_lines:
            f2 = l2.get_normalized(samples_mean)
            S.append(cosine_similarity(f1, f2)[0][0])
        if np.median(S) > 0.9:
            lines.append(l1.cells)
    return lines


class OcrLineWord(object):
    def __init__(self, word):
        self.word = word
        self.line = None
        self.lines = []


class OcrLine(object):

    def __init__(self, content):
        self.content = content
        self.index = 0
        self.extrapolated_y = 0
        self.words = []
        self.spaces = []

    def y(self):
        if not self.words:
            return self.extrapolated_y
        return np.mean([w.word.yB[0] for w in self.words])

    def compute_spaces(self):
        if len(self.words) < 2:
            return
        s = []
        s.append(self.words[0].word.xR[-1])
        for w in self.words[1:-1]:
            s.append(w.word.xL[0])
            s.append(w.word.xR[-1])
        s.append(self.words[-1].word.xL[0])
        self.spaces = zip(s[0::2], s[1::2])
        assert len(self.spaces) == len(self.words) - 1

    def debug(self):
        print self.content
        for w in self.words:
            print '\t' + w.word.content

def extrapolate_y(lines):
    missingY = []
    lastY = 0
    for line in lines:
        if not line.y():
            missingY.append(line)
        else:
            newY = line.y()
            for l in missingY:
                l.extrapolated_y = (newY + lastY) / 2
            missingY = []
            lastY = newY
    for l in missingY:
        l.extrapolated_y = lastY + 20


def get_binary_score(line1, line2):
    spaces1 = line1.spaces
    spaces2 = line2.spaces
    if not spaces1 or not spaces2:
        return 0
    i1 = 0
    i2 = 0
    s = 0
    s1 = np.sum([x[1] - x[0] for x in spaces1])
    s2 = np.sum([x[1] - x[0] for x in spaces2])
    while i1 < len(spaces1) and i2 < len(spaces2):
        start1 = spaces1[i1][0]
        start2 = spaces2[i2][0]
        end1 = spaces1[i1][1]
        end2 = spaces2[i2][1]
        if start1 > end2:
            i2 += 1
        elif start2 > end1:
            i1 += 1
        else:
            s += min(end1, end2) - max(start1, start2)
            if end1 < end2:
                i1 += 1
            else:
                i2 += 1
    return 2 * float(s) / (s1 + s2)


def is_digit(w):
    return re.match('^[-0-9.$\sT]+$', w) is not None


def get_unary_score(line):
    hasDigit = False
    hasText = False

    for w in line.words:
        content = w.word.content
        if is_digit(content):
            hasDigit = True
        else:
            hasText = True
    return 1 if hasDigit and hasText else 0


def has_food_items(text):
    tokens = word_tokenize(text)
    tokens = filter(lambda x: not x.isdigit() and len(x) > 2, tokens)
    for t in tokens:
        for s in wn.synsets(t):
            h = [s]
            while h:
                name = h[0].name().split('.')[0]
                #print t, name
                if name in ['container', 'food', 'animal', 'equipment']:
                    return True
                    break
                h = h[0].hypernyms()
    return False


def can_merge_lines(line1, line2):
    if not line1.words or not line2.words:
        return False
    w1 = line1.words[-1].word
    w2 = line2.words[0].word
    return w1.xR[-1] < w2.xL[0]


def can_merge_groups(group1, group2):
    binary_scores = []
    for line1 in group1:
        for line2 in group2:
            binary_scores.append(get_binary_score(line1, line2))
    return np.mean(binary_scores) > 0.9


def merge_lines(line1, line2):
    line1.words += line2.words
    line1.content += line2.content
    line2.content = ""
    line2.words = []


def get_group_score(lines):
    score = 0
    for l in lines:
        itemFound = False
        digits = 0
        for w in l.words:
            itemFound = itemFound or has_food_items(w.word.content)
            if is_digit(w.word.content):
                digits += 1
        if itemFound or digits > 2:
            score += 1
        else:
            score += 0.2
    return score
