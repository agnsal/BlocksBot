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
            if isinstance(elem, dict) and any(elem in emotions for elem in list(elem.keys())):
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
    pyDatalog.create_terms('attitudeLThreshold, attitudeRThreshold, firstEmoPercept, secondEmoPercept, '
                           'poseAttitudePercept, takeDecision, D, negativeEmotion, positiveEmotion, neutralEmotion')
    print("Learning started...")
    pyDatalog.assert_fact('attitudeLThreshold', DMAConfig['attitudeLThreshold'])
    pyDatalog.assert_fact('attitudeRThreshold', DMAConfig['attitudeRThreshold'])
    pyDatalog.assert_fact('positiveEmotion', 'happiness')
    pyDatalog.assert_fact('neutralEmotion', 'neutral')
    for negEmo in ['sadness', 'fear', 'angry']:
        pyDatalog.assert_fact('negativeEmotion', negEmo)

    pyDatalog.load("""    
    positive(P) <= positiveEmotion(P)
    positive(P) <= attitude(P) & attitudeRThreshold(R) & (P >= R)
    neutral(O) <= neutralEmotion(O)
    neutral(O) <= attitude(O) & attitudeRThreshold(R) & (R > O) & attitudeLThreshold(L) & (O > L)
    negative(N) <= negativeEmotion(N)
    negative(N) <= attitude(N) & attitudeLThreshold(L) & (N <= L)
    
    firstEmo(X) <= firstEmoPercept(X)
    secondEmo(Y) <= secondEmoPercept(Y)
    attitude(A) <= poseAttitudePercept(A)
    estimations(X, Y, A) <= firstEmo(X) & secondEmo(Y) & attitude(A)

    takeDecision(X) <= estimations(X, Y, A) & neutral(Y) & neutral(A)
    takeDecision(Y) <= estimations(X, Y, A) & neutral(X) & neutral(A)

    # 0, +, -
    takeDecision(X) <= estimations(X, Y, A) & neutral(X) & positive(Y) & negative(A)
    # 0, -, +
    takeDecision(X) <= estimations(X, Y, A) & neutral(X) & negative(Y) & positive(A)
    # +, 0, +
    takeDecision(X) <= estimations(X, Y, A) & positive(X) & neutral(Y) & positive(A)
    # -, 0, -
    takeDecision(X) <= estimations(X, Y, A) & negative(X) & neutral(Y) & negative(A)

    # -, -, _ 
    takeDecision(X) <= estimations(X, Y, A) & negative(X) & negative(Y)
    # +, +, _ 
    takeDecision(X) <= estimations(X, Y, A) & positive(X) & positive(Y)

    # 0, +, +
    takeDecision(Y) <= estimations(X, Y, A) & neutral(X) & positive(Y) & positive(A)
    # 0, -, -
    takeDecision(Y) <= estimations(X, Y, A) & neutral(X) & negative(Y) & negative(A)
    # +, 0, -
    takeDecision(Y) <= estimations(X, Y, A) & positive(X) & neutral(Y) & negative(A)
    # -, 0, +
    takeDecision(Y) <= estimations(X, Y, A) & negative(X) & neutral(Y) & positive(A)
    
    # _, _, 0
    takeDecision(X) <= estimations(X, Y, A) & neutral(A)
    # -, +, +
    takeDecision(Y) <= estimations(X, Y, A) & negative(X) & positive(Y) & positive(A)
    # -, +, -
    takeDecision(X) <= estimations(X, Y, A) & negative(X) & positive(Y) & negative(A)
    # +, -, -
    takeDecision(Y) <= estimations(X, Y, A) & positive(X) & negative(Y) & negative(A)
    # +, -, +
    takeDecision(X) <= estimations(X, Y, A) & positive(X) & negative(Y) & positive(A)
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
                msgContent = newMsg['data'].decode()
                print("Vocal Result: " + str(newMsg))  # Test
                facialRes = getAverageEmotionsFromRedisQueue(r, queue=RedisConfig['FacialQueue'],
                                                           emotions=DMAConfig['emotions'])
                if msgContent == str(RedisConfig['voidMsg']):
                    facialVocal = facialRes
                else:
                    vocalRes = ast.literal_eval(msgContent)
                    facialVocal = facialVocalCompare(facialRes, vocalRes, emotions=DMAConfig['emotions'],
                                                 facialW=DMAConfig['facialWeight'], vocalW=DMAConfig['vocalWeight'])
                print("FACIAL VOCAL:" + str(facialVocal))  # Test
                if facialVocal:
                    sortedEmotions = {k: v for k, v in sorted(facialVocal.items(), key=lambda item: item[1])}
                    print(sortedEmotions)  # Test
                    sortedEmoList = list(sortedEmotions.items())
                    firstEmotion = sortedEmoList[-1]
                    secondEmotion = sortedEmoList[-2]
                    topEmotions = dict([firstEmotion, secondEmotion])
                    decisionWithPer = firstEmotion
                    diff = 0
                    for k in topEmotions:
                        diff -= topEmotions[k]
                    diff = abs(diff)
                    attitude = getAverageAttitudeFromRedisQueue(r, queue=RedisConfig['PoseQueue'])
                    print("DATA: " + str(firstEmotion) + ", " + str(secondEmotion) + ", " + str(attitude))
                    if diff <= DMAConfig['poseTestThreshold']:
                        if attitude:
                            pyDatalog.assert_fact('firstEmoPercept', firstEmotion[0])
                            pyDatalog.assert_fact('secondEmoPercept', secondEmotion[0])
                            pyDatalog.assert_fact('poseAttitudePercept', attitude)
                            decision = str(pyDatalog.ask("takeDecision(D)")).replace("{('", "").replace("'", "").split(",")[0]
                            decisionWithPer = (decision, str(topEmotions[decision]))
                            pyDatalog.retract_fact('firstEmoPercept', firstEmotion[0])
                            pyDatalog.retract_fact('secondEmoPercept', secondEmotion[0])
                            pyDatalog.retract_fact('poseAttitudePercept', attitude)
                    r.setOnRedis(key=RedisConfig['DecisionSet'], value=str(decisionWithPer))
                    r.publishOnRedis(channel=RedisConfig['newDecisionPubSubChannel'], msg=str(decisionWithPer))
                    print("Decision: " + str(decisionWithPer))  # Test
                r.deleteRedisElemsByKeyPatternAndTimestamp(RedisConfig['imageHsetRoot'] + '*', now,
                                                           DMAConfig['timeThreshold'])
                r.deleteRedisElemsByKeyPatternAndTimestamp(RedisConfig['audioHsetRoot'] + '*', now,
                                                           DMAConfig['timeThreshold'])



if __name__ == '__main__':
    main()