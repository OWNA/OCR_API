import re
import random
from matching.constants import *

def generate_random_seeds(n, seed=5):
    random.seed(seed)
    return random.sample(range(1, n+1), n)

def jaccard_similarity(set_a, set_b, debug=False):
    if debug:
        print len(set_a.intersection(set_b)), len(set_a.union(set_b))
    return len(set_a.intersection(set_b)) * 1.0 / len(set_a.union(set_b))

def getFloat(content, default=0):
    try:
        matches = re.findall(r'[0-9.]+', content)
        return float(matches[0])
    except Exception as e:
        return default

def get_price_values(price_value, valuePart, quantity, gstPercent):
    unit_price_pre_gst = 0
    price_pre_gst = 0
    unit_price = 0
    price = 0

    if valuePart == UNIT_VALUE:
        unit_price_pre_gst = price_value
        price_pre_gst = unit_price_pre_gst * quantity
        unit_price = unit_price_pre_gst * (1 + gstPercent / 100.)
        price = price_pre_gst * (1 + gstPercent / 100.)
    elif valuePart == VALUE:
        price_pre_gst = price_value
        unit_price_pre_gst = price_pre_gst / quantity
        price = price_pre_gst * (1 + gstPercent / 100.)
        unit_price = unit_price_pre_gst * (1 + gstPercent / 100.)
    elif valuePart == TOTAL_UNIT_VALUE:
        unit_price = price_value
        price = unit_price * quantity
        unit_price_pre_gst = unit_price / (1 + gstPercent / 100.)
        price_pre_gst = price / (1 + gstPercent / 100.)
    elif valuePart == TOTAL_VALUE:
        price = price_value
        unit_price = price / quantity
        price_pre_gst = price / (1 + gstPercent / 100.)
        unit_price_pre_gst = unit_price / (1 + gstPercent / 100.)
    return price, unit_price, price_pre_gst, unit_price_pre_gst


def index(arr, v):
    return arr.index(v) if v in arr else -1
