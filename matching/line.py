#!/usr/bin/python

import math
import sys
import swalign
import re
from utils.items import Item, ItemsList, NewItem
from constants import *
from flags import ALTERNATIVE_CHARS


def getNumericScore(a, b, absolute=False):
    """
    Computes a score for matching two numeric values, with the following
    requirements:
     - Symmetric
     - Between 0 and 1
     - Equal to 1 for a == b
     - Quick decrease when |a - b| << 1
     - Slow decrease when |a - b| >> 1
    """
    if absolute:
        score = math.exp(- abs(a - b) / 10.)
    elif not a or not b:
        return 0
    else:
        score1 = math.exp(- 2.0 * abs(a - b) / b)
        score2 = math.exp(- 2.0 * abs(a - b) / a)
        score = min(score1, score2)
    return score


class ItemPartMatch(object):


    def __init__(self, reference, score, isNumeric, matchingValue, offset, end):
        """
        Initialized the result of an item part match

        :type reference: string
        :param reference: the reference part that was matched against the OCR'd line

        :type score: float
        :param score: the ratio of the alignment score to the maximum score

        """
        self.reference = reference
        self.score = score
        self.isNumeric = isNumeric
        self.matchingValue = matchingValue
        self.offset = offset
        self.end = end

    def __str__(self):
        return '{} to {}: {} [{},{}]'.format(
            self.reference, self.matchingValue, self.score,
            self.offset, self.end)


def isPositiveFloat(v):
    try:
        return float(v) > 0
    except:
        return False
    else:
        return True


class LineComparator(object):


    def __init__(self, match=2, mismatch=-1):
        """
        Initialized the line comparator

        :type match: int
        :param match: the weight of match in the Smith-Waterman alignment

        :type mismatch: int
        :param match: the weight of mismatch in the Smith-Waterman alignment

        """
        scoring = swalign.NucleotideScoringMatrix(match, mismatch)
        self.sw = swalign.LocalAlignment(scoring)


    def alignNumericPart(self, content, part, relevantPart):
        content = content.lower()
        if ALTERNATIVE_CHARS:
            for char, target in (['o', 0], ['q', 0],
                                 ['[|]', 1], ['i', 1],
                                 ['l', 1], ['e', 1],
                                 ['-', '.']):
                # This has caused issue with http://ocr.owna.io/images/336/
                #['s', 5]):
                content = re.sub(r'(?<![a-zA-Z])' + char + '(?![a-zA-Z])',
                                 str(target), content)
        matchingValues = re.findall(r'[0-9.]+', content)
        offsets = [m.start() for m in re.finditer(r'[0-9.]+', content)]
        partMatches = []
        for matchingValue, offset in zip(matchingValues, offsets):
            if not(isPositiveFloat(matchingValue)):
                continue
            if part:
                score = getNumericScore(float(matchingValue), float(part),
                                        relevantPart == QUANTITY)
            else:
                score = 1
            #score = max(1 - abs(float(matchingValue) - part)**2 / part, 0)
            end = offset + len(matchingValue)
            partMatches.append(ItemPartMatch(part, score,
                                             True, matchingValue,
                                             offset, end))
        return partMatches


    def alignNonNumericPart(self, content, part):
            aln = self.sw.align(part, content)
            if len(part) > 0:
                matchingValue = content[aln.q_pos:aln.q_end]
                score = aln.score / (2.0 * len(part))
                offset = aln.q_pos
                end = aln.q_end
                if score < 0.7 and False:
                    aln.dump()
            else:
                matchingValue = content
                offset = 0
                end = len(content) - 1
                score = 1
            return ItemPartMatch(part, score,
                                 False, matchingValue,
                                 offset, end)

    def align(self, productItem, word, relevantPart):
        """
        Aligns a textLine with its matching productLine

        :type productItem: lineMatcher.Item
        :param productItem: the product line object

        :type word: Word
        :param word: the word from the OCR output
        """
        if relevantPart == DESCRIPTION:
            isNumeric = False
        else:
            isNumeric = True
        if type(productItem) == NewItem:
            if isNumeric:
                return self.alignNumericPart(word.content, None, relevantPart)
            else:
                if not re.match('^[0-9.$\s]+$', word.content):
                    return [self.alignNonNumericPart(word.content, '')]
                return []
        code = productItem.code
        description = productItem.description
        brand = productItem.brand
        packSize = productItem.packSize
        quantity = productItem.quantity
        unitValue = float(productItem.unitPrice)
        value = unitValue * quantity
        totalUnitValue = float(productItem.totalUnitPrice)
        totalValue = totalUnitValue * quantity
        partMatches = []
        if relevantPart == DESCRIPTION:
            part = description
        elif relevantPart == VALUE:
            part = value
        elif relevantPart == QUANTITY:
            part = quantity
        elif relevantPart == CODE:
            isNumeric = False
            part = code
        elif relevantPart == TOTAL_VALUE:
            part = totalValue
        elif relevantPart == TOTAL_UNIT_VALUE:
            part = totalUnitValue
        elif relevantPart == UNIT_VALUE:
            part = unitValue
        else:
            raise NotImplemented('Usupported relevant part')
        matchingValue = None
        if isNumeric:
            return self.alignNumericPart(word.content, part, relevantPart)
        else:
            return [self.alignNonNumericPart(word.content, part)]

