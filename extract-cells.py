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
    horizontalKernel = cv.getStructuringElement(cv.MORPH_RECT, (kernelLength, 1))

    # Apply erosion then dilation to detect vertical lines using the vertical kernel
    erodedImg = cv.erode(binaryImg, verticalKernel, iterations=3)
    verticalLinesImg = cv.dilate(erodedImg, verticalKernel, iterations=3)

    # Apply erosion then dilation to detect horizontal lines using the horizontal kernel
    erodedImg = cv.erode(binaryImg, horizontalKernel, iterations=3)
    horizontalLinesImg = cv.dilate(erodedImg, horizontalKernel, iterations=3)
    
    return verticalLinesImg, horizontalLinesImg


def getIntersections(pixels):
    intersections = []
    for i in range(pixels.shape[0]):
        for j in range(pixels.shape[1]):
            if pixels[i][j] != 0:
                intersections.append((i, j))
    return intersections


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


def run(imgPath):
    img = cv.imread(imgPath, 0)

    # thresholding
    (thresh, binaryImg) = cv.threshold(img, 128, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)
    binaryImg = 255 - binaryImg

    verticalLinesImg, horizontalLinesImg = getLines(img, binaryImg, x = 7)
    
    verticalLinesImg = houghLines(verticalLinesImg, "vertical")
    horizontalLinesImg = houghLines(horizontalLinesImg, "horizontal")

    return verticalLinesImg, horizontalLinesImg, cv.bitwise_and(verticalLinesImg, horizontalLinesImg)


def runGetIntersections():
    mypath = "SingleInput"
    intersections = "Intersections/"
    verticalLines = "verticalLines/"
    horizontalLines = "horizontalLines/"
    files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for fileName in files:
        vertical, horizontal, result_image = run(mypath + "/" + fileName)
        cv.imwrite(verticalLines + fileName, vertical)
        cv.imwrite(horizontalLines + fileName, horizontal)
        cv.imwrite(intersections + fileName, result_image)

def deleteFiles():
    files = glob.glob('Intersections/')
    for file in files:
        os.remove(file)
    files = glob.glob('verticalLines/')
    for file in files:
        os.remove(file)
    files=glob.glob('horizontalLines/')
    for file in files:
        os.remove(file)

runGetIntersections()
