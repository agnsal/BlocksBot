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
import base64

from RedisManager import RedisManager
import Yamler

RedisConfig = Yamler.getConfigDict("Configs/RedisConfig.yaml")


def extractEmotionsFromAudioFile(frames, params):
    emotions = {}
    print("Reading sound file...")  # Test
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
        emotions["happiness"] = emotionProbabilities.happiness
        emotions["sadness"] = emotionProbabilities.sadness
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
    sub = r.getRedisPubSub()
    sub.subscribe(RedisConfig['newAudioPubSubChannel'])
    for item in sub.listen():
        print(item)  # Test
        if item['type'] == 'message':
            newMsg = item['data']
            print("New Msg: " + str(newMsg))  # Test
            if not isinstance(newMsg, str):
                newMsg = newMsg.decode()
            audioID = newMsg
            audioContent = r.hgetFromRedis(key=audioID, field=RedisConfig['audioHsetB64Field'])
            audioParams = r.hgetFromRedis(key=audioID, field=RedisConfig['audioHsetParamsField'])
            if audioContent:
                if isinstance(audioParams, bytes):
                    audioParams = audioParams.decode('utf-8')
                if isinstance(audioContent, bytes):
                    audioContent = audioContent.decode('utf-8')
                audioContent = base64.b64decode(audioContent)
                audioContent = ast.literal_eval(audioContent.decode('utf-8'))
                audioParams = ast.literal_eval(audioParams)
                audioEmotions = extractEmotionsFromAudioFile(audioContent, audioParams)
                print(audioEmotions)  # Test
                if not audioEmotions:
                    audioEmotions = RedisConfig['voidMsg']
                r.publishOnRedis(channel=RedisConfig['VocalChannel'], msg=str(audioEmotions))
                r.hsetOnRedis(key=audioID, field=RedisConfig['audioHsetVocalResultField'], value=str(audioEmotions))



if __name__ == '__main__':
    main()

