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


import redis


def publishOnRedis(channel, msg, host="localhost", port=6379, db=0):
    assert isinstance(channel, str)
    assert isinstance(msg, str)
    assert isinstance(host, str)
    assert isinstance(port, int)
    assert isinstance(db, int)
    r = redis.StrictRedis(host=host, port=port, db=db)
    return r.publish(channel, msg)


def subscribeToRedis(channel, host="localhost", port=6379, db=0):
    assert isinstance(channel, str)
    assert isinstance(host, str)
    assert isinstance(port, int)
    assert isinstance(db, int)
    r = redis.StrictRedis(host=host, port=port, db=db)
    pubSub = r.pubsub()
    print(type(pubSub))
    sub = pubSub.subscribe(channel)
    return sub


def deleteFromRedis(key, host="localhost", port=6379, db=0):
    assert isinstance(key, str)
    assert isinstance(host, str)
    assert isinstance(port, int)
    assert isinstance(db, int)
    r = redis.StrictRedis(host=host, port=port, db=db)
    return r.delete(key)


def setBase64FileOnRedis(base64File, key, host="localhost", port=6379, db=0):
    assert isinstance(base64File, bytes)
    assert isinstance(key, str)
    assert isinstance(host, str)
    assert isinstance(port, int)
    assert isinstance(db, int)
    r = redis.StrictRedis(host=host, port=port, db=db)
    return r.set(key, base64File)


def getBase64FileFromRedis(key, host="localhost", port=6379, db=0):
    assert isinstance(key, str)
    assert isinstance(host, str)
    assert isinstance(port, int)
    assert isinstance(db, int)
    r = redis.StrictRedis(host=host, port=port, db=db)
    return r.get(key)


def setStringOnRedis(stringContent, key, host="localhost", port=6379, db=0):
    assert isinstance(stringContent, str)
    assert isinstance(key, str)
    assert isinstance(host, str)
    assert isinstance(port, int)
    assert isinstance(db, int)
    r = redis.StrictRedis(host=host, port=port, db=db)
    return r.set(key, stringContent)


def getStringFromRedis(key, host="localhost", port=6379, db=0, decodedResponses=True):
    assert isinstance(key, str)
    assert isinstance(host, str)
    assert isinstance(port, int)
    assert isinstance(db, int)
    r = redis.StrictRedis(host=host, db=db, port=port, decode_responses=decodedResponses)
    return r.get(key)


def hsetOnRedis(key, field, value, host="localhost", port=6379, db=0):
    assert isinstance(key, str)
    assert isinstance(field, str)
    assert isinstance(value, str)
    assert isinstance(host, str)
    assert isinstance(port, int)
    assert isinstance(db, int)
    r = redis.StrictRedis(host=host, port=port, db=db)
    return r.hset(key, field, value)


def hgetFromRedis(key, field, host="localhost", port=6379, db=0):
    assert isinstance(key, str)
    assert isinstance(field, str)
    assert isinstance(host, str)
    assert isinstance(port, int)
    assert isinstance(db, int)
    r = redis.StrictRedis(host=host, port=port, db=db)
    return r.hget(key, field)
