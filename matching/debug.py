from constants import *
from utils.items import NewItem


def getRelevantPart(productItem, relevantPart):
    if relevantPart == DESCRIPTION:
        return productItem.description
    elif relevantPart == UNIT_VALUE:
        return productItem.unitPrice
    elif relevantPart == TOTAL_UNIT_VALUE:
        return productItem.totalUnitPrice
    elif relevantPart == TOTAL_VALUE:
        return productItem.totalUnitPrice * productItem.quantity
    elif relevantPart == VALUE:
        return productItem.unitPrice * productItem.quantity
    elif relevantPart == QUANTITY:
        return productItem.quantity
    else:
        raise NotImplemented('Unsupported relevant part')


def printAssignment(assignment):
    for lineIndex, productItem in enumerate(assignment.productItems):
        print productItem
        for relevantIndex, relevantPart in enumerate(assignment.relevantParts):
            if type(productItem) == NewItem:
                print '\t%s' % [
                    ass.value for ass in assignment.matching[lineIndex][relevantIndex]]
                continue
            print '\t%s %s' % (
                getRelevantPart(productItem, relevantPart),
                [ass.value for ass in assignment.matching[lineIndex][relevantIndex]])
