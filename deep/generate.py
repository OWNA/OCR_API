import threading
import os
import pickle
import numpy as np
from tqdm import tqdm
import tensorflow as tf

from deep.helpers import number_to_label
from deep.constants import *
from deep.paint import paint_text


def paint1(text, img_w, img_h):
    return paint_text(
        text, img_w, img_h,
        multi_fonts=True,
        translate=True,
        rotate=True,
        shapes=False,
        background=False,
        noise=False,
        artifacts=False,
        warping=False,
        other_chars=False)


def paint2(text, img_w, img_h):
    return paint_text(
        text, img_w, img_h,
        multi_fonts=True,
        translate=True,
        rotate=True,
        shapes=True,
        background=True,
        noise=False,
        artifacts=False,
        warping=False,
        other_chars=False)


def paint3(text, img_w, img_h):
    return paint_text(
        text, img_w, img_h,
        multi_fonts=True,
        translate=True,
        rotate=True,
        shapes=True,
        background=True,
        noise=False,
        artifacts=True,
        warping=True,
        other_chars=True)


def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


def generate_images(paint_func, num_words, filename):
    absolute_max_string_len = ABSOLUTE_MAX_STRING_LEN
    max_string_len = 6
    whole_number_fraction = 0.5
    string_list = [''] * num_words
    Y_data = np.ones([num_words, absolute_max_string_len]) * -1
    X_data = np.ones([num_words, IMAGE_WIDTH, IMAGE_HEIGHT, 1])
    X_text = []
    Y_len = [0] * num_words
    writer = tf.python_io.TFRecordWriter(filename)
    for i in xrange(num_words):
        number_size = np.random.randint(max_string_len) + 1
        number = np.random.randint(10 ** number_size)
        if np.random.rand() < whole_number_fraction:
            fraction_position = np.random.randint(min(3, number_size)) + 1
            number = number / 10. ** fraction_position
        if number < 0.001:
            number = 0
        word = str(number)
        image = paint_func(word, IMAGE_WIDTH, IMAGE_HEIGHT)[:, :].T
        lab = number_to_label(
            word, NUMBER_GENERATOR_OUPUT_SIZE, ABSOLUTE_MAX_STRING_LEN)
        example = tf.train.Example(features=tf.train.Features(feature={
            'word_length': _int64_feature(len(word)),
            'image_raw': _bytes_feature(image.tostring()),
            'label_str': _bytes_feature(word),
            'label': tf.train.Feature(int64_list=tf.train.Int64List(value=lab))
        }))
        writer.write(example.SerializeToString())


if __name__ == '__main__':
    generate_images(paint1, MINIBATCH_SIZE * 400 * 4, 'data/train/1.tfrecords')
    generate_images(paint2, MINIBATCH_SIZE * 400 * 6, 'data/train/2.tfrecords')
    generate_images(paint3, MINIBATCH_SIZE * 400 * 25, 'data/train/3.tfrecords')
    generate_images(paint3, MINIBATCH_SIZE * 400 * 25, 'data/train/4.tfrecords')
