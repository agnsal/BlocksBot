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

import scipy.io.wavfile
import Vokaturi
import wave
import ast

from RedisManager import RedisManager
import Yamler

RedisConfig = Yamler.getConfigDict("Configs/RedisConfig.yaml")


def extractEmotionsFromAudioFile(audioContent):
    assert isinstance(audioContent, str)
    emotions = {}
    print("Reading sound file...")  # Test
    data = ast.literal_eval(audioContent)
    frames = data[0]
    params = data[1]
    waveFile = wave.open("audio.wav", 'wb')
    waveFile.setnchannels(int(params['channels']))
    waveFile.setsampwidth(params['sampwidth'])
    waveFile.setframerate(params['rate'])
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
    (sampleRate, samples) = scipy.io.wavfile.read("audio.wav")
    bufferLen = len(samples)
    cBuffer = Vokaturi.SampleArrayC(bufferLen)
    if samples.ndim == 1:
        cBuffer[:] = samples[:] / 32768.0  # mono
    else:
        cBuffer[:] = 0.5 * (samples[:, 0] + 0.0 + samples[:, 1]) / 32768.0  # stereo
    voice = Vokaturi.Voice(sampleRate, bufferLen)
    voice.fill(bufferLen, cBuffer)
    print("Extracting emotions from VokaturiVoice...")  # Test
    quality = Vokaturi.Quality()
    emotionProbabilities = Vokaturi.EmotionProbabilities()
    voice.extract(quality, emotionProbabilities)
    if quality.valid:
        emotions["neutral"] = emotionProbabilities.neutrality
        emotions["happy"] = emotionProbabilities.happiness
        emotions["sad"] = emotionProbabilities.sadness
        emotions["angry"] = emotionProbabilities.anger
        emotions["fear"] = emotionProbabilities.fear
    voice.destroy()
    return emotions


def main():
    print("Loading library...")
    Vokaturi.load("lib/open/win/OpenVokaturi-3-3-win64.dll")
    print("Analyzed by: %s" % Vokaturi.versionAndLicense())

    r = RedisManager(host=RedisConfig['host'], port=RedisConfig['port'], db=RedisConfig['db'],
                     password=RedisConfig['password'], decodedResponses=RedisConfig['decodedResponses'])
    ps = r.getRedisPubSub()
    ps.subscribe(RedisConfig['newAudioPubSubChannel'])
    for newMsg in ps.listen():
        print(newMsg)
        print(type(newMsg))
        audioContent = r.hgetFromRedis(key=newMsg, field=RedisConfig['audioHsetB64Field'])
        audioEmotions = extractEmotionsFromAudioFile(audioContent)
        print(audioEmotions)  # Test


if __name__ == '__main__':
    main()

