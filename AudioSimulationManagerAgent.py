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

import pyaudio
import base64

from TimeManager import getTimestamp
from RedisManager import RedisManager
import Yamler

RedisConfig = Yamler.getConfigDict("Configs/RedisConfig.yaml")
SimConfig = Yamler.getConfigDict("Configs/SimulationConfig.yaml")


def audioRecordToRedis(redis, audioSeconds, format, channels, rate, framesPerBuffer):
    assert isinstance(channels, int)
    assert isinstance(rate, int)
    assert isinstance(framesPerBuffer, int)
    assert isinstance(audioSeconds, int) or isinstance(audioSeconds, float)
    timestamp = getTimestamp()
    audio = pyaudio.PyAudio()
    stream = audio.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=framesPerBuffer)
    print("recording...")  # Test
    frames = []
    for i in range(0, int(rate / framesPerBuffer * audioSeconds)):
        data = stream.read(framesPerBuffer)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    audio.terminate()
    frames = str(frames).encode('utf-8')
    frames = base64.b64encode(frames)
    params = {'channels': channels, 'sampwidth': audio.get_sample_size(format), 'rate': rate}
    redis.hsetOnRedis(key=RedisConfig['audioHsetRoot']+str(timestamp), field=RedisConfig['audioHsetB64Field'],
                      value=frames)
    redis.hsetOnRedis(key=RedisConfig['audioHsetRoot'] + str(timestamp), field=RedisConfig['audioHsetParamsField'],
                      value=str(params))
    redis.publishOnRedis(channel=RedisConfig['newAudioPubSubChannel'],
                         msg=RedisConfig['audioHsetRoot']+str(timestamp))


def main():
    r = RedisManager(host=RedisConfig['host'], port=RedisConfig['port'], db=RedisConfig['db'],
                     password=RedisConfig['password'], decodedResponses=RedisConfig['decodedResponses'])
    while True:
        audioRecordToRedis(r, audioSeconds=SimConfig['audioSeconds'], format=pyaudio.paInt16,
                           channels=SimConfig['audioNChannels'], rate=SimConfig['audioRate'],
                           framesPerBuffer=SimConfig['audioFramesPerBuffer'])


if __name__ == '__main__':
    main()