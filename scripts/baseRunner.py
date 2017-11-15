import os
import random
import matplotlib.pyplot as plt
import json
import pickle
import numpy as np
from utils.helpers import *
from matching.line import *
import copy
from multiprocessing import Manager, Process, Pool, cpu_count
import cv2
from utils.geometry import rotate
from deep.evaluate import predict_images
from deep.constants import IMAGE_WIDTH, IMAGE_HEIGHT
from flags import USE_DEEP_LEARNING_HINTS
from utils.files import XMLFile, SimpleWord, JSONFile
import traceback
from utils.loader import loadData
from PIL import Image, ExifTags


def extractTableWorkerSafe(fileIndex):
    try:
        return extractTableWorker(fileIndex)
    except Exception as e:
        filename = _ocrTextFiles[fileIndex]
        print "Failed to process {}".format(filename)
        traceback.print_exc()
        raise e


def drawImageCells(image, filename, cells):
    image_f = image.copy()
    image_c = image.copy()
    num = 0
    for cell in cells:
        xL = cell.l
        xR = cell.r
        yT = cell.t
        yB = cell.b
        x1, y1 = int(xL), int(yT)
        x3, y3 = int(xR), int(yB)
        if cell.is_number():
            color = (0, 255, 0)
        elif cell.is_possible_number():
            color = (255, 0, 255)
        elif cell.is_description():
            color = (0, 255, 255)
        elif cell.is_other():
            color = (0, 0, 255)
        cv2.rectangle(image_f, (x1, y1), (x3, y3), color, -1)
        num += 1
    image_f = image_c * 0.4 + image_f * 0.6
    #image_f = cv2.resize(image_f, (0,0), fx=0.5, fy=0.5)
    cv2.imwrite(filename, image_f)


def extractTableWorkerMicrosoft(fileIndex):

    classIndex = fileIndex // len(_counters)
    className = _classes[classIndex]
    counter = _counters[fileIndex % len(_counters)]
    filename = _ocrTextFiles[fileIndex]
    filenameJ = filename.replace('-p1-original.xml', '-microsoft.json')

    if not os.path.isfile(filenameJ):
        return None

    if not os.path.isfile(filename):
        return None

    xmlFile = XMLFile(filename)
    xmlFile.parseWithVariants(split=True)
    imageFilename = _imageFiles[fileIndex]
    image = Image.open(imageFilename)

    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation] == 'Orientation':
            break
    exif_orientation = None

    width, height = image.width, image.height
    if image._getexif():
        exif = dict(image._getexif().items())
        exif_orientation = exif[orientation]
        if exif_orientation in (6, 8):
            width, height = height, width

    fileJ = JSONFile(filenameJ)
    # The width and height of the original image without the application
    # of Exif rotations
    fileJ.parse(width, height)

    cells = extractTable(xmlFile.words, _originalItems[counter])

    matches = 0
    mismatches = 0
    total_words = 0

    for cell in cells:
        if not cell.is_number():
            continue
        total_words += 1
        cell = cell.rotate(-xmlFile.rotation)
        # Use the XML file width and height as they represent the width
        # and height after applying the exif orientation rotation.
        cell = cell.correct_exif(
            exif_orientation, xmlFile.width, xmlFile.height)
        interesect = 0
        matching_word = None
        for word in fileJ.words:
            if cell.intersect(word) > interesect:
                interesect = cell.intersect(word)
                matching_word = word
        if not matching_word:
            pass
            #print 'missing', cell
        else:
            if matching_word.content == cell.content:
                matches += 1
            else:
                mismatches += 1
                #print 'mismatch', matching_word, cell


    return counter, classIndex, matches, mismatches, total_words


