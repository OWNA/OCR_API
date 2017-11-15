from table.extractor import extractTableStructure
from matching.optimizer import optimizeMatching
from matching.constants import *
from matching.exceptions import MaxDurationReached
import swalign

from termcolor import colored


def getPart(productItem, valuePart):
    if valuePart == VALUE:
        return productItem.price
    elif valuePart == UNIT_VALUE:
        return productItem.unitPrice
    elif valuePart == TOTAL_UNIT_VALUE:
        return productItem.totalUnitPrice
    elif valuePart == TOTAL_VALUE:
        return productItem.totalPrice
    else:
        raise NotImplementedError()


def compare(bestAssignment, originalItems, generatedItems,
            counter, className, verbose=True):
    expectedNotFound = 0
    unexpectedNotFound = 0
    unexpectedFound = 0
    unexpectedPriceChange = 0
    unexpectedPriceNoChange = 0
    unexpectedPriceChangeOK = 0
    unexpectedPriceNoChangeOK = 0
    expectedQuantityChanged = 0
    unexpectedQuantityChanged = 0
    expectedNewItems = 0
    unexpectedNewItems = 0
    matching = bestAssignment.matching
    descriptionIndex = bestAssignment.descriptionIndex
    quantityIndex = bestAssignment.quantityIndex
    priceIndex = bestAssignment.priceIndex
    valuePart = bestAssignment.relevantParts[priceIndex]

    originalKeys = set([p.key for p in originalItems])
    generatedKeys = set([p.key for p in generatedItems])

    generatedKeysDict = dict(zip([p.key for p in generatedItems], generatedItems))

    missingKeys = originalKeys - generatedKeys
    newKeys = generatedKeys - originalKeys
    commonKeys = generatedKeys.intersection(originalKeys)

    foundKeys = set([])
    for matchingItem in matching[len(originalItems):]:
        matchingDescription = matchingItem[descriptionIndex]
        matchingQuantity = matchingItem[quantityIndex]
        matchingPrice = matchingItem[priceIndex]
        quantity = float(matchingQuantity[0].value)
        description = matchingDescription[0].value
        price = float(matchingPrice[0].value)

        matchedItem = None
        for newKey in newKeys:
            generatedItem = generatedKeysDict[newKey]
            realQuantity = generatedItem.quantity
            realValue = getPart(generatedItem, valuePart)
            scoring = swalign.NucleotideScoringMatrix(2, -1)
            sw = swalign.LocalAlignment(scoring)
            aln = sw.align(description, generatedItem.description)
            description = description[aln.r_pos:aln.r_end]
            aln = sw.align(description, generatedItem.description)
            score = aln.score / (2.0 * len(generatedItem.description))
            if (abs(price - realValue) < 1 and
                abs(quantity - realQuantity) < 1 and
                score > 0.3
            ):
                matchedItem = generatedItem
            else:
                print (price, realValue,
                       quantity, realQuantity,
                       description, generatedItem.description,
                       score)

            if matchedItem:
                foundKeys.add(matchedItem.key)
                expectedNewItems += 1
            else:
                unexpectedNewItems += 1
    if newKeys - foundKeys:
        unexpectedNotFound += len(newKeys)

    for lineIndex, productItem in enumerate(originalItems):
        matchingItem = matching[lineIndex]
        matchingDescription = matchingItem[descriptionIndex]
        matchingQuantity = matchingItem[quantityIndex]
        matchingPrice = matchingItem[priceIndex]
        if (matchingDescription is None or not len(matchingDescription) or
            matchingPrice is None or not len(matchingPrice) or
            matchingQuantity is None or not len(matchingQuantity)):
            if productItem.key in commonKeys:
                unexpectedNotFound += 1
            else:
                expectedNotFound += 1
        elif productItem.key in missingKeys:
            unexpectedFound += 1
            print ('{}{} - Unexpected Found'.format(
                counter,
                className,
                colored(productItem,
                        'red' if matchedOther else 'red')))
        else:
            generatedItem = generatedKeysDict[productItem.key]
            quantity = float(matchingQuantity[0].value)
            description = matchingDescription[0].value
            price = float(matchingPrice[0].value)

            expectedValue = getPart(productItem, valuePart)
            realValue = getPart(generatedItem, valuePart)

            expectedQuantity = productItem.quantity
            realQuantity = generatedItem.quantity
            matchedOther = False
            otherValues = [
                generatedItem.price,
                generatedItem.totalPrice,
                generatedItem.totalUnitPrice,
                generatedItem.unitPrice,
            ]
            for otherValue in otherValues:
                if abs(price - otherValue) < 1:
                    matchedOther = True
            if (abs(price - expectedValue) > 1 and
                abs(price - realValue) > 1):
                if verbose:
                    print ('{}{} - Unexpected Price changed from {} -> {} ' +
                           '[Real:{:.2f}] for {}').format(
                               counter,
                               className,
                               expectedValue,
                               price,
                               realValue,
                               colored(productItem,
                                       'green' if matchedOther else 'red')
                           )
                if matchedOther:
                    unexpectedPriceChangeOK += 1
                else:
                    unexpectedPriceChange += 1
            elif abs(price - realValue) > 1:
                if verbose:
                    print ('{}{} - Unexpected Price no-change from {} -> {} ' +
                           '[Real:{:.2f}] for {}').format(
                               counter,
                               className,
                               expectedValue,
                               price,
                               realValue,
                               colored(productItem,
                                       'green' if matchedOther else 'red')
                           )
                if matchedOther:
                    unexpectedPriceNoChangeOK += 1
                else:
                    unexpectedPriceNoChange += 1
            if (abs(quantity - expectedQuantity) > 0.01 * expectedQuantity):
                if abs(quantity - realQuantity) < 0.01 * realQuantity:
                    expectedQuantityChanged += 1
                else:
                    if verbose:
                        print ('{}{} - Unexpected qty changed from {} -> {} ' +
                               'for {}').format(
                                   counter,
                                   className,
                                   productItem.quantity,
                                   quantity,
                                   colored(productItem, 'red')
                               )
                    unexpectedQuantityChanged += 1
    return (expectedNotFound,
            expectedNewItems,
            unexpectedNotFound,
            unexpectedFound,
            unexpectedPriceChange,
            unexpectedPriceChangeOK,
            unexpectedPriceNoChange,
            unexpectedPriceNoChangeOK,
            unexpectedQuantityChanged,
            unexpectedNewItems)


def runOptimizer(words, originalItems, generatedItems, counter, className):
    failedToComplete = False
    totalSoftErrors = 0
    totalErrors = 0
    try:
        bestCost, bestAssignment = optimizeMatching(words, originalItems)
    except MaxDurationReached:
        print 'Failed to complete'
        failedToComplete = True
    else:
        results = compare(bestAssignment,
                          originalItems,
                          generatedItems, counter, className)
        (expectedNotFound,
         expectedNewItems,
         unexpectedNotFound,
         unexpectedFound,
         unexpectedPriceChange,
         unexpectedPriceChangeOK,
         unexpectedPriceNoChange,
         unexpectedPriceNoChangeOK,
         unexpectedQuantityChanged,
         unexpectedNewItems) = results
        print '%d, %d, %s, %s, %s, %d, %s, %d, %s, %s' % (
            results[0],
            results[1],
            colored(str(results[2]), 'red'),
            colored(str(results[3]), 'red'),
            colored(str(results[4]), 'red'),
            results[5],
            colored(str(results[6]), 'red'),
            results[7],
            colored(str(results[8]), 'red'),
            colored(str(results[9]), 'red')
        )
        totalSoftErrors += unexpectedPriceChangeOK + unexpectedPriceNoChangeOK
        totalErrors += (unexpectedPriceChange +
                        unexpectedPriceNoChange +
                        unexpectedNotFound +
                        unexpectedFound +
                        unexpectedQuantityChanged)
    return failedToComplete, totalSoftErrors, totalErrors


def extractTable(words, originalItems):
    return extractTableStructure(words, originalItems)
