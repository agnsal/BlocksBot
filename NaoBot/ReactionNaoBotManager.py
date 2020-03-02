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
    while True:
        currentDecision = r.getFromRedis(RedisConfig['DecisionSet'])
        if isinstance(currentDecision, bytes):
            currentDecision.decode()
        currentDecision = ast.literal_eval(currentDecision)
        currentEmotion = currentDecision[0]
        if currentEmotion in EmotionConfig['emotions']:
            tts = ALProxy("ALTextToSpeech", NaoConfig['IP'], NaoConfig['PORT'])
            reaction = EmotionConfig['NaoReactions'][currentEmotion]
            tts.say("Current emotion is: " + reaction + " " + currentEmotion)
        time.sleep(NaoConfig['reactionSleepSec'])


if __name__ == '__main__':
    main()