def extractTableWorkerFull(fileIndex):

    classIndex = fileIndex // len(_counters)
    className = _classes[classIndex]
    counter = _counters[fileIndex % len(_counters)]

    filename = _ocrTextFiles[fileIndex]
    filenameT = filename.replace('-original', '')


    items = _originalItems[counter]

    if not os.path.isfile(filename) or not items:
        return None

    xmlFile = XMLFile(filename)
    xmlFile.parseWithVariants()

    xmlFileSplit = XMLFile(filename)
    xmlFileSplit.parseWithVariants(split=True)

    imageFilename = _imageFiles[fileIndex]
    image = cv2.imread(imageFilename, 3 | cv2.IMREAD_IGNORE_ORIENTATION)
    width, height, _ = image.shape

    cells = extractTable(xmlFileSplit.words, _originalItems[counter])

    filename = 'out/images/{0}{1}.png'.format(className, counter + 1)
    drawImageCells(image, filename,
                   [cell.rotate(-xmlFile.rotation) for cell in cells])

    cell_images = []
    cell_positions = []
    cell_contents = []
    cell_filenames = []
    index = 0
    for cell in cells:
        if not cell.is_number() and not cell.is_possible_number():
            continue
        xL = cell.l
        xR = cell.r
        yT = cell.t
        yB = cell.b

        dx, dy = (xR - xL) // 2, (yB - yT) // 2
        if dx <= 0 or dy <= 0:
            continue
        dx = int(dx)
        dy = int(dy)
        xx = (xR + xL) // 2
        yy = (yT + yB) // 2
        if cell.is_possible_number():
            dx = int(dx * 1.2)
            dy = int(dy * 1.2)
        dx += 5
        dy += 5
        cell_image = np.ndarray((2 * dy, 2 * dx))
        pattern = re.compile("^\s*(?:\$)?([0-9.]+)\s*$")
        for i in xrange(2 * dy):
            for j in xrange(2 * dx):
                x, y = rotate(xx - dx + j, yy - dy + i,
                              -xmlFile.rotation, rounding=True)
                if y < width and x < height and y >= 0 and x >= 0:
                    cell_image[i, j] = image[y, x, 0]
        if cell.content:
            matches = pattern.match(cell.content)
            content = matches.group(1)
        else:
            content = 'unknown'
        cell_images.append(cell_image)
        cell_positions.append((cell.l, cell.t, cell.r, cell.b))
        cell_contents.append(content)
        cellFilename = _crops_dir + '/{0}_{1}_{2}_{3}.png'.format(
            className, counter + 1, index, content)
        cv2.imwrite(cellFilename, cell_image)
        cell_filenames.append(cellFilename)
        index += 1

    results = []
    hints = []

    if USE_DEEP_LEARNING_HINTS:
        if cell_images:
            results = predict_images(_model, cell_images)

        for result, position, content, cell_filename in zip(
                results, cell_positions, cell_contents, cell_filenames):
            l, t, r, b = position
            if content != str(result) and len(str(result)) > 0:
                w = SimpleWord(result, l, r, t, b)
                hints.append(w)

    xmlFileT = XMLFile(filenameT)
    xmlFileT.parseWithVariants()
    if hints:
        xmlFile.transform(xmlFileT, hints, image)

    failedToComplete, totalSoftErrors, totalErrors = runOptimizer(
        xmlFileT.words + hints,
        _originalItems[counter],
        _items[counter],
        counter,
        className)
    return counter, classIndex, failedToComplete, totalSoftErrors, totalErrors


def extractTableWorker(fileIndex):
    #return extractTableWorkerMicrosoft(fileIndex)
    return extractTableWorkerFull(fileIndex)


_originalItems = None
_ocrTextFiles = None
_imageFiles = None
_model = None
_classes = None
_counters = None
_items = None


def runSingleThread(originalItems, items, ocrTextFiles,
                    imageFiles, model, classes, counters, crops_dir, fn):
    pool = Pool(processes=1)
    global _ocrTextFiles, _imageFiles, _model, _crops_dir
    global _counters, _classes, _originalItems, _items
    _originalItems = originalItems
    _ocrTextFiles = ocrTextFiles
    _model = model
    _imageFiles = imageFiles
    _classes = classes
    _counters = counters
    _items = items
    _crops_dir = crops_dir
    results = []
    for fileIndex in range(len(ocrTextFiles)):
        results.append(fn(fileIndex))
    return results


def runMultiThread(originalItems, items, ocrTextFiles,
                   imageFiles, model, classes, counters, crops_dir, fn):
    global _ocrTextFiles, _imageFiles, _model, _crops_dir
    global _counters, _classes, _originalItems, _items
    _originalItems = originalItems
    _ocrTextFiles = ocrTextFiles
    _imageFiles = imageFiles
    _model = model
    _classes = classes
    _counters = counters
    _items = items
    _crops_dir = crops_dir
    pool = Pool(processes=9)
    results = pool.map(fn, range(len(ocrTextFiles)))
    return results


def drawResults(results, filename, classes, classNames, fileTypes, fileTypeNames):
    nTypes = len(classNames) * len(fileTypeNames)

    classStats = np.zeros((nTypes, 4))

    failedToCompleteF = []
    errorsF = []
    softErrorsF = []

    for result in results:
        if not result:
            continue
        counter, classIndex, failedToComplete, totalSoftErrors, totalErrors = result
        for fileTypeIndex, fileType in enumerate(fileTypes):
            if counter >= fileType:
                currentFileTypeIndex = fileTypeIndex
        classIndex = classIndex + currentFileTypeIndex * len(classes)
        if failedToComplete:
            failedToCompleteF.append(counter)
            classStats[classIndex, 0] += 1
        elif totalErrors > 0:
            errorsF.append(counter)
            classStats[classIndex, 2] += 1
        elif totalSoftErrors > 0:
            softErrorsF.append(counter)
            classStats[classIndex, 1] += 1
        else:
            classStats[classIndex, 3] += 1

    print classStats

    print 'Failed to complete', failedToCompleteF
    print 'Hard errors', errorsF
    print 'Soft errors', softErrorsF

    plt.figure()
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)

    p1 = plt.bar(np.arange(nTypes),
                 classStats[:,0],
                 0.5,
                 color='gray')
    p2 = plt.bar(np.arange(nTypes),
                 classStats[:,1],
                 0.5,
                 bottom=classStats[:,0],
                 color='yellow')
    p3 = plt.bar(np.arange(nTypes),
                 classStats[:,2],
                 0.5,
                 bottom=classStats[:,0] + classStats[:,1],
                 color='red')
    p4 = plt.bar(np.arange(nTypes),
                 classStats[:,3],
                 0.5,
                 bottom=classStats[:,0] + classStats[:,1] + classStats[:,2],
                 color='green')
    plt.legend((p1[0], p2[0], p3[0], p4[0]), (
        'Failed to complete',
        'Soft fail to match',
        'Fail to match',
        'Success'))
    plt.ylim([0,20])
    locs, labels = plt.xticks(
        np.arange(nTypes),
        ['{0} ({1})'.format(fileTypeName, className)
         for fileTypeName in fileTypeNames for className in classNames])
    plt.setp(labels, rotation=80)

    plt.savefig(filename)


def drawMicrosoftResults(results, filename, classes,
                        classNames, fileTypes, fileTypeNames):
    nTypes = len(classNames) * len(fileTypeNames)

    classStats = np.zeros((nTypes, 3))
    counts = np.zeros((nTypes))

    for result in results:
        if not result:
            continue
        counter, classIndex, matches, mismatches, total_words = result
        for fileTypeIndex, fileType in enumerate(fileTypes):
            if counter >= fileType:
                currentFileTypeIndex = fileTypeIndex
        classIndex = classIndex + currentFileTypeIndex * len(classes)
        classStats[classIndex, 0] += matches
        classStats[classIndex, 1] += mismatches
        classStats[classIndex, 2] += total_words - (matches + mismatches)
        counts[classIndex] += total_words

    sums = np.sum(classStats, axis=1)
    classStats = classStats / sums[:, np.newaxis]

    print classStats
    print counts

    plt.figure()
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)

    p1 = plt.bar(np.arange(nTypes),
                 classStats[:,0],
                 0.5,
                 color='gray')
    p2 = plt.bar(np.arange(nTypes),
                 classStats[:,1],
                 0.5,
                 bottom=classStats[:,0],
                 color='yellow')
    p3 = plt.bar(np.arange(nTypes),
                 classStats[:,2],
                 0.5,
                 bottom=classStats[:,0] + classStats[:,1],
                 color='red')
    plt.legend((p1[0], p2[0], p3[0]), (
        'Matched',
        'Mismatched',
        'Missing'))
    plt.ylim([0,1])
    locs, labels = plt.xticks(
        np.arange(nTypes),
        ['{0} ({1})'.format(fileTypeName, className)
         for fileTypeName in fileTypeNames for className in classNames])
    plt.setp(labels, rotation=80)

    plt.savefig(filename)
