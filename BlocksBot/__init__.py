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

from abc import ABC, abstractmethod
import json

# Abstract Robot Component. Components can be sensors or actuators
class Component(ABC):
    __ID = None
    __name = None
    __model = None

    @abstractmethod
    def __init__(self, ID, name, model):
        self.__ID = str(ID)
        self.__name = str(name)
        self.__model = str(model)

    def getID(self):
        return self.__ID

    def getName(self):
        return self.__name

    def getModel(self):
        return self.__model

    def setName(self, name):
        self.__name = str(name)

    def setID(self, ID):
        self.__ID = str(ID)

    def setModel(self, model):
        self.__model = str(model)

    @abstractmethod
    def getClass(self):
        pass


# Concrete component of a simulation robot
class SimulationComponent(Component):
    __state = None
    __handle = None

    def __init__(self, ID, name, model, handle=None, state=None):
        super().__init__(ID, name, model)
        if handle is not None:
            self.__handle = int(handle)
        if state is not None:
            self.__state = int(state)

    def getHandle(self):
        return self.__handle

    def getState(self):
        return self.__state

    def setHandle(self, handle):
        self.__handle = int(handle)

    def setState(self, state):
        self.__state = int(state)

    def getClass(self):
        return "SimulationComponent"

    def __str__(self):
        return self.getID() + " - " + self.getName() + " - " + self.getModel() + " - " + str(self.__state) + " - " + \
               str(self.__handle) + " - " + self.getClass()


# Concrete component of a real robot
class RealComponent(Component):

    def __init__(self, ID, name, model):
        super().__init__(ID, name, model)

    def getClass(self):
        return "RealComponent"

    def __str__(self):
        return self.getID() + " - " + self.getName() + " - " + self.getModel() + " - " + self.getClass()



# Robot is an abstract factory, and it is a composite of Sensors and Actuators, that are both RobotComponents
# (see Composite Pattern and Abstract Factory Pattern)
class RobotBody(ABC):
    __ID = None
    __name = None
    __model = None
    __sensors = None
    __actuators = None

    @abstractmethod
    def __init__(self, ID, name, model):
        self.__ID = str(ID)
        self.__name = str(name)
        self.__model = str(model)
        self.__sensors = {}
        self.__actuators = {}

    def getID(self):
        return self.__ID

    def getName(self):
        return self.__name

    def getModel(self):
        return self.__model

    def getSensors(self):
        return self.__sensors

    def getSensor(self, sensorID):
        return self.__sensors[str(sensorID)]

    def getActuators(self):
        return self.__actuators

    def getActuator(self, actuatorID):
        return self.__actuators[str(actuatorID)]

    def setRobotBody(self, robotBody={}):
        # robotBody = {"sensors": {"1": {"name": "sensorX", "model": "visionSensor"},
        #       "2": {"name": "sensorY", "model": "visionSensor"}},
        #       "actuators": {"1": {"name": "actuatorX", "model": "motor"}, "2": {"name": "ledY", "model": "RGBLed"}}}
        # robotBody = {"sensors": {"1": Component(1, "sensorX", "visionSensor"),
        #       "2": Component(2, "sensorY", "visionSensor")},
        #       "actuators": {"1": Component("1", "actuatorX", "motor", "2": Component("ledY", "RGBLed")}}
        assert isinstance(robotBody, dict)
        sensors = robotBody["sensors"]
        actuators = robotBody["actuators"]
        self.setSensors(sensors)
        self.setActuators(actuators)

    def setSensors(self, sensors={}):
        # sensors = {"1": {"name": "sensorX", "model": "visionSensor"}, "2": {"name": "sensorY", "model": "visionSensor"}}
        # sensors = {"1": Component(1, "sensorX", "visionSensor"), "2": Component(2, "sensorY", "visionSensor")}
        assert isinstance(sensors, dict)
        for sensorID in sensors:
            self.addSensor(sensorID, sensors[sensorID])

    def setActuators(self, actuators={}):
        # actuators = {"1": {"name": "actuatorX", "model": "motor"}, "2": {"name": "ledY", "model": "RGBLed"}}
        # actuators = {"1": Component("1", "actuatorX", "motor", "2": Component("ledY", "RGBLed")}
        assert isinstance(actuators, dict)
        for actuatorID in actuators:
            self.addActuator(actuatorID, actuators[actuatorID])

    @abstractmethod
    def addSensor(self, sensor, sensorArgs):
        pass

    def removeSensor(self, sensorID):
        del self.__sensors[str(sensorID)]

    @abstractmethod
    def addActuator(self, actuator, actuatorArgs):
        pass

    def removeActuator(self, actuatorID):
        del self.__actuators[str(actuatorID)]

    @abstractmethod
    def getClass(self):
        pass

    def buildFromJsonString(self, jsonString="{}"):
        jsonModel = json.loads(str(jsonString))
        self.setSensors(jsonModel["sensors"])
        self.setActuators(jsonModel["actuators"])

    def buildFormJsonFile(self, path=""):
        try:
            with open(str(path)) as jsonFile:
                self.buildFromJsonString(jsonFile.read())
        except IOError:
            print(path, " not accessible")

    def printComponents(self):
        print("#### Robot ID ", self.__ID, " -> name = ", self.__name, ", model = ", self.__model, ", class = ", self.getClass())
        print("    Sensors: ")
        for sensorID in self.__sensors:
            print("        ", self.__sensors[sensorID])
        print("    Actuators: ")
        for actuatorID in self.__actuators:
            print("        ", self.__actuators[actuatorID])


