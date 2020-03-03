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

import os
import time

from RedisManager import RedisManager
from Configs import RunnerConfig, RedisConfig, DeployPath, PythonExecutable


def parallelRun(f):
    command = PythonExecutable + " " + f + " &"
    print(command)
    p = os.system(command)
    return p


def main():
    r = RedisManager(host=RedisConfig['host'], port=RedisConfig['port'], db=RedisConfig['db'],
                     password=RedisConfig['password'], decodedResponses=RedisConfig['decodedResponses'])
    sub = r.getRedisPubSub()
    sub.subscribe(RedisConfig['StartStopChannel'])
    pList = []
    for item in sub.listen():
        print(item)
        if item['type'] == 'message':
            newMsg = item['data']
            if not isinstance(newMsg, str):
                newMsg = newMsg.decode()
            if newMsg == "start" and len(pList) == 0:
                agents = RunnerConfig['RunnableAgents']
                for a in agents:
                    print(DeployPath + a)
                    parallelRun(DeployPath + a)
                    pList.append(a)
            elif newMsg == "stop" and len(pList) > 0:
                time.sleep(1)
                pList = []
                print("Stopped")
            elif newMsg == "exit":
                r.publishOnRedis(channel=RedisConfig['StartStopChannel'], msg="stop")
                time.sleep(1)
                print("The End")
                return


if __name__ == '__main__':
    main()