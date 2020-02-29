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
import wave

from naoqi import ALProxy


def setAudioToRedis(redis, audioFile, channels, rate):
    assert isinstance(audioFile, str)
    assert isinstance(channels, int)
    assert isinstance(rate, int)
    timestamp = getTimestamp()
    audio = wave.open(audioFile, 'rb')
    nFrames = audio.getnframes()
    frames = audio.readframes(nFrames)
    params = {'channels': channels, 'sampwidth': audio.getsampwidth(), 'rate': rate}
    redisStr = "[" + str(frames) + ", " + str(params) + "]"
    redis.hsetOnRedis(key=RedisConfig['audioHsetRoot']+str(timestamp), field=RedisConfig['audioHsetB64Field'],
                      value=redisStr)
    redis.publishOnRedis(channel=RedisConfig['newAudioPubSubChannel'],
                         msg=RedisConfig['newAudioMsgRoot']+str(timestamp))

def main():
    audioProxy = ALProxy("ALAudioDevice", NaoConfig['IP'], NaoConfig['PORT'])
    r = RedisManager(host=RedisConfig['host'], port=RedisConfig['port'], db=RedisConfig['db'],
                     password=RedisConfig['password'], decodedResponses=RedisConfig['decodedResponses'])
    while True:
        audioProxy.startMicrophonesRecording(NaoConfig['audioFile'], "wav", NaoConfig['audioSampleRate'],
                                             NaoConfig['audioChannels'])
        time.sleep(NaoConfig['audioSeconds'])
        audioProxy.stopMicrophonesRecording()
        setAudioToRedis(r, audioFile=NaoConfig['audioFile'], channels=NaoConfig['nAudioCh'],
                        rate=NaoConfig['audioSampleRate'])


if __name__ == '__main__':
    main()
