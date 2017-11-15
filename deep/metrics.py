import itertools
import cv2
import re
import glob
import numpy as np

import matplotlib.pyplot as plt

from deep.constants import *
from deep.helpers import expand_image_for_evaluation
from deep.helpers import number_to_label, label_to_number


def get_eval_images(num, epoch):
  p = num // 7
  imageFilenames  = glob.glob("images/crops/B/A_*[0-9.].png")[0:p]
  imageFilenames += glob.glob("images/crops/B/B_*[0-9.].png")[0:p]
  imageFilenames += glob.glob("images/crops/B/C_*[0-9.].png")[0:p]
  imageFilenames += glob.glob("images/crops/B/D_*[0-9.].png")[0:p]
  imageFilenames += glob.glob("images/crops/B/E_*[0-9.].png")[0:p]
  imageFilenames += glob.glob("images/crops/C/scan_*[0-9.].png")[0:p]
  imageFilenames += glob.glob("images/crops/C/photo_*[0-9.].png")[0:num - p * 6]
  images = []
  labels = []
  for imageFilename in imageFilenames:
    pattern = re.compile(".*_([0-9.]+).png")
    matches = pattern.match(imageFilename)
    labels.append(number_to_label(
      matches.group(1), NUMBER_GENERATOR_OUPUT_SIZE, ABSOLUTE_MAX_STRING_LEN))
    image = cv2.imread(imageFilename, 1)
    image = image[:,:,0]
    image = expand_image_for_evaluation(image, IMAGE_WIDTH, IMAGE_HEIGHT)
    image = np.reshape(image.T, (IMAGE_WIDTH, IMAGE_HEIGHT, 1))
    images.append(image)
  return np.array(images), np.array(labels)


def evaluate(images, labels, batched_predictions, classes=None):

  predictions = []
  for batch in batched_predictions:
    for index in range(batch.shape[0]):
      predictions.append(batch[index])

  correct = 0
  details = {}
  for index, (image, label, prediction) in enumerate(
      zip(images, labels, predictions)):
    prediction = list(np.argmax(prediction, 1))
    prediction = [k for k, g in itertools.groupby(prediction)]
    true_label = label_to_number(label)
    decoded_label = label_to_number(prediction)
    if classes:
      className = classes[index]
      if not className in details:
        details[className] = [0, 0]
      details[className][1] += 1
    #print '[{}], [{}]'.format(true_label, decoded_label)
    try:
      decoded_number = float(decoded_label)
      true_number = float(true_label)
      if abs(decoded_number - true_number) < 0.01:
        correct += 1
        if classes:
          details[className][0] += 1
    except:
      pass
  if classes:
    for className in details:
      print "Class {} accurracy {}% on {} images".format(
        className,
        details[className][0] * 100. / details[className][1],
        details[className][1])
  print "Eval accurracy {}% on {} images".format(
    correct * 100. / len(images), len(images))
