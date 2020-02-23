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


def getAttitude(body):
    RHandX = body['landmark']['right_hand']['x']
    RShoulderX = body['landmark']['right_shoulder']['x']
    LHandX = body['landmark']['left_hand']['x']
    LShoulderX = body['landmark']['left_shoulder']['x']
    bodyWidth = body['body_rectangle']['width']
    return (abs(int(RHandX) - int(RShoulderX)) + abs(int(LHandX) - int(LShoulderX))) / int(bodyWidth)


def main():
    r = RedisManager(host=RedisConfig['host'], port=RedisConfig['port'], db=RedisConfig['db'],
                     password=RedisConfig['password'], decodedResponses=RedisConfig['decodedResponses'])
    sub = r.getRedisPubSub()
    sub.subscribe(RedisConfig['newImagePubSubChannel'])
    while True:
        newMsg = sub.get_message()
        detectedAttitudes = []
        if newMsg:
            if newMsg['type'] == 'message':
                print("New Msg: " + str(newMsg))  # Test
                imgID = newMsg['data'].decode()
                img = r.hgetFromRedis(key=imgID, field=RedisConfig['imageHsetB64Field'])
                if not isinstance(img, bytes):
                    img = base64.b64encode(img)
                data = getBodies(img)
                bodies = data['skeletons']
                for elem in bodies:
                    detectedAttitudes.append(getAttitude(elem))
            print("Detected Attitudes: " + str(detectedAttitudes))
        '''
        print(data)  # Test
        if data:
            bodies = data['skeletons']
            for b in bodies:
                print(b)  # Test
                attitude = getAttitude(b)
                print(attitude)  # Test
        '''



if __name__ == '__main__':
    main()