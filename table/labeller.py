import re
import xgboost as xgb
import numpy as np
from utils.util import getFloat
from nltk.corpus import wordnet as wn
from nltk.stem import PorterStemmer
import swalign
from table.training.rnn_train import predict
from table.training.reader import most_common_header_words, TARGET_NAMES


scoring = swalign.NucleotideScoringMatrix(2, -1)
sw = swalign.LocalAlignment(scoring)
ps = PorterStemmer()


class CellFeatures(object):

    def __init__(self, cell):
        self.cell = cell
        self.size = 0
        self.has_float = False
        self.has_integer = False
        self.is_quantity = False
        self.is_quantity_or_price = False
        self.is_pre_gst_price = False
        self.is_gst_price = False
        self.is_code = False
        self.is_packsize = False
        self.is_unit_of_measure = False
        self.compute_unary_features()

    def compute_unary_features(self):
        c = self.cell
        cl = self.cell.lower().replace(' ', '')
        f = getFloat(c)
        self.size = len(c)
        self.has_float = f > 0 and f < 1000
        self.has_integer = f > 0 and f < 100 and int(f) == f
        self.is_quantity = re.match('^[0-9]{1,2}(.0+)?([ ]*[a-zA-Z]+)?$', c) is not None
        type_1_reg = '^[0-9a-zA-Z]{4,20}$'
        type_2_reg = '^[0-9a-zA-Z]{2,20}[- ][0-9a-zA-Z]{2,20}$'
        code_type_1 = re.match(type_1_reg, c) is not None
        code_type_2 = re.match(type_2_reg, c) is not None
        is_word = len(wn.synsets(c)) > 0
        self.is_code = (code_type_1 or code_type_2) and not is_word
        self.is_unit_of_measure = re.match(
            '(ea|each|pkt|packet|ctn)', cl) is not None
        packsize_type_1_reg = '^[.0-9]+(gr|kg|ml|l|lt)$'
        packsize_type_2_reg = '^[.0-9]+\'s$'
        packsize_type_3_reg = '^[.0-9]+x[0-9]+(gr|kg|ml|l|lt)$'
        packsize_type_4_reg = '^[.0-9]+x[0-9]+$'
        packsize_type_1 = re.match(packsize_type_1_reg, cl) is not None
        packsize_type_2 = re.match(packsize_type_2_reg, cl) is not None
        packsize_type_3 = re.match(packsize_type_3_reg, cl) is not None
        packsize_type_4 = re.match(packsize_type_4_reg, cl) is not None
        self.is_packsize = (packsize_type_1 or
                            packsize_type_2 or
                            packsize_type_3 or
                            packsize_type_4)
        self.has_dollar = '$' in c
        self.equals_1 = f == 1
        self.contains_dot = '.' in c
        self.value = f


class ColumnFeatures(object):

    def __init__(self, cell_features, header, numbers):
        self.size = np.mean([c.size for c in cell_features])
        self.is_code = np.mean([c.is_code for c in cell_features])
        self.is_unit_of_measure = np.mean([
            c.is_unit_of_measure for c in cell_features])
        self.is_packsize = np.mean([c.is_packsize for c in cell_features])
        self.is_quantity = np.mean([c.is_quantity for c in cell_features])
        self.is_pre_gst_price = np.mean([c.is_pre_gst_price for c in cell_features])
        self.is_gst_price = np.mean([c.is_gst_price for c in cell_features])
        self.is_quantity_or_price = np.mean(
            [c.is_quantity_or_price for c in cell_features])
        self.has_float = np.mean([c.has_float for c in cell_features])
        self.has_integer = np.mean([c.has_integer for c in cell_features])
        self.has_dollar = np.mean([c.has_dollar for c in cell_features])
        self.equals_1 = np.mean([c.equals_1 for c in cell_features])
        self.contains_dot = np.mean([c.contains_dot for c in cell_features])
        self.total = np.sum([c.value for c in cell_features])
        self.matches_total = 0
        for number in numbers:
            if abs(self.total - number) < 0.1:
                self.matches_total = 1
        self.header = header


    def __str__(self):
        titles = ['Size',
                  'Code',
                  '$',
                  'Qty',
                  'GST',
                  'pre-GST',
                  'Qty or Price',
                  'Float',
                  'Int',
                  '=total',
                  '=1',
                  '.',
                  'Unit Of Measure',
                  'Packsize']
        string_format = ', '.join(['<{}> {{:05.2f}}'.format(t) for t in titles])
        return string_format.format(
            self.size,
            self.is_code,
            self.has_dollar,
            self.is_quantity,
            self.is_gst_price,
            self.is_pre_gst_price,
            self.is_quantity_or_price,
            self.has_float,
            self.has_integer,
            self.matches_total,
            self.equals_1,
            self.contains_dot,
            self.is_unit_of_measure,
            self.is_packsize,
        )


def compute_multi_column_features(features):
    features = [f for f in features if f.has_float]
    for f1 in features:
        c1 = f1.cell
        flt1 = getFloat(c1)
        for f2 in features:
            c2 = f2.cell
            flt2 = getFloat(c2)
            if f2 == f1:
                continue
            if abs(flt1 - 0.9 * flt2) < 1 and (flt1 != flt2):
                f1.is_pre_gst_price = True
            if ((abs(10 * flt1 - flt2) < 1
                 or
                 abs(11 * flt1 - flt2) < 1
                 or flt1 == 0 and flt2 > 0)
                and
                flt1 != flt2):
                f1.is_gst_price = True
            for f3 in features:
                c3 = f3.cell
                flt3 = getFloat(c3)
                if f3 == f1 or f3 == f2:
                    continue
                if abs(flt1 * flt2 - flt3) < 1:
                    f1.is_quantity_or_price = True
                    f2.is_quantity_or_price = True


