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
import time

from RedisManager import hsetOnRedis, publishOnRedis
import Yamler

RedisConfig = Yamler.getConfigDict("Configs/RedisConfig.yaml")


def audioRecordToRedis(set, audioSeconds, format, channels, rate, framesPerBuffer):
    assert isinstance(set, str)
    assert isinstance(channels, int)
    assert isinstance(rate, int)
    assert isinstance(framesPerBuffer, int)
    assert isinstance(audioSeconds, int) or isinstance(audioSeconds, float)
    timestamp = time.time()
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
    params = {'channels': channels, 'sampwidth': audio.get_sample_size(format), 'rate': rate}
    redisStr = "[" + str(frames) + ", " + str(params) + "]"
    hsetOnRedis(key=RedisConfig['audioHsetRoot']+str(timestamp), field=RedisConfig['audioHsetB64Field'], value=redisStr,
                host=RedisConfig['host'], port=RedisConfig['port'], db=RedisConfig['db'])
    publishOnRedis(channel=RedisConfig['newAudioPubSubChannel'], msg=RedisConfig['newAudioMsgRoot']+str(timestamp),
                   host=RedisConfig['host'], port=RedisConfig['port'], db=RedisConfig['db'])


def main():
    format = pyaudio.paInt16
    channels = 2
    rate = 44100
    framesPerBuffer = 1024
    audioSeconds = 5
    audio = "test"
    while True:
        audioRecordToRedis(audio, audioSeconds, format, channels, rate, framesPerBuffer)


if __name__ == '__main__':
    main()