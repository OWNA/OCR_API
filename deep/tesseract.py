from PIL import Image
from tesserocr import PyTessBaseAPI
import glob
import  cv2
import re
from tqdm import tqdm
import numpy as np

if __name__ == '__main__':
    images = []
    originals = []
    ground_truth = []

    imageFilenames = glob.glob("images/crops/B/*.png")
    imageFilenames += glob.glob("images/crops/C/*.png")
    for imageFilename in imageFilenames:
        pattern = re.compile(".*_([0-9.]+).png")
        matches = pattern.match(imageFilename)
        ground_truth.append(matches.group(1))
        image = cv2.imread(imageFilename, 1)
        image = image[:,:,0]
        originals.append(image)
        images.append(image)

    results = []
    N = len(images)
    with PyTessBaseAPI() as api:
        api.ReadConfigFile('digits')
        for image in tqdm(images):
            api.SetImage(Image.fromarray(image))
            text = api.GetUTF8Text()
            results.append(text.rstrip().lstrip())
    mismatch = 0.
    N = 0
    for r1, r2, imageFilename, original in zip(
            ground_truth, results, imageFilenames, originals):
        try:
            r1 = float(r1)
        except Exception:
            continue
        N += 1
        try:
            r2 = float(r2)
            if r1 != r2:
                mismatch += 1
                print r1, r2, imageFilename
                cv2.imwrite('out/cells/error{}.png'.format(mismatch), original)
        except Exception:
            mismatch += 1
    print 'Accuracy {0} on {1} samples'.format((N - mismatch) / N, N)
