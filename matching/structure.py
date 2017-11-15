from matching.debug import getRelevantPart
from utils.items import NewItem
from utils.util import get_price_values

import json


class StructureLine(object):
    def __init__(self):
        pass


class Structure(object):

    def __init__(self, assignment):
        self.assignment = assignment

    def get_json(self):
        a = self.assignment
        m = a.matching
        lines = []
        descriptionIndex = a.descriptionIndex
        quantityIndex = a.quantityIndex
        priceIndex = a.priceIndex
        valuePart = a.relevantParts[priceIndex]

        for lineIndex, productItem in enumerate(a.productItems):
            matchingDescription = m[lineIndex][descriptionIndex]
            matchingQuantity = m[lineIndex][quantityIndex]
            matchingPrice = m[lineIndex][priceIndex]

            if not len(matchingDescription):
                continue

            quantity = float(matchingQuantity[0].value)
            description = matchingDescription[0].value
            price_value = float(matchingPrice[0].value)

            if not quantity:
                continue

            price, unit_price, price_pre_gst, unit_price_pre_gst = get_price_values(
                price_value, valuePart, quantity, productItem.gstPercent)
            lines.append({
                'description': description,
                'quantity': quantity,
                'price': price,
                'y': matchingDescription[0].getY()
            })
        lines = sorted(lines, key=lambda item: item['y'])
        for line in lines:
            del line['y']
        return lines
