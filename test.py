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


from Configs import API_KEY, API_SECRET
from urllib.request import HTTPError
import base64
import requests

def getFacesAndEmotions():
    httpDetect = 'https://api-us.faceplusplus.com/facepp/v3/detect'
    key = API_KEY
    secret = API_SECRET
    filepath = "Files/Res.jpg"
    with open(filepath, "rb") as image_file:
        base64Img = base64.b64encode(image_file.read())
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
        print(faces["faces"][0]["attributes"]["emotion"])
        return faces
    except HTTPError as e:
        print(e.read())


getFacesAndEmotions()