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

from RedisManager import RedisManager
import Yamler

FacePPConfig = Yamler.getConfigDict("Configs/FacePlusPlusConfig.yaml")
RedisConfig = Yamler.getConfigDict("Configs/RedisConfig.yaml")


def getFacesAndEmotions(base64Img):
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
    i = 0
    r = RedisManager(host=RedisConfig['host'], port=RedisConfig['port'], db=RedisConfig['db'],
                     password=RedisConfig['password'], decodedResponses=RedisConfig['decodedResponses'])
    while True:
        # print(i)  # Test
        if i == 50:
            data = getFacesAndEmotions(r.getBase64FileFromRedis("capture"))
            if data:
                if data["faces"]:
                    emotions = data["faces"][0]["attributes"]["emotion"]
                    print("EMOTIONS: " + str(emotions))
                i = 0
        i += 1


if __name__ == '__main__':
    main()