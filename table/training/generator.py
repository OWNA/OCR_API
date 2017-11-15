#!/usr/bin/python
import numpy as np
import os
import swalign
from tabulate import tabulate
import random
import fileinput
import json

from utils.files import XMLFile
from utils.util import getFloat
from utils.items import ItemsList
from utils.loader import loadData
from table.segmenter import segment_from_raw_ocr
from table.labeller import compute_features, MetaInfo
from table.pdf import segment_pdf

# Initialize PRNGs for reproducibility
np.random.seed(1234)
random.seed(1234)

scoring = swalign.NucleotideScoringMatrix(2, -1)
sw = swalign.LocalAlignment(scoring)

NAMES = [
    'description',
    'descriptionPackSize',
    'code', 'quantity',
    'gst',
    'price1', 'price2',
    'price3', 'price4'
]
TYPES = [
    'description',
    'description',
    'code', 'quantity',
    'gst',
    'price1', 'price2',
    'price3', 'price4'
]
LABELS = [
    'description',
    'code', 'quantity',
    'gst',
    'price1', 'price2',
    'price3', 'price4',
    'packSize', 'brand',
    'unitOfMeasure'
]
ATTRIBUTE_NAMES = [
    'description', 'descriptionPackSize',
    'code', 'quantity',
    'gst',
    'unitPrice', 'totalUnitPrice',
    'price', 'totalPrice'
]
HEADERS = [
    ['', 'Description'],
    ['', 'Description'],
    ['', 'Item'],
    ['', 'Quantity'],
    ['', 'Gst'],
    ['', 'Ex-Gst'],
    ['', 'Unit price',],
    ['', 'Price'],
    ['', 'Total',],
]


def process_files(textFormat, xmlFormat, groundTruth, offset, classes,
                  output_filename, counters):
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

    out_f = open(output_filename, 'w')
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
        table, meta_info = segment_from_raw_ocr(lines, xmlFile.words)
        features = get_features(textFile, table, meta_info)
        labels = np.zeros((len(LABELS), len(table[0])))
        for line in table:
            matching_product = None
            for product in invoice:
                if matching_product:
                    break
                for c_index, c in enumerate(line):
                    aln = sw.align(product.description, c)
                    score = aln.score / float(2 * len(product.description))
                    if score > 0.5:
                        matching_product = product
                        labels[0, c_index] += 1
                        break
            if matching_product:
                def compare_num(c, value, threshold):
                    return 1 if abs(getFloat(c) - value) < threshold else 0
                def compare_str(c, value):
                    if value:
                        value = str(value).replace(' ', '').lower()
                        c = c.replace(' ', '').lower()
                        if c == value:
                            return 1
                    return 0
                for c_index, c in enumerate(line):
                    if (abs(getFloat(c) * 10 - matching_product.unitPrice) < 0.01 or
                        getFloat(c, -1) == 0):
                        labels[3, c_index] += 1
                    mp = matching_product
                    labels[1, c_index] += compare_str(c, mp.code)
                    labels[2, c_index] += compare_num(c, mp.quantity, 0.01)
                    labels[2, c_index] += compare_num(c, mp.quantity, 0.5)
                    labels[4, c_index] += compare_num(c, mp.unitPrice, 0.01)
                    labels[4, c_index] += compare_num(c, mp.unitPrice, 0.5)
                    labels[5, c_index] += compare_num(c, mp.totalUnitPrice, 0.01)
                    labels[5, c_index] += compare_num(c, mp.totalUnitPrice, 0.5)
                    labels[6, c_index] += compare_num(c, mp.price, 0.01)
                    labels[6, c_index] += compare_num(c, mp.price, 0.5)
                    labels[7, c_index] += compare_num(c, mp.totalPrice, 0.01)
                    labels[7, c_index] += compare_num(c, mp.totalPrice, 0.5)
                    labels[8, c_index] += compare_str(c, mp.packSize)
                    labels[9, c_index] += compare_str(c, mp.brand)
                    labels[10, c_index] += compare_str(c, mp.unitOfMeasure)
        headers_scores = np.max(labels, axis=0)
        headers_indices = []
        for label, score in zip(labels.transpose(), headers_scores):
            headers_indices.append(max([k for k, v in enumerate(label) if v == score]))
        best_scores = {}
        for p, score in zip(headers_indices, headers_scores):
            if p in best_scores and best_scores[p] < score:
                best_scores[p] = score
            elif p not in best_scores:
                best_scores[p] = score
        K = np.max(labels[0,:])
        expected_headers = [
            LABELS[i] if headers_scores[k] > K * 0.5 and
            headers_scores[k] == best_scores[i] else ''
            for k, i in enumerate(headers_indices)]
        #print(tabulate(table, expected_headers))
        # expected_headers = [LABELS[i] if headers_scores[k] > K * 0.5 else ''
        #                     for k, i in enumerate(headers_indices)]
        for f, h in zip(features, expected_headers):
            f = [h or 'NULL'] + [str(v) for v in f]
            out_f.write(','.join(f))
            out_f.write('\n')
    out_f.close()


def get_features(filename, table, meta_info=MetaInfo([])):
    cfs = compute_features(table, meta_info)
    for cf in cfs:
        continue
        print cf
    return [[
        filename,
        cf_index,
        cf.size,
        cf.is_code,
        cf.has_dollar,
        cf.is_quantity,
        cf.is_gst_price,
        cf.is_pre_gst_price,
        cf.is_quantity_or_price,
        cf.has_float,
        cf.has_integer,
        cf.matches_total,
        cf.equals_1,
        cf.contains_dot,
        cf.is_unit_of_measure,
        cf.is_packsize,
        cf.header or ''] for cf_index, cf in enumerate(cfs)]


def process_structure_files(directory, output_filename):
    out_f = open(output_filename, 'w')
    for structure_id in os.listdir(directory):
        pdf_filename = os.path.join(directory, structure_id, 'file.pdf')
        truth_filename = os.path.join(directory, structure_id, 'truth.json')
        if os.path.exists(pdf_filename):
            assert os.path.exists(truth_filename)
            table, meta_info = segment_pdf(pdf_filename)
            features = get_features(pdf_filename, table, meta_info)
            truth = json.load(open(truth_filename, 'r'))
            expected_headers = truth['headers']
            #print tabulate(table, expected_headers)
            for f, h in zip(features, expected_headers):
                f = [h or 'NULL'] + [str(v) for v in f]
                out_f.write(','.join(f))
                out_f.write('\n')
    out_f.close()


def generate_sample(_):
    items = items_list.sample(np.random.randint(1, 30))
    column_options = [
        ['code', 'description', 'price1', 'quantity', 'price4'],
        ['code', 'description', 'price1', 'quantity', 'price4'],
        ['description', 'quantity', 'price3'],
        ['descriptionPackSize', 'quantity', 'price3'],
        ['descriptionPackSize', 'code', 'quantity', 'price1', 'price2',
         'price3', 'price4']
    ]
    columns = np.random.choice(column_options)
    column_names = [np.random.choice(HEADERS[NAMES.index(c)]) for c in columns]
    table = []
    format_option = np.random.choice(['{:0.2f}', '{:0.1f}', '{:0.0f}'])
    for item in items:
        item.quantity = np.random.choice([1, 1, 1, 1, 1, 1, 1.2, 2, 2.1, 3, 4])
        if np.random.random() < .8:
            item.quantity = item.quantity * (1 + random.random())
        item.price = item.quantity * item.unitPrice
        item.totalPrice = item.quantity * item.totalUnitPrice
        line = []
        for column_name in columns:
            value = getattr(item, ATTRIBUTE_NAMES[NAMES.index(column_name)])
            if column_name.startswith('price') or column_name == 'quantity':
                value = format_option.format(value)
            line.append(value)
        table.append(line)
    #print tabulate(table, columns)
    features = get_features(None, table)
    return features, [TYPES[NAMES.index(c)] for c in columns]


def generate_samples(items_file, out_file, N=75):
    global items_list
    items_list = ItemsList(items_file, shingle_length=0)
    #pool = Pool(processes=9)
    #samples = pool.map(generate_sample, range(N))
    samples = [generate_sample(k) for k in range(N)]
    out_f = open(out_file, 'w')
    for sample in samples:
        features, columns = sample
        for f, h in zip(features, columns):
            f = [h or 'NULL'] + [str(v) for v in f]
            out_f.write(','.join(f))
            out_f.write('\n')
    out_f.close()

process_structure_files(
    'data/production/structure',
    'out/train_prod.dat')

generate_samples('data/list.csv', 'out/train_synthetic.dat')

process_files(
    'data/processed/C/{className}-{counter}-p1.txt',
    'data/processed/C/{className}-{counter}-p1.xml',
    'data/original/C.csv',
    0,
    ('scan',),
    'out/train_C.dat',
    range(0, 114))

process_files(
    'data/processed/B/{counter}{className}-p1.txt',
    'data/processed/B/{counter}{className}-p1.xml',
    'data/original/B.csv',
    1,
    ('A',),
    'out/train_B.dat',
    range(1, 76))

with open('out/train.dat', 'w') as fout:
    fin = fileinput.input([
        'out/train_C.dat', 'out/train_B.dat', 'out/train_prod.dat'
    ])
    for line in fin:
        fout.write(line)
    fin.close()

exit(1)
