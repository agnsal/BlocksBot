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


import platform
import subprocess
from multiprocessing import Pool
import time

from RedisManager import RedisManager
import Yamler

RunnerConfig = Yamler.getConfigDict("Configs/RunnerConfig.yaml")
RedisConfig = Yamler.getConfigDict("Configs/RedisConfig.yaml")

activeProcesses = []


def parallelRur(f):
    global activeProcesses
    operativeS = platform.system()
    command = "python"
    if 'Windows' in operativeS:
        command = "py -3.6"
    p = subprocess.Popen(command + " " + f)
    print("Process " + str(p) + str(" running..."))  # Test
    activeProcesses.append(p)


def main():
    global activeProcesses
    agents = RunnerConfig['RunnableAgents']
    r = RedisManager(host=RedisConfig['host'], port=RedisConfig['port'], db=RedisConfig['db'],
                     password=RedisConfig['password'], decodedResponses=RedisConfig['decodedResponses'])
    sub = r.getRedisPubSub()
    sub.subscribe(RedisConfig['StartStopChannel'])
    for item in sub.listen():
        print(item)
        if item['type'] == 'message':
            newMsg = item['data']
            if not isinstance(newMsg, str):
                newMsg = newMsg.decode()
            if newMsg == "start" and len(activeProcesses) == 0:
                with Pool(len(agents)) as p:
                    p.map(parallelRur, agents)
            elif newMsg == "exit":
                r.publishOnRedis(channel=RedisConfig['StartStopChannel'], msg="exited")
                for p in activeProcesses:
                    p.kill()
                    time.sleep(1)
                print("The End")
                return



if __name__ == '__main__':
    main()