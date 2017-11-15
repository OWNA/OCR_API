import csv
from items import Item

def loadData(filename):
    originalItems = []
    items = []
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            code = row['code']
            description = row['description']
            packSize = row['packSize']
            brand = row['brand']
            unitOfMeasure = row['unitOfMeasure']
            fileIndex = int(row['fileIndex'])
            while len(items) <= fileIndex:
                items.append([])
                originalItems.append([])

            orderedQuantity = float(row['orderedQuantity'])
            orderedUnitPrice = float(row['orderedUnitPrice'])
            orderedPrice = float(row['orderedPrice'])
            orderedTotalPrice = float(row['orderedTotalPrice'])
            gstPercent = orderedTotalPrice / orderedPrice * 100 - 100

            quantity = float(row['quantity'])
            unitPrice = float(row['unitPrice'])
            price = float(row['price'])
            totalPrice = float(row['totalPrice'])

            originalItem = Item(code, description,
                                brand, packSize, unitOfMeasure,
                                orderedUnitPrice, gstPercent,
                                shingle_length = 0)
            originalItem.quantity = orderedQuantity
            originalItem.price = orderedPrice
            originalItem.totalPrice = orderedTotalPrice
            originalItems[fileIndex].append(originalItem)

            item = Item(code, description,
                        brand, packSize, unitOfMeasure,
                        unitPrice, gstPercent,
                        shingle_length = 0)
            item.quantity = quantity
            item.price = price
            item.totalPrice = totalPrice
            items[fileIndex].append(item)
    return originalItems, items
