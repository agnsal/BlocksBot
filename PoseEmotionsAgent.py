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


from Configs import API_KEY, API_SECRET

from urllib.request import HTTPError
import requests
from RedisManager import getBase64FileFromRedis


def getBodies(base64Img):
    httpDetect = 'https://api-us.faceplusplus.com/humanbodypp/v1/skeleton'
    key = API_KEY
    secret = API_SECRET
    data = {
        'api_key': key,
        'api_secret': secret,
        'image_base64': base64Img,
    }
    try:
        #post data to server
        resp = requests.post(httpDetect, data)
        #get response
        faces = resp.json()
        return faces
    except HTTPError as e:
        print(e.read())


def getAttitude(body):
    #ToDo
    return


def main():
    i = 0
    while True:
        # print(i)  # Test
        if i == 50:
            data = getBodies(getBase64FileFromRedis("capture", "localhost", 0))
            print(data)  # Test
            if data:
                bodies = data['skeletons']
                for b in bodies:
                    print(b)  # Test
                    getAttitude(b)
            i = 0
        i += 1


if __name__ == '__main__':
    main()