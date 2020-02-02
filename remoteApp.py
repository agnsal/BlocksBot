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

import time
from PIL import Image as I
import matplotlib.pyplot as plt

def main():
    naoFile = "RobotsModels/NAO.json"
    realNao = RealRobotBody("nao1", "Naetto", "NAO")
    realNao.buildFormJsonFile(naoFile)
    realNao.printComponents()

    s = Simulation()
    s.connect()
    print("NAO_vision1 handle: " + str(s.getObjectStateAndHandle("NAO_vision1")))
    print("NAO_vision2 handle: " + str(s.getObjectStateAndHandle("NAO_vision2")))
    print("Not present object handle: " + str(s.getObjectStateAndHandle("obj")))
    simNao = SimulationRobotBody("naoSim1", "Naetto", "NAO")
    simNao.buildFormJsonFile(naoFile)
    s.addSimRobot(simNao)
    simNao.printComponents()
    s.setSimRobotsComponetsStateAndHandles()
    simNao.printComponents()

    s.readVisionSensorImage("NAO_vision1", True, False)
    plt.ion()
    # Initialiazation of the figure
    time.sleep(1)
    code, resolution, image = s.readVisionSensorImage("NAO_vision1", True, False)
    print(code)
    print(resolution)
    im = I.new("RGB", (resolution[0], resolution[1]), "white")
    plotimg = plt.imshow(im)
    plt.show()
    time.sleep(1)

    s.closeConnection()


if __name__ == '__main__':
    main()