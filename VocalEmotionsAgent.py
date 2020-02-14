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


import Vokaturi
import sounddevice as sd

fs = 44100
duration = 5  # seconds

record = sd.rec(duration * fs, samplerate=fs, channels=2, dtype='float64')
print("Recording...")
sd.wait()
print("Recorded")

#sd.play(record, fs)  # Test
#sd.wait()  # Test

print("Loading library...")
Vokaturi.load("lib/open/win/OpenVokaturi-3-3-win64.dll")
print("Analyzed by: %s" % Vokaturi.versionAndLicense())

print("Allocating Vokaturi sample array...")
bufferLen = len(record)
print("   %d samples, %d channels" % (bufferLen, record.ndim))
c_buffer = Vokaturi.SampleArrayC(bufferLen)
if record.ndim == 1:
    c_buffer[:] = record[:] / 32768.0  # mono
else:
    c_buffer[:] = 0.5*(record[:,0]+0.0+record[:,1]) / 32768.0  # stereo

print("Creating VokaturiVoice...")
voice = Vokaturi.Voice(fs, bufferLen)

print("Filling VokaturiVoice with samples...")
voice.fill(bufferLen, c_buffer)

print("Extracting emotions from VokaturiVoice...")
quality = Vokaturi.Quality()
emotionProbabilities = Vokaturi.EmotionProbabilities()
voice.extract(quality, emotionProbabilities)

#print("Quality: " + str(quality.valid))
#print("Emotions: " + str(emotionProbabilities.neutrality))

if quality.valid:
    print("Neutral: %.3f" % emotionProbabilities.neutrality)
    print("Happy: %.3f" % emotionProbabilities.happiness)
    print("Sad: %.3f" % emotionProbabilities.sadness)
    print("Angry: %.3f" % emotionProbabilities.anger)
    print("Fear: %.3f" % emotionProbabilities.fear)

voice.destroy()

