# Copyright 2017 Apex.AI, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum
import itertools
import os
import signal
import subprocess
import sys
import yaml
import datetime
import generate_cmd as gc
import time

#max cache sizeの目安サイズ(1秒のレコードサイズ⇨topicサイズ*rate)
def max_cache_size_rule_of_thumb(topic,rate):
    mcs_dic = {"Array1k":1044,"Array4k":4116,"Array16k":16404,"Array32k":32768,"Array64k":65556,"Array256k":262164,"Array1m":1048596,"Array2m":2097172,
    "Struct256":532,"Struct4k":8468,"Struct32k":67732,"PointCloud512k":526740,"PointCloud1m":1051028,"PointCloud2m":2099604,"PointCloud4m":4196756,
    "Range":308,"NavSatFix":396,"RadarDetection":84,"RadarTrack":844}
    mcs_rule_of_thumb = mcs_dic[topic]*int(rate)
    return mcs_rule_of_thumb

#eval.pyでこのプログラムを実行する際のコマンドライン引数を取得
record_product = list(gc.get_record_product()[int(sys.argv[1])]) #argv[1]番目のrecordのパラメータ
perf_test_product = list(gc.get_perf_test_product()[int(sys.argv[2])]) # argv[2]番目のperf_testのパラメータ
output_path = sys.argv[3]
bagfile_path = output_path + "/bagfile" #argv[3]のパスにbagfileを作成
num_of_publish = gc.get_perf_test_num_of_publish()


topic = perf_test_product[0]
rate = perf_test_product[1]
perf_qos_r = perf_test_product[3]
perf_qos_d = perf_test_product[4]

record_qos_r = record_product[0]
record_qos_d = record_product[1]
no_discovery = record_product[2]
max_cache_size = record_product[3]
storage_preset_profile = record_product[4]

#recordコマンドを作成
record_nd_cmd = ""
record_mcs_cmd = ""
base_spp_cmd = ""
record_spp_cmd = ""
record_qos_cmd = f"record_qos_override/{topic}/{record_qos_r}:{record_qos_d}.yaml"
record_cmd = ""

if no_discovery == "true":
    record_nd_cmd = "--no-discovery"

if max_cache_size == "guide": #mcsを目安にする(topicサイズ*rate)
    mcs_rule_of_thumb = max_cache_size_rule_of_thumb(topic,rate)
    record_mcs_cmd = f"--max-cache-size {mcs_rule_of_thumb}"
elif max_cache_size == "default":
    record_mcs_cmd = ""
else:
    record_mcs_cmd = f"--max-cache-size {max_cache_size}"

if storage_preset_profile == "resilient":
    record_spp_cmd = f"--storage-preset-profile resilient"

record_cmd =  f"ros2 bag record /test_{topic} -o {bagfile_path}" 
record_cmd_option = f" --qos-profile-overrides-path {record_qos_cmd} {record_nd_cmd} {record_mcs_cmd} {record_spp_cmd} "
record_cmd += record_cmd_option

record_process = None

done_experiment = False

current_index = 0 #1回だけ実行



# class Type(Enum):
#     """Define the enumeration for the experiment types."""

#     PUBLISHER = 0
#     SUBSCRIBER = 1
#     BOTH = 2


