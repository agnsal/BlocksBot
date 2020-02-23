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

from naoqi import ALProxy
import vision_definitions

from RedisManager import RedisManager
import Yamler

RedisConfig = Yamler.getConfigDict("Configs/RedisConfig.yaml")

import sys
import time

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

from optparse import OptionParser

NAO_IP = "127.0.0.1"
NAO_PORT = 64187


# Global variable to store the HumanGreeter module instance
HumanGreeter = None
memory = None


class HumanGreeterModule(ALModule):
    """ A simple module able to react
    to facedetection events

    """
    def __init__(self, name):
        ALModule.__init__(self, name)
        # No need for IP and port here because
        # we have our Python broker connected to NAOqi broker

        # Create a proxy to ALTextToSpeech for later use
        self.tts = ALProxy("ALTextToSpeech")

        # Subscribe to the FaceDetected event:
        global memory
        memory = ALProxy("ALMemory")
        memory.subscribeToEvent("FaceDetected",
            "HumanGreeter",
            "onFaceDetected")

    def onFaceDetected(self, *_args):
        """ This will be called each time a face is
        detected.

        """
        # Unsubscribe to the event when talking,
        # to avoid repetitions
        memory.unsubscribeToEvent("FaceDetected",
            "HumanGreeter")

        self.tts.say("Hello, you")

        # Subscribe again to the event
        memory.subscribeToEvent("FaceDetected",
            "HumanGreeter",
            "onFaceDetected")


def main():
    ####
    # Create proxy on ALVideoDevice

    print "Creating ALVideoDevice proxy to ", NAO_IP

    camProxy = ALProxy("ALVideoDevice", NAO_IP, NAO_PORT)

    ####
    # Register a Generic Video Module

    resolution = vision_definitions.kQVGA
    colorSpace = vision_definitions.kYUVColorSpace
    fps = 30

    nameId = camProxy.subscribe("python_GVM", resolution, colorSpace, fps)
    print nameId

    '''
    print 'getting images in local'
    for i in range(0, 20):
      camProxy.getImageLocal(nameId)
      camProxy.releaseImage(nameId)

    resolution = vision_definitions.kQQVGA
    camProxy.setResolution(nameId, resolution)
    '''

    print 'getting images in remote'
    for i in range(0, 20):
      camProxy.getImageRemote(nameId)

    camProxy.unsubscribe(nameId)

    print 'end of gvm_getImageLocal python script'


    parser = OptionParser()
    parser.add_option("--pip",
        help="Parent broker port. The IP address or your robot",
        dest="pip")
    parser.add_option("--pport",
        help="Parent broker port. The port NAOqi is listening to",
        dest="pport",
        type="int")
    parser.set_defaults(
        pip=NAO_IP,
        pport=NAO_PORT)

    (opts, args_) = parser.parse_args()
    pip   = opts.pip
    pport = opts.pport

    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       pip,         # parent broker IP
       pport)       # parent broker port


    # Warning: HumanGreeter must be a global variable
    # The name given to the constructor must be the name of the
    # variable
    global HumanGreeter
    HumanGreeter = HumanGreeterModule("HumanGreeter")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        myBroker.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()