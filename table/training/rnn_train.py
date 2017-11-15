from tqdm import tqdm
from deep.helpers import count_number_trainable_params
import tensorflow as tf
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
import numpy as np
from table.training.reader import extract

np.random.seed(1234)


class Config(object):

  def __init__(self,
               max_length=0,
               feature_size=0,
               minibatch_size=0,
               num_batches=0,
               rnn_size=32,
               rnn_num_layers=2,
               num_classes=12,
               learning_rate=0.01):
    self.minibatch_size = minibatch_size
    self.learning_rate = learning_rate
    self.rnn_num_layers = rnn_num_layers
    self.rnn_size = rnn_size
    self.max_length = max_length
    self.feature_size = feature_size
    self.num_classes = num_classes
    self.num_batches = num_batches


def cell(rnn_size):
    return tf.contrib.rnn.GRUCell(rnn_size)


class Model(object):

  def __init__(self, x, y, config):

    self.config = config
    with tf.name_scope('Train'):
      with tf.variable_scope("Model", reuse=None):
        loss, optimizer, output, prediction = self.build(x, y, train=True)
    with tf.name_scope('Val') as scope:
      val_x = tf.placeholder(x.dtype, shape=(
        config.minibatch_size,
        config.max_length,
        config.feature_size), name="val_x")
      val_y = tf.placeholder(y.dtype, shape=(
        config.minibatch_size,
        config.max_length), name="val_y")
      with tf.variable_scope("Model", reuse=True):
        val_loss, val_output, val_prediction = self.build(val_x, val_y)

    self.x = x
    self.y = y
    self.loss = loss
    self.output = output
    self.prediction = prediction

    self.val_x = val_x
    self.val_y = val_y
    self.optimizer = optimizer
    self.val_loss = val_loss
    self.val_output = val_output
    self.val_prediction = val_prediction


  def build(self, x, y, train=False):
    rnn_size = self.config.rnn_size
    rnn_num_layers = self.config.rnn_num_layers
    feature_size = self.config.feature_size
    max_length = self.config.max_length
    minibatch_size = self.config.minibatch_size
    num_batches = self.config.num_batches
    num_classes = self.config.num_classes

    rnn_input = x
    for k in range(rnn_num_layers):
      with tf.variable_scope("gru{}".format(k + 1)):
        (output_fw, output_bw), states = (
          tf.nn.bidirectional_dynamic_rnn(
            cell(rnn_size),
            cell(rnn_size),
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
        rnn_size * 2,
        num_classes
      ], tf.float32)
    fc2_biases = tf.get_variable("fc2_biases",  [num_classes], tf.float32)

    logits = tf.matmul(reshape, fc2_weights) + fc2_biases
    logits = tf.reshape(
      logits,
      [output_shape[0], output_shape[1], num_classes])

    loss = tf.reduce_sum(tf.reduce_mean(
      tf.nn.sparse_softmax_cross_entropy_with_logits(
        labels=y,
        logits=logits
      ), axis=0))

    outputs = tf.nn.softmax(logits)
    predictions = tf.argmax(outputs, 2)

    if train:
      batch = tf.Variable(0, trainable=False, name="batch")
      learning_rate = tf.train.exponential_decay(
          self.config.learning_rate,
          batch * minibatch_size,
          num_batches,
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
      return loss, optimizer, outputs, predictions
    else:
      return loss, outputs, predictions


def prepare_model(x_train, y_train):

  N, max_length, feature_size = x_train.shape
  N, max_length = y_train.shape
  minibatch_size = 1
  num_batches = N // minibatch_size

  with tf.Graph().as_default() as graph:

    x = tf.convert_to_tensor(x_train, dtype=np.float32)
    y = tf.convert_to_tensor(y_train, dtype=np.int32)
    i = tf.train.range_input_producer(num_batches, shuffle=False).dequeue()

    x = tf.strided_slice(
      x,
      [i, 0, 0],
      [i + minibatch_size, max_length, feature_size])
    x.set_shape([minibatch_size, max_length, feature_size])

    y = tf.strided_slice(
      y,
      [i, 0],
      [i + minibatch_size, max_length])
    y.set_shape([minibatch_size, max_length])

    model = Model(x, y, Config(
      max_length=max_length,
      feature_size=feature_size,
      minibatch_size=minibatch_size,
      num_batches=num_batches
    ))
    saver = tf.train.Saver()
    #print "Total number of trainable params: {:,}".format(
    #  count_number_trainable_params())

  return model, saver, graph, num_batches


def execute_training_epoch(model, session, epoch, y_train):
  N, _ = y_train.shape
  num_batches = N // model.config.minibatch_size

  pbar = tqdm(range(num_batches), unit="batch")
  losses = []
  predictions = []
  for i in pbar:
    p, _, l = session.run([model.prediction,
                           model.optimizer,
                           model.loss], feed_dict={})
    losses.append(l)
    predictions.append(p.flatten())
    pbar.set_description('Epoch %d: Minibatch loss: %.3f' % (
      epoch, np.mean(losses)))
  predictions = np.array(predictions)
  score = accuracy_score(y_train.flatten(), predictions.flatten())
  print('Training accuracy: %.3f' % (score * 100))


def execute_test_epoch(model, session, x):
  minibatch_size = model.config.minibatch_size
  N, _, _ = x.shape
  num_batches = N // minibatch_size

  pbar = tqdm(range(num_batches), unit="batch")
  predictions = []
  for i in pbar:
    p, _ = session.run([model.val_prediction, model.val_loss], feed_dict={
      model.val_x: x[i * minibatch_size:(i + 1) * minibatch_size, ...],
      model.val_y: np.zeros((minibatch_size, model.config.max_length))
    })
    predictions.append(p.flatten())
  predictions = np.array(predictions)
  return predictions


def execute_eval_epoch(model, session, epoch, x_val, y_val):
  minibatch_size = model.config.minibatch_size
  N_val, _, _ = x_val.shape
  num_batches_val = N_val // minibatch_size

  pbar = tqdm(range(num_batches_val), unit="batch")
  losses = []
  predictions = []
  for i in pbar:
    p, l = session.run([model.val_prediction, model.val_loss], feed_dict={
      model.val_x: x_val[i * minibatch_size:(i + 1) * minibatch_size, ...],
      model.val_y: y_val[i * minibatch_size:(i + 1) * minibatch_size, ...]
    })
    losses.append(l)
    predictions.append(p.flatten())
    pbar.set_description('Epoch %d: Eval loss: %.3f' % (
      epoch, np.mean(losses)))
  predictions = np.array(predictions)
  score = accuracy_score(y_val.flatten(), predictions.flatten())
  print('Eval accuracy: %.3f' % (score * 100))
  return score


def train_validate(x_train, y_train, x_val, y_val, epochs=25):

  model, saver, graph, num_batches = prepare_model(x_train, y_train)

  with tf.Session(graph=graph) as session:

    session.run(tf.local_variables_initializer())
    session.run(tf.global_variables_initializer())

    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(coord=coord)

    for epoch in range(epochs):
      execute_training_epoch(model, session, epoch, y_train)
      score = execute_eval_epoch(model, session, epoch, x_val, y_val)

    return score


def train(x_train, y_train, epochs=25):

  model, saver, graph, num_batches = prepare_model(x_train, y_train)

  with tf.Session(graph=graph) as session:

    session.run(tf.local_variables_initializer())
    session.run(tf.global_variables_initializer())

    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(coord=coord)

    for epoch in range(epochs):
      execute_training_epoch(model, session, epoch, y_train)
      save_path = saver.save(
        session, "out/deep/tensorflow/model-{}.ckpt".format(epoch))


def prepare_data(filename):
  features, targets, filenames = extract(filename, with_null=True)

  last_filename = None
  x = []
  y = []
  max_length = 0
  for feature_vector, target, filename in zip(features, targets, filenames):
    if filename != last_filename:
      x.append([])
      y.append([])
    x[-1].append(feature_vector)
    y[-1].append(target)
    max_length = max(max_length, len(x[-1]))
    last_filename = filename

  feature_size = len(x[0][0])
  for x_group, y_group in zip(x, y):
    L = len(x_group)
    for i in range(L, max_length):
      x_group.append([0] * feature_size)
      y_group.append(0)

  x = np.array(x)
  y = np.array(y)

  N, _ = y.shape
  permutation = np.random.permutation(N)
  x = x[permutation]
  y = y[permutation]
  return x, y


def predict(x, model_filename):
  _, max_length, feature_size = x.shape
  model, saver, graph, num_batches = prepare_model(
    np.zeros((1, max_length, feature_size)),
    np.zeros((1, max_length)))

  with tf.Session(graph=graph) as session:

    saver.restore(session, model_filename)
    return execute_test_epoch(model, session, x)


def run():

  features, targets = prepare_data('out/train.dat')
  kf = KFold(n_splits=5)
  scores = []
  for train_index, test_index in kf.split(features):
    train_features = features[train_index]
    test_features = features[test_index]
    train_targets = targets[train_index]
    test_targets = targets[test_index]
    score = train_validate(train_features, train_targets,
                           test_features, test_targets)
    scores.append(score)

  train(features, targets)
  predictions = predict(features, 'out/deep/tensorflow/model-24.ckpt')
  print 'Training score: {}'.format(
    accuracy_score(targets.flatten(), predictions.flatten()))
  print 'Evaluation score: {}'.format(np.mean(scores))


if __name__ == "__main__":
    run()