class Instance:
    """perf_test process encapsulation."""

    def __init__(self):
        """
        Construct the object.
        
        :param operation_type: Type of the operation
        """
        self.product = perf_test_product
        self.process = None

    def run(self):
        global record_process
        with open(f'{output_path}/pub_time_before_del.txt','w') as f:
            if no_discovery == "true": #no discoveryがONなら、perf_testを先に起動し、トピックを作成、メッセージをパブリッシュするまでにレコードを起動
                self.process = subprocess.Popen(self.perf_cmd(), stdout=f, shell=True,encoding='UTF-8', universal_newlines=True)
                time.sleep(1000)
                record_process = subprocess.Popen(record_cmd,shell=True)
            else:
                record_process = subprocess.Popen(record_cmd,shell=True)
                self.process = subprocess.Popen(self.perf_cmd(), stdout=f, shell=True,encoding='UTF-8', universal_newlines=True)
        # record_process = subprocess.Popen(record_cmd,shell=True)
        # time.sleep(0.1)
        # self.process = subprocess.Popen(self.perf_cmd(), shell=True)

    def perf_cmd(self):
        command = 'ros2 run performance_test perf_test'
        pubs_args = ' -p 1 '

        fixed_args = ' --communication rclcpp-single-threaded-executor '

        topic_name = f'test_{topic}' #トピックの名前を逐次変更する(理由：Only topics with one type are supported)
        perf_test_qos_r = ""
        perf_test_qos_d = ""
        if perf_qos_r == "reliable":
            perf_test_qos_r = "--reliable"
        if perf_qos_d == "transient":
            perf_test_qos_d = "--transient"
        dyn_args = f" --msg {topic} --topic {topic_name} --rate {rate} -s 0 {perf_test_qos_r} {perf_test_qos_d}"

        print('*********perf_test_command**********')
        print(command + ' ' + fixed_args + dyn_args + pubs_args)

        #recordコマンド
        print('*********record_command**********')
        print(record_cmd)
        print('*******************')
        #record開始(envコマンドを使用するためコマンド全体を''で分割)
        # record_process = subprocess.Popen(['ros2', 'bag', 'record',
        #     topic_name, '-o', bagfile_path,'--qos-profile-overrides-path',record_qos_cmd,
        #     record_nd_cmd,'--max-cache-size',record_mcs_cmd,base_cpp_cmd,record_spp_cmd],shell=True)
        # record_process = subprocess.Popen(record_cmd,shell=True)

        return command + ' ' + fixed_args + dyn_args + pubs_args + "| grep qqq.*"

    def kill(self):
        """Kill the associated performance test process."""
        if self.process is not None:
            self.process.kill()

    def num_runs(self):
        """Return the number of experiments runs this instance can execute."""
        return len(self.product)

    def __del__(self):#デストラクタ
        """Kill the associated performance test process."""
        self.kill()


def signal_handler(sig, frame):
    """Signal handler to handle Ctrl-C."""
    print('You pressed Ctrl+C! Terminating experiment')
    subprocess.Popen('killall -2 perf_test', shell=True)
    subprocess.Popen('killall -2 ros2 bag record', shell=True)
    sys.exit(0)

    
def row_number_info(sig=None, frame=None): #数秒毎に、ファイルの行数を確認し、指定回数パブリッシュされていたらexit。ずっと変わらなくてもexit
    global count
    if count == 5:
        count = 1
        print(f"推定パブリッシュ時間{experiment_length}から{interval*count}秒経過しても{num_of_publish}回パブリッシュされなかった")
        evaluation_stop()
    if sum([1 for _ in open(f'{output_path}/pub_time_before_del.txt')]) >= num_of_publish:
        print(f"正常に{num_of_publish}回パブリッシュされた")
        evaluation_stop()
    count += 1

def evaluation_stop():
    publisher.kill()
    subprocess.Popen('killall -2 perf_test', shell=True)
    subprocess.Popen('killall -2 ros2', shell=True)
    exit(0)



#パブリッシュ回数/rate+数秒、perf_test,rosbag2 recordを実行する
experiment_length = (num_of_publish/int(rate)) + 1.5
interval = 3

signal.signal(signal.SIGALRM, row_number_info)
signal.signal(signal.SIGINT, signal_handler)
signal.setitimer(signal.ITIMER_REAL, experiment_length, interval) #experiment_length秒後に、interval秒間隔でファイルの行数を確認する

count = 1
publisher = Instance()
publisher.run()
print('Press Ctrl+C to abort experiment')

while True:
    time.sleep(1)