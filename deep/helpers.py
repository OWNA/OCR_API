import tensorflow as tf
from tabulate import tabulate
import cv2
import numpy as np


def label_to_number(labels):
    number = ''
    for label in labels:
        if label == -1:
            break
        elif label == 10:
            number += '.'
        elif label == 11:
            number += ''
        else:
            number += str(label)
    return number

def number_to_label(text, num_classes, max_len):
    ret = np.ones([max_len], dtype=np.int64) * -1
    for index, char in enumerate(text):
        if char >= '0' and char <= '9':
            ret[index] = ord(char) - ord('0')
        elif char == '.':
            ret[index] = num_classes - 2
        elif char == ' ':
            ret[index] = num_classes - 1
        else:
            raise Exception('Unsupported character {0} in word {1}'.format(
                char, text))
    return ret


def count_number_trainable_params():
    """ Counts the number of trainable variables. """

    def get_nb_params_shape(shape):
      nb_params = 1
      for dim in shape:
        nb_params = nb_params*int(dim)
      return nb_params

    tot_nb_params = 0
    names = []
    counts = []
    shapes = []
    for trainable_variable in tf.trainable_variables():
      shape = trainable_variable.get_shape()
      current_nb_params = get_nb_params_shape(shape)
      tot_nb_params = tot_nb_params + current_nb_params
      names.append(trainable_variable.name)
      shapes.append(trainable_variable.shape)
      counts.append(current_nb_params)
    print tabulate(zip(names, shapes, counts), headers=[
      'Variables', 'Shapes', 'Trainable parameters'])
    return tot_nb_params


def expand_image_for_evaluation(image, img_w, img_h):
    h, w = image.shape
    if w > img_w or h > img_h:
        fx = float(w) / img_w
        fy = float(h) / img_h
        if fx > fy:
            dst_w = img_w
            dst_h = int(h / fx)
        else:
            dst_w = int(w / fy)
            dst_h = img_h
        image = cv2.resize(image, (dst_w, dst_h))

    h, w = image.shape
    h_border = img_w - w
    v_border = img_h - h
    image = cv2.copyMakeBorder(
        image,
        v_border // 2, v_border - v_border // 2,
        h_border // 2, h_border - h_border // 2,
        cv2.BORDER_REPLICATE)
    return image / 255.