class RealRobotBody(RobotBody):

    def __init__(self, ID, name, model, sensors={}, actuators={}):
        super().__init__(ID, name, model)
        self.setSensors(sensors)
        self.setActuators(actuators)

    def addSensor(self, sensorID, sensorArgs):
        # sensorArgs = {"name": "sensorX", "model": "visionSensor"}
        # sensorArgs = RealComponent("sensorX", "visionSensor")
        assert isinstance(sensorArgs, dict) or \
               (hasattr(sensorArgs, "getClass") and sensorArgs.getClass() == "RealComponent")
        sensorID = str(sensorID)
        if isinstance(sensorArgs, dict):
            self.getSensors()[sensorID] = RealComponent(sensorID, sensorArgs["name"], sensorArgs["model"])
        else:
            self.getSensors()[sensorID] = sensorArgs

    def addActuator(self, actuatorID, actuatorArgs):
        # actuatorArgs = {"name": "actuatorX", "model": "led"}
        # actuatorArgs = RealComponent("actuatorX", "led")
        assert isinstance(actuatorArgs, dict) or \
               (hasattr(actuatorArgs, "getClass") and actuatorArgs.getClass() == "RealComponent")
        actuatorID = str(actuatorID)
        if isinstance(actuatorArgs, dict):
            self.getActuators()[actuatorID] = RealComponent(actuatorID, actuatorArgs["name"], actuatorArgs["model"])
        else:
            self.getActuators()[actuatorID] = actuatorArgs

    def getClass(self):
        return "RealRobot"


class SimulationRobotBody(RobotBody):

    def __init__(self, ID, name, model, sensors={}, actuators={}):
        super().__init__(ID, name, model)
        self.__sensors = self.setSensors(sensors)

    def addSensor(self, sensorID, sensorArgs):
        # sensorArgs = {"name": "sensorX", "model": "visionSensor"}
        # sensorArgs = SimulationComponent("sensorX", "visionSensor")
        assert isinstance(sensorArgs, dict) or \
               (hasattr(sensorArgs, "getClass") and sensorArgs.getClass() == "SimulationComponent")
        sensorID = str(sensorID)
        if isinstance(sensorArgs, dict):
            self.getSensors()[sensorID] = SimulationComponent(sensorID, sensorArgs["name"], sensorArgs["model"])
        else:
            self.getSensors()[sensorID] = sensorArgs

    def addActuator(self, actuatorID, actuatorArgs):
        # actuatorArgs = {"name": "actuatorX", "model": "led"}
        # actuatorArgs = SimulationComponent("actuatorX", "led")
        assert isinstance(actuatorArgs, dict) or \
               (hasattr(actuatorArgs, "getClass") and actuatorArgs.getClass() == "SimulationComponent")
        actuatorID = str(actuatorID)
        if isinstance(actuatorArgs, dict):
            self.getActuators()[actuatorID] = SimulationComponent(actuatorID, actuatorArgs["name"], actuatorArgs["model"])
        else:
            self.getActuators()[actuatorID] = actuatorArgs

    def getClass(self):
        return "SimulationRobot"



def main():
    naoFile = "../RobotsModels/NAO.json"
    nao = RealRobotBody("nao1", "Naetto", "NAO")
    nao.buildFormJsonFile(naoFile)
    nao.printComponents()

    s = Simulation()
    s.connect()
    print("NAO_vision1 handle: " + str(s.getObjectHandle("NAO_vision1")))
    print("NAO_vision2 handle: " + str(s.getObjectHandle("NAO_vision2")))
    print("Not present object handle: " + str(s.getObjectHandle("obj")))
    code, res, img = s.readVisionSensor("NAO_vision1", True, True)
    print(img)
    s.closeConnection()


if __name__ == '__main__':
    main()