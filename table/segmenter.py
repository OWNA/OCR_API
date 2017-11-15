import numpy as np
from table.cluster import bestKMeansByK
from table.labeller import MetaInfo, label_columns
from tabulate import tabulate

from table.line import OcrLine, OcrLineWord, extrapolate_y, \
    get_binary_score, get_unary_score, can_merge_groups, \
    can_merge_lines, merge_lines, get_group_score, contain_header_words


def segment_from_raw_ocr(lines, words):
    lines = [OcrLine(line.decode('utf-8')) for line in lines]
    words = [OcrLineWord(word) for word in words]

    # Associate words to lines of text file
    for w in words:
        for line in lines:
            if w.word.content in line.content:
                w.lines.append(line)
        if len(w.lines) == 1:
            w.lines[0].words.append(w)
            w.line = w.lines[0]

    for _ in range(2):
        for w in words:
            if not w.line and w.lines:
                closestLine = None
                undefined = False
                closestLineD = 0
                for l in w.lines:
                    if not l.y():
                        undefined = True
                    if not closestLine or closestLineD > abs(l.y() - w.word.yB[0]):
                        closestLine = l
                        closestLineD = abs(l.y() - w.word.yB[0])
                if undefined:
                    continue
                w.line = closestLine
                closestLine.words.append(w)
        extrapolate_y(lines)

    for line in lines:
        line.words.sort(key=lambda w: w.word.xL)

    for line1, line2 in zip(lines, lines[1:]):
        if can_merge_lines(line1, line2):
            merge_lines(line1, line2)
        elif can_merge_lines(line2, line1):
            merge_lines(line2, line1)

    for lineIndex, line in enumerate(lines):
        line.compute_spaces()
        line.index = lineIndex
        #line.debug()

    # Segment into groups of lines
    groups = []
    scores = []
    lines = list(filter(lambda x: len(x.words) > 1, lines))

    for line1, line2 in zip(lines, lines[1:]):
        binary_score = get_binary_score(line1, line2)
        unary_score = get_unary_score(line2)
        #print unary_score, binary_score, line2.content[0:100]
        if unary_score > 0.5:
            if groups and groups[-1][-1] == line1 and binary_score > 0.5:
                groups[-1].append(line2)
                scores[-1].append([binary_score, unary_score])
            else:
                groups.append([line2])
                scores.append([[binary_score, unary_score]])

    for g_index, (g, s) in enumerate(zip(groups, scores)):
        continue
        s = np.mean(np.array(s), axis=0)
        print "Group {} - Unary[{:0.2f}] Binary[{:0.2f}]".format(
            g_index, s[0], s[1])
        for l in g:
            print l.content

    if not groups:
        return [], None
    while True:
        new_groups = [groups[0]]
        for i in range(1, len(groups)):
            group1 = new_groups[-1]
            group2 = groups[i]
            if can_merge_groups(group1, group2):
                new_groups.pop()
                new_groups.append(group1 + group2)
            else:
                new_groups.append(group2)
        if len(new_groups) < len(groups):
            groups = new_groups
        else:
            break

    for g_index, g in enumerate(groups):
        continue
        print "Group {}".format(g_index)
        for l in g:
            print l.content

    # Pick the largest group and segment into columns
    table = groups[np.argmax([get_group_score(g) for g in groups])]
    header = None
    for line in lines:
        if ((table[0].index - line.index) in  (0, 1, 2) and
            contain_header_words(line.content)):
            header = line
    if contain_header_words(table[0].content):
        table = table[1:]
    coordinates = []
    max_clusters = 0
    if header is not None:
        table = [header] + table
    for l in table:
        max_clusters = max(max_clusters, len(l.words))
        for w in l.words:
            coordinates.append(np.mean(w.word.xL))
    x_clusters, x_centers = bestKMeansByK(
        coordinates,
        maxClusters=max_clusters + 1)
    C = len(x_centers)
    N = len(table)
    lines = []
    index = 0
    x_centersPI = sorted(range(C), key=lambda k: x_centers[k])
    x_centersP = [0] * C
    for k in range(C):
        x_centersP[x_centersPI[k]] = k
    for l in table:
        line = [""] * C
        for w in l.words:
            column = x_centersP[x_clusters[index]]
            line[column] = w.word.content
            index += 1
        lines.append(line)
    if header:
        meta_info = MetaInfo(words, lines[0])
        lines = lines[1:]
    else:
        meta_info = MetaInfo(words)
    return lines, meta_info


def segment_and_label_from_raw_ocr(lines, words):
    lines, meta_info = segment_from_raw_ocr(lines, words)
    labels = label_columns(lines, meta_info)
    return lines, labels
