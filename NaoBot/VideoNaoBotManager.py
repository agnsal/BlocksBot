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
from Configs import RedisConfig, NaoConfig

import time
from PIL import Image
import base64
import cStringIO

from naoqi import ALProxy


def saveImageOnRedis(redis, base64Capture):
    timestamp = getTimestamp()
    redis.hsetOnRedis(key=RedisConfig['imageHsetRoot']+str(timestamp), field=RedisConfig['imageHsetB64Field'],
                      value=base64Capture)
    redis.publishOnRedis(channel=RedisConfig['newImagePubSubChannel'],
                         msg=RedisConfig['newImageMsgRoot']+str(timestamp))

def main():
    resolution = vision_definitions.kQVGA
    colorSpace = vision_definitions.kYUVColorSpace
    camProxy = ALProxy("ALVideoDevice", NaoConfig['IP'], NaoConfig['PORT'])
    camSub = camProxy.subscribe("python_client", resolution, colorSpace, NaoConfig['imageFPS'])
    r = RedisManager(host=RedisConfig['host'], port=RedisConfig['port'], db=RedisConfig['db'],
                     password=RedisConfig['password'], decodedResponses=RedisConfig['decodedResponses'])
    while True:
        naoImage = camProxy.getImageRemote(camSub)
        im = Image.fromstring("RGB", (naoImage[0], naoImage[1]), naoImage[6])
        buffer = cStringIO.StringIO()
        im.save(buffer, format="JPEG")
        imgB64 = base64.b64encode(buffer.getvalue())
        saveImageOnRedis(r, imgB64)
        time.sleep(0.1)


if __name__ == '__main__':
    main()


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