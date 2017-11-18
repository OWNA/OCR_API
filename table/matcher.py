import json
import numpy as np

from scipy.stats import linregress

from matching.constants import *
from table.line import TableLine, remove_outliers, contain_header_words
from table.labeller import MetaInfo, label_columns
from cluster import bestKMeansByK
from tabulate import tabulate


def segment_with_matching(words, assignment):
    class Page():
        def __init__(self):
            self.line_indices = []
            self.coordinates = []
            self.word_contents = []
            self.descriptions = []
            self.quantities = []
            self.price_values = []
            self.max_num_columns = 0
            self.labels = []

    pages = {}
    a = assignment
    m = a.matching
    description_index = a.descriptionIndex
    quantity_index = a.quantityIndex
    price_index = a.priceIndex
    value_part = a.relevantParts[price_index]
    for product_index, product_item in enumerate(a.productItems):
        num_columns = 0
        matching_description = m[product_index][description_index]
        matching_quantity = m[product_index][quantity_index]
        matching_price = m[product_index][price_index]
        if not len(matching_description):
            continue
        quantity = matching_quantity[0]
        description = matching_description[0]
        price_value = matching_price[0]
        line = []
        for item in (quantity, description, price_value):
            line.append([item.xL, item.yT])
            line.append([item.xR, item.yB])
        reg = linregress(np.array(line))
        slope = reg.slope
        intercept = reg.intercept
        page_index = description.page_index
        if not page_index in pages:
            pages[page_index] = Page()
        page = pages[page_index]
        if value_part == VALUE:
            value_type = 'price3'
        elif value_part == TOTAL_VALUE:
            value_type = 'price4'
        elif value_part == TOTAL_UNIT_VALUE:
            value_type = 'price2'
        elif value_part == UNIT_VALUE:
            value_type = 'price1'
        page.labels = ['description', 'quantity', value_type]
        coordinates = page.coordinates
        word_contents = page.word_contents
        line_indices = page.line_indices
        page.descriptions.append(description)
        page.price_values.append(price_value)
        page.quantities.append(quantity)
        line_index = len(page.descriptions)
        for w in words:
            if w.page_index != page_index:
                continue
            box = w.box
            x, y = box.center
            distance = (np.abs(y - slope * x - intercept) /
                        np.sqrt(1 + slope * slope))
            for item in [description, quantity, price_value]:
                if ((box.l >= item.xL and box.l <= item.xR) or
                    (item.xL >= box.l and item.xL <= box.r)):
                    distance = 100000
            if distance < 10:
                num_columns += 1
                line_indices.append(line_index - 1)
                coordinates.append(x)
                word_contents.append(w.content)
        page.max_num_columns = max(page.max_num_columns, num_columns)
    tables = []
    for page in pages.values():
        coordinates = page.coordinates
        max_num_columns = page.max_num_columns
        descriptions = page.descriptions
        quantities = page.quantities
        price_values = page.price_values
        word_contents = page.word_contents
        line_indices = page.line_indices
        x_clusters, x_centers = bestKMeansByK(coordinates, max_num_columns + 1)
        items_center = [
          np.mean([(d.xL + d.xR) / 2 for d in items])
          for items in [descriptions, quantities, price_values]
        ]
        x_centers = [v[0] for v in x_centers]
        x_centers = items_center + x_centers
        sort_index = np.argsort(np.argsort(x_centers))
        num_columns = len(x_centers)
        lines = []
        labels = [''] * num_columns
        for label_index, label in enumerate(page.labels):
            labels[sort_index[label_index]] = label
        for description, quantity, price_value in zip(
          descriptions, quantities, price_values):
            lines.append([])
            lines[-1] = [''] * num_columns
            lines[-1][sort_index[0]] = description.value
            lines[-1][sort_index[1]] = quantity.value
            lines[-1][sort_index[2]] = price_value.value
        for j, i, word_content, coordinate in zip(
            x_clusters, line_indices, word_contents, coordinates):
            lines[i][sort_index[j + 3]] = word_content
        tables.append([lines, labels])
    return tables


def segment_and_label_with_matching(words, assignment):
    tables = segment_with_matching(words, assignment)
    lines_and_labels = []
    for lines, matcher_labels in tables:
        labels = label_columns(lines)
        for label_index, matcher_label in enumerate(matcher_labels):
            if len(matcher_label):
                labels[label_index] = matcher_label
        lines_and_labels.append([lines, labels])
    return lines_and_labels
