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


def getFacesAndEmotions(base64Img):
    assert isinstance(base64Img, bytes)
    data = {
        'api_key': FacePPConfig['API_KEY'],
        'api_secret': FacePPConfig['API_SECRET'],
        'image_base64': base64Img,
        'return_attributes': 'emotion',
    }
    try:
        #post data to server
        resp = requests.post(FacePPConfig['DETECT_URL'], data)
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
    while True:
        newMsg = sub.get_message()
        if newMsg:
            if newMsg['type'] == 'message':
                print("New Msg: " + str(newMsg))  # Test
                imgID = newMsg['data'].decode()
                img = base64.b64encode(r.hgetFromRedis(key=imgID, field=RedisConfig['imageHsetB64Field']))
                data = getFacesAndEmotions(img)
                if data:
                    print(data)  # Test
                    if "faces" in data.keys():
                        emotions = data["faces"][0]["attributes"]["emotion"]
                        print("EMOTIONS: " + str(emotions))  # test
                    else:
                        print("No face detected")  # Test
                else:
                    print("No data detected")  # Test


if __name__ == '__main__':
    main()