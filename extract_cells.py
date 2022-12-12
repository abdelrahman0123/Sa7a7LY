# import libraries
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from os import listdir
import glob
import os
from os.path import isfile, join
from utils.commonfunctions import *
mpl.rcParams['image.cmap'] = 'gray'


def getLines(img, binaryImg, x):
    # Kernel Length
    kernelLength = np.array(img).shape[1] // x

    # Vertical Kernel (1 x kernelLength)
    verticalKernel = cv.getStructuringElement(cv.MORPH_RECT, (1, kernelLength))

    # Horizontal Kernel (kernelLength x 1)
    horizontalKernel = cv.getStructuringElement(
        cv.MORPH_RECT, (kernelLength, 1))

    # Apply erosion then dilation to detect vertical lines using the vertical kernel
    erodedImg = cv.erode(binaryImg, verticalKernel, iterations=3)
    verticalLinesImg = cv.dilate(erodedImg, verticalKernel, iterations=3)

    # Apply erosion then dilation to detect horizontal lines using the horizontal kernel
    erodedImg = cv.erode(binaryImg, horizontalKernel, iterations=3)
    horizontalLinesImg = cv.dilate(erodedImg, horizontalKernel, iterations=3)

    return verticalLinesImg, horizontalLinesImg


def getIntersections(pixels):
    intersections = {}
    for i in range(pixels.shape[0]):
        for j in range(pixels.shape[1]):
            if pixels[i][j] != 0:
                if i in intersections:
                    intersections[i].append((i, j))
                else:
                    intersections[i] = []
                    intersections[i].append((i, j))

    keys = list(intersections.keys())
    uniqueKeys = []
    uniqueKeys.append(keys[0])
    for i in range(1, len(keys), 1):
        if (keys[i] - keys[i - 1] > 5):
            uniqueKeys.append(keys[i])

    rows = []
    for i in uniqueKeys:
        rows.append(intersections[i])

    finalIntersections = []
    index = 0
    for row in rows:
        finalIntersections.append([])
        finalIntersections[index].append(row[0])
        for i in range(1, len(row), 1):
            if (row[i][1] - row[i - 1][1] > 5):
                finalIntersections[index].append(row[i])
        index += 1

    return finalIntersections


def houghLines(img, type):
    lines = cv.HoughLinesP(img.astype(np.uint8), 0.5, np.pi/180, 100,
                           minLineLength=0.25*min(img.shape[0], img.shape[1]), maxLineGap=10)

    hough_lines_out = np.zeros(img.shape)
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if (type == "vertical"):
            cv.line(hough_lines_out, (x1, 0),
                    (x2, img.shape[0]), (255, 255, 255), 1)
        else:
            cv.line(hough_lines_out, (0, y1),
                    (img.shape[1], y2), (255, 255, 255), 1)
    return hough_lines_out


def runGetIntersections(imgPath):
    img = cv.imread(imgPath, 0)

    # thresholding
    (thresh, binaryImg) = cv.threshold(
        img, 128, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
    binaryImg = 255 - binaryImg

    verticalLinesImg, horizontalLinesImg = getLines(img, binaryImg, x=10)

    verticalLinesImg = houghLines(verticalLinesImg, "vertical")
    horizontalLinesImg = houghLines(horizontalLinesImg, "horizontal")

    return binaryImg, verticalLinesImg, horizontalLinesImg, cv.bitwise_and(verticalLinesImg, horizontalLinesImg)


def runGetCells(img, intersections):
    cells = {}
    intersections = np.array(intersections)
    height = img.shape[0]
    width = img.shape[1]
    for col in range(intersections.shape[1] - 1):
        cells[col] = []
        for row in range(intersections.shape[0] - 1):
            x_min = intersections[row][col][0]
            x_max = intersections[row + 1][col][0]
            y_min = intersections[row][col][1]
            y_max = intersections[row][col + 1][1]
            cell = img[x_min:x_max, y_min:y_max]
            cell[0:10, 0:width] = 0
            cell[-10:height, 0:width] = 0
            cell[0:height, 0:12] = 0
            cell[0:height, -5:width] = 0
            cells[col].append(cell)

    labels = ["Cells/Code/", "Cells/StudentName/",
              "Cells/EnglishName/", "Cells/1/", "Cells/2/", "Cells/3/"]
    for key in list(cells.keys()):
        for i in range(len(cells[key])):
            cv.imwrite(labels[key] + str(i) + ".jpg", cells[key][i])


def deleteFiles():
    files = glob.glob('Intersections/')
    for file in files:
        os.remove(file)
    files = glob.glob('verticalLines/')
    for file in files:
        os.remove(file)
    files = glob.glob('horizontalLines/')
    for file in files:
        os.remove(file)


def run():
    mypath = "SingleInput"
    intersections = "Intersections/"
    verticalLines = "verticalLines/"
    horizontalLines = "horizontalLines/"
    binaryImgs = "binaryImgs/"
    Cells = "Cells/"
    EnglishName = "Cells/EnglishName/"
    Code = "Cells/Code/"
    StudentName = "Cells/StudentName/"
    Symbol_1, Symbol_2, Symbol_3 = "Cells/1", "Cells/2", "Cells/3"
    if(not os.path.exists(verticalLines)):
        os.makedirs(verticalLines)
    if(not os.path.exists(horizontalLines)):
        os.makedirs(horizontalLines)
    if(not os.path.exists(intersections)):
        os.makedirs(intersections)
    if(not os.path.exists(binaryImgs)):
        os.makedirs(binaryImgs)
    if(not os.path.exists(binaryImgs)):
        os.makedirs(binaryImgs)
    if(not os.path.exists(Cells)):
        os.makedirs(Cells)
    if(not os.path.exists(EnglishName)):
        os.makedirs(EnglishName)
    if(not os.path.exists(Code)):
        os.makedirs(Code)
    if(not os.path.exists(StudentName)):
        os.makedirs(StudentName)
    if(not os.path.exists(Symbol_1)):
        os.makedirs(Symbol_1)
    if(not os.path.exists(Symbol_2)):
        os.makedirs(Symbol_2)
    if(not os.path.exists(Symbol_3)):
        os.makedirs(Symbol_3)
    files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for fileName in files:
        img, vertical, horizontal, result_image = runGetIntersections(
            mypath + "/" + fileName)
        positions = getIntersections(result_image)
        runGetCells(img, positions)
        cv.imwrite(verticalLines + fileName, vertical)
        cv.imwrite(horizontalLines + fileName, horizontal)
        cv.imwrite(intersections + fileName, result_image)
        cv.imwrite(binaryImgs + fileName, img)


run()
