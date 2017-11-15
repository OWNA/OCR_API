import csv

originalItemsFile = 'experiments/m3/abbyy/original.csv'

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

with open(originalItemsFile) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        code = row['code']
        description = row['description']
        fileIndex = int(row['file_index'])
        orderedQuantity = float(row['ordered_quantity'] or 0)
        quantity = float(row['quantity'] or 0)
        unitPrice = float(row['unit_price'] or 0)
        totalUnitPrice = float(row['total_unit_price'] or 0)
        price = float(row['price'] or 0)
        totalPrice = float(row['total_price'] or 0)
        if not totalPrice and quantity:
            orderedQuantity = quantity
            quantity = 0
        # Complete totalUnitPrice
        if not unitPrice and not totalUnitPrice:
            assert quantity and totalPrice
            totalUnitPrice = totalPrice / quantity
        assert unitPrice or totalUnitPrice, row
        assert not (unitPrice and totalUnitPrice), row
        assert (quantity and totalPrice) or (not quantity and not totalPrice)
        # Complete unit price and price
        if unitPrice:
            if price:
                assert abs(price - quantity * unitPrice) < 0.1, row
            else:
                price = unitPrice * quantity
        elif totalUnitPrice:
            if price:
                assert quantity, row
                unitPrice = price / quantity
            else:
                # There is neither price not unitPrice
                unitPrice = totalUnitPrice
        # Complete totalUnitPrice
        gstPercent = 0
        if abs(totalPrice - quantity * unitPrice) < 0.1:
            # Assume no gst
            totalUnitPrice = unitPrice
        else:
            gstPercent = .1
            totalUnitPrice = unitPrice * 1.1
        assert abs(totalPrice - quantity * totalUnitPrice) < 0.1, (
            row, totalPrice, quantity, totalUnitPrice)
        if not orderedQuantity:
            orderedQuantity = quantity
        printLine([
            # Stable values
            code,
            description,
            fileIndex,
            gstPercent,
            # Values in the order
            orderedQuantity,
            unitPrice,
            totalUnitPrice,
            unitPrice * orderedQuantity,
            totalUnitPrice * orderedQuantity,
            # Values in the invoice
            quantity,
            unitPrice,
            totalUnitPrice,
            price,
            totalPrice
        ])
