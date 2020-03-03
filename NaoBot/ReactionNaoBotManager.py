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

from RedisManager import RedisManager
from Configs import RedisConfig, NaoConfig, EmotionConfig

import time
import ast


def main():
    r = RedisManager(host=RedisConfig['host'], port=RedisConfig['port'], db=RedisConfig['db'],
                     password=RedisConfig['password'], decodedResponses=RedisConfig['decodedResponses'])
    subD = r.getRedisPubSub()
    subD.subscribe(RedisConfig['newDecisionPubSubChannel'])
    sub = r.getRedisPubSub()
    sub.subscribe(RedisConfig['StartStopChannel'])
    tts = ALProxy("ALAnimatedSpeech", NaoConfig['IP'], NaoConfig['PORT'])
    motionProxy = ALProxy("ALMotion", NaoConfig['IP'], NaoConfig['PORT'])
    postureProxy = ALProxy("ALRobotPosture", NaoConfig['IP'], NaoConfig['PORT'])
    motionProxy.wakeUp()  # Wake up robot
    postureProxy.goToPosture("StandInit", 0.5)  # Send robot to Stand Init
    while True:
        newMsg = sub.get_message()
        newD = subD.get_message()
        if newMsg:
            if newMsg['type'] == 'message':
                command = newMsg['data']
                if not isinstance(command, str):
                    command = command.decode()
                if command == "stop":
                    break
        elif newD:
            print(newD)
            if newD['type'] == 'message':
                decision = newD['data']
                if isinstance(decision, bytes):
                    decision = decision.decode()
                decision = ast.literal_eval(decision)
                currentEmotion = decision[0]
                print(currentEmotion)
                if currentEmotion in EmotionConfig['emotions']:
                    print("working...")
                    reaction = EmotionConfig['NaoReactions'][currentEmotion]
                    ita = EmotionConfig['NaoTranslate'][currentEmotion]
                    tts.say("^start(" + reaction + ") " + ita + " ^wait(" + reaction + ")")
        print("Reading...")
        time.sleep(NaoConfig['reactionSleepSec'])
    motionProxy.rest()  # Go to rest position


if __name__ == '__main__':
    main()
