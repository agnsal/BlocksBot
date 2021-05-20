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


from urllib.request import HTTPError
import requests
import base64

from RedisManager import RedisManager
import Yamler

FacePPConfig = Yamler.getConfigDict("Configs/FacePlusPlusConfig.yaml")
RedisConfig = Yamler.getConfigDict("Configs/RedisConfig.yaml")


def getBodies(base64Img):
    key = FacePPConfig['API_KEY']
    secret = FacePPConfig['API_SECRET']
    httpSkeleton = FacePPConfig['SKELETON_URL']
    data = {
        'api_key': key,
        'api_secret': secret,
        'image_base64': base64Img,
    }
    try:
        #post data to server
        resp = requests.post(httpSkeleton, data)
        #get response
        bodies = resp.json()
        return bodies
    except HTTPError as e:
        print(e.read())


def getAttitude(body, errorThreshold):
    attitude = None
    if (body['landmark']['right_hand']['score'] > errorThreshold and
            body['landmark']['left_hand']['score'] > errorThreshold):
        RHandX = body['landmark']['right_hand']['x']
        LHandX = body['landmark']['left_hand']['x']
        bodyWidth = body['body_rectangle']['width']
        attitude = abs(RHandX - LHandX) / bodyWidth
    return attitude


def main():
    errorThreshold = 0.50
    r = RedisManager(host=RedisConfig['host'], port=RedisConfig['port'], db=RedisConfig['db'],
                     password=RedisConfig['password'], decodedResponses=RedisConfig['decodedResponses'])
    sub = r.getRedisPubSub()
    sub.subscribe(RedisConfig['newImagePubSubChannel'])
    for item in sub.listen():
        print(item)  # Test
        if item['type'] == 'message':
            newMsg = item['data']
            print("New Msg: " + str(newMsg))  # Test
            if not isinstance(newMsg, str):
                newMsg = newMsg.decode()
            detectedAttitudes = []
            imgID = newMsg
            img = r.hgetFromRedis(key=imgID, field=RedisConfig['imageHsetB64Field'])
            if img:
                if not isinstance(img, bytes):
                    img = base64.b64encode(img)
                data = getBodies(img)
                bodies = data['skeletons']
                for elem in bodies:
                    detectedAttitudes.append(getAttitude(elem, errorThreshold))
                r.rPushToRedisQueue(queue=RedisConfig['PoseQueue'], item=str(detectedAttitudes))
                r.hsetOnRedis(key=imgID, field=RedisConfig['imageHsetPoseResultField'], value=str(detectedAttitudes))
                print("Detected Attitudes: " + str(detectedAttitudes))  # Test


if __name__ == '__main__':
    main()