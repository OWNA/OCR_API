import tensorflow as tf
from deep.constants import *

def read_and_decode(filename_queue, pad=False):
    reader = tf.TFRecordReader()
    _, serialized_example = reader.read(filename_queue)
    features = tf.parse_single_example(
      serialized_example,
      # Defaults are not specified since both keys are required.
      features={
        'word_length': tf.FixedLenFeature([], tf.int64),
        'image_raw': tf.FixedLenFeature([], tf.string),
        'label_str': tf.FixedLenFeature([], tf.string),
        'label': tf.FixedLenFeature([ABSOLUTE_MAX_STRING_LEN], tf.int64),
        })
    image = tf.decode_raw(features['image_raw'], tf.float32)
    image.set_shape([IMAGE_WIDTH * IMAGE_HEIGHT])
    image = tf.reshape(image, [IMAGE_WIDTH, IMAGE_HEIGHT, 1])
    label = tf.cast(features['label'], tf.int32)
    if pad:
        indices = tf.where(tf.equal(label, -1))
        c = tf.constant(NUMBER_GENERATOR_OUPUT_SIZE,
                        shape=[ABSOLUTE_MAX_STRING_LEN])
        values = tf.gather_nd(c, indices)
        update = tf.scatter_nd(indices, values, [ABSOLUTE_MAX_STRING_LEN])
        label = label + update

    return tf.train.shuffle_batch(
        [image, label],
        batch_size=MINIBATCH_SIZE,
        capacity=30,
        num_threads=2,
        min_after_dequeue=10)

