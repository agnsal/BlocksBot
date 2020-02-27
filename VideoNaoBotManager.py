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
from TimeManager import getTimestamp
import Yamler

RedisConfig = Yamler.getConfigDict("Configs/RedisConfigNao.yaml")

import sys
import time
import cv2

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

from optparse import OptionParser

NAO_IP = "192.168.0.100"
NAO_PORT = 9559
resolution = vision_definitions.kQVGA
colorSpace = vision_definitions.kYUVColorSpace
fps = 15


def initCamProxy(proxyName, IP, PORT):
    assert isinstance(proxyName, str)
    assert isinstance(IP, str)
    assert isinstance(PORT, int)
    return ALProxy(proxyName, IP, PORT)


def camProxySubscribe(camProxy, channel, resolution, colorSpace, fps):
    assert isinstance(channel, str)
    assert isinstance(resolution, int)
    assert isinstance(colorSpace, int)
    assert isinstance(fps, int)
    return camProxy.subscribe(channel, resolution, colorSpace, fps)


def camProxyUnsubscribe(camProxy, camProxySub):
    return camProxy.unsubscribe(camProxySub)


def saveImageOnRedis(redis, img):
    timestamp = getTimestamp()
    _, jpg = cv2.imencode('.jpg', img)
    base64Capture = base64.b64encode(jpg)
    redis.hsetOnRedis(key=RedisConfig['imageHsetRoot']+str(timestamp), field=RedisConfig['imageHsetB64Field'],
                      value=base64Capture)
    redis.publishOnRedis(channel=RedisConfig['newImagePubSubChannel'],
                         msg=RedisConfig['newImageMsgRoot']+str(timestamp))


# Global variable to store the HumanGreeter module instance
HumanGreeter = None
memory = None
camProxy = initCamProxy("ALVideoDevice", NAO_IP, NAO_PORT)
camSub = camProxySubscribe(camProxy, "ALVideoDevice", resolution, colorSpace, fps)
r = RedisManager(host=RedisConfig['host'], port=RedisConfig['port'], db=RedisConfig['db'],
                     password=RedisConfig['password'], decodedResponses=RedisConfig['decodedResponses'])


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
        naoImage = camProxy.getImageRemote(camSub)

        saveImageOnRedis(r, naoImage[6])

        # Subscribe again to the event
        memory.subscribeToEvent("FaceDetected",
            "HumanGreeter",
            "onFaceDetected")


def main():
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
        print "Interrupted by user, shutting down"
        myBroker.shutdown()
        sys.exit(0)




'''
def getNaoImage(IP, PORT, resolution, colorSpace):
      camProxy = ALProxy("ALVideoDevice", IP, PORT)
      resolution = 2    # VGA
      colorSpace = 11   # RGB
      videoClient = camProxy.subscribe("python_client", resolution, colorSpace, 5)
      t0 = time.time()

      # Get a camera image.
      # image[6] contains the image data passed as an array of ASCII chars.
      naoImage = camProxy.getImageRemote(videoClient)

      t1 = time.time()

      # Time the image transfer.
      print "acquisition delay ", t1 - t0

      camProxy.unsubscribe(videoClient)


  # Now we work with the image returned and save it as a PNG  using ImageDraw
  # package.

  # Get the image size and pixel array.
  imageWidth = naoImage[0]
  imageHeight = naoImage[1]
  array = naoImage[6]

  # Create a PIL Image from our pixel array.
  im = Image.fromstring("RGB", (imageWidth, imageHeight), array)

  # Save the image.
  im.save("camImage.png", "PNG")

  #im.show()
  
'''