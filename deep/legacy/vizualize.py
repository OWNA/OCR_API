import os
import editdistance
from keras import backend as K
import keras.callbacks
import matplotlib.pyplot as plt
import glob
import re
import cv2
import numpy as np

from deep.constants import OUTPUT_DIR, IMAGE_WIDTH, IMAGE_HEIGHT
from deep.legacy.evaluate import expand_image_for_evaluation


class VizCallback(keras.callbacks.Callback):

    def __init__(self, run_name, test_func, img_gen,
                 decode_func, num_display_words=6):
        self.test_func = test_func
        self.decode_func = decode_func
        self.output_dir = os.path.join(
            OUTPUT_DIR, run_name)
        self.img_gen = img_gen
        self.num_display_words = num_display_words
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def show_edit_distance(self, num):
        num_left = num
        mean_norm_ed = 0.0
        mean_ed = 0.0
        accuracy = 0.
        while num_left > 0:
            word_batch = next(self.img_gen)[0]
            num_proc = min(word_batch['the_input'].shape[0], num_left)
            decoded_res = self.decode_func(self.test_func,
                                           word_batch['the_input'][0:num_proc])
            for j in range(0, num_proc):
                edit_dist = editdistance.eval(
                    decoded_res[j],
                    word_batch['source_str'][j])
                mean_ed += float(edit_dist)
                try:
                    if float(decoded_res[j]) == float(word_batch['source_str'][j]):
                        accuracy += 1
                except Exception:
                    pass
                mean_norm_ed += float(edit_dist) / len(
                    word_batch['source_str'][j])
            num_left -= num_proc
        mean_norm_ed = mean_norm_ed / num
        mean_ed = mean_ed / num
        accuracy = accuracy / num
        print('\nOut of %d samples:  Mean edit distance: %.3f ' \
              'Mean normalized edit distance: %0.3f Accuracy: %0.3f' % (
                  num, mean_ed, mean_norm_ed, accuracy))


    def dev_evaluate(self, num, epoch):
        p = num // 7
        imageFilenames  = glob.glob("images/crops/B/A_*[0-9.].png")[0:p]
        imageFilenames += glob.glob("images/crops/B/B_*[0-9.].png")[0:p]
        imageFilenames += glob.glob("images/crops/B/C_*[0-9.].png")[0:p]
        imageFilenames += glob.glob("images/crops/B/D_*[0-9.].png")[0:p]
        imageFilenames += glob.glob("images/crops/B/E_*[0-9.].png")[0:p]
        imageFilenames += glob.glob("images/crops/C/scan_*[0-9.].png")[0:p]
        imageFilenames += glob.glob("images/crops/C/photo_*[0-9.].png")[0:p]
        images = []
        ground_truth = []
        print len(imageFilenames)
        for imageFilename in imageFilenames:
            pattern = re.compile(".*_([0-9.]+).png")
            matches = pattern.match(imageFilename)
            ground_truth.append(matches.group(1))
            image = cv2.imread(imageFilename, 1)
            image = image[:,:,0]
            image = expand_image_for_evaluation(image, IMAGE_WIDTH, IMAGE_HEIGHT)
            image = np.reshape(image.T, (IMAGE_WIDTH, IMAGE_HEIGHT, 1))
            images.append(image)

        results = []
        N = len(ground_truth)
        for n in range(N // 256 + 1):
            results += self.decode_func(
                self.test_func,
                images[n * 256:min((n + 1) * 256, N)])
        mismatches = [0] * 7
        counts = [0] * 7

        selectedImages = np.random.choice(range(p), 5)
        fig, _ = plt.subplots()
        k = 0
        for classIndex in range(7):
            for index in selectedImages:
                k += 1
                plt.subplot(7, 5, k)
                i = classIndex * p + index
                plt.imshow(images[i][:,:,0].T, cmap='Greys_r', vmin=0, vmax=1)
                plt.xlabel('Truth = \'%s\'\nDecoded = \'%s\'' % (
                    ground_truth[i], results[i]))
        fig.set_size_inches(30, 18)
        plt.savefig(os.path.join(self.output_dir, 'eval-%02d.png' % (epoch)))

        for idx, (r1, r2) in enumerate(zip(ground_truth, results)):
            typeIdx = idx // p
            try:
                r1 = float(r1)
            except Exception:
                continue
            counts[typeIdx] += 1
            try:
                r2 = float(r2)
                if r1 != r2:
                    mismatches[typeIdx] += 1
            except Exception:
                mismatches[typeIdx] += 1
        for count, mismatch in zip(counts, mismatches):
            accuracy = (count - mismatch) / float(count)
            print('Out of %d eval samples Accuracy %0.3f' % (count, accuracy))
        total_counts = np.sum(counts)
        total_mismatches = float(np.sum(mismatches))
        total_accuracy = (total_counts - total_mismatches) / total_counts
        print 'Out of %d eval samples Accuracy %0.3f' % (total_counts, total_accuracy)


    def on_epoch_end(self, epoch, logs={}):
        self.model.save_weights(os.path.join(
            self.output_dir,
            'weights%02d.h5' % (epoch)))
        self.show_edit_distance(1024)
        self.dev_evaluate(2048, epoch)
        word_batch = next(self.img_gen)[0]
        res = self.decode_func(
            self.test_func,
            word_batch['the_input'][0:self.num_display_words])
        if word_batch['the_input'][0].shape[0] < 256:
            cols = 2
        else:
            cols = 1
        fig, _ = plt.subplots()
        for i in range(self.num_display_words):
            plt.subplot(self.num_display_words // cols, cols, i + 1)
            if K.image_dim_ordering() == 'th':
                the_input = word_batch['the_input'][i, 0, :, :]
            else:
                the_input = word_batch['the_input'][i, :, :, 0]
            plt.imshow(the_input.T, cmap='Greys_r', vmin=0, vmax=1)
            plt.xlabel('Truth = \'%s\'\nDecoded = \'%s\'' % (
                word_batch['source_str'][i], res[i]))
        fig.set_size_inches(10, 13)
        plt.savefig(os.path.join(self.output_dir, 'dev-eval-%02d.png' % (epoch)))
