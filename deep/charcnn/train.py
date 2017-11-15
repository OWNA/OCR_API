import argparse
import tensorflow as tf
import numpy as np
import threading
import os

from tqdm import tqdm
from tensorflow.python.client import timeline

from deep.helpers import count_number_trainable_params
from deep.input import read_and_decode
from deep.charcnn.model import Model, Config
from deep.metrics import evaluate, get_eval_images
from deep.constants import *

import matplotlib.pyplot as plt


parser = argparse.ArgumentParser( description="OCR using Char CNN")
parser.add_argument("--num_layers", default=5, type=int)
parser.add_argument("--num_channels", default=64, type=int)
parser.add_argument("--hidden_size", default=256, type=int)
parser.add_argument("--max_char", default=6, type=int)
parser.add_argument("--learning_rate", default=0.01, type=float)


def runOnSession(variables, session, debug=False, feed_dict={}):
  run_metadata = tf.RunMetadata()

  if debug:
    outputs = session.run(
      variables,
      feed_dict=feed_dict,
      options=tf.RunOptions(
        trace_level=tf.RunOptions.FULL_TRACE),
      run_metadata=run_metadata)
    trace = timeline.Timeline(
      step_stats=run_metadata.step_stats)
    with open('out/timeline.ctf.json', 'w') as trace_file:
      trace_file.write(trace.generate_chrome_trace_format())
  else:
    outputs = session.run(variables, feed_dict=feed_dict)
  return outputs


def train():

  with tf.Graph().as_default() as graph:
    filename_queue = tf.FIFOQueue(capacity=100, dtypes=[tf.string])
    enq1 = filename_queue.enqueue("data/train/1.tfrecords")
    enq2 = filename_queue.enqueue("data/train/2.tfrecords")
    enq3 = filename_queue.enqueue("data/train/3.tfrecords")
    enq4 = filename_queue.enqueue("data/train/4.tfrecords")

    x, y = read_and_decode(filename_queue, pad=True)
    args = parser.parse_args()
    config = Config(
      conv_num_layers=args.num_layers,
      conv_num_channels=args.num_channels,
      max_char_count=args.max_char,
      hidden_size=args.hidden_size,
      learning_rate=args.learning_rate
    )
    model = Model(x, y, config)
    saver = tf.train.Saver()
    print "Total number of trainable params: {:,}".format(
      count_number_trainable_params())

  with tf.Session(graph=graph) as session:

    session.run(tf.local_variables_initializer())
    session.run(tf.global_variables_initializer())

    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(coord=coord)

    session.run(enq1)
    session.run(enq1)
    session.run(enq2)
    session.run(enq2)
    session.run(enq3)
    session.run(enq3)
    session.run(enq4)

    #saver.restore(session, "out/deep/tensorflow/model-19.ckpt")

    for epoch in range(80):
      num_batches = WORDS_PER_EPOCH // MINIBATCH_SIZE
      pbar = tqdm(range(num_batches), unit="batch")
      losses = []
      # Run the training
      for i in pbar:
        _, l = runOnSession([model.optimizer, model.loss], session, debug=False)
        losses.append(l)
        pbar.set_description('Epoch %d: Minibatch loss: %.3f' % (
          epoch, np.mean(losses)))
      images, labels = get_eval_images(EVAL_SIZE, epoch)
      # Run the eval
      num_batches = EVAL_SIZE // MINIBATCH_SIZE
      pbar = tqdm(range(num_batches), unit="batch")
      losses = []
      predictions = []
      labels[labels == -1] = NUMBER_GENERATOR_OUPUT_SIZE - 1
      for i in pbar:
        l, p = runOnSession(
          [model.val_loss, model.val_output],
          session, debug=False, feed_dict={
            model.val_x: images[i * MINIBATCH_SIZE:(i + 1) * MINIBATCH_SIZE, ...],
            model.val_y: labels[i * MINIBATCH_SIZE:(i + 1) * MINIBATCH_SIZE, ...]
        })
        losses.append(l)
        predictions.append(p)
        pbar.set_description('Epoch %d: Eval Minibatch loss: %.3f' % (
          epoch, np.mean(losses)))
      evaluate(images, labels, predictions)
      save_path = saver.save(
        session, "out/deep/tensorflow/model-{}.ckpt".format(epoch))

    coord.request_stop()
    coord.join(threads)

if __name__ == "__main__":
    train()
