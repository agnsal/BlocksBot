# -*- coding: utf-8 -*-
from Configs import API_KEY, API_SECRET
from urllib.request import HTTPError
import base64
import requests
import cv2

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