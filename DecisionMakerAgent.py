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

from RedisManager import RedisManager
import Yamler

RedisConfig = Yamler.getConfigDict("Configs/RedisConfig.yaml")


def getAverageResultFromRedisQueue(redis, queue, queueRange):
    assert isinstance(queue, str)
    assert isinstance(queueRange, int)
    avg = {}
    resList = []
    for i in range(0, queueRange + 1):
        elem = redis.rPopFromRedisQueue(queue)
        if isinstance(elem, bytes):
            elem = elem.decode()
        if elem:
            resList.append(ast.literal_eval(elem)[0])
    print(resList)  # Test
    redis.deleteFromRedis(key=RedisConfig['FacialQueue'])
    happinessSum = 0
    neutralSum = 0
    sadnessSum = 0
    fearSum = 0
    disgustSum = 0
    resN = len(resList)
    if resN != 0:
        for elem in resList:
            happinessSum += elem['happiness']
            neutralSum += elem['neutral']
            sadnessSum += elem['sadness']
            fearSum += elem['fear']
            disgustSum += elem['disgust']
        avg = {'happiness': happinessSum/resN, 'neutral': neutralSum/resN, 'sadness': sadnessSum/resN,
                'fear': fearSum/resN, 'disgust': disgustSum/resN}
    return avg


def facialVocalCompare(facialRes, vocalRes, facialW=2, vocalW=1):
    assert isinstance(facialRes, dict)
    assert isinstance(facialW, int) or isinstance(facialW, float)
    assert isinstance(vocalW, int) or isinstance(vocalW, float)
    res = {}
    tot = facialW + vocalW
    for emo in ['happiness', 'neutral', 'sadness', 'fear', 'disgust']:
        print(facialRes[emo])
        res[emo] = (facialRes[emo] * facialW + vocalRes[emo] * vocalW) / tot
    return res


def main():
    queueRange = 10
    r = RedisManager(host=RedisConfig['host'], port=RedisConfig['port'], db=RedisConfig['db'],
                     password=RedisConfig['password'], decodedResponses=RedisConfig['decodedResponses'])
    sub = r.getRedisPubSub()
    sub.subscribe(RedisConfig['VocalChannel'])
    while True:
        newMsg = sub.get_message()
        if newMsg:
            if newMsg['type'] == 'message':
                print("Vocal Result: " + str(newMsg))  # Test
                vocalRes = newMsg['data'].decode()
                facialRes = getAverageResultFromRedisQueue(r, RedisConfig['FacialQueue'], queueRange)
                facialVocal = facialVocalCompare(facialRes, vocalRes)
                print(facialVocal)



if __name__ == '__main__':
    main()