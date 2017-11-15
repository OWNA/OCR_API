#!/usr/bin/python

import os
import argparse
import random
from utils.items import Line, ItemsList


class LineMatcher(object):
    """ Matches the lines of a text OCR'd file with a set of
    possible line orders."""

    def __init__(self, itemsList):
        """
        Initialized the line matcher

        :type itemsList: ItemsList
        :param itemsList: the list of possibly matching lines

        """
        self.itemsList = itemsList

    def matchLinesOf(self, ocrTextFilename, shingle_length=3):
        """ Will match the lines of the ocr's file one by one with the
        list of possible line items. """
        matches = []
        with open(ocrTextFilename, 'r') as f:
            content = f.readlines()
            for text in content:
                matchedItem = None
                minDistance = float("inf")
                lastMinDistance = float("inf")
                line = Line(text.strip(), shingle_length=shingle_length)
                for item in self.itemsList.items:
                    distance = item.matchWithLine(line)
                    if distance < minDistance:
                        lastMinDistance = minDistance
                        minDistance = distance
                        matchedItem = item

                matches.append([line, matchedItem, minDistance, lastMinDistance])
        return matches
