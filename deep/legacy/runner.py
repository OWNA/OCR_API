#!/usr/bin/python

# This deep learning pipeline was initially inspired from the
# Kera example
# https://github.com/fchollet/keras/blob/master/examples/image_ocr.py

import datetime
import numpy as np

from deep.legacy.train import train
from deep.constants import IMAGE_WIDTH, IMAGE_HEIGHT
np.random.seed(55)

run_name = datetime.datetime.now().strftime('%Y:%m:%d:%H:%M:%S')
run_name = 'thin-dollars'
train(run_name, 0, 30, IMAGE_WIDTH, IMAGE_HEIGHT)
