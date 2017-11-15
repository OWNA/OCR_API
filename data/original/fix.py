import os
import csv


def fixGst(filename, output_filename, unchanged_prices=True):
    f = open(filename)
    fileReader = csv.DictReader(f)
    writer = csv.DictWriter(open(output_filename, 'w'),
                            fieldnames=fileReader.fieldnames,
                            lineterminator='\n')
    has_changes = False
    writer.writeheader()
    for line in fileReader:
        gstPercent = float(line['gstPercent'])
        if gstPercent == 0.1:
            gstPercent = 10
        line['gstPercent']  = gstPercent

        fileIndex = line['fileIndex']
        description = line['description']

        unitPrice = float(line['unitPrice'])
        totalUnitPrice = float(line['totalUnitPrice'])
        price = float(line['price'])
        totalPrice = float(line['totalPrice'])
        quantity = float(line['quantity'])

        orderedUnitPrice = float(line['orderedUnitPrice'])
        orderedTotalUnitPrice = float(line['orderedTotalUnitPrice'])
        orderedPrice = float(line['orderedPrice'])
        orderedTotalPrice = float(line['orderedTotalPrice'])
        orderedQuantity = float(line['orderedQuantity'])

        def assertE(v1, v2, r=2):
            assert (round(v1, r) == round(v2, r) or
                    round(v1, r + 1) == round(v2, r + 1)), (
                        fileIndex, description, v1, v2)

        if gstPercent > 0:
            assert gstPercent == 10
            if (price == totalPrice
                or
                unitPrice == totalUnitPrice
                or
                orderedUnitPrice == orderedTotalUnitPrice
                or
                orderedPrice == orderedTotalPrice):
                assertE(price, totalPrice)
                assertE(unitPrice, totalUnitPrice)
                assertE(orderedUnitPrice, orderedTotalUnitPrice)
                assertE(orderedPrice, orderedTotalPrice)
                line['price'] = round(totalPrice / 1.1, 4)
                line['unitPrice'] = round(totalUnitPrice / 1.1, 4)
                line['orderedUnitPrice'] = round(orderedTotalUnitPrice / 1.1, 4)
                line['orderedPrice'] = round(orderedTotalPrice / 1.1, 4)
                has_changes = True
                print line
            else:
                assertE(totalPrice / 1.1, price)
                assertE(totalUnitPrice / 1.1, unitPrice)
                assertE(orderedTotalUnitPrice / 1.1, orderedUnitPrice)
                assertE(orderedTotalPrice / 1.1, orderedPrice)
        else:
            assertE(price, totalPrice)
            assertE(unitPrice, totalUnitPrice)
            assertE(orderedUnitPrice, orderedTotalUnitPrice)
            assertE(orderedPrice, orderedTotalPrice)
        if round(orderedUnitPrice * orderedQuantity, 2) != round(orderedPrice, 2):
            orderedPrice = orderedUnitPrice * orderedQuantity
            line['orderedPrice'] = orderedPrice
            has_changes = True
            print line
        if round(orderedTotalUnitPrice * orderedQuantity, 2) != round(orderedTotalPrice, 2):
            orderedTotalPrice = orderedTotalUnitPrice * orderedQuantity
            line['orderedTotalPrice'] = orderedTotalPrice
            has_changes = True
            print line
        assertE(orderedUnitPrice * orderedQuantity, orderedPrice)
        assertE(unitPrice * quantity, price)
        assertE(orderedTotalUnitPrice * orderedQuantity, orderedTotalPrice)
        assertE(totalUnitPrice * quantity, totalPrice)
        if unchanged_prices:
            assertE(orderedUnitPrice, unitPrice)
            assertE(orderedTotalUnitPrice, totalUnitPrice)
        writer.writerow(line)
    if not has_changes:
        os.remove(output_filename)

fixGst('data/original/C.csv', 'data/original/C-fixed.csv', True)
fixGst('data/original/B.csv', 'data/original/B-fixed.csv', False)
