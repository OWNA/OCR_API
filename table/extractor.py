import numpy as np
import re
from scipy.cluster.vq import kmeans

from utils.files import Word, XMLFile, ProcessReceiptXMLFile
from matching.constants import *
from matching.optimizer import optimizeMatchingForParts
from matching.exceptions import MaxDurationReached
from cluster import bestKMeansByK, bestKMeansByTransform
from utils.geometry import rotate
from cells import *


def computeClusterSize(coordinatesS, coordinatesE, clusterIndices, angle, xOrY):
    """
    Given the start and end of the value that contributed to a point
    in a cluster, this algorithm will return the size of the cluster in
    the xOrY direction.
    """
    clusters = [[] for _ in xrange(np.max(clusterIndices) + 1)]
    for index, clusterIndex in enumerate(clusterIndices):
        x1, y1 = coordinatesS[index]
        x2, y2 = coordinatesE[index]
        v1 = rotate(x1, y1, angle)[xOrY]
        v2 = rotate(x2, y2, angle)[xOrY]
        clusters[clusterIndex].append(v1)
        clusters[clusterIndex].append(v2)
    return [(np.min(v), np.max(v)) for v in clusters]


def extractCells(words, productItems):

    try:
        _, _, a = optimizeMatchingForParts(
            productItems, words, [DESCRIPTION],
            includeEmpty=True,
            mergeCells=False
        )
    except MaxDurationReached:
        return []

    cells = []

    startY = float("inf")
    endY = -float("inf")
    startX = float("inf")
    endX = -float("inf")
    for lineIndex, productItem in enumerate(a.productItems):
        if a.matching[lineIndex][0]:
            match = a.matching[lineIndex][0][0]
            cells.append(Cell(match.xL,
                              match.xR,
                              match.yT,
                              match.yB,
                              match.value,
                              CELL_DESCRIPTION))
            endX = max(endX, match.xR - 50)
            startX = min(startX, match.xL + 50)
            startY = min(startY, match.yT - 50)
            endY = max(endY, match.yB + 50)

    pattern = re.compile("^\s*(?:\$)?([0-9]+[0-9.]*)\s*$")
    for word in words:
        content = word.content
        if not content:
            continue
        offset = 0
        end = offset + len(content)
        xL = word.xL[offset]
        xR = word.xR[end - 1]
        yT = word.minYT(offset, end)
        yB = word.maxYB(offset, end)
        if yT > startY and yB < endY and (xL > endX or xR < startX):
            if pattern.match(content):
                cells.append(Cell(xL, xR, yT, yB, content, CELL_NUMBER))
            else:
                cells.append(Cell(xL, xR, yT, yB, content, CELL_OTHER))
    return cells


def extractTableStructure(words, productItems):
    """
    Extracts the table cell positions.
    """
    cells = extractCells(words, productItems)

    coordinates = []
    coordinatesS = []
    coordinatesE = []
    numLines = 0
    for cell in cells:
        if cell.is_number():
            l, t, r, b = cell.l, cell.t, cell.r, cell.b
        elif cell.is_description():
            l, t, r, b = cell.l, cell.t, cell.r, cell.b
            numLines += 1
        else:
            continue
        coordinatesS.append((l, t))
        coordinatesE.append((r, b))
        coordinates.append(((l + r) / 2, (t + b) / 2))

    angle = 0
    if coordinates and len(coordinates) >= numLines and numLines > 1:
        yClusters, yCenters, angle = bestKMeansByTransform(
            coordinates,
            numLines,
            rotate,
            np.linspace(-5, 5, 21))
        cellsY = computeClusterSize(coordinatesS, coordinatesE, yClusters, angle, 1)

        xClusters, xCenters = bestKMeansByK([
            rotate(x, y, angle)[0] for x, y in coordinates
        ], numLines == 1)
        cellsX = computeClusterSize(coordinatesS, coordinatesE, xClusters, angle, 0)

        predictedCells = [False] * (len(yCenters) * len(xCenters))

        for x, y in zip(xClusters, yClusters):
            predictedCells[x * len(yCenters) + y] = True
        for index, predictedCell in enumerate(predictedCells):
            ix = index // len(yCenters)
            iy = index % len(yCenters)
            l, r = cellsX[ix]
            t, b = cellsY[iy]
            newCell = Cell(l, r, t, b, None, CELL_POSSIBLE_NUMBER)
            newCell = newCell.rotate(-angle)
            if not predictedCell:
                intersect = None
                for cell in cells:
                    if cell.intersect(newCell):
                        intersect = cell
                        break
                if not intersect:
                    cells.append(newCell)
                if intersect and intersect.is_other():
                    cell.copy(newCell)

    return cells
