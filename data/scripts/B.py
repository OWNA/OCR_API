#!/usr/bin/python


import matplotlib
import os
import random
import matplotlib.pyplot as plt
import json
import pickle
import numpy as np
from utils.items import *

generatorData = pickle.load(open('experiments/m2/generated/data/B.pickle', 'rb'))

itemsFile = 'experiments/m2/list/list.csv'
itemsList = ItemsList(itemsFile, shingle_length = 0)

def printLine(X):
    print ",".join([str(x) for x in X])

printLine([
    # Stable values
    'code',
    'description',
    'fileIndex',
    'gstPercent',
    # Values in the order
    'orderedQuantity',
    'orderedUnitPrice',
    'orderedTotalUnitPrice',
    'orderedPrice',
    'orderedTotalPrice',
    # Values in the invoice
    'quantity',
    'unitPrice',
    'totalUnitPrice',
    'price',
    'totalPrice'
])

incompleteInvoices = {1:8, 9:15, 15: 12, 31: 9, 41: 16, 45: 7, 51: 11, 53: 8,
                      56: 13, 59: 9, 66: 15, 71: 10, 75: 11}

for counter, data in enumerate(generatorData):
    generatedItems = data['items']
    originalItems = []
    itemCount = len(generatedItems)
    random.seed(counter)
    changedQuantityCount = int(random.choice([0.1, 0.2, 0.3, 0.5]) * itemCount)
    changedQuantitySample = random.sample(range(itemCount), changedQuantityCount)
    for itemIndex, item in enumerate(generatedItems):
        originalItem = itemsList.get(item.code)
        quantity = float(item.quantity)
        originalItem.quantity = quantity
        if itemIndex in changedQuantitySample:
            originalItem.quantity = quantity + 1
        originalItem.price = quantity * float(originalItem.unitPrice)
        originalItem.totalPrice = quantity * float(originalItem.totalUnitPrice)
        originalItems.append(originalItem)

    if (counter + 1) in incompleteInvoices:
        size = incompleteInvoices[counter + 1]
        generatedItems = generatedItems[0:size]
        originalItems = originalItems[0:size]

    for generatedItem, originalItem in zip(generatedItems, originalItems):
        printLine([
            # Stable values
            originalItem.code,
            originalItem.description,
            counter,
            originalItem.gstPercent,
            # Values in the order
            originalItem.quantity,
            originalItem.unitPrice,
            originalItem.totalUnitPrice,
            originalItem.price,
            originalItem.totalPrice,
            # Values in the invoice
            generatedItem.quantity,
            generatedItem.unitPrice,
            generatedItem.totalUnitPrice,
            generatedItem.price,
            generatedItem.totalPrice
        ])
