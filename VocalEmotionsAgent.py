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
import pyaudio
import wave
import ast

from RedisManager import setBase64FileOnRedis, getBase64FileFromRedis, setStringOnRedis, getStringFromRedis

def audioRecordToRedis(set, audioSeconds, format, channels, rate, framesPerBuffer):
    assert isinstance(set, str)
    assert isinstance(channels, int)
    assert isinstance(rate, int)
    assert isinstance(framesPerBuffer, int)
    assert isinstance(audioSeconds, int) or isinstance(audioSeconds, float)
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
    '''
    waveFile = wave.open(set + ".wav", 'wb')
    waveFile.setnchannels(channels)
    waveFile.setsampwidth(audio.get_sample_size(format))
    waveFile.setframerate(rate)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
    '''
    params = {'channels': channels, 'sampwidth': audio.get_sample_size(format), 'rate': rate}
    setStringOnRedis("[" + str(frames) + ", " + str(params) + "]", set)



def extractEmotionsFromAudioFile(audio):
    print("Reading sound file...")  # Test
    data = ast.literal_eval(getStringFromRedis(audio))
    frames = data[0]
    params = data[1]
    waveFile = wave.open(audio + ".wav", 'wb')
    waveFile.setnchannels(int(params['channels']))
    waveFile.setsampwidth(params['sampwidth'])
    waveFile.setframerate(params['rate'])
    waveFile.writeframes(b''.join(frames))
    waveFile.close()
    (sampleRate, samples) = scipy.io.wavfile.read(audio + ".wav")
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
    emotions = {}
    if quality.valid:
        print("Neutral: %.3f" % emotionProbabilities.neutrality)
        print("Happy: %.3f" % emotionProbabilities.happiness)
        print("Sad: %.3f" % emotionProbabilities.sadness)
        print("Angry: %.3f" % emotionProbabilities.anger)
        print("Fear: %.3f" % emotionProbabilities.fear)
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

    format = pyaudio.paInt16
    channels = 2
    rate = 44100
    framesPerBuffer = 1024
    audioSeconds = 5
    audio = "test"

    while True:
        audioRecordToRedis(audio, audioSeconds, format, channels, rate, framesPerBuffer)
        extractEmotionsFromAudioFile(audio)


if __name__ == '__main__':
    main()

