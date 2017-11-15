#!/usr/bin/python
import matplotlib
matplotlib.use('Agg')

import numpy as np
from baseRunner import loadData, runMultiThread, runSingleThread
from baseRunner import drawResults, drawMicrosoftResults, extractTableWorkerSafe

counters = xrange(0, 114)
classes = ('scan', 'photo')

classNames = ('S', 'P')
#fileTypes = (0, 7, 16, 27, 37, 47, 58, 70, 81, 92, 104)
fileTypes = (0,)

fileTypeNames = (
    'Norco', 'FreshBaked', 'Bidvest', 'Platinum',
    'PFD', 'NCF', 'Jubilee', 'GlobalFood',
    'SmallGoods', 'Pitchers', 'Tetris')

ocrTextFiles = [
    'data/processed/C/{className}-{counter}-p1-original.xml'.format(
        counter=counter, className=className)
    for className in classes
    for counter in counters
]

imageFiles = [
    'images/C/{className}-{counter}.jpg'.format(
        counter=counter, className=className)
    for className in classes
    for counter in counters
]

model = 'deep/weights/ctcrnn/model.ckpt'

originalItems, items = loadData('data/original/C.csv')
results = runMultiThread(originalItems, items, ocrTextFiles, imageFiles, model,
                         classes, counters, 'images/crops/C',
                         extractTableWorkerSafe)

#drawResults(results, 'out/graphs/C_stats.png',
#            classes, classNames, fileTypes, fileTypeNames)
drawResults(results, 'out/graphs/C_stats.png',
            classes, classNames, fileTypes, fileTypeNames)
