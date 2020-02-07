# coding : utf-8

'''
Copyright 2020 Agnese Salutari.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License
'''


import numpy as np
import cv2
from os import path


def imgDetection(img, cascadeClassifier="", resultFile="", getCoordsOnly=True):
    assert isinstance(img, np.ndarray)
    assert isinstance(cascadeClassifier, str)
    assert path.exists(cascadeClassifier)
    assert isinstance(resultFile, str)
    assert isinstance(getCoordsOnly, bool)
    cascade = cv2.CascadeClassifier(cascadeClassifier)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Convert into grayscale
    detectedObjs = cascade.detectMultiScale(gray, 1.1, 4)
    for (x, y, w, h) in detectedObjs:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
    if resultFile:
        cv2.imwrite(resultFile, img)
    if getCoordsOnly:
        return detectedObjs
    else:
        return img, detectedObjs


def photoDetection(photo="", cascadeClassifier="", resultFile="", getCoordsOnly=True):
    assert isinstance(photo, str)
    assert path.exists(photo)
    img = cv2.imread(photo)
    return imgDetection(img, cascadeClassifier, resultFile, getCoordsOnly)


def webcamDetection(framesNumber=30, cascadeClassifier="", resultFile="", getCoordsOnly=True):
    assert isinstance(framesNumber, int)
    assert isinstance(resultFile, str)
    video = cv2.VideoCapture(0)
    results = []
    if framesNumber == 1:
        _, img = video.read()  # img is a frame
        results.append([imgDetection(img, cascadeClassifier, resultFile, getCoordsOnly)])
    else:
        resultFile = resultFile.split(".")
        for i in range(0, framesNumber):
            _, img = video.read()  # img is a frame
            results.append([imgDetection(img, cascadeClassifier, resultFile[0] + str(i) + "." + resultFile[1], getCoordsOnly)])
    video.release()
    return results


def videoDetection(video="", framesNumber=30, cascadeClassifier="", resultFile="", getCoordsOnly=True):
    assert isinstance(video, str)
    if video:
        assert path.exists(video)
    assert isinstance(framesNumber, int)
    assert isinstance(resultFile, str)
    video = cv2.VideoCapture(video)
    results = []
    resultFile = resultFile.split(".")
    for i in range(0, framesNumber):
        _, img = video.read()  # img is a frame
        results.append([imgDetection(img, cascadeClassifier, resultFile[0] + str(i) + "." + resultFile[1], getCoordsOnly)])
    video.release()
    return results
