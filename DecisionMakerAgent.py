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

import ast
import collections
from pyDatalog import pyDatalog

from RedisManager import RedisManager
import Yamler

RedisConfig = Yamler.getConfigDict("Configs/RedisConfig.yaml")
DMAConfig = Yamler.getConfigDict("Configs/DMAConfig.yaml")


def getAverageResultFromRedisQueue(redis, queue, emotions):
    assert isinstance(queue, str)
    assert isinstance(emotions, list)
    avg = {}
    resList = []
    print(queue + ": " + str(redis.getRedisQueueLen(queue)))
    while redis.getRedisQueueLen(queue) > 0:
        elem = redis.lPopFromRedisQueue(queue)
        if isinstance(elem, bytes):
            elem = elem.decode()
        resList.append(ast.literal_eval(elem))
    print(resList)  # Test
    happinessSum = 0
    neutralSum = 0
    sadnessSum = 0
    fearSum = 0
    disgustSum = 0
    resN = len(resList)
    if resN != 0:
        for elem in resList:
            if isinstance(elem, dict) and set(emotions) <= set(elem.keys()):
                happinessSum += elem['happiness']
                neutralSum += elem['neutral']
                sadnessSum += elem['sadness']
                fearSum += elem['fear']
                disgustSum += elem['disgust']
        avg = {'happiness': happinessSum/resN, 'neutral': neutralSum/resN, 'sadness': sadnessSum/resN,
                'fear': fearSum/resN, 'disgust': disgustSum/resN}
    return avg


def facialVocalCompare(facialRes, vocalRes, emotions, facialW=2, vocalW=1):
    assert isinstance(facialRes, dict)
    assert isinstance(vocalRes, dict)
    assert isinstance(facialW, int) or isinstance(facialW, float)
    assert isinstance(vocalW, int) or isinstance(vocalW, float)
    assert isinstance(emotions, list)
    res = {}
    tot = facialW + vocalW
    if isinstance(facialRes, dict) and isinstance(vocalRes, dict) and set(emotions) <= set(facialRes.keys()) \
            and set(emotions) <= set(vocalRes.keys()):
        for emo in emotions:
            res[emo] = (facialRes[emo] * facialW + vocalRes[emo] * vocalW) / tot
    elif isinstance(facialRes, dict) and set(emotions) <= set(facialRes.keys()):
        res = facialRes
    elif isinstance(vocalRes, dict) and set(emotions) <= set(vocalRes.keys()):
        res = vocalRes
    return res


def main():
    r = RedisManager(host=RedisConfig['host'], port=RedisConfig['port'], db=RedisConfig['db'],
                     password=RedisConfig['password'], decodedResponses=RedisConfig['decodedResponses'])
    sub = r.getRedisPubSub()
    sub.subscribe(RedisConfig['VocalChannel'])

    behaviourFilePath = 'behaviour.dl'

    while True:
        newMsg = sub.get_message()
        if newMsg:
            if newMsg['type'] == 'message':
                print("Vocal Result: " + str(newMsg))  # Test
                vocalRes = ast.literal_eval(newMsg['data'].decode())
                facialRes = getAverageResultFromRedisQueue(r, queue=RedisConfig['FacialQueue'],
                                                           emotions=DMAConfig['emotions'])
                facialVocal = facialVocalCompare(facialRes, vocalRes, emotions=DMAConfig['emotions'])
                print(facialVocal)  # Test
                sortedEmotions = {k: v for k, v in sorted(facialVocal.items(), key=lambda item: item[1])}
                print(sortedEmotions)  # Test
                sortedEmoList = list(sortedEmotions.items())
                topEmotions = dict([sortedEmoList[-1], sortedEmoList[-2]])
                print(topEmotions)



if __name__ == '__main__':
    main()