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

try:
    from BlocksBot.coppeliaSimBinder import sim
except:
    print('--------------------------------------------------------------')
    print('"sim.py" could not be imported. This means very probably that')
    print('either "simConst.py" or the remoteApi library could not be found.')
    print('Make sure both are in the same folder as this file,')
    print('or appropriately adjust the file "sim.py"')
    print('--------------------------------------------------------------')
    print('')


class Simulation:
    __host = None
    __portNumber = None
    __clientID = None
    __simRobots = None

    def __init__(self, host='127.0.0.1', portNumber=19997, simRobots=set()):
        self.__host = host
        self.__port = portNumber
        self.__simRobots = set()
        self.setSimRobots(simRobots)

    def connect(self):
        '''
        Connect with CoppeliaSim Simulator.
        :return: True if the connection has been established, False otherwise.
        '''
        # just in case, close all opened connections
        sim.simxFinish(-1)
        # Connect to CoppeliaSim
        self.__clientID = sim.simxStart(self.__host, self.__port, True, True, 5000, 5)
        # check clientID for a good connection...
        if self.__clientID == -1:
            return False
        else:
            return True

    def closeConnection(self):
        '''
        Close connection with the robot simulation
        :return:
        '''
        # Before closing the connection to CoppeliaSim, make sure that the last command sent out had time to arrive.
        # You can guarantee this with (for example):
        sim.simxGetPingTime(self.__clientID)
        # Now close the connection to CoppeliaSim:
        sim.simxFinish(self.__clientID)

    def getSimRobots(self):
        return self.__simRobots

    def setSimRobots(self, simRobots=set()):  # simRobots = set of SimulationRobot
        assert isinstance(simRobots, set)
        for robot in simRobots:
            self.addSimRobot(robot)

    def addSimRobot(self, simRobot):
        assert simRobot.getClass() == "SimulationRobot"
        self.__simRobots.add(simRobot)

    def removeSimRobot(self, simRobot):
        assert simRobot.getClass() == "SimulationRobot"
        self.__simRobots.remove(simRobot)

    def setSimRobotsComponetsStateAndHandles(self):
        for robot in self.__simRobots:
            sensors = robot.getSensors()
            actuators = robot.getActuators()
            for sensorID in sensors:
                sensor = robot.getSensor(sensorID)
                state, handle = self.getObjectStateAndHandle(sensor.getName())
                sensor.setState(state)
                sensor.setHandle(handle)
            for actuatorID in actuators:
                actuator = robot.getActuator(actuatorID)
                state, handle = self.getObjectStateAndHandle(actuator.getName())
                actuator.setState(state)
                actuator.setHandle(handle)

    def getObjectStateAndHandle(self, objName):
        '''
        Returns the simulation handle of ad object, given its simulation name.
        :param objName: name of the sensor as defined in the simulator
        :return: state, handle
        '''
        objName = str(objName)
        state, handle = sim.simxGetObjectHandle(self.__clientID, objName, sim.simx_opmode_blocking)
        return state, handle

    def readProximitySensor(self, sensorName, blocking=True):
        '''
        Implements sensor reading from the robot simulator
        :param sensorName: name of the sensor as defined in the simulator
        :return: out:
        '''
        sensorName = str(sensorName)
        blocking = bool(blocking)
        if blocking:
            mode = sim.simx_opmode_blocking
        else:
            mode = sim.simx_opmode_oneshot
        state, handle = self.getObjectStateAndHandle(sensorName)
        out = sim.simxReadProximitySensor(self.__clientID, handle, mode)
        return out

    def readVisionSensor(self, sensorName, colorImage=True, blocking=True):
        '''
        Implements sensor reading from the robot simulator
        :param sensorName: name of the sensor as defined in the simulator
        :return: out:
        '''
        sensorName = str(sensorName)
        blocking = bool(blocking)
        colorImage = int(bool(colorImage))
        if blocking:
            mode = sim.simx_opmode_blocking
        else:
            mode = sim.simx_opmode_oneshot
        state, handle = self.getObjectStateAndHandle(sensorName)
        returnCode, resolution, image = sim.simxGetVisionSensorImage(self.__clientID, handle, colorImage, mode)
        return returnCode, resolution, image


def main():
    from BlocksBot import SimulationRobotBody
    nao = SimulationRobotBody("nao1", "naetto", "NAO", {"1": {"name": "sensorX", "model": "visionSensor"}})
    s = Simulation()
    s.addSimRobot(nao)
    for robot in s.getSimRobots():
        robot.printComponents()
    s.connect()
    s.setSimRobotsComponetsStateAndHandles()
    for robot in s.getSimRobots():
        robot.printComponents()
    print("NAO_vision1 handle: " + str(s.getObjectStateAndHandle("NAO_vision1")))
    print("NAO_vision2 handle: " + str(s.getObjectStateAndHandle("NAO_vision2")))
    print("Not present object handle: " + str(s.getObjectStateAndHandle("obj")))
    code, res, img = s.readVisionSensor("NAO_vision1", True, True)
    print(img)
    s.closeConnection()

if __name__ == '__main__':
    main()