import tensorflow as tf
from deep.constants import *


class Config(object):

  def __init__(self,
               attention_size=16,
               conv_num_layers=2,
               conv_num_channels=64,
               conv_filter_width=3,
               conv_pool_size=2,
               rnn_size=256,
               time_dense_size=256,
               rnn_num_layers=2,
               learning_rate=0.01):
    self.attention_size = attention_size
    self.conv_num_layers = conv_num_layers
    self.conv_num_channels = conv_num_channels
    self.conv_filter_width = conv_filter_width
    self.conv_pool_size = conv_pool_size
    self.rnn_size = rnn_size
    self.time_dense_size = time_dense_size
    self.learning_rate = learning_rate
    self.rnn_num_layers = rnn_num_layers


def cell(rnn_size, attention_size=0):
  with_attention = attention_size > 0
  if with_attention:
    return tf.contrib.rnn.AttentionCellWrapper(
      cell(rnn_size), attention_size,
      state_is_tuple=True,
      reuse=tf.get_variable_scope().reuse)
  else:
    return tf.contrib.rnn.GRUCell(rnn_size)


class Model(object):

  def __init__(self, x, y, config):

    self.config = config
    with tf.name_scope('Train'):
      with tf.variable_scope("Model", reuse=None):
        loss, optimizer, prediction, output = self.build(
          x, y, train=True)
    with tf.name_scope('Val') as scope:
      val_x = tf.placeholder(x.dtype, shape=(
        MINIBATCH_SIZE, IMAGE_WIDTH, IMAGE_HEIGHT, 1), name="val_x")
      val_y = tf.placeholder(y.dtype, shape=(
        MINIBATCH_SIZE, ABSOLUTE_MAX_STRING_LEN), name="val_y")
      with tf.variable_scope("Model", reuse=True):
        val_loss, val_prediction, val_output = self.build(
          val_x, val_y)

    self.x = x
    self.y = y
    self.loss = loss
    self.prediction = prediction
    self.output = output

    self.val_x = val_x
    self.val_y = val_y
    self.optimizer = optimizer
    self.val_loss = val_loss
    self.val_prediction = val_prediction
    self.val_output = val_output


  def build(self, x, y, train=False):
    idx = tf.where(tf.not_equal(y, -1))
    y_sparse = tf.SparseTensor(idx, tf.gather_nd(y, idx), y.get_shape())

    conv_num_channels = self.config.conv_num_channels
    conv_filter_width = self.config.conv_filter_width
    conv_num_layers = self.config.conv_num_layers
    conv_pool_size = self.config.conv_pool_size

    time_dense_size = self.config.time_dense_size
    attention_size = self.config.attention_size
    rnn_size = self.config.rnn_size
    rnn_num_layers = self.config.rnn_num_layers

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

    fc1_weights = tf.get_variable(
      "fc1_weights",
      [
        IMAGE_HEIGHT // 4 * conv_num_channels * 2,
        time_dense_size
      ], tf.float32)
    fc1_biases = tf.get_variable("fc1_biases", [time_dense_size], tf.float32)
    pool_shape = pool.get_shape().as_list()
    reshape = tf.reshape(
        pool,
        [pool_shape[0] * pool_shape[1], pool_shape[2] * pool_shape[3]])
    hidden = tf.nn.relu(tf.matmul(reshape, fc1_weights) + fc1_biases)
    reshape = tf.reshape(
        hidden,
        [pool_shape[0], pool_shape[1], time_dense_size])

    rnn_input = reshape
    for k in range(rnn_num_layers):
      with tf.variable_scope("gru{}".format(k + 1)):
        (output_fw, output_bw), states = (
          tf.nn.bidirectional_dynamic_rnn(
            cell(rnn_size, attention_size),
            cell(rnn_size, attention_size),
            rnn_input,
            dtype=tf.float32,
          ))
        rnn_input = output_fw + output_bw

    output = tf.concat([output_fw, output_bw], axis=-1)
    output_shape = output.get_shape().as_list()
    reshape = tf.reshape(
      output,
      [output_shape[0] * output_shape[1], output_shape[2]])

    fc2_weights = tf.get_variable(
      "fc2_weights",
      [
        time_dense_size * 2,
        NUMBER_GENERATOR_OUPUT_SIZE
      ], tf.float32)
    fc2_biases = tf.get_variable(
      "fc2_biases",  [NUMBER_GENERATOR_OUPUT_SIZE], tf.float32)

    logits = tf.matmul(reshape, fc2_weights) + fc2_biases
    logits = tf.reshape(
      logits,
      [output_shape[0], output_shape[1], NUMBER_GENERATOR_OUPUT_SIZE])

    # Remove the first 2 bits in the logits
    logits = tf.slice(
      logits,
      [0, 2, 0],
      [output_shape[0], output_shape[1] - 2, NUMBER_GENERATOR_OUPUT_SIZE])
    loss = tf.reduce_mean(
        tf.nn.ctc_loss(
          y_sparse,
          logits,
          sequence_length=[output_shape[1] - 2
                           for _ in range(output_shape[0])],
          time_major=False
        ))

    sequence_length = tf.constant(
      ABSOLUTE_MAX_STRING_LEN, shape=[MINIBATCH_SIZE])
    outputs = tf.nn.softmax(logits)
    ctc_logits = tf.transpose(logits, [1, 0, 2])
    prediction, _ = tf.nn.ctc_greedy_decoder(ctc_logits, sequence_length)
    prediction = tf.sparse_tensor_to_dense(prediction[0], default_value=-1)
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
      return loss, optimizer, prediction, outputs
    else:
      return loss, prediction, outputs
