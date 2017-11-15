#!/usr/bin/python
import swalign
from tabulate import tabulate
import numpy as np
import os.path
from termcolor import colored

from utils.loader import loadData
from utils.files import XMLFile
from utils.util import getFloat
from table.segmenter import segment_and_label_from_raw_ocr


textFormat = 'data/processed/B/{counter}{className}-p1.txt'
xmlFormat = 'data/processed/B/{counter}{className}-p1.xml'
groundTruth = 'data/original/B.csv'
offset = 1
classes = ('A',)
counters = range(1, 76)
# Latest out of 75
# Description: 57
# Description + Total price: 57
# Description + Price: 53
# Description + Quantity + Total price: 53
# All Fields: 51
# counters = [
#    1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 19, 20, 21, 22, 23, 25,
#    28, 29, 30, 32, 34, 35, 36, 38, 39, 40, 41, 42, 44, 47, 48, 49, 50,
#    51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68,
#    69, 70, 71, 72, 73, 74, 75,
# ]
# Expected issue with line joining in 13, 59, 25

textFormat = 'data/processed/C/{className}-{counter}-p1.txt'
xmlFormat = 'data/processed/C/{className}-{counter}-p1.xml'
groundTruth = 'data/original/C.csv'
offset = 0
classes = ('scan',)
counters = range(0, 114)
# Latest out of 113
# Description: 90
# Description + Total price: 76
# Description + Price: 63
# Description + Quantity + Total price: 55
# All Fields: 57
# List of errors:
# - Quantity on the ordered quantity column: 45
# - 26,56,106
# - No Avail in quantity column:40,46
# - Missing quantity in quantity column:32,49,52,58,59,60,62,63,65,66,67,70,73,75,77,78
# - Missing quantity column:81,86
# - Missing price in price column:27,104,105,109,110,111,113
# - Price / Quantity flipped:13
#counters = [
#   0, 1, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 21, 22, 25, 26, 27,
#   28, 29, 30, 31, 32, 33, 34, 35, 36, 38, 39, 40, 41, 42, 44, 45, 46,
#   47, 48, 49, 50, 51, 52, 54, 55, 56, 58, 59, 60, 61, 62, 63, 64, 65,
#   66, 67, 68, 69, 70, 71, 72, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83,
#   84, 85, 86, 87, 88, 89, 90, 91, 94, 95, 97, 104, 106, 107, 108, 109,
#   112, 113
#]
## cluster issue: 43, 111
## line grouping issue: 73
## unmatched numbers: 99

ocrTextFiles = [
    textFormat.format(counter=counter, className=className)
    for className in classes
    for counter in counters
]
ocrXMLFiles = [
    xmlFormat.format(counter=counter, className=className)
    for className in classes
    for counter in counters
]
originalInvoices, invoices = loadData(groundTruth)

scoring = swalign.NucleotideScoringMatrix(2, -1)
sw = swalign.LocalAlignment(scoring)

results = [0, 0, 0, 0, 0, 0]
DESCRIPTION_MATCH = 0
DESCRIPTION_TOTAL_PRICE_MATCH = 1
DESCRIPTION_PRICE_MATCH = 2
DESCRIPTION_QUANTITY_TOTAL_PRICE_MATCH = 3
ALL_FIELDS_MATCH = 4
TOTAL = 5

for fileIndex, textFile in enumerate(ocrTextFiles):
    if not os.path.exists(textFile):
        continue
    f = open(textFile)
    i = 0
    j = 0
    xmlFile = XMLFile(ocrXMLFiles[fileIndex])
    xmlFile.parseWithVariants(split=True)
    counter = counters[fileIndex % len(counters)] - offset
    classIndex = fileIndex // len(counters)
    invoice = invoices[counter]
    lines = []
    for line in f.readlines():
        if line.strip():
            lines.append(line.strip())
    table, headers = segment_and_label_from_raw_ocr(lines, xmlFile.words)
    results[TOTAL] += 1
    matches = [0, 0, 0, 0, 0]
    if table and table[0]:
        codeIndex = np.argmax([h == 'code' for h in headers])
        descriptionIndex = np.argmax([h == 'description' for h in headers])
        quantityIndex = np.argmax([h == 'quantity' for h in headers])
        totalPriceIndex = np.argmax([h == 'price4' or h == 'price3' for h in headers])
        priceIndex = np.argmax([h == 'price2' or h == 'price1' for h in headers])
        items = [
            [
                line[codeIndex],
                line[descriptionIndex],
                getFloat(line[quantityIndex]),
                getFloat(line[priceIndex]),
                getFloat(line[totalPriceIndex]),
            ] for line in table]
        for product in invoice:
            bestLine = None
            bestScore = 0
            for line in items:
                code, description, _, _, _ = line
                expectedDescription = product.description

                aln = sw.align(expectedDescription, description)
                globalScore = aln.score / float(2 * len(expectedDescription))

                expectedDescription = expectedDescription[aln.r_pos:aln.r_end]
                aln = sw.align(expectedDescription, description)
                localScore = (aln.score / float(2 * len(expectedDescription))
                               if expectedDescription else 0)
                if globalScore > 0.5 and localScore > 0.7:
                    if product.code and code == product.code:
                        bestScore = 1
                        bestLine = line
                    elif globalScore > bestScore:
                        bestScore = globalScore
                        bestLine = line

            if bestLine:
                code, description, quantity, price, totalPrice = bestLine
                expectedQuantity = product.quantity
                expectedTotalPrice = product.totalPrice
                expectedPrice = product.price
                expectedTotalUnitPrice = product.totalUnitPrice
                expectedUnitPrice = product.unitPrice
                matches[DESCRIPTION_MATCH] += 1
                if quantity and totalPrice:
                    price = totalPrice / quantity
                total_price_match = False
                price_match = False
                quantity_match = False
                if (abs(expectedTotalPrice - totalPrice) < 1
                    or
                    abs(expectedPrice - totalPrice) < 1):
                    total_price_match = True
                if (abs(expectedTotalUnitPrice - price) < 1
                    or
                    abs(expectedUnitPrice - price) < 1):
                    price_match = True
                if (abs(expectedQuantity - quantity) < 0.01):
                    quantity_match = True
                matches[DESCRIPTION_TOTAL_PRICE_MATCH] += total_price_match
                matches[DESCRIPTION_PRICE_MATCH] += price_match
                matches[DESCRIPTION_QUANTITY_TOTAL_PRICE_MATCH] += (
                    quantity_match and total_price_match)
                matches[ALL_FIELDS_MATCH] += (
                    price_match and quantity_match)
    for i in range(TOTAL):
        results[i] += matches[i] == len(invoice)
    if matches[DESCRIPTION_MATCH] < len(invoice):
        print colored(textFile, 'red')
    elif matches[ALL_FIELDS_MATCH] < len(invoice):
        print colored(textFile, 'yellow')
    else:
        print colored(textFile, 'green')

    if (matches[DESCRIPTION_MATCH] == len(invoice) and
        matches[ALL_FIELDS_MATCH] < len(invoice)):
        print tabulate(table, headers)

print results
