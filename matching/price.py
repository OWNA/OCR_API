from constants import *
from line import LineComparator
from exceptions import TooManyPriceParts


def isValidPriceMatching(price, words):
    if not price:
        return False
    lineComparator = LineComparator()
    partMatches = []
    for word in words:
        partMatches += lineComparator.alignNumericPart(
            word.content, price, VALUE)
    partMatches = sorted(partMatches, key=lambda m: -m.score)
    matchingValue = float(partMatches[0].matchingValue)
    return abs(price - matchingValue) < 1


def computePrice(assignment):
    relevantPriceIndex = None
    relevantQuantityIndex = None
    descriptionIndex = None
    for relevantIndex, part in enumerate(assignment.relevantParts):
        if part == QUANTITY:
            relevantQuantityIndex = relevantIndex
        if part == DESCRIPTION:
            descriptionIndex = relevantIndex
        if (part == VALUE or part == TOTAL_VALUE or part == UNIT_VALUE
            or part == TOTAL_UNIT_VALUE):
            if relevantPriceIndex:
                raise TooManyPriceParts
            relevantPriceIndex = relevantIndex
    if not relevantPriceIndex or not relevantQuantityIndex:
        return 0, 0
    totalAllItemsPrice = 0
    allItemsPrice = 0
    relevantPart = assignment.relevantParts[relevantPriceIndex]
    for lineIndex, productItem in enumerate(assignment.productItems):
        description = assignment.matching[lineIndex][descriptionIndex]
        price = assignment.matching[lineIndex][relevantPriceIndex]
        quantity = assignment.matching[lineIndex][relevantQuantityIndex]
        if not description:
            continue
        if price and quantity:
            price = float(price[0].value)
            quantity = float(quantity[0].value)
            if relevantPart == VALUE:
                allItemsPrice += price
                totalAllItemsPrice += price * (1 + productItem.gstPercent / 100.)
            elif relevantPart == TOTAL_VALUE:
                totalAllItemsPrice += price
                allItemsPrice += price / (1 + productItem.gstPercent / 100.)
            elif relevantPart == TOTAL_UNIT_VALUE:
                totalAllItemsPrice += price * quantity
                allItemsPrice += price * quantity / (1 + productItem.gstPercent / 100.)
            elif relevantPart == UNIT_VALUE:
                allItemsPrice += price * quantity
                totalAllItemsPrice += price * quantity * (
                    1 + productItem.gstPercent / 100.)
            else:
                raise NotImplemented('Unsupported relevant part')
        else:
            return 0, 0
    return totalAllItemsPrice, allItemsPrice
