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
from PIL import Image

def main():
    naoFile = "RobotsModels/NAO.json"
    realNao = RealRobotBody("nao1", "Naetto", "NAO")
    realNao.buildFormJsonFile(naoFile)
    realNao.printComponents()

    s = Simulation()
    s.connect()
    simNao = SimulationRobotBody("naoSim1", "Naetto", "NAO")
    simNao.buildFormJsonFile(naoFile)
    s.addSimRobot(simNao)
    simNao.printComponents()
    s.setSimRobotsComponetsStateAndHandles()
    simNao.printComponents()

    for i in range(0, 10):
        code, resolution, image = s.readVisionSensorImage("NAO_vision1", True, True)
        img = Image.new("RGB", (resolution[0], resolution[1]), "white")
        img.putdata(image)
        img = img.rotate(angle=180)
        img.show(title=i)
        time.sleep(1)
        del img
    s.closeConnection()


if __name__ == '__main__':
    main()