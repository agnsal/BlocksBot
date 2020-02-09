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

from BlocksBot.coppeliaSimBinder import Simulation
from BlocksBot import RealRobotBody, SimulationRobotBody

import cv2
from Configs import API_KEY, API_SECRET
from urllib.request import HTTPError
import base64
import requests


def stepTurnNeckR(simulation, stepAngle=0.5):
    # print(simulation.getJointPosition("HeadYaw"))
    simulation.setJointTargetPosition("HeadYaw", stepAngle, blocking=False)
    # print(simulation.getJointPosition("HeadYaw"))

def stepTurnNeckL(simulation, stepAngle=0.5):
    # print(simulation.getJointPosition("HeadYaw"))
    simulation.setJointTargetPosition("HeadYaw", -stepAngle, blocking=False)
    # print(simulation.getJointPosition("HeadYaw"))

def stepTurnNeckU(simulation, stepAngle=0.5):
    # print(simulation.getJointPosition("HeadPitch"))
    simulation.setJointTargetPosition("HeadPitch", -stepAngle, blocking=False)
    # print(simulation.getJointPosition("HeadPitch"))

def stepTurnNeckD(simulation, stepAngle=0.5):
    # print(simulation.getJointPosition("HeadPitch"))
    simulation.setJointTargetPosition("HeadPitch", stepAngle, blocking=False)
    #print(simulation.getJointPosition("HeadPitch"))

def neckInOOVerical(simulation):
    # print("Verical 0")
    simulation.setJointTargetPosition("HeadPitch", 0, blocking=False)

def neckInOOHorizontal(simulation):
    # print("Horizontal 0")
    simulation.setJointTargetPosition("HeadYaw", 0, blocking=False)


def getFacesAndEmotions(filepath):
    httpDetect = 'https://api-us.faceplusplus.com/facepp/v3/detect'
    key = API_KEY
    secret = API_SECRET
    with open(filepath, "rb") as image_file:
        base64Img = base64.b64encode(image_file.read())
    data = {
        'api_key': key,
        'api_secret': secret,
        'image_base64': base64Img,
        'return_attributes': 'emotion',
    }
    try:
        #post data to server
        resp = requests.post(httpDetect, data)
        #get response
        faces = resp.json()
        return faces
    except HTTPError as e:
        print(e.read())

def main():
    naoFile = "RobotsModels/NAO.json"

    '''
    realNao = RealRobotBody("nao1", "Naetto", "NAO")
    realNao.buildFormJsonFile(naoFile)
    realNao.printComponents()
    '''

    s = Simulation()
    s.connect()
    simNao = SimulationRobotBody("naoSim1", "Naetto", "NAO")
    simNao.buildFormJsonFile(naoFile)
    s.addSimRobot(simNao)
    simNao.printComponents()
    s.setSimRobotsComponetsStateAndHandles()
    simNao.printComponents()

    neckInOOVerical(s)
    neckInOOHorizontal(s)
    faceCascade = cv2.CascadeClassifier('CascadeFiles/haarcascade_frontalface_alt_tree.xml')
    resultFile = "Files/Res.jpg"
    cap = cv2.VideoCapture(0)
    i = 0
    while True:
        # print(i)
        moveRangeO = 100
        moveRangeV = 20
        _, img = cap.read()
        img = cv2.flip(img, 1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.1, 4)
        cv2.imshow('img', img)
        if len(faces) > 0:
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            if i == 20:
                cv2.imwrite(resultFile, img)
                emotions = getFacesAndEmotions(resultFile)
                emotions = emotions["faces"][0]["attributes"]["emotion"]
                print("EMOTIONS: " + str(emotions))
                i = 0
            # Display
            cv2.imshow('img', img)
            (x, y, w, h) = faces[0]
            xMax, yMax = img.shape[0:2]
            middleX = xMax / 2
            middleY = yMax / 2
            middlePosX = (w / 2) + x
            middlePosY = (h / 2) + y
            # print("New Pos: " + str(x) + " - " + str(y))
            if middlePosX > middleX + moveRangeO:
                 # print("Nao Direction = R")
                stepTurnNeckR(s)
            elif middlePosX < middleX - moveRangeO:
                # print("Nao Direction = L")
                stepTurnNeckL(s)
            else:
                neckInOOHorizontal(s)
            if middlePosY > middleY - moveRangeV:
                # print("Nao Direction = D")
                stepTurnNeckD(s)
            elif middlePosY < middleY + moveRangeV:
                # print("Nao Direction = U")
                stepTurnNeckU(s)
            else:
                neckInOOVerical(s)
            i += 1
        # Stop if escape key is pressed
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break
    cap.release()



    '''
    for i in range(0, 10):
        code, resolution, image = s.readVisionSensorImage("NAO_vision1", True, True)
        img = Image.new("RGB", (resolution[0], resolution[1]), "white")
        img.putdata(image)
        img = img.rotate(angle=180)
        img.show(title=i)
        time.sleep(1)
        del img
    s.closeConnection()
    '''


if __name__ == '__main__':
    main()