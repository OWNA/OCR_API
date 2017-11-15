from collections import Counter
import numpy as np
import swalign

scoring = swalign.NucleotideScoringMatrix(2, -1)
sw = swalign.LocalAlignment(scoring)

TARGET_NAMES = ['code', 'description', 'gst', 'price1', 'price2',
                'price3', 'price4', 'quantity',
                'packSize', 'brand', 'unitOfMeasure']

most_common_header_words = [
    'description', 'price', 'total', 'code', 'item', 'amount', 'qty',
    'value', 'gst', 'pregst', 'product', 'unit', 'supplied', 'quantity',
    'net', 'discount', 'brand', 'ordered', 'per', 'amt', 'rate', 'tax',
    'carton', 'size', 'details', 'name', 'measure', 'totals', 'count',
    'items', 'number', 'type', 'num', 'delivered', 'id', 'ord', 'pack']


def extract(filename, with_null):
    target_names = ['NULL'] + TARGET_NAMES if with_null else TARGET_NAMES
    f = open(filename)
    features = []
    targets = []
    filenames = []
    for l in f:
        l = l.split(',')
        if not with_null:
            if l[0] == 'NULL':
                continue
        targets.append(l[0])
        filenames.append(l[1])
        features.append([v.strip() for v in l[2:]])
    # Transform non-numeric features
    c = Counter()
    for s in features:
        for w in s[-1].split(' '):
            if w:
                c[w] += 1
    #print [w for w, _ in c.most_common(40)]
    for s in features:
        header = s.pop(-1)
        for common_word in most_common_header_words:
            s.append(0)
            if header:
                for w in header.split(' '):
                    aln = sw.align(common_word, w.lower())
                    score = aln.score / float(2 * len(common_word))
                    s[-1] = max(s[-1], score)
    features = np.array(features, dtype=np.float32)
    filenames = np.array(filenames)
    targets = np.array([target_names.index(t) for t in targets])
    return features, targets, filenames
