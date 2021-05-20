# coding : utf-8

'''
Copyright 2020-2021 Agnese Salutari.
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


def getFacesAndEmotions(base64Img):
    assert isinstance(base64Img, bytes)
    key = FacePPConfig['API_KEY']
    secret = FacePPConfig['API_SECRET']
    httpDetect = FacePPConfig['DETECT_URL']
    data = {
        'api_key': key,
        'api_secret': secret,
        'image_base64': base64Img,
        'return_attributes': 'emotion',
    }
    try:
        #post data to server
        resp = requests.post(httpDetect, data)
        #get response
        faces = resp.json()
        return faces
    except HTTPError as e:
        print(e.read())


def main():
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
            detectedEmotions = []
            imgID = newMsg
            img = r.hgetFromRedis(key=imgID, field=RedisConfig['imageHsetB64Field'])
            if img:
                if not isinstance(img, bytes):
                    img = base64.b64encode(img)
                data = getFacesAndEmotions(img)
                if data:
                    print(data)  # Test
                    if "faces" in data.keys():
                        faces = data['faces']
                        for elem in faces:
                            detectedEmotions.append(elem['attributes']['emotion'])
                        print("Detected emotions: " + str(detectedEmotions))  # Test
                        r.rPushToRedisQueue(queue=RedisConfig['FacialQueue'], item=str(detectedEmotions))
                        r.hsetOnRedis(key=imgID, field=RedisConfig['imageHsetFacialResultField'],
                                      value=str(detectedEmotions))
                    else:
                        print("No face detected")  # Test
                else:
                    print("No data detected")  # Test


if __name__ == '__main__':
    main()