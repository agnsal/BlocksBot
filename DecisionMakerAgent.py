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
from pyDatalog import pyDatalog
from TimeManager import getTimestamp

from RedisManager import RedisManager
import Yamler

RedisConfig = Yamler.getConfigDict("Configs/RedisConfig.yaml")
DMAConfig = Yamler.getConfigDict("Configs/DMAConfig.yaml")


def getAverageEmotionsFromRedisQueue(redis, queue, emotions):
    assert isinstance(queue, str)
    assert isinstance(emotions, list)
    avg = {}
    resList = []
    print(queue + ": " + str(redis.getRedisQueueLen(queue)))
    while redis.getRedisQueueLen(queue) > 0:
        elem = redis.lPopFromRedisQueue(queue)
        if isinstance(elem, bytes):
            elem = elem.decode()
        elem = ast.literal_eval(elem)
        if isinstance(elem, list) and len(elem) > 0:
            elem = elem[0]
        resList.append(elem)
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


def getAverageAttitudeFromRedisQueue(redis, queue):
    assert isinstance(queue, str)
    avg = {}
    resList = []
    print(queue + ": " + str(redis.getRedisQueueLen(queue)))
    while redis.getRedisQueueLen(queue) > 0:
        elem = redis.lPopFromRedisQueue(queue)
        if isinstance(elem, bytes):
            elem = elem.decode()
        elem = ast.literal_eval(elem)
        if isinstance(elem, list) and len(elem) > 0:
            elem = elem[0]
        resList.append(elem)
        resList.append(elem)
    print(resList)  # Test
    attitude = 0
    resN = len(resList)
    if resN != 0:
        for elem in resList:
            if isinstance(elem, float) or isinstance(elem, int):
                attitude += elem
        avg = attitude / resN
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

def learn():
    pyDatalog.create_terms('positive, neutral, negative, firstEmo, secondEmo, poseAttitude, X, Y, A, takeDecision, D, H, I, K')
    print("Learning started...")
    pyDatalog.assert_fact('positive', 'happiness')
    pyDatalog.assert_fact('neutral', 'neutral')
    pyDatalog.assert_fact('negative', 'sadness')
    pyDatalog.assert_fact('negative', 'fear')
    pyDatalog.assert_fact('negative', 'angry')

    pyDatalog.load("""
    firstEmo(X) <= firstAvgEmo(X)
    secondEmo(Y) <= secondAvgEmo(Y)
    attitude(A) <= poseAttitude(A)

    takeDecision(X) <= firstEmo(X) & secondEmo(Y) & attitude(A) & neutral(Y) & neutral(A)
    takeDecision(Y) <= firstEmo(X) & secondEmo(Y) & attitude(A) & neutral(X) & neutral(A)

    # 0, +, -
    takeDecision(X) <= firstEmo(X) & secondEmo(Y) & attitude(A) & neutral(X) & positive(Y) & negative(A)
    # 0, -, +
    takeDecision(X) <= firstEmo(X) & secondEmo(Y) & attitude(A) & neutral(X) & negative(Y) & positive(A)
    # +, 0, +
    takeDecision(X) <= firstEmo(X) & secondEmo(Y) & attitude(A) & positive(X) & neutral(Y) & positive(A)
    # -, 0, -
    takeDecision(X) <= firstEmo(X) & secondEmo(Y) & attitude(A) & negative(X) & neutral(Y) & negative(A)

    # -, -, _ (-, -, + problem ???????????)
    takeDecision(X) <= firstEmo(X) & secondEmo(Y) & attitude(A) & negative(X) & negative(Y) & neutral(A)
    # +, +, _ (+, +, - problem ???????????)
    takeDecision(X) <= firstEmo(X) & secondEmo(Y) & attitude(A) & negative(X) & negative(Y) & neutral(A)

    # 0, +, +
    takeDecision(Y) <= firstEmo(X) & secondEmo(Y) & attitude(A) & neutral(X) & positive(Y) & positive(A)
    # 0, -, -
    takeDecision(Y) <= firstEmo(X) & secondEmo(Y) & attitude(A) & neutral(X) & negative(Y) & negative(A)
    # +, 0, -
    takeDecision(Y) <= firstEmo(X) & secondEmo(Y) & attitude(A) & positive(X) & neutral(Y) & negative(A)
    # -, 0, +
    takeDecision(Y) <= firstEmo(X) & secondEmo(Y) & attitude(A) & negative(X) & neutral(Y) & positive(A)
    """)

    print("Learning finished")


def main():
    r = RedisManager(host=RedisConfig['host'], port=RedisConfig['port'], db=RedisConfig['db'],
                     password=RedisConfig['password'], decodedResponses=RedisConfig['decodedResponses'])
    sub = r.getRedisPubSub()
    sub.subscribe(RedisConfig['VocalChannel'])
    learn()
    while True:
        newMsg = sub.get_message()
        if newMsg:
            if newMsg['type'] == 'message':
                now = getTimestamp()
                print("Vocal Result: " + str(newMsg))  # Test
                vocalRes = ast.literal_eval(newMsg['data'].decode())
                facialRes = getAverageEmotionsFromRedisQueue(r, queue=RedisConfig['FacialQueue'],
                                                           emotions=DMAConfig['emotions'])
                facialVocal = facialVocalCompare(facialRes, vocalRes, emotions=DMAConfig['emotions'])
                print(facialVocal)  # Test
                if facialVocal:
                    sortedEmotions = {k: v for k, v in sorted(facialVocal.items(), key=lambda item: item[1])}
                    print(sortedEmotions)  # Test
                    sortedEmoList = list(sortedEmotions.items())
                    firstEmotion = sortedEmoList[-1]
                    secondEmotion = sortedEmoList[-2]
                    topEmotions = dict([firstEmotion, secondEmotion])
                    # print(topEmotions)  # Test
                    decision = firstEmotion
                    diff = 0
                    for k in topEmotions:
                        diff -= topEmotions[k]
                    diff = abs(diff)
                    if diff <= DMAConfig['poseTestThreshold']:
                        attitude = getAverageAttitudeFromRedisQueue(r, queue=RedisConfig['PoseQueue'])
                        if attitude:
                            pyDatalog.assert_fact('firstAvgEmo', str(firstEmotion))
                            pyDatalog.assert_fact('secondAvgEmo', str(secondEmotion))
                            pyDatalog.assert_fact('poseAttitude', str(attitude))
                            decision = str(pyDatalog.ask("takeDecision(D)"))
                            pyDatalog.retract_fact('firstEmo', str(firstEmotion))
                            pyDatalog.retract_fact('secondEmo', str(secondEmotion))
                            pyDatalog.retract_fact('poseAttitude', str(attitude))
                    r.setOnRedis(key=RedisConfig['DecisionSet'], value=str(decision))
                    r.publishOnRedis(channel=RedisConfig['newDecisionPubSubChannel'], msg=str(decision))
                    print("Decision: " + str(decision))  # Test
                r.deleteRedisElemsByKeyPatternAndTimestamp(RedisConfig['imageHsetRoot'] + '*', now,
                                                           DMAConfig['timeThreshold'])
                r.deleteRedisElemsByKeyPatternAndTimestamp(RedisConfig['audioHsetRoot'] + '*', now,
                                                           DMAConfig['timeThreshold'])



if __name__ == '__main__':
    main()