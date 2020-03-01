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

class RedisManager:
    __host = None
    __port = None
    __db = None
    __password = None
    __decodedResponses = None
    __redis = None

    def __init__(self, host="localhost", port=6379, db=0, password='', decodedResponses=True):
        assert isinstance(host, str)
        assert isinstance(port, int)
        assert isinstance(db, int)
        assert isinstance(password, str)
        assert isinstance(decodedResponses, bool)
        self.__host = host
        self.__port = port
        self.__db = db
        self.__password = password
        self.__decodedResponses = decodedResponses
        self.update()

    def getHost(self):
        return self.__host

    def getPort(self):
        return self.__port

    def getDB(self):
        return self.__db

    def getPassword(self):
        return self.__password

    def getDecodedResponses(self):
        return self.__decodedResponses

    def update(self):
        self.__redis = redis.Redis(host=self.__host, port=self.__port, db=self.__db, password=self.__password,
                                         decode_responses=self.__decodedResponses)

    def setHost(self, host):
        assert isinstance(host, str)
        self.__host = host
        self.update()

    def setPort(self, port):
        assert isinstance(port, int)
        self.__port = port
        self.update()

    def setDB(self, db):
        assert isinstance(db, int)
        self.__db = db
        self.update()

    def setPassword(self, password):
        assert isinstance(password, str)
        self.__password = password
        self.update()

    def setDecodedResponses(self, decodedResponses):
        assert isinstance(decodedResponses, bool)
        self.__decodedResponses = decodedResponses
        self.update()

    def publishOnRedis(self, channel, msg):
        assert isinstance(channel, str)
        assert isinstance(msg, str)
        print(msg)
        return self.__redis.publish(channel, msg)

    def getRedisPubSub(self):
        return self.__redis.pubsub()

    def deleteFromRedis(self, key):
        assert isinstance(key, str)
        return self.__redis.delete(key)

    def setOnRedis(self, key, value):
        assert isinstance(key, str)
        assert isinstance(value, str) or isinstance(value, bytes)
        return self.__redis.set(key, value)

    def getFromRedis(self, key):
        assert isinstance(key, str)
        return self.__redis.get(key)

    def hsetOnRedis(self, key, field, value):
        assert isinstance(key, str)
        assert isinstance(field, str)
        assert isinstance(value, str) or isinstance(value, bytes)
        return self.__redis.hset(key, field, value)

    def hgetFromRedis(self, key, field):
        assert isinstance(key, str)
        assert isinstance(field, str)
        return self.__redis.hget(key, field)

    def rPushToRedisQueue(self, queue, item):
        assert isinstance(queue, str)
        assert isinstance(item, str) or isinstance(item, bytes)
        return self.__redis.rpush(queue, item)

    def lPushToRedisQueue(self, queue, item):
        assert isinstance(queue, str)
        assert isinstance(item, str) or isinstance(item, bytes)
        return self.__redis.lpush(queue, item)

    def rPopFromRedisQueue(self, queue):
        assert isinstance(queue, str)
        return self.__redis.rpop(queue)

    def lPopFromRedisQueue(self, queue):
        assert isinstance(queue, str)
        return self.__redis.lpop(queue)

    def getRedisQueueLen(self, queue):
        assert isinstance(queue, str)
        return self.__redis.llen(queue)

    def getRedisElemsByKeyPattern(self, pattern):
        assert isinstance(pattern, str)
        return self.__redis.keys(pattern)

    def deleteRedisElemsByKeyPattern(self, pattern):
        assert isinstance(pattern, str)
        keys = self.__redis.keys(pattern)
        for k in keys:
            self.__redis.delete(k)

    def deleteRedisElemsByKeyPatternAndTimestamp(self, pattern, now, threshold):
        assert isinstance(pattern, str)
        assert isinstance(now, int) or isinstance(now, float)
        assert isinstance(threshold, int) or isinstance(threshold, float)
        keys = self.__redis.keys(pattern)
        for k in keys:
            if not isinstance(k, str):
                k = k.decode()
            pattern = pattern.replace('*', '')
            oldTime = str(k).replace(pattern, '')
            if now - float(oldTime) >= threshold:
                self.__redis.delete(k)
