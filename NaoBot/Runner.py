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

from Configs import RunnerConfig


def parallelRur(f):
    operativeS = platform.system()
    command = "python"
    if 'Windows' in operativeS:
        command = "py -2.7"
    subprocess.call(command + " " + f)


def main():
    agents = RunnerConfig['RunnableAgents']
    pool = Pool(len(agents))
    pool.map(parallelRur, agents)


if __name__ == '__main__':
    main()