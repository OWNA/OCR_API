from keras import backend as K
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.layers import Input, Dense, Activation, Dropout
from keras.layers import Reshape, Lambda, merge
from keras.models import Model
from keras.layers.recurrent import GRU

from deep.legacy.helpers import ctc_lambda_func
from deep.constants import POOL_SIZE, CONV_NUM_FILTERS, TIME_DENSE_SIZE, \
    RNN_SIZE, FILTER_SIZE, CONV_COUNT


class OCRModel:

    def __init__(self, img_w, img_h, output_size, absolute_max_string_len):
        self.img_w = img_w
        self.img_h = img_h
        self.output_size = output_size
        self.absolute_max_string_len = absolute_max_string_len

    def build(self):
        if K.image_dim_ordering() == 'th':
            input_shape = (1, self.img_w, self.img_h)
        else:
            input_shape = (self.img_w, self.img_h, 1)

        act = 'relu'
        input_data = Input(name='the_input',
                           shape=input_shape,
                           dtype='float32')
        for i in range(CONV_COUNT):
            name = 'conv{0}'.format(i + 1)
            inner = Convolution2D(CONV_NUM_FILTERS * (2 ** i),
                                  FILTER_SIZE, FILTER_SIZE,
                                  border_mode='same',
                                  activation=act,
                                  init='he_normal',
                                  name=name)(input_data if i == 0 else inner)
            name = 'max{0}'.format(i + 1)
            inner = MaxPooling2D(pool_size=(POOL_SIZE, POOL_SIZE), name=name)(inner)

        conv_to_rnn_dims = (self.img_w // (POOL_SIZE ** CONV_COUNT),
                            (self.img_h // (POOL_SIZE ** CONV_COUNT)) *
                            CONV_NUM_FILTERS * (2 ** (CONV_COUNT - 1)))
        inner = Reshape(target_shape=conv_to_rnn_dims, name='reshape')(inner)

        # cuts down input size going into RNN:
        inner = Dense(TIME_DENSE_SIZE, activation=act, name='dense1')(inner)

        # Two layers of bidirectional GRUs
        # GRU seems to work as well, if not better than LSTM:
        gru_1 = GRU(RNN_SIZE,
                    return_sequences=True,
                    init='he_normal',
                    name='gru1')(inner)
        gru_1b = GRU(RNN_SIZE,
                     return_sequences=True,
                     go_backwards=True,
                     init='he_normal',
                     name='gru1_b')(inner)
        gru1_merged = merge([gru_1, gru_1b], mode='sum')
        gru_2 = GRU(RNN_SIZE,
                    return_sequences=True,
                    init='he_normal',
                    name='gru2')(gru1_merged)
        gru_2b = GRU(RNN_SIZE,
                     return_sequences=True,
                     go_backwards=True,
                     init='he_normal',
                     name='gru2_b')(gru1_merged)

        # transforms RNN output to character activations:
        inner = Dense(self.output_size, init='he_normal',
                      name='dense2')(merge([gru_2, gru_2b], mode='concat'))
        y_pred = Activation('softmax', name='softmax')(inner)
        Model(input=[input_data], output=y_pred).summary()

        labels = Input(name='the_labels',
                       shape=[self.absolute_max_string_len], dtype='float32')
        input_length = Input(name='input_length', shape=[1], dtype='int64')
        label_length = Input(name='label_length', shape=[1], dtype='int64')
        # Keras doesn't currently support loss funcs with extra parameters
        # so CTC loss is implemented in a lambda layer
        loss_out = Lambda(ctc_lambda_func,
                          output_shape=(1,), name='ctc')(
                              [y_pred, labels, input_length, label_length])

        model = Model(
            input=[input_data, labels, input_length, label_length],
            output=[loss_out])
        return model, input_data, y_pred