class MetaInfo(object):

    def __init__(self, words, header=None):
        self.words = words
        self.header = header


def compute_features(lines, meta_info):
    cell_features = [[CellFeatures(cell) for cell in line] for line in lines]
    header = meta_info.header if meta_info else None
    words = meta_info.words if meta_info else []
    [compute_multi_column_features(line) for line in cell_features]
    cell_features = map(list, zip(*cell_features))
    column_features = []

    numbers = []
    for w in words:
        f = getFloat(w.word.content)
        if f:
            numbers.append(f)
    for k in range(len(cell_features)):
        column = cell_features[k]
        header_c = None
        if header:
            header_c = header[k]
            header_c = re.sub(r'([^\s\w]|_)+', '', header_c)
            header_c = header_c.lower()
        column_features.append(ColumnFeatures(column, header_c, numbers))
    return column_features


class Features:
    INDEX=0
    SIZE=1
    IS_CODE=2
    HAS_DOLLAR=3
    IS_QUANTITY=4
    IS_GST_PRICE=5
    IS_PRE_GST_PRICE=6
    IS_QUANTITY_OR_PRICE=7
    HAS_FLOAT=8
    HAS_INTEGER=9
    MATCHES_TOTAL=10
    EQUALS_1=11
    CONTAINS_DOT=12
    IS_UNIT_OF_MEASURE=13
    IS_PACKSIZE=14


def transform_features(cfs):
    features = [[cf_index,
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
                 cf.header or '']
                for cf_index, cf in enumerate(cfs)]
    for s in features:
        header = s.pop(-1)
        for common_word in most_common_header_words:
            s.append(0)
            if header:
                for w in header.split(' '):
                    aln = sw.align(common_word, w)
                    score = aln.score / float(2 * len(common_word))
                    s[-1] = max(s[-1], score)
    features = np.array(features, dtype=np.float32)
    return features


def label_features_legacy(features):
    C, _ = features.shape
    labels = ['NULL'] * C
    exclusions = []

    def __reset__(vector, exclude):
        for e in exclude:
            vector[e] = 0

    def __get_max__(regression, exclusions, name):
        __reset__(regression, exclusions)
        if regression is not None and max(regression):
            index = np.argmax(regression)
            labels[index] = name
            exclusions.append(index)

    description_size = features[:, Features.SIZE]
    __get_max__(description_size, exclusions, 'description')

    # Price
    has_float = [v for v in features[:, Features.HAS_FLOAT]]
    __reset__(has_float, exclusions)
    float_columns = [i for i, v in enumerate(has_float) if v > 0.5]
    if float_columns:
        total_price_index = float_columns[-1]
    else:
        total_price_index = C - 1
    labels[total_price_index] = 'price4'
    exclusions.append(total_price_index)

    is_quantity = (3 * features[:, Features.IS_QUANTITY_OR_PRICE] +
                   features[:, Features.HAS_INTEGER] +
                   features[:, Features.IS_QUANTITY])
    __get_max__(is_quantity, exclusions, 'quantity')

    is_price = (features[:, Features.HAS_FLOAT] +
                features[:, Features.IS_QUANTITY_OR_PRICE] -
                features[:, Features.IS_QUANTITY])
    __get_max__(is_price, exclusions, 'price2')

    is_code = features[:, Features.IS_CODE]
    __get_max__(is_code, exclusions, 'code')

    is_gst_price = (features[:, Features.IS_GST_PRICE] +
                    features[:, Features.CONTAINS_DOT] +
                    features[:, Features.IS_QUANTITY] -
                    features[:, Features.HAS_INTEGER] -
                    features[:, Features.HAS_FLOAT])
    __get_max__(is_gst_price, exclusions, 'gst')

    return labels


def label_columns_legacy(lines, meta_info):

    cfs = compute_features(lines, meta_info)
    features = transform_features(cfs)
    labels = label_features_legacy(features)

    if "quantity" in labels:
        quantity_index = labels.index("quantity")
        # Cleanup and fill values
        for line in lines:
            quantity = line[quantity_index]
            quantity = quantity.replace('i', '1')
            line[quantity_index] = quantity

    return labels


def label_columns_ml(lines, meta_info):

    names = ['NULL'] + TARGET_NAMES

    cfs = compute_features(lines, meta_info)
    features = transform_features(cfs)

    bst = xgb.Booster({'nthread':4})
    bst.load_model('out/train_with_null.model')
    dfeatures = xgb.DMatrix(features)
    preds = bst.predict(dfeatures)

    preds = bst.predict(dfeatures, output_margin=True)
    preds_max = np.max(preds, axis=1)
    best_scores = {}
    preds_argmax = np.argmax(preds, axis=1)
    for p, score in zip(preds_argmax, preds_max):
        if p in best_scores and best_scores[p] < score:
            best_scores[p] = score
        elif p not in best_scores:
            best_scores[p] = score
    return [names[k] if best_scores[k] == v else names[0]
            for k, v in zip(preds_argmax, preds_max)]


def label_columns_deep(lines, meta_info):

    names = ['NULL'] + TARGET_NAMES

    cfs = compute_features(lines, meta_info)
    features = transform_features(cfs)
    C, features_size = features.shape

    labels = [''] * C
    C = min(C, 12)
    x = np.zeros((1, 12, features_size))
    x[0, 0:C, :] = features[0:C, :]
    predictions = predict(x, 'table/training/models/model.ckpt')

    labels[0:C] = [names[k] for k in predictions[0][0:C]]
    return labels


def label_columns(lines, meta_info=None):
    if not lines:
        return []
#    return label_columns_legacy(lines, meta_info)
#    return label_columns_ml(lines, meta_info)
    return label_columns_deep(lines, meta_info)
