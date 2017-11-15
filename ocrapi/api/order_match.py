import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from matching.exceptions import *
from matching.constants import *
from matching.line import LineComparator


def tokenize(text):
    stopset = set(stopwords.words('english'))
    tokens = word_tokenize(str(text))
    return [w for w in tokens if not w in stopset]


def compute_hard_distance(items, words):
    matching_set = []
    for item in items:
        matching_set += tokenize(item.code)
        matching_set += tokenize(item.description)
        matching_set += tokenize(item.unitPrice)
        matching_set += tokenize(item.totalUnitPrice)
        matching_set += tokenize(item.price)
        matching_set += tokenize(item.totalPrice)
        matching_set += tokenize(item.quantity)
    matching_set = set(matching_set)
    union = len(words.union(matching_set))
    intersection = len(words.intersection(matching_set))
    return 1 - float(intersection) / float(union)


lineComparator = LineComparator()

def get_best_score(item, words, relevantPart):
    scores = []
    for word in words:
        matches = lineComparator.align(item, word, relevantPart)
        scores += [m.score for m in matches]
    return float(np.max(scores))

def compute_soft_distance(items, words):
    matching_set = []
    scores = []
    count = 0
    for item in items:
        scores.append(get_best_score(item, words, DESCRIPTION))
        if item.code:
            scores.append(get_best_score(item, words, CODE))
        if item.quantity and item.price:
            scores.append(
                max(get_best_score(item, words, TOTAL_VALUE),
                    get_best_score(item, words, VALUE),
                    get_best_score(item, words, TOTAL_UNIT_VALUE),
                    get_best_score(item, words, UNIT_VALUE)))
            scores.append(get_best_score(item, words, QUANTITY))
    return 1 - np.mean(scores)

def find_best_soft_match(orders, words):
    if not orders:
        raise NoMatchingOrder
    best_order = None
    best_distance = 1
    for order_id, order in orders:
        distance = compute_soft_distance(order, words)
        if distance < best_distance:
            best_distance = distance
            best_order = order_id, order
    if best_distance > 0.2:
        raise NoMatchingOrder
    return best_distance, best_order


def find_best_match(orders, words):
    expected_set = []
    if not orders:
        raise NoMatchingOrder
    for word in words:
        expected_set += tokenize(word.content.encode('ascii', 'ignore'))
    expected_set = set(expected_set)
    best_order = None
    best_distance = 1
    for order_id, order in orders:
        distance = compute_hard_distance(order, expected_set)
        if distance < best_distance:
            best_distance = distance
            best_order = order_id, order
    return best_distance, best_order

