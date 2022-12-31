
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from recognition.knn import classify_unlabelled_directory, mapChars
import glob
import os

path = './Cells/'


def show_images(images, titles=None):
    n_ims = len(images)
    if titles is None:
        titles = ['(%d)' % i for i in range(1, n_ims + 1)]
    fig = plt.figure()
    n = 1
    for image, title in zip(images, titles):
        a = fig.add_subplot(1, n_ims, n)
        if image.ndim == 2:
            plt.gray()
        plt.imshow(image)
        a.set_title(title)
        n += 1
    fig.set_size_inches(np.array(fig.get_size_inches()) * n_ims)
    plt.show()


def segmentCodes(img):
    img = cv.imread(img, 0)
    img = cv.normalize(img, None, alpha=0, beta=255,
                       norm_type=cv.NORM_MINMAX)
    res, img = cv.threshold(img, 64, 255, cv.THRESH_BINARY)

    contours, hierarchy = cv.findContours((img).astype("uint8"),
                                          cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    contours = sorted(contours, key=lambda ctr: cv.boundingRect(ctr))
    white_img_large_contours = np.ones(img.shape)
    dimensions_contours = []
    for contour in contours:
        (x, y, w, h) = cv.boundingRect(contour)
        if(w*h > 40):
            dimensions_contours.append((x, y, w, h))
            cv.rectangle(white_img_large_contours,
                         (x, y), (x+w, y+h), (0, 0, 255), 1)
    cropped_digits = []
    i = 0
    filtered_img = img
    for dimension in dimensions_contours:
        (x, y, w, h) = dimension
        cropped_digits.append(filtered_img[y-1:y+h+1, x-1:x+w+1])
        imgCopy = filtered_img[y-1:y+h+1, x-1:x+w+1]
        x = imgCopy.shape[1]
        number_of_images = 1
        if(x > 25):
            number_of_images = np.ceil(x / 23.0)
            for j in range(int(number_of_images)):
                imgTemp = cv.resize(imgCopy[:, j*23:(j+1)*23], (200, 100))
                imgTemp = cv.resize(imgTemp, None, fx=3, fy=3,
                                    interpolation=cv.INTER_CUBIC)
                cv.imwrite("outputs/"+str(i)+".jpg", imgTemp)
                i += 1

        else:
            imgCopy = cv.resize(imgCopy, (200, 100))
            imgCopy = cv.resize(imgCopy, None, fx=3, fy=3,
                                interpolation=cv.INTER_CUBIC)
            cv.imwrite("outputs/"+str(i)+".jpg", imgCopy)
            i += 1

    result = classify_unlabelled_directory('./outputs/')
    result = mapChars(result)
    files = glob.glob('/outputs/*')
    for file in files:
        os.remove(file)
    return result

# show_images([img, white_img_large_contours])
# return dimensions_contours, img
# img = cv.imread('./input/q.jpg', 0)
# segmented_dimensions, filtered_img = segmentCodes(255*img)
# show_images(cropped_digits)