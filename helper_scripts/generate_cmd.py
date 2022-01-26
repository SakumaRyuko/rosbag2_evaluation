import itertools
import yaml
import datetime

#現在時刻を変数に格納する
dt_now = datetime.datetime.now()
dt_str = dt_now.strftime('%m%d_%H:%M:%S')

#パラメータが設定してあるyamlを読み込む
with open('rosbag2_evaluation_parameters.yaml', 'r') as yaml_file:
    eval_cfg_yaml = yaml.load(yaml_file, Loader=yaml.FullLoader)
    eval_cfg = (eval_cfg_yaml['rosbag2_evaluation']
                                ['ros__parameters'])

#-----ddsのパラメータを変数に格納-----
dds_of_eval = eval_cfg['dds']
#-----perf_testのパラメータを変数に格納-----
perf_test_params = eval_cfg['perf_test_parameters']
#perf_testのコマンド
perf_test_topics = perf_test_params['topics']
perf_test_rate = perf_test_params['rate']
perf_test_num_subs = ['0'] #評価には関係ないので基本的に０
perf_test_reliability = perf_test_params['reliability']
perf_test_durability = perf_test_params['durability']
perf_test_num_of_publish = perf_test_params['number_of_publish']

#perf_testコマンドの直積を取る
perf_test_product = list(itertools.product(perf_test_topics, 
    perf_test_rate,perf_test_num_subs, perf_test_reliability, perf_test_durability))


#-----rosbag2のパラメータ-----
rosbag2_params = eval_cfg['rosbag2_parameters']

#-----recordのパラメータを変数に格納-----
record_params = rosbag2_params['record']
#recordのオプション
record_qos_params = record_params['qos']
record_qos_reliability = record_qos_params['reliability']
record_qos_durability = record_qos_params['durability']
no_discovery = record_params['no_discovery']
max_cache_size = record_params['max_cache_size']
storage_preset_profile = record_params['storage_preset_profile']

#rosbag2 recordコマンドの直積を取る
record_product = list(itertools.product(record_qos_reliability, 
    record_qos_durability,no_discovery, max_cache_size, storage_preset_profile))

# nd_mcs_spp_product = list(itertools.product(no_discovery, max_cache_size, storage_preset_profile)) #latex用
nd_mcs_spp_array = []
nd_mcs_spp_array.append(no_discovery)
nd_mcs_spp_array.append(max_cache_size)
nd_mcs_spp_array.append(storage_preset_profile)

#-----playのパラメータを変数に格納-----
play_params = rosbag2_params['play']
#playのオプション
play_qos_params = play_params['qos']
play_qos_reliability = play_qos_params['reliability']
play_qos_durability = play_qos_params['durability']
read_ahead_queue_size = play_params['read_ahead_queue_size']
play_rate = play_params['rate']

#rosbag2 playコマンドの直積を取る
play_product = list(itertools.product(play_qos_reliability, 
    play_qos_durability, read_ahead_queue_size, play_rate))

#latexへ出力するための、表自体のパラメータ直積(dds,rate,reliability,durability)
latex_product = list(itertools.product(dds_of_eval,perf_test_rate,
    record_qos_reliability,record_qos_durability))

#-----パラメータを参照したパス,コマンド作成-----
# 時刻/dds/record/perf_test/play

#ddsのパス(時刻/dds)
dds_path_list = []
for i in range(len(dds_of_eval)):
    dds_cfg_path = f"{dt_str}/{dds_of_eval[i]}"
    dds_path_list.append(dds_cfg_path)

#rosbag2 recordのパス(/QoS/no_discovery=bool:max_cache_size=int:storage_preset_profile=string)
record_path_list = []
for i in range(len(record_product)):
    c = list(record_product[i])
    record_cfg_path = f"qos={c[0]}:{c[1]}/nd={c[2]}:mcs={c[3]}:spp={c[4]}"
    record_path_list.append(record_cfg_path)

#perf_testのパス(/msg:rate)
perf_test_path_list = [] 
for i in range(len(perf_test_product)):
    perf_cfg_path = ""
    c = list(perf_test_product[i])
    perf_cfg_path = f"{c[0]}:rate={c[1]}"       
    perf_test_path_list.append(perf_cfg_path)

#rosbag2 playのコマンド、パス(rate=int/queue_size=int)
play_path_list = []
play_cmd_list = []
for i in range(len(play_product)):
    play_cfg_path = ""
    play_cfg_cmd = ""
    c = list(play_product[i])
    #パスを作成
    play_cfg_path = f"raqs={c[2]}:rate={c[3]}"
    play_path_list.append(play_cfg_path)
    #コマンドを作成
    if c[3] != "default":
        play_cfg_cmd = f" --rate {c[3]}"
    play_cfg_cmd += f" --read-ahead-queue-size {c[2]}"
    play_cmd_list.append(play_cfg_cmd)

#パラメータパスの3次元リストを作成([dds][record][perf_test])
time_output_path_3dlist = [[[f"./time_output/{dds_path_list[k]}/{record_path_list[j]}/{perf_test_path_list[i]}" 
    for i in range(len(perf_test_product))] for j in range(len(record_product))] for k in range(len(dds_of_eval))]

def get_dt_str():
    return dt_str

def get_dds_of_eval():
    return dds_of_eval

def get_dds_path_list():
    return dds_path_list
#-----perf_testに関する変数-----

def get_perf_test_product():
    return perf_test_product

def get_perf_test_path_list():
    return perf_test_path_list

def get_perf_test_topics():
    return perf_test_topics

def get_perf_test_num_of_publish():
    return perf_test_num_of_publish

#-----rosbag2 recordに関する変数-----
def get_record_product():
    return record_product

def get_nd_mcs_spp_array():
    return nd_mcs_spp_array
# print(nd_mcs_spp_array)

def get_record_path_list():
    return record_path_list

#-----rosbag2 playに関する変数-----
def get_play_product():
    return play_product

def get_play_path_list():
    return play_path_list

def get_play_cmd_list():
    return play_cmd_list

#-----3次元リスト-----
def get_time_output_path_3dlist():
    return time_output_path_3dlist

#latexに出力用のパラメータの直積
def get_latex_product():
    return latex_product