import itertools
import glob
import cv2
import tensorflow as tf
import re
import numpy as np
import threading
import os

from tqdm import tqdm
from tensorflow.python.client import timeline

from deep.helpers import count_number_trainable_params
from deep.input import read_and_decode
from deep.ctcrnn.model import Model, Config
from deep.metrics import evaluate
from deep.helpers import expand_image_for_evaluation
from deep.helpers import number_to_label, label_to_number
from deep.constants import *

import matplotlib.pyplot as plt


def predict_images(model_name, images):
  labels = np.zeros((len(images), ABSOLUTE_MAX_STRING_LEN))
  images = [expand_image_for_evaluation(img, IMAGE_WIDTH, IMAGE_HEIGHT) for img in images]
  images = [np.reshape(image.T, (IMAGE_WIDTH, IMAGE_HEIGHT, 1)) for image in images]
  _, batched_predictions = evaluate_images(model_name, images, labels, gpu=False)
  predictions = []
  predicted_labels = []
  for batch in batched_predictions:
    for index in range(batch.shape[0]):
      predictions.append(batch[index])
  for prediction in predictions:
    prediction = list(np.argmax(prediction, 1))
    prediction = [k for k, g in itertools.groupby(prediction)]
    label = label_to_number(prediction)
    predicted_labels.append(label)
  return predicted_labels


def evaluate_images(model_name, images, labels, gpu=True):
  with tf.Graph().as_default() as graph:
    filename_queue = tf.FIFOQueue(capacity=100, dtypes=[tf.string])
    enq1 = filename_queue.enqueue("data/train/1.tfrecords")
    enq2 = filename_queue.enqueue("data/train/2.tfrecords")
    enq3 = filename_queue.enqueue("data/train/3.tfrecords")

    x, y = read_and_decode(filename_queue)
    config = Config(
      attention_size=0,
      conv_num_layers=2,
      conv_num_channels=128,
      rnn_size=512,
      time_dense_size=512,
      learning_rate=0.01
    )
    model = Model(x, y, config)
    saver = tf.train.Saver()
    print "Total number of trainable params: {:,}".format(
      count_number_trainable_params())

  config = tf.ConfigProto(device_count = {'GPU': 1 if gpu else 0})
  with tf.Session(graph=graph, config=config) as session:

    session.run(tf.local_variables_initializer())
    session.run(tf.global_variables_initializer())

    saver.restore(session, model_name)

    N = len(images)

    # Run the eval
    num_batches = int(np.ceil(N / float(MINIBATCH_SIZE)))

    images, labels = np.array(images), np.array(labels)

    pbar = tqdm(range(num_batches), unit="batch")
    losses = []
    predictions = []
    for i in pbar:
      start = i * MINIBATCH_SIZE
      end = min(N, (i + 1) * MINIBATCH_SIZE)
      images_batch = np.zeros((MINIBATCH_SIZE, IMAGE_WIDTH, IMAGE_HEIGHT, 1))
      labels_batch = np.zeros((MINIBATCH_SIZE, ABSOLUTE_MAX_STRING_LEN))
      images_batch[0:end-start, ...] = images[start:end, ...]
      labels_batch[0:end-start, ...] = labels[start:end, ...]
      l, p = session.run(
          [model.val_loss, model.val_output],
          feed_dict={
              model.val_x: images_batch,
              model.val_y: labels_batch
          })
      losses.append(l)
      predictions.append(p[0:end-start, ...])
    return losses, predictions


def run():

  imageFilenames  = glob.glob("images/crops/B/A_*[0-9.].png")
  imageFilenames += glob.glob("images/crops/B/B_*[0-9.].png")
  imageFilenames += glob.glob("images/crops/B/C_*[0-9.].png")
  imageFilenames += glob.glob("images/crops/B/D_*[0-9.].png")
  imageFilenames += glob.glob("images/crops/B/E_*[0-9.].png")
  imageFilenames += glob.glob("images/crops/C/scan_*[0-9.].png")
  imageFilenames += glob.glob("images/crops/C/photo_*[0-9.].png")
  images = []
  labels = []
  classes = []
  for imageFilename in imageFilenames:
      pattern = re.compile(".*/([^_]+).*_([0-9.]+).png")
      matches = pattern.match(imageFilename)
      labels.append(number_to_label(
          matches.group(2), NUMBER_GENERATOR_OUPUT_SIZE, ABSOLUTE_MAX_STRING_LEN))
      image = cv2.imread(imageFilename, 1)
      image = image[:,:,0]
      image = expand_image_for_evaluation(image, IMAGE_WIDTH, IMAGE_HEIGHT)
      image = np.reshape(image.T, (IMAGE_WIDTH, IMAGE_HEIGHT, 1))
      images.append(image)
      classes.append(matches.group(1))

  losses, predictions = evaluate_images(
    "deep/weights/ctcrnn/model.ckpt", images, labels)
  #print('Average loss: %.3f' % (np.mean(losses)))
  evaluate(images, labels, predictions, classes)


if __name__ == "__main__":
    run()
