from constants import *
from exceptions import TooManyPriceParts, MissingDescriptionPart
from line import LineComparator, getNumericScore
from utils.items import NewItem
from flags import MAX_LINE_Y_DIFF, MIN_SCORE_MATCH

lineComparator = LineComparator()


class Assignment:

    def __init__(self, productItems, relevantParts, words):

        self.productItems = productItems
        self.relevantParts = relevantParts
        self.words = words
        self.matching = None
        self.quantityIndex = None
        self.priceIndex = None
        self.descriptionIndex = None
        for relevantIndex, relevantPart in enumerate(relevantParts):
            if relevantPart == QUANTITY:
                self.quantityIndex = relevantIndex
            elif relevantPart == DESCRIPTION:
                self.descriptionIndex = relevantIndex
            elif (relevantPart == VALUE or
                  relevantPart == TOTAL_VALUE or
                  relevantPart == TOTAL_UNIT_VALUE or
                  relevantPart == UNIT_VALUE):
                if self.priceIndex:
                    raise TooManyPriceParts()
                self.priceIndex = relevantIndex
            else:
                raise NotImplementedError()
        if self.descriptionIndex is None:
            raise MissingDescriptionPart()

    def buildFromLight(self, lightAssignment, original):
        self.matching = []
        for lineIndex, _ in enumerate(original.matching):
            self.matching.append([])
            for relevantPart, _ in enumerate(original.matching[lineIndex]):
                lightIndex = lightAssignment[lineIndex][relevantPart]
                if lightIndex != -1 and lightIndex != EMPTY:
                    self.matching[lineIndex].append([
                        original.matching[lineIndex][relevantPart][lightIndex]
                    ])
                else:
                    self.matching[lineIndex].append([])


    def build(self, preAssignment=None):

        self.matching = []
        for lineIndex, productItem in enumerate(self.productItems):
            self.matching.append([])
            for relevantIndex, relevantPart in enumerate(self.relevantParts):
                self.matching[lineIndex].append([])
                if (preAssignment and relevantPart in preAssignment.relevantParts
                    and lineIndex < len(preAssignment.matching)):
                    self.matching[lineIndex][relevantIndex] = (
                        preAssignment.matching[lineIndex][relevantIndex])
                    continue
                for word in self.words:
                    partMatches = lineComparator.align(productItem, word, relevantPart)
                    for partMatch in partMatches:
                        isNumeric = partMatch.isNumeric
                        if (partMatch.score > MIN_SCORE_MATCH or
                            partMatch.isNumeric or type(productItem) == NewItem):
                            self.matching[lineIndex][relevantIndex].append(
                                CellAssignment(
                                    partMatch.score,
                                    word.x(partMatch.offset),
                                    word.x(partMatch.end - 1),
                                    word.meanYT(partMatch.offset, partMatch.end),
                                    word.meanYB(partMatch.offset, partMatch.end),
                                    partMatch.matchingValue,
                                    word.page_index,
                                    type(productItem) == NewItem
                                ))
            unMatchedLine = False
            for relevantIndex, relevantPart in enumerate(self.relevantParts):
                if len(self.matching[lineIndex][relevantIndex]) == 0:
                    unMatchedLine = True
            # Either the whole line is matched or un matched
            if unMatchedLine:
                for relevantIndex, relevantPart in enumerate(self.relevantParts):
                    self.matching[lineIndex][relevantIndex] = []
            # Dont keep options that do not fall within a certain margin
            # from the description
            assert self.descriptionIndex is not None
            for relevantIndex, relevantPart in enumerate(self.relevantParts):
                filteredAssignments = []
                for ass in self.matching[lineIndex][relevantIndex]:
                    for descAss in self.matching[lineIndex][self.descriptionIndex]:
                        if abs(ass.getY() - descAss.getY()) < MAX_LINE_Y_DIFF:
                            filteredAssignments.append(ass)
                            break
                self.matching[lineIndex][relevantIndex] = filteredAssignments


class CellAssignment:
    """ This represents a single assignment for a line x column """

    def __init__(self, score, xL, xR, yT, yB, value, page_index, newItem):
        self.score = score
        self.xL = xL
        self.xR = xR
        self.yT = yT
        self.yB = yB
        self.value = value
        self.page_index = page_index
        self.newItem = newItem

    def updateNumericScore(self, matchedValue, absolute=False):
        self.score = getNumericScore(float(self.value), matchedValue, absolute)

    def getY(self):
        return (self.yB + self.yT) / 2.

    def getX(self, options):
        justify = options['justify']
        if justify == LEFT:
            return self.xL
        elif justify == RIGHT:
            return self.xR
        else:
            return (self.xL + self.xR) / 2.

    def __str__(self):
        return '%s, %f, {%f, %f} @%d' % (
            self.value.encode('utf-8'), self.score, self.xL, self.getY(),
            self.page_index)


def emptyLight(assignment):
    lightAssignment = []
    for lineIndex, _ in enumerate(assignment.matching):
        lightAssignment.append([])
        for relevantPart, _ in enumerate(assignment.matching[lineIndex]):
            lightAssignment[lineIndex].append(-1)
    return lightAssignment
