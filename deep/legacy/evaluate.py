from utils.fixmatplot import *

import scipy.misc
import re
import glob
import cv2
import os
import numpy as np
from keras import backend as K
from keras.optimizers import SGD
from keras.utils.data_utils import get_file
import matplotlib.pyplot as plt
from scipy import ndimage

from deep.legacy.helpers import decode_number_batch
from deep.legacy.model import OCRModel
from deep.constants import OUTPUT_DIR, NUMBER_GENERATOR_OUPUT_SIZE
from deep.constants import ABSOLUTE_MAX_STRING_LEN, POOL_SIZE
from deep.constants import IMAGE_WIDTH, IMAGE_HEIGHT
from deep.paint import paint_text
from deep.legacy.number_generate import NumberImageGenerator
from deep.helpers import expand_image_for_evaluation


def load_model(weight_file, img_w, img_h):
    """
    Loads the model weights once, so it can be reused for several
    images sequentially.
    """
    model, input_data, y_pred = OCRModel(
        img_w, img_h,
        NUMBER_GENERATOR_OUPUT_SIZE,
        ABSOLUTE_MAX_STRING_LEN).build()
    test_func = K.function([input_data], [y_pred])

    model.load_weights(weight_file)
    return model, test_func


def evaluate(model, img, test_func, img_w, img_h):
    """
    Given an image and a model, return the result of the model
    prediction on that image.
    """
    size = 2 # For some reason, it fails for a single value
    labels = np.ones([size, ABSOLUTE_MAX_STRING_LEN])
    input_length = np.zeros([size, 1])
    label_length = np.ones([size, 1])
    X_data = np.ones([size, img_w, img_h, 1])
    for i in xrange(size):
        X_data[i, 0:img_w, :, 0] = img.T
        input_length[i] = img_w // POOL_SIZE ** 2 - 2
    data = {
        'the_input': X_data,
        'the_labels': labels,
        'input_length': input_length,
        'label_length': label_length,
    }
    model.predict(data, batch_size=size, verbose=2)
    result = decode_number_batch(test_func, X_data)
    return result[0]


def evaluate_batch(model, images, test_func, img_w, img_h):
    """
    Given images and a model, return the results of the model
    prediction on those images.
    """
    if len(images) == 1:
        return [evaluate(model, images[0], test_func, img_w, img_h)]
    size = len(images) # For some reason, it fails for a single value
    labels = np.ones([size, ABSOLUTE_MAX_STRING_LEN])
    input_length = np.zeros([size, 1])
    label_length = np.ones([size, 1])
    X_data = np.ones([size, img_w, img_h, 1])
    for i, image in enumerate(images):
        X_data[i, 0:img_w, :, 0] = image.T
        input_length[i] = img_w // POOL_SIZE ** 2 - 2
    data = {
        'the_input': X_data,
        'the_labels': labels,
        'input_length': input_length,
        'label_length': label_length,
    }
    model.predict(data, batch_size=size, verbose=2)
    return decode_number_batch(test_func, X_data)


def extract_image_for_evaluation(image, img_w, img_h):
    h, w = image.shape
    fx = float(w) / img_w
    fy = float(h) / img_h
    if fx > fy:
        dst_w = int(fy * img_w)
        dst_h = h
    else:
        dst_w = w
        dst_h = int(fx * img_h)
    delta_w = (w - dst_w) // 2
    delta_h = (h - dst_h) // 2
    image = image[delta_h:(h - delta_h),delta_w:(w - delta_w)]
    image = cv2.resize(image, (img_w, img_h))
    image = image / 255.
    return image


if __name__ == '__main__':
    model, test_func = load_model(
       'deep/weights/thin-dollars.v3.h5', IMAGE_WIDTH, IMAGE_HEIGHT)

    images = []
    originals = []
    ground_truth = []
    classes = []
    stats = np.zeros((7, 2))
    partitions = [
        len(glob.glob("images/crops/B/A_*.png")),
        len(glob.glob("images/crops/B/B_*.png")),
        len(glob.glob("images/crops/B/C_*.png")),
        len(glob.glob("images/crops/B/D_*.png")),
        len(glob.glob("images/crops/B/E_*.png")),
        len(glob.glob("images/crops/C/scan_*.png")),
        len(glob.glob("images/crops/C/photo_*.png")),
    ]
    partitions = np.cumsum(partitions)
    imageFilenames = sorted(glob.glob("images/crops/B/*.png"))
    imageFilenames += sorted(glob.glob("images/crops/C/*.png"))

    for imageIndex, imageFilename in enumerate(imageFilenames):
        pattern = re.compile(".*_([0-9.]+).png")
        matches = pattern.match(imageFilename)
        if not matches:
            continue
        ground_truth.append(matches.group(1))
        image = cv2.imread(imageFilename, 1)
        image = image[:,:,0]
        image = expand_image_for_evaluation(image, IMAGE_WIDTH, IMAGE_HEIGHT)
        originals.append(image * 255)
        images.append(image)
        classes.append(len([p for p in partitions if p < imageIndex]))

    results = []
    N = len(ground_truth)
    K = 512
    for n in range(N // K + 1):
        start = n * K
        end = min(N, (n + 1) * K)
        results += evaluate_batch(model, images[start:end],
                                  test_func, IMAGE_WIDTH, IMAGE_HEIGHT)
    mismatch = 0.
    N = 0
    ignored = 0
    for r1, r2, imageFilename, original, classType in zip(
            ground_truth, results, imageFilenames, originals, classes):
        try:
            r1 = float(r1)
        except Exception:
            ignored += 1
            continue
        N += 1
        stats[classType][0] += 1
        try:
            r2 = float(r2)
            filename = imageFilename.split('/')[-1]
            if r1 != r2:
                mismatch += 1
                stats[classType][1] += 1
                annotated_cell = np.ones((IMAGE_HEIGHT * 2, IMAGE_WIDTH, 3)) * 255
                annotated_cell[IMAGE_HEIGHT:,:,0] = original
                annotated_cell[IMAGE_HEIGHT:,:,1] = original
                annotated_cell[IMAGE_HEIGHT:,:,2] = original
                annotation = '{} vs {}'.format(r1, r2)
                cv2.putText(annotated_cell, annotation, (15, 30),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            .5, (0, 255, 0), 1, cv2.LINE_AA)
                cv2.imwrite('out/cells/{}'.format(filename), annotated_cell)
        except Exception as e:
            stats[classType][1] += 1
            mismatch += 1

    print 'Accuracy {0} on {1} samples, with {2} ignored'.format(
        (N - mismatch) / N, N, ignored)
    for n, m in stats:
        n = float(n)
        print 'Detailed: Accuracy {0} on {1} samples'.format((n - m) / n, int(n))
