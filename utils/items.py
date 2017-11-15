from shingles import ShingledText
import csv
from termcolor import colored
import hashlib
import random

class Line(object):
    """ A line representation with cached shingles """

    def __init__(self, content, shingle_length=3):
        self.content = content
        self.shingle = ShingledText(content, shingle_length=shingle_length)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['shingle']
        return state

    def __str__(self):
        return self.content[:100]


class NewItem(object):
    """ A new item that was never ordered """

    def __init__(self):
        self.gstPercent = 0.

    def __str__(self):
        return 'New Item'


class Item(object):
    """ Possible Order line"""

    def __init__(self, code, description, brand, packSize,
                 unitOfMeasure, unitPrice, gstPercent,
                 shingle_length=3):
        self.code = code
        self.description = description
        self.key = hashlib.sha256(code + description).hexdigest()
        self.brand = brand
        self.packSize = packSize
        self.descriptionPackSize = description + ' ' + packSize
        self.unitOfMeasure = unitOfMeasure
        self.unitPrice = float(unitPrice)
        self.gstPercent = float(gstPercent if gstPercent else 0)
        self.totalUnitPrice = self.unitPrice * (1 + self.gstPercent / 100.)
        self.quantity = 0 # Filled from the order value else zero
        if shingle_length:
            self.shingle = ShingledText(
                ' '.join([
                    code, description, brand, packSize,
                    unitOfMeasure, unitPrice]),
                shingle_length=shingle_length)

    def __str__(self):
        if self.quantity:
            return '{}[{}] {}@{}'.format(
                self.code, self.description,
                colored(self.quantity, 'green'),
                colored(self.totalPrice, 'blue'))
        else:
            return '{}[{}] @{}'.format(
                self.code, self.description, self.totalUnitPrice)

    def __getstate__(self):
        state = self.__dict__.copy()
        if 'shingle' in state:
            del state['shingle']
        return state

    def matchWithLine(self, line, debug=False):
        return 1 - self.shingle.similarity(line.shingle, debug)


class OrderedItem(Item):

    def __init__(self, item_id, code, description,
                 brand, packSize, unitOfMeasure,
                 unitPrice, totalUnitPrice,
                 price, totalPrice,
                 quantity):
        self.code = code
        self.item_id = item_id
        self.description = description
        self.brand = brand
        self.packSize = packSize
        self.unitOfMeasure = unitOfMeasure
        self.unitPrice = float(unitPrice)
        self.totalUnitPrice = float(totalUnitPrice)
        self.price = float(price)
        self.totalPrice = float(totalPrice)
        self.gstPercent = (100 * (totalUnitPrice - unitPrice) / unitPrice
                           if unitPrice else 0)
        self.quantity = float(quantity)


class ItemsList(object):
    """ List of possible order lines """

    def __init__(self, filename, shingle_length=3):
        self.filename = filename
        self.items = []
        self.codes = {}
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                code = row['Code']
                unitPrice = row['Unit Price']
                if code and unitPrice:
                    description = row['Item Description']
                    brand = row['Brand']
                    packSize = row['Pack Size']
                    unitOfMeasure = row['Unit of Measure']
                    unitPrice = row['Unit Price']
                    gstPercent = row['GST Value']
                    item = Item(code,
                                description,
                                brand,
                                packSize,
                                unitOfMeasure,
                                unitPrice,
                                gstPercent,
                                shingle_length=shingle_length)
                    self.codes[code] = item
                    self.items.append(item)

    def __str__(self):
        return '\n'.join([str(item) for item in self.items])

    def sample(self, num_items=10):
        return random.sample(self.items, num_items)

    def size(self):
        return len(self.items)

    def get(self, code):
        return self.codes[code]
