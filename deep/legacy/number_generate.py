import numpy as np

from deep.legacy.generate import AbstractImageGenerator
from deep.paint import paint_text
from deep.constants import ABSOLUTE_MAX_STRING_LEN, NUMBER_GENERATOR_OUPUT_SIZE
from deep.constants import WORD_LIST_SIZE


def number_to_labels(text, num_classes):
    ret = []
    for char in text:
        if char >= '0' and char <= '9':
            ret.append(ord(char) - ord('0'))
        elif char == '.':
            ret.append(num_classes - 2)
        elif char == ' ':
            ret.append(num_classes - 1)
        else:
            raise Exception('Unsupported character {0} in word {1}'.format(
                char, text))
    return ret


class NumberImageGenerator(AbstractImageGenerator):

    def __init__(self, minibatch_size,
                 img_w, img_h, downsample_factor, val_split,
                 absolute_max_string_len=16):

        self.minibatch_size = minibatch_size
        self.img_w = img_w
        self.img_h = img_h
        self.downsample_factor = downsample_factor
        self.val_split = val_split
        self.blank_label = NUMBER_GENERATOR_OUPUT_SIZE - 1
        self.absolute_max_string_len = ABSOLUTE_MAX_STRING_LEN
        self.last_epoch = -1

    def build_word_list(self, num_words, max_string_len=None,
                        whole_number_fraction=0.5):
        assert max_string_len <= self.absolute_max_string_len
        assert num_words % self.minibatch_size == 0
        assert (self.val_split * num_words) % self.minibatch_size == 0
        self.num_words = num_words
        self.string_list = [''] * self.num_words
        self.max_string_len = max_string_len
        self.Y_data = np.ones([self.num_words, self.absolute_max_string_len]) * -1
        self.X_text = []
        self.Y_len = [0] * self.num_words

        for i in xrange(self.num_words):
            number_size = np.random.randint(max_string_len) + 1
            number = np.random.randint(10 ** number_size)
            if np.random.rand() < whole_number_fraction:
                fraction_position = np.random.randint(min(3, number_size)) + 1
                number = number / 10. ** fraction_position
            if number < 0.001:
                number = 0
            word = str(number)
            self.Y_len[i] = len(word)
            self.Y_data[i, 0:len(word)] = number_to_labels(
                word, NUMBER_GENERATOR_OUPUT_SIZE)
            self.X_text.append(word)

        assert len(self.X_text) == self.num_words

        self.Y_len = np.expand_dims(np.array(self.Y_len), 1)

        self.cur_val_index = self.val_split
        self.cur_train_index = 0

    def on_train_begin(self, logs={}):
        self.paint_func = lambda text: paint_text(
            text, self.img_w, self.img_h,
            multi_fonts=True,
            translate=True,
            rotate=True,
            shapes=False,
            background=False,
            noise=False,
            artifacts=False,
            warping=False,
            other_chars=False)
        self.build_word_list(WORD_LIST_SIZE, 7)

    def on_epoch_begin(self, epoch, logs={}):
        if epoch >= 4 and self.last_epoch < 4:
            self.paint_func = lambda text: paint_text(
                text, self.img_w, self.img_h,
                multi_fonts=True,
                translate=True,
                rotate=True,
                shapes=True,
                background=True,
                noise=False,
                artifacts=False,
                warping=False,
                other_chars=False
            )
        if epoch >= 10 and self.last_epoch < 10:
            self.paint_func = lambda text: paint_text(
                text, self.img_w, self.img_h,
                multi_fonts=True,
                translate=True,
                rotate=True,
                shapes=True,
                background=True,
                noise=True,
                artifacts=True,
                warping=True,
                other_chars=True
            )
        # Add noise and other chars
        self.last_epoch = epoch
