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


import redis


def setBase64FileOnRedis(base64File, name, host="localhost", db=0):
    assert isinstance(base64File, bytes)
    assert isinstance(name, str)
    assert isinstance(host, str)
    assert isinstance(db, int)
    r = redis.StrictRedis(host=host, db=db)
    r.set(name, base64File)
    print(type(r.get(name)))


def getBase64FileFromRedis(imageName, host="localhost", db=0):
    assert isinstance(imageName, str)
    assert isinstance(host, str)
    assert isinstance(db, int)
    r = redis.StrictRedis(host=host, db=db)
    return r.get(imageName)