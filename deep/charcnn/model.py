import numpy as np
import tensorflow as tf
from deep.constants import *


class Config(object):

  def __init__(self,
               conv_num_layers=5,
               conv_num_channels=64,
               conv_filter_width=3,
               conv_pool_size=2,
               max_char_count=6,
               hidden_size=256,
               learning_rate=0.01):
    self.conv_num_layers = conv_num_layers
    self.conv_num_channels = conv_num_channels
    self.conv_filter_width = conv_filter_width
    self.conv_pool_size = conv_pool_size
    self.max_char_count = max_char_count
    self.hidden_size = hidden_size
    self.learning_rate = learning_rate


class Model(object):

  def __init__(self, x, y, config):

    self.config = config
    with tf.name_scope('Train'):
      with tf.variable_scope("Model", reuse=None):
        loss, optimizer, output = self.build(
          x, y, train=True)
    with tf.name_scope('Val') as scope:
      val_x = tf.placeholder(x.dtype, shape=(
        MINIBATCH_SIZE, IMAGE_WIDTH, IMAGE_HEIGHT, 1), name="val_x")
      val_y = tf.placeholder(y.dtype, shape=(
        MINIBATCH_SIZE, ABSOLUTE_MAX_STRING_LEN), name="val_y")
      with tf.variable_scope("Model", reuse=True):
        val_loss, val_output = self.build(
          val_x, val_y)

    self.x = x
    self.y = y
    self.loss = loss
    self.output = output

    self.val_x = val_x
    self.val_y = val_y
    self.optimizer = optimizer
    self.val_loss = val_loss
    self.val_output = val_output


  def build(self, x, y, train=False):

    conv_num_layers = self.config.conv_num_layers
    conv_num_channels = self.config.conv_num_channels
    conv_filter_width = self.config.conv_filter_width
    conv_pool_size = self.config.conv_pool_size

    conv_input = x
    for k in range(conv_num_layers):
      with tf.variable_scope("conv{}".format(k)):
        conv_weights = tf.get_variable(
          "conv_weights",
          [
            conv_filter_width,
            conv_filter_width,
            conv_num_channels * 2 ** (k - 1) if k > 0 else 1,
            conv_num_channels * 2 ** k,
        ], tf.float32)
        conv_biases = tf.get_variable(
          "conv_biases", [conv_num_channels * 2 ** k], tf.float32)
        conv = tf.nn.conv2d(
            conv_input,
            conv_weights,
            strides=[1, 1, 1, 1],
            padding='SAME')
        relu = tf.nn.relu(tf.nn.bias_add(conv, conv_biases))
        pool = tf.nn.max_pool(
            relu,
            ksize=[1, conv_pool_size, conv_pool_size, 1],
            strides=[1, conv_pool_size, conv_pool_size, 1],
            padding='SAME')
        conv_input = pool

    char_losses = []
    outputs = []
    size = (
      IMAGE_HEIGHT // 2 ** conv_num_layers *
      IMAGE_WIDTH // 2 ** conv_num_layers *
      conv_num_channels * 2 ** (conv_num_layers - 1)
    )
    for k in range(self.config.max_char_count):
      with tf.variable_scope("char{}".format(k)):
        fc1_weights = tf.get_variable(
          "fc1_weights",
          [
            size,
            self.config.hidden_size
          ], tf.float32)
        fc1_biases = tf.get_variable(
          "fc1_biases", [self.config.hidden_size], tf.float32)
        # Pool shape is mini batch size x width x heigh x channels
        pool_shape = pool.get_shape().as_list()
        reshape = tf.reshape(
            pool,
            [pool_shape[0], pool_shape[1] * pool_shape[2] * pool_shape[3]])
        hidden = tf.nn.relu(tf.matmul(reshape, fc1_weights) + fc1_biases)

        fc2_weights = tf.get_variable(
          "fc2_weights",
          [
            self.config.hidden_size,
            NUMBER_GENERATOR_OUPUT_SIZE
          ], tf.float32)
        fc2_biases = tf.get_variable(
          "fc2_biases",  [NUMBER_GENERATOR_OUPUT_SIZE], tf.float32)

        char_logits = tf.matmul(hidden, fc2_weights) + fc2_biases
        y_char =  tf.slice(y, [0, k], [MINIBATCH_SIZE, 1])

        char_loss = tf.reduce_mean(
          tf.nn.sparse_softmax_cross_entropy_with_logits(
            labels=tf.reshape(y_char, [-1]),
            logits=char_logits
          ))
        char_losses.append(char_loss)
        char_outputs = tf.nn.softmax(char_logits)
        outputs.append(char_outputs)

    loss = tf.reduce_sum(char_losses)
    outputs = tf.transpose(outputs, [1, 0, 2])
    if train:
      batch = tf.Variable(0, trainable=False, name="batch")
      learning_rate = tf.train.exponential_decay(
          self.config.learning_rate,
          batch * MINIBATCH_SIZE,
          WORDS_PER_EPOCH,
          0.95,
          staircase=True)
      opt = tf.train.MomentumOptimizer(learning_rate, 0.9, use_nesterov=True)
      grads_and_vars = opt.compute_gradients(loss)
      capped_grads_and_vars = [
        (tf.clip_by_norm(gv[0], 5), gv[1])
        for gv in grads_and_vars
      ]
      optimizer = opt.apply_gradients(
        capped_grads_and_vars, global_step=batch)
      return loss, optimizer, outputs
    else:
      return loss, outputs
