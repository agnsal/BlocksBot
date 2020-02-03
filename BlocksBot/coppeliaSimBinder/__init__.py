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

    def __init__(self, host='127.0.0.1', portNumber=19997, clientID=None, simRobots=set()):
        self.__host = host
        self.__port = portNumber
        self.__clientID = clientID
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

    def getClientID(self):
        return self.__clientID

    def setClientID(self, clientID):
        self.__clientID = clientID

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
        assert isinstance(objName, str)
        return sim.simxGetObjectHandle(self.__clientID, objName, sim.simx_opmode_blocking)

    def getProperSimMode(self, blocking=True):
        assert isinstance(blocking, bool)
        if blocking:
            mode = sim.simx_opmode_blocking
        else:
            mode = sim.simx_opmode_oneshot
        return mode

    def readForceSensor(self, sensorName, blocking=True):
        '''
        Reads the force and torque applied to a force sensor (filtered values are read),
        and its current state ('unbroken' or 'broken')
        :param sensorName: name of the sensor as defined in the simulator
        :param blocking: boolean
        :return: returnCode, state (bit 0 set: force and torque data is available, otherwise it is not (yet) available,
        bit 1 set: force sensor is broken, otherwise it is still unbroken), forceVector (x,y,z), torqueVector (x,y,z)
        '''
        assert isinstance(sensorName, str)
        mode = self.getProperSimMode(blocking)
        state, handle = self.getObjectStateAndHandle(sensorName)
        return sim.simxReadForceSensor(self.__clientID, handle, mode)

    def readProximitySensor(self, sensorName, blocking=True):
        '''
        Implements sensor reading from the robot simulator
        :param sensorName: name of the sensor as defined in the simulator
        :param blocking: boolean
        :return: returnCode, detectionState, detectedPoint, detectedObjectHandle, detectedSurfaceNormalVector
        '''
        assert isinstance(sensorName, str)
        mode = self.getProperSimMode(blocking)
        state, handle = self.getObjectStateAndHandle(sensorName)
        return sim.simxReadProximitySensor(self.__clientID, handle, mode)

    def readVisionSensorState(self, sensorName, blocking=True):
        '''
        Reads the state of a vision sensor
        :param sensorName: name of the sensor as defined in the simulator
        :param blocking: boolean
        :return: returnCode, detectionState, auxPackets
        '''
        assert isinstance(sensorName, str)
        mode = self.getProperSimMode(blocking)
        state, handle = self.getObjectStateAndHandle(sensorName)
        return sim.simxReadVisionSensor(self.__clientID, handle, mode)

    def readVisionSensorImage(self, sensorName, colorImage=True, blocking=True):
        '''
        Implements sensor reading from the robot simulator
        :param sensorName: name of the sensor as defined in the simulator
        :param colorImage: boolean
        :param blocking: boolean
        :return: returnCode, resolution, image
        '''
        assert isinstance(sensorName, str)
        assert isinstance(colorImage, bool)
        mode = self.getProperSimMode(blocking)
        state, handle = self.getObjectStateAndHandle(sensorName)
        return sim.simxGetVisionSensorImage(self.__clientID, handle, int(colorImage), mode)

    def readExternalVisionSensorImage(self, sensorName, externalImage, options, blocking=True):
        '''
        Implements sensor reading from the robot simulator
        :param sensorName: name of the sensor as defined in the simulator
        :param externalImage: image
        :param options: image options (bit-coded: bit0 set: each image pixel is a byte -> greyscale image,
        otherwise each image pixel is a rgb byte-triplet)
        :param blocking: boolean
        :return: returnCode, resolution, image
        '''
        assert isinstance(sensorName, str)
        mode = self.getProperSimMode(blocking)
        state, handle = self.getObjectStateAndHandle(sensorName)
        return sim.simxSetVisionSensorImage(self.__clientID, handle, externalImage, options, mode)

    def readVisionSensorDepth(self, sensorName, blocking=True):
        '''
        Retrieves the depth buffer of a vision sensor
        :param sensorName: name of the sensor as defined in the simulator
        :param blocking: boolean
        :return: returnCode, resolution, buffer (values are in the range of 0-1: 0=closest to sensor,
        1=farthest from sensor)
        '''
        assert isinstance(sensorName, str)
        mode = self.getProperSimMode(blocking)
        state, handle = self.getObjectStateAndHandle(sensorName)
        return sim.simxGetVisionSensorDepthBuffer(self.__clientID, handle, mode)

    def getJointForce(self, jointName, blocking=True):
        '''
        Retrieves the force or torque applied to a joint along/about its active axis
        :param jointName: name of the joint as defined in the simulator
        :param blocking: boolean
        :return: returnCode, force
        '''
        assert isinstance(jointName, str)
        state, handle = self.getObjectStateAndHandle(jointName)
        mode = self.getProperSimMode(blocking)
        return sim.simxGetJointForce(self.__clientID, handle, mode)

    def getJointMatrix(self, jointName, blocking=True):
        '''
        Retrieves the intrinsic transformation matrix of a joint (the transformation caused by the joint movement)
        :param jointName: name of the joint as defined in the simulator
        :param blocking: boolean
        :return: returnCode, matrix (array containing 12 values)
        '''
        assert isinstance(jointName, str)
        state, handle = self.getObjectStateAndHandle(jointName)
        mode = self.getProperSimMode(blocking)
        return sim.simxGetJointMatrix(self.__clientID, handle, mode)

    def getJointPosition(self, jointName, blocking=True):
        '''
        Retrieves the intrinsic position of a joint
        :param jointName: name of the joint as defined in the simulator
        :param blocking: boolean
        :return: returnCode, position (intrinsic position of the joint. This is a one-dimensional value: if the joint
        is revolute, the rotation angle is returned, if the joint is prismatic, the translation amount is returned, etc)
        '''
        assert isinstance(jointName, str)
        state, handle = self.getObjectStateAndHandle(jointName)
        mode = self.getProperSimMode(blocking)
        return sim.simxGetJointPosition(self.__clientID, handle, mode)

    def setJointForce(self, jointName, force, blocking=True):
        '''
        Sets the maximum force or torque that a joint can exert
        :param jointName: name of the joint as defined in the simulator
        :param force:
        :param blocking: boolean
        :return: returnCode
        '''
        assert isinstance(jointName, str)
        state, handle = self.getObjectStateAndHandle(jointName)
        mode = self.getProperSimMode(blocking)
        return sim.simxSetJointForce(self.__clientID, handle, force, mode)

    def setJointPosition(self, jointName, position, blocking=True):
        '''
        Sets the intrinsic position of a joint
        :param jointName: name of the joint as defined in the simulator
        :param position: number (angular or linear value depending on the joint type)
        :param blocking: boolean
        :return: returnCode
        '''
        assert isinstance(jointName, str)
        assert isinstance(position, int) or isinstance(position, float)
        state, handle = self.getObjectStateAndHandle(jointName)
        mode = self.getProperSimMode(blocking)
        return sim.simxSetJointPosition(self.__clientID, handle, position, mode)

    def setJointTargetPosition(self, jointName, position, blocking=True):
        '''
        Sets the target position of a joint if the joint is in torque/force mode
        :param jointName: name of the joint as defined in the simulator
        :param position: number (angular or linear value depending on the joint type)
        :param blocking: boolean
        :return: returnCode
        '''
        assert isinstance(jointName, str)
        assert isinstance(position, int) or isinstance(position, float)
        state, handle = self.getObjectStateAndHandle(jointName)
        mode = self.getProperSimMode(blocking)
        return sim.simxSetJointTargetPosition(self.__clientID, handle, position, mode)

    def setJointTargetVelocity(self, jointName, velocity, blocking=True):
        '''
        Sets the intrinsic target velocity of a non-spherical joint
        :param jointName: name of the joint as defined in the simulator
        :param velocity: number (angular or linear value depending on the joint type)
        :param blocking: boolean
        :return: returnCode
        '''
        assert isinstance(jointName, str)
        assert isinstance(velocity, int) or isinstance(velocity, float)
        state, handle = self.getObjectStateAndHandle(jointName)
        mode = self.getProperSimMode(blocking)
        return sim.simxSetJointTargetVelocity(self.__clientID, handle, velocity, mode)


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
    code, res, img = s.readVisionSensorImage("NAO_vision1", True, True)
    print(img)
    s.closeConnection()

if __name__ == '__main__':
    main()