from utils.fixmatplot import *

import time
import os
import numpy as np
from scipy import ndimage
from skimage.draw import line
from skimage.util import random_noise
from keras.preprocessing import image
import random
import string
import cv2
from PIL import ImageFont, ImageDraw, Image


from deep.constants import OUTPUT_DIR, FONTS


def paint_for_all_fonts():
    """
    Find the fonts on the traget machine
    """
    output_dir = os.path.join(OUTPUT_DIR, 'fonts')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    index = 0
    images = []
    names = []
    total = []
    for font_path in FONTS[:200]:
        string = 'abcdef.' + ' '.join([str(i) for i in xrange(10)])
        font_size = np.random.choice(np.linspace(15, 60, 23))
        start = time.time()
        img = paint_text_with_font(
            string, 512, 64,
            font_path,
            font_size,
            background=True,
            translate=True,
            rotate=True,
            shapes=True,
            noise=True,
            artifacts=True,
            warping=True,
            other_chars=True)
        total.append(time.time() - start)
        filename = '{0}.png'.format(font_path.split('.')[0])
        cv2.imwrite(os.path.join(output_dir, filename), img[:,:] * 255)
    print 'It takes on average %.02fms to finish' % (np.mean(total) * 1000)

def speckle(img):
    if np.random.rand() < 0.5:
        blur = ndimage.gaussian_filter(
            np.random.randn(*img.shape) *
            np.random.uniform(0, 0.3),
            2 + np.random.randint(4))
        img = (img + blur)
        img[img > 1] = 1
        img[img <= 0] = 0

    img = ndimage.gaussian_filter(
        img, np.random.choice([0, 0, 0, 0, 0, 1, 2]))
    img = random_noise(
        img, mode='s&p', amount=np.random.choice([0, 0, 0, 0.05, 0.1]))
    return img


# paints the string in a random location the bounding box
# also uses a random font, a slight random rotation,
# and a random amount of noise

def paint_text(text, w, h,
               multi_fonts=False,
               translate=False,
               rotate=False,
               noise=False,
               artifacts=False,
               warping=False,
               shapes=False,
               background=False,
               other_chars=False):
    if multi_fonts:
        font_path = np.random.choice(FONTS)
        font_size = np.random.choice(np.linspace(15, 60, 23))
    else:
        font_path = os.listdir(FONTS_DIRECTORY)[0]
        font_size = 22
    return paint_text_with_font(text, w, h,
                                font_path,
                                font_size,
                                translate=translate,
                                rotate=rotate,
                                noise=noise,
                                artifacts=artifacts,
                                warping=warping,
                                shapes=shapes,
                                background=background,
                                other_chars=other_chars)


def elastic_transform(image, alpha, sigma):
    """Elastic deformation of images as described in [Simard2003]
       Simard, Steinkraus and Platt, "Best Practices for
       Convolutional Neural Networks applied to Visual Document Analysis", in
       Proc. of the International Conference on Document Analysis and
       Recognition, 2003.
    """
    shape = image.shape
    dx = ndimage.gaussian_filter((np.random.rand(*shape) * 2 - 1), sigma,
                                 mode="constant", cval=0) * alpha
    dy = ndimage.gaussian_filter((np.random.rand(*shape) * 2 - 1), sigma,
                                 mode="constant", cval=0) * alpha
    x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
    indices = np.reshape(y + dy, (-1, 1)), np.reshape(x + dx, (-1, 1))

    return ndimage.map_coordinates(image, indices, order=1).reshape(shape)


def morphological_ops(image):
    if np.random.rand() < 0.3:
        initial_count = np.sum(image == 1)
        count = initial_count
        new_image = image
        size = 0
        while count > initial_count * 0.4:
            size += 1
            new_image = cv2.erode(image * 255, np.ones((size, size)),
                                  iterations=1) / 255.
            count = np.sum(new_image == 1)
        if size:
            image = cv2.erode(image * 255, np.ones((size - 1, size - 1)),
                              iterations=1) / 255.
    elif np.random.rand() < 0.3:
        image = cv2.dilate(image * 255, np.ones((4, 4)), iterations=1) / 255.
    return image


def paint_text_with_font(text, w, h,
                         font_path,
                         font_size,
                         translate=False,
                         rotate=False,
                         noise=False,
                         artifacts=False,
                         warping=False,
                         shapes=False,
                         background=False,
                         other_chars=False):
    word = ''
    if other_chars:
        if np.random.rand() < 0.4:
            text = '$' + text
        if np.random.rand() < 0.4:
            word =  ''.join(random.choice(string.ascii_letters)
                            for _ in range(random.randint(1,5)))
    font = ImageFont.truetype(font_path, int(font_size))
    a = Image.fromarray(np.zeros((h, w)))
    left_x = 0
    top_y = 0
    left_x_2 = 0
    draw = ImageDraw.Draw(a)
    size = draw.textsize(text, font=font)
    size_2 = draw.textsize(word, font=font)
    offset = font.getoffset(text)
    offset_2 = font.getoffset(word)
    max_shift_x = max(w - size[0] - offset[0], 1)
    max_shift_y = max(h - size[1] - offset[1], 1)
    if translate:
        left_x = np.random.randint(0, max_shift_x)
        top_y = np.random.randint(0, max_shift_y)
        if left_x > max_shift_x * 0.5:
            left_x_2 = left_x - size_2[0] * np.random.choice([1, 1.5, 2])
        else:
            left_x_2 = left_x + size[0] * np.random.choice([1, 1.5, 2])
    draw.text((left_x, top_y), text, font=font)
    draw.text((left_x_2, top_y), word, font=font)
    a = np.array(a)
    indices = np.indices((h, w))
    indices = zip(indices[0].flatten(), indices[1].flatten())
    if artifacts:
        a = morphological_ops(a)
    a = 1 - a
    if background:
        background_choices = [1, 1, 1, 1, 1, 1, .9, .8, .7, .6, .5]
        background_color = np.random.choice(background_choices)
        a[a == 1] = background_color
        color_choices = [0, 0, 0, 0, 0, 0.1, 0.1, 0.1, 0.2, 0.3]
        color_choices = np.array(color_choices)
        color_choices = color_choices[color_choices < background_color]
        a[a == 0] = np.random.choice(color_choices)
    a = np.expand_dims(a, axis=0)
    if rotate:
        a = image.random_rotation(a,  5 * (w - left_x) / w + 1)
    a = np.squeeze(a, axis=0)
    if noise:
        a = speckle(a)
    if shapes:
        if np.random.rand() < 0.5:
            color = np.random.uniform(0, 1)
        else:
            color = 0
        if np.random.rand() < 0.5:
            rows = np.random.randint(3)
            cols = np.random.randint(3)
            m = np.random.choice([1, 1, 1, 2, 3, 4])
            r_points = np.random.randint(h - m, size=rows) if rows else []
            c_points = np.random.randint(w - m, size=cols) if cols else []
            for c in c_points:
                for k in range(m):
                    rr, cc = line(0, c + k, h - 1, c + k)
                    a[rr, cc] = color
            for r in r_points:
                for k in range(m):
                    rr, cc = line(r + k, 0, r + k, w - 1)
                    a[rr, cc] = color
        elif np.random.rand() < 0.75:
            for _ in range(np.random.randint(3)):
                m = np.random.randint(10)
                c0 = np.random.randint(w - m)
                c1 = np.random.randint(w - m)
                r0 = np.random.randint(h - m)
                r1 = np.random.randint(h - m)
                for k in range(m):
                    rr, cc = line(r0 + k, c0, r1 + k, c1)
                    a[rr, cc] = color
    if artifacts:
        scale = np.random.choice([1, 1, 1, 1, 1.5, 1.5, 1.5, 2, 2])
        a = cv2.resize(a, (int(w / scale), int(h / scale)))
        a = cv2.resize(a, (w, h))
    if warping:
        alpha, sigma = [
            [30, 3], [30, 4], [20, 2], [10, 2],
            [1, 1], [1, 1], [1, 1], [1, 1]
        ][np.random.randint(8)]
        a = elastic_transform(a, alpha, sigma)

    return a

if __name__ == '__main__':
    np.random.seed(55)
    paint_for_all_fonts()
