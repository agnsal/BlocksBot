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

import cv2
import base64

from TimeManager import getTimestamp
from BlocksBot.coppeliaSimBinder import Simulation
from BlocksBot import SimulationRobotBody
from RedisManager import RedisManager
import Yamler

RedisConfig = Yamler.getConfigDict("Configs/RedisConfig.yaml")


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


def RArmInOO(simulation):
    simulation.setJointTargetPosition("RShoulderPitch3", 1.4, blocking=False)


def LArmInOO(simulation):
    simulation.setJointTargetPosition("LShoulderPitch3", 1.4, blocking=False)


def initialPose(simulation):
    neckInOOVerical(simulation)
    neckInOOHorizontal(simulation)
    RArmInOO(simulation)
    LArmInOO(simulation)


def analyzeImage(img, faces):
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
    cv2.imshow('img', img)
    (x, y, w, h) = faces[0]
    xMax, yMax = img.shape[0:2]
    middleX = xMax / 2
    middleY = yMax / 2
    middlePosX = (w / 2) + x
    middlePosY = (h / 2) + y
    #cv2.rectangle(img, (int(middlePosX), int(middlePosY)), (int(middlePosX) + 20, int(middlePosY) + 20), (0, 255, 0), 2)
    return {'middleX': middleX, 'middlePosX': middlePosX, 'middleY': middleY, 'middlePosY': middlePosY}


def behaviour(simulation, points, moveRangeO, moveRangeV):
    assert isinstance(simulation, Simulation)
    assert isinstance(points, dict)
    if points['middlePosX'] > points['middleX'] + moveRangeO:
        # print("Nao Direction = R")
        stepTurnNeckR(simulation)
    elif points['middlePosX'] < points['middleX'] - moveRangeO:
        # print("Nao Direction = L")
        stepTurnNeckL(simulation)
    else:
        neckInOOHorizontal(simulation)
    if points['middlePosY'] > points['middleY'] - moveRangeV:
        # print("Nao Direction = D")
        stepTurnNeckD(simulation)
    elif points['middlePosY'] < points['middleY'] + moveRangeV:
        # print("Nao Direction = U")
        stepTurnNeckU(simulation)
    else:
        neckInOOVerical(simulation)


def saveImageOnRedis(redis, img):
    timestamp = getTimestamp()
    _, jpg = cv2.imencode('.jpg', img)
    base64Capture = base64.b64encode(jpg)
    redis.hsetOnRedis(key=RedisConfig['imageHsetRoot']+str(timestamp), field=RedisConfig['imageHsetB64Field'],
                      value=base64Capture)
    redis.publishOnRedis(channel=RedisConfig['newImagePubSubChannel'],
                         msg=RedisConfig['newImageMsgRoot']+str(timestamp))


def main():
    naoFile = "RobotsModels/NAO.json"
    faceCascadeFile = "CascadeFiles/haarcascade_frontalface_alt_tree.xml"
    deltaFrames = 50
    moveRangeO = 100
    moveRangeV = 20

    s = Simulation()
    s.connect()
    simNao = SimulationRobotBody("naoSim1", "Naetto", "NAO")
    simNao.buildFormJsonFile(naoFile)
    s.addSimRobot(simNao)
    simNao.printComponents()
    s.setSimRobotsComponetsStateAndHandles()
    simNao.printComponents()
    initialPose(s)

    faceCascade = cv2.CascadeClassifier(faceCascadeFile)
    cap = cv2.VideoCapture(0)

    r = RedisManager(host=RedisConfig['host'], port=RedisConfig['port'], db=RedisConfig['db'],
                     password=RedisConfig['password'], decodedResponses=RedisConfig['decodedResponses'])
    i = 0
    outputW = s.createAuxiliaryConsoleWindow("Emotion Detection")[1]
    while True:
        _, img = cap.read()
        img = cv2.flip(img, 1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.1, 4)
        cv2.imshow('img', img)
        # print(i)  # Test
        if i == deltaFrames:
            print("Save on Redis")  # test
            saveImageOnRedis(r, img)
            i = 0
        if len(faces) > 0:
            points = analyzeImage(img, faces)
            behaviour(s, points, moveRangeO, moveRangeV)
        decision = r.getFromRedis(RedisConfig['DecisionSet'])
        if not isinstance(decision, str):
            decision = decision.decode()
        s.printInAuxiliryConsoleWindow(console=outputW, msg=decision)
        s.printInAuxiliryConsoleWindow(console=outputW, msg='\n')
        # Stop if escape key is pressed
        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break
        i += 1
    cap.release()


if __name__ == '__main__':
    main()