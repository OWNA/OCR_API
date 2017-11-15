#!/usr/bin/python
import matplotlib
matplotlib.use('Agg')

import random
import numpy as np
from baseRunner import loadData, runMultiThread, runSingleThread
from baseRunner import extractTableWorkerSafe, drawResults, drawMicrosoftResults

random.seed(1234)

counters = xrange(0, 75)
classes = ('A', 'B', 'C', 'D', 'E')

classNames = ('Natural Light',
              'Curved',
              'Room Light',
              'Perspective',
              'Marked')
fileTypes = (0,)
fileTypeNames = ('',)

ocrTextFiles = [
    'data/processed/B/{counter}{className}-p1-original.xml'.format(
        counter=(counter + 1), className=className)
    for className in classes
    for counter in counters
]

imageFiles = [
    'images/B/{className}/{counter}{className}.jpg'.format(
        counter=(counter + 1), className=className)
    for className in classes
    for counter in counters
]

model = 'deep/weights/ctcrnn/model.ckpt'

originalItems, items = loadData('data/original/B.csv')
#for originalItem in originalItems:
#    if len(originalItem) > 2:
#        index = random.randint(0, len(originalItem) - 1)
#        originalItem.pop(index)

results = runMultiThread(originalItems, items, ocrTextFiles, imageFiles, model,
                         classes, counters, 'images/crops/B',
                         extractTableWorkerSafe)

drawResults(results, 'out/graphs/B_stats.png',
            classes, classNames, fileTypes, fileTypeNames)
