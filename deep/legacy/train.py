import os
from keras import backend as K
from keras.optimizers import SGD
from keras.utils.data_utils import get_file
from keras.callbacks import TensorBoard

from deep.legacy.helpers import decode_text_batch, decode_number_batch
from deep.legacy.model import OCRModel
from deep.legacy.text_generate import TextImageGenerator
from deep.legacy.number_generate import NumberImageGenerator
from deep.legacy.vizualize import VizCallback
from deep.constants import *


def train(run_name, start_epoch, stop_epoch, img_w, img_h):
    # Input Parameters
    words_per_epoch = WORDS_PER_EPOCH
    val_split = 0.2
    val_words = int(words_per_epoch * (val_split))

    fdir = os.path.dirname(get_file(
        'wordlists.tgz',
        origin='http://www.isosemi.com/datasets/wordlists.tgz', untar=True))

    text_img_gen = TextImageGenerator(
        monogram_file=os.path.join(fdir, 'wordlist_mono_clean.txt'),
        bigram_file=os.path.join(fdir, 'wordlist_bi_clean.txt'),
        minibatch_size=MINIBATCH_SIZE,
        img_w=img_w,
        img_h=img_h,
        downsample_factor=(POOL_SIZE ** CONV_COUNT),
        val_split=words_per_epoch - val_words
    )
    number_img_gen = NumberImageGenerator(
        minibatch_size=MINIBATCH_SIZE,
        img_w=img_w,
        img_h=img_h,
        downsample_factor=(POOL_SIZE ** CONV_COUNT),
        val_split=words_per_epoch - val_words
    )
    img_gen = number_img_gen
    decode_func = decode_number_batch

    model, input_data, y_pred = OCRModel(
        img_w, img_h,
        NUMBER_GENERATOR_OUPUT_SIZE,
        img_gen.absolute_max_string_len).build()

    # clipnorm seems to speeds up convergence
    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True, clipnorm=5)

    # the loss calc occurs elsewhere, so use a dummy lambda func for the loss
    model.compile(loss={'ctc': lambda y_true, y_pred: y_pred}, optimizer=sgd)
    if start_epoch > 0:
        weight_file = os.path.join(OUTPUT_DIR, os.path.join(
            run_name, 'weights%02d.h5' % (start_epoch - 1)))
        model.load_weights(weight_file)
    # captures output of softmax so we can decode the output during visualization
    test_func = K.function([input_data], [y_pred])

    viz_cb = VizCallback(run_name, test_func, img_gen.next_val(), decode_func)

    tb_log_dir = os.path.join(OUTPUT_DIR, os.path.join(run_name, 'logs'))
    tb_cb = TensorBoard(log_dir=tb_log_dir,
                        histogram_freq=1,
                        write_graph=True,
                        write_images=True)
    model.fit_generator(generator=img_gen.next_train(),
                        samples_per_epoch=(words_per_epoch - val_words),
                        nb_epoch=stop_epoch,
                        validation_data=img_gen.next_val(),
                        nb_val_samples=val_words,
                        callbacks=[viz_cb, img_gen, tb_cb],
                        initial_epoch=start_epoch)
