import copy
from cost import computeCost, computeLightCost
from price import isValidPriceMatching, computePrice
from constants import *
from flags import DEBUG, INCLUDE_EMPTY, DETECT_NEW_ITEMS, MAX_DURATION
from exceptions import MaxDurationReached
from assignment import emptyLight, Assignment
from joiner import merge
from utils.files import Word
from utils.items import NewItem
from heapq import heappush, heappop
from debug import printAssignment
import time
from termcolor import colored


def optimizeMatchingForParts(productItems,
                             words,
                             relevantParts,
                             includeEmpty=False,
                             mergeCells=True,
                             options=None,
                             preAssignment=None):
    startTime = time.time()
    assignment = Assignment(productItems, relevantParts, words)
    assignment.build(preAssignment=preAssignment)
    if mergeCells:
        merge(assignment)
    if DEBUG > 1:
        printAssignment(assignment)
    assignments = []
    lightAssignment = emptyLight(assignment)
    if options:
        heappush(assignments, (0, [lightAssignment, options]))
    else:
        for option in [LEFT, MIDDLE, RIGHT]:
            options = {'justify': option}
            heappush(assignments, (0, [lightAssignment, options]))
    bestCost = INFINITE_COST
    bestLightAssignment = None
    bestOptions = None
    numRounds = 0
    copyTime = 0
    computeTime = 0
    initTime = time.time() - startTime
    orderedIndexes = []
    # Order in such a way that we start putting together the items that have the
    # fewest options first.
    for lineIndex, _ in enumerate(productItems):
        for relevantIndex, _ in enumerate(relevantParts):
            orderedIndexes.append(
                (len(assignment.matching[lineIndex][relevantIndex]),
                 [lineIndex, relevantIndex]))
    def indexComparator(key1, key2):
        len1, (line1, col1) = key1
        len2, (line2, col2) = key2
        k1 =  line1 * len(relevantParts) + col1
        k2 =  line2 * len(relevantParts) + col2
        if len1 < 2 and len2 >= 2:
            return -1
        if len2 < 2 and len1 >= 2:
            return 1
        if k1 < k2:
            return -1
        else:
            return 1
    orderedIndexes = sorted(orderedIndexes, cmp=indexComparator)
    while(len(assignments) > 0):
        if time.time() - startTime > MAX_DURATION:
            print 'Performance:{},{},{},{}'.format(
                numRounds, initTime, copyTime, computeTime)
            raise MaxDurationReached()
        numRounds += 1
        currentCost, (currentLightAssignment, options) = heappop(assignments)
        if currentCost > bestCost:
            continue
        incomplete = False
        for _, (lineIndex, relevantIndex) in orderedIndexes:
            if (len(assignment.matching[lineIndex][relevantIndex]) > 0 and
                currentLightAssignment[lineIndex][relevantIndex] == -1 and
                not incomplete):
                indexOptions = range(len(assignment.matching[lineIndex][relevantIndex]))
                if includeEmpty:
                    indexOptions.append(EMPTY)
                for index in indexOptions:
                    start = time.time()
                    newLightAssignment = copy.deepcopy(currentLightAssignment)
                    copyTime += (time.time() - start)
                    start = time.time()
                    newLightAssignment[lineIndex][relevantIndex] = index
                    newPartialCost = computeLightCost(assignment,
                                                      currentCost,
                                                      newLightAssignment,
                                                      lineIndex,
                                                      relevantIndex,
                                                      options,
                                                      debug=(DEBUG > 2))
                    assert newPartialCost >= -1E-6, \
                        'Cost cannot be negative: round %d - ass %s @ %f' % (
                            numRounds, newLightAssignment, newPartialCost)
                    newCost = newPartialCost
                    heappush(assignments, (newCost, (newLightAssignment, options)))
                    computeTime += (time.time() - start)
                incomplete = True
        if not incomplete and currentCost < bestCost:
            #print 'Best so far {} - {}'.format(currentCost, currentLightAssignment)
            bestCost = currentCost
            bestLightAssignment = currentLightAssignment
            bestOptions = options
    if DEBUG > 0:
        print 'Best {} - {}'.format(bestCost, bestLightAssignment)
        print 'Performance:{},{},{},{}'.format(
            numRounds, initTime, copyTime, computeTime)
    bestAssignment = Assignment(productItems, relevantParts, words)
    if bestLightAssignment:
        bestAssignment.buildFromLight(bestLightAssignment, assignment)
    return bestCost, bestOptions, bestAssignment


def addNewItems(cost, preAssignment, options):
    productItems = copy.deepcopy(preAssignment.productItems)
    relevantParts = preAssignment.relevantParts
    words = preAssignment.words
    productItems.append(NewItem())
    optCost, options, assignment = optimizeMatchingForParts(
        productItems,
        words,
        relevantParts,
        includeEmpty=INCLUDE_EMPTY,
        options=options,
        preAssignment=preAssignment)
    return optCost, assignment


def optimizeMatching(words, productItems):

    bestCost = INFINITE_COST
    bestMatchingPriceCount = 0
    optCost, optOptions, preAssignment = optimizeMatchingForParts(
        productItems, words, [DESCRIPTION], includeEmpty=True)
    for relevantParts in (
            [DESCRIPTION, QUANTITY, TOTAL_VALUE],
            [DESCRIPTION, QUANTITY, VALUE],
            [DESCRIPTION, QUANTITY, TOTAL_UNIT_VALUE],
            [DESCRIPTION, QUANTITY, UNIT_VALUE]):
        try:
            optCost, options, assignment = optimizeMatchingForParts(
                productItems,
                words,
                relevantParts,
                includeEmpty=INCLUDE_EMPTY,
                options=optOptions,
                preAssignment=preAssignment)
            if optCost == INFINITE_COST:
                continue
            cost = computeCost(assignment, options, debug=(DEBUG>1))
        except MaxDurationReached:
            continue

        while DETECT_NEW_ITEMS:
            newCost, newAssignment = addNewItems(cost, assignment, options)
            # The reasoning behind this number is the following
            # We assume the cost was k1 + n * n * delta = K
            # And with the addition of the new items it becomes K + 2 * n * delta
            # The increase is therefore 2 / n in the worst case where k1 = 0
            # We consider the worst increase to be double that amount
            if newCost > cost * (1 + 4. / len(assignment.productItems)):
                break
            else:
                cost = newCost
                assignment = newAssignment

        totalAllItemsPrice, allItemsPrice = computePrice(assignment)
        #if abs(cost - optCost) > 1E-6:
        #    print colored('Cost{} != OptCost{}'.format(cost, optCost), 'red')
        matchingPriceCount = 0
        if isValidPriceMatching(allItemsPrice, words):
            matchingPriceCount += 1
        if isValidPriceMatching(totalAllItemsPrice, words):
            matchingPriceCount += 1
        if (cost < bestCost and matchingPriceCount == bestMatchingPriceCount or
            matchingPriceCount > bestMatchingPriceCount):
            bestAssignment = assignment
            bestCost = cost
            bestMatchingPriceCount = matchingPriceCount
    if bestCost == INFINITE_COST:
        raise MaxDurationReached

    newCost = bestCost
    newAssignment = bestAssignment
    if DEBUG > 1:
        printAssignment(bestAssignment)
    return bestCost, bestAssignment
