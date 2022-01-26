import subprocess
import sqlite3
import generate_cmd as gc
import os
import shutil
import sys
import time
import datetime
import signal
import make_messageloss_latextable as mml
import message_loss_distribution as mld
#評価開始時刻
start = datetime.datetime.now()
#-----パラメータの直積とそれに対応したパスのリストを取得-----
dt_str = gc.get_dt_str()
dds_of_eval = gc.get_dds_of_eval()
perf_test_product = gc.get_perf_test_product()
record_product = gc.get_record_product()
time_output_path_3dlist = gc.get_time_output_path_3dlist()
dds_path_list = gc.get_dds_path_list()
play_path_list = gc.get_play_path_list()
play_cmd_list = gc.get_play_cmd_list()
latex_product = gc.get_latex_product()
num_of_publish = gc.get_perf_test_num_of_publish()
repeat_count = 1

#bagfileのtimestampを取得
def get_record_timestamp(bagfile_path):
    dbpath = bagfile_path + "/bagfile_0.db3"
    #SQL命令文（messagesテーブル内のtimestampレコードを取得）
    db = sqlite3.connect(dbpath ,isolation_level=None)
    sql = "SELECT timestamp FROM messages"
    c = db.cursor()
    c.execute(sql)
    time =[]
    for row in c:
        time.append(row)
    return time
#bagfileのdata.idを取得(perf_test専用)
def get_record_id_list(bagfile_path):
    dbpath = bagfile_path + "/bagfile_0.db3"
    #SQL命令文（messagesテーブル内のdataレコードの後ろから8個の16進数の数を取得）
    db = sqlite3.connect(dbpath ,isolation_level=None)
    sql = "SELECT hex(substr(data,-8,8)) FROM messages"
    c = db.cursor()
    c.execute(sql)
    # print(f"レコードされた数は{len(c)}")
    id_list = []
    for row in c:
        str_rev_id = str(row[0]) #tupleなので、16進数のデータだけ取り出す
        str_id = ""
        for j in range(8):
            str_id += str_rev_id[14-2*j:16-2*j] #bagfileに２個ずつ逆順でidの値が保存されているので、元に戻す(UDPはビッグエンディアンだから？)
        int_id = int(str_id,16) #16進数を整数に変換
        id_list.append(int_id)
    return id_list

def exec_run_experiment(record_param, perf_test_param, output_path):
    #実行するパラメータ、bagfileの保存場所をrun_experiment.pyに渡し、grepで出力結果を操作する
    bagfile_path = output_path + "/bagfile"
    experiment_cmd = f"python3 run_experiment.py {record_param} {perf_test_param} {output_path}"
    global repeat_count
    repeat_count = 1
    while(True):
        subprocess.run(experiment_cmd,shell=True)
        timestamp = get_record_timestamp(bagfile_path)
        if len(timestamp) >= 1: #bagfileに保存されている(timestampリストの長さが1以上)ならbreak
            print("bagfileが生成された")
            break
        if repeat_count == 5: #recordされ続けなかったらbreak
            print(f"{repeat_count}回実行してもbagfileにメッセージがレコードされなかった")
            break
        os.remove(f'{output_path}/pub_time_before_del.txt') #pub_time_before_del.txtとbagfileを削除する
        shutil.rmtree(bagfile_path)
        print(f"bagfileに保存されなかったため、再度run_experiment.pyを実行({repeat_count+1}回目)")
        repeat_count += 1
        # time.sleep(5)

def create_perf_test_time_txt(output_path):
    print("---perf_test_time.txt---")
    before_delete = []
    after_delete = []
    with open(f'{output_path}/pub_time_before_del.txt','r') as f:
        print(f'{output_path}/pub_time_before_del.txt')
        before_delete = f.readlines()
        
        print(f"qqqを削除した前の配列の個数は{len(before_delete)}")
        for k in range(len(before_delete)):
            after_delete.append(before_delete[k][3:-1])
    print(f"qqqを削除したあとの配列の個数は{len(after_delete)}")
    #os.remove(f'{output_path}/pub_time_before_del.txt') #使用済みなので、容量確保のため削除
    with open(f'{output_path}/perf_test_time.txt','w') as f:
        d = "\n".join(after_delete)
        f.write(d)

def create_record_time_txt(output_path):
    print("---record_time.txt---")
    bagfile_path = output_path + "/bagfile"
    with open(f'{output_path}/record_time.txt','w') as f:
        timestamp = get_record_timestamp(bagfile_path)
        for i in timestamp:
            f.write("%s\n" %i)
def create_play_time_txt(output_path):
    print("---play_time.txt---")
    bagfile_path = output_path + "/bagfile"
    for i in range(len(play_path_list)):
        play_cmd = f"ros2 bag play {play_cmd_list[i]} {bagfile_path}"
        play_output_path = f"{time_output_path}/{play_path_list[i]}"
        os.makedirs(play_output_path, exist_ok=True)
        with open(f'{play_output_path}/play_time.txt', 'w') as f:
            subprocess.run(play_cmd, shell=True,encoding='UTF-8', stdout=f,universal_newlines=True)

def create_perf_test_time_for_jitter_txt(dds, record_param, perf_test_param, output_path):
    bagfile_path = output_path + "/bagfile"
    d = dds_of_eval[dds]
    r = list(record_product[record_param])
    p = list(perf_test_product[perf_test_param])
    with open(f'{output_path}/perf_test_time_for_jitter.txt','w') as ffp:
        perf_time_after_row_delete = []
        perf_time_before_row_delete = []
        with open(f'{output_path}/perf_test_time.txt','r') as fp:
            perf_time_before_row_delete = fp.readlines()
            id_list = get_record_id_list(bagfile_path) #recordされたメッセージのidのリストを取得
            print(f"id_listの数は{len(id_list)}")
            number_of_message_loss = len(perf_time_before_row_delete)-len(id_list) #ロストしたメッセージの個数を取得
            m_loss_output_path = f"{message_loss_output_path}/{d},{p[1]},{r[0]},{r[1]},{p[0]}.txt"
            m_loss_dist_output_path = f"{m_loss_dist_dir}/{d},{p[1]},{r[0]},{r[1]}.txt"
            mld.message_loss_dist(id_list,1000,m_loss_dist_output_path,p[0]) #1000毎のロスト数を計算
            output_message_loss_result(number_of_message_loss,m_loss_output_path) #output_pathにロスト数を出力
            for i in range(len(id_list)):
                perf_time_after_row_delete.append(perf_time_before_row_delete[id_list[i]-1]) #id_listの要素の箇所だけをperf_test_time.txtから取得する
        for i in perf_time_after_row_delete:
            ffp.write("%s" %i)
    shutil.rmtree(bagfile_path) #容量のため、bagfileを削除

def output_message_loss_result(num_of_message_loss,output_path):
    if repeat_count >= 2: #bagfileが正常にデータがレコードされるまでの回数も追記(1回は記載しない)
        output_text = f"{num_of_message_loss}({repeat_count})"
    else:
        output_text = f"{num_of_message_loss}"
        with open(f'{output_path}','a') as f:
            #ロストしたメッセージの個数を、time_output/時刻/number_of_message_loss/DDS,rate,reliability,durability,topic type.txtに出力
            print(f"{output_text}",file=f)

def calc_jitter_of_perf_and_record(record_param,perf_test_param,output_path):
    calc_cmd = f"python3 calc_jitter_perf_record.py {record_param} {perf_test_param} {output_path}"
    subprocess.run(calc_cmd, shell=True)
def calc_jitter_of_record_and_play(output_path):
    for i in range(len(play_path_list)):
        #ここではoutput_pathとplay_path_listは分割する。calc.pyの方でoutput_pathを参照するかもしれないため
        calc_cmd = f"python3 calc_jitter_record_play.py {i} {output_path}"
        subprocess.run(calc_cmd, shell=True)

def signal_handler(sig, frame):
    """Signal handler to handle Ctrl-C."""
    print('@@@@@ You pressed Ctrl+C. Terminating rosbag2 experiment @@@@@')
    subprocess.Popen('killall -2 perf_test', shell=True)
    subprocess.Popen('killall -2 ros2', shell=True)
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
#ロストしたメッセージの結果を保存するディレクトリ
message_loss_output_path = f'./time_output/{dt_str}/number_of_message_loss'
os.makedirs(message_loss_output_path,exist_ok=True)
m_loss_dist_dir = f"{message_loss_output_path}/dist"
os.makedirs(m_loss_dist_dir,exist_ok=True)

#----------評価を行う----------
for h in range(len(dds_of_eval)):
    os.environ["RMW_IMPLEMENTATION"] = dds_of_eval[h]
    for i in range(len(record_product)):
        for j in range(len(perf_test_product)):
            time_output_path = time_output_path_3dlist[h][i][j]     #bagfile,時刻txtなどを出力するパス
            os.makedirs(time_output_path, exist_ok=True)            #time_output_pathのディレクトリを作成
            #----------perf_test,record,playを実行し、時刻データを取得----------
            print(f"-----実行パラメータ-----\nDDS:{dds_of_eval[h]}\nperf_test:{list(perf_test_product[j])[:2]}\nrosbag2 record:{list(record_product[i])}")
            print("-----perf_test,rosbag2 recordを実行-----")
            exec_run_experiment(i,j,time_output_path)               #run_experiment.pyを実行し、pub_time_before_del.txtとbagfileを生成。メッセージが保存されるまでにかかった回数も取得
            print("-----タイムスタンプを保存したファイルを作成-----")
            create_perf_test_time_txt(time_output_path)             #pub_time_before_del.txtから「publish_time:」を削除してperf_test_time.txtに保存
            create_record_time_txt(time_output_path)                #bagfileのタイムスタンプを取得しrecord_time.txtに保存
            #create_play_time_txt(time_output_path)                 #bagfileをplayし、play_time.txtに保存
            #----------メッセージロスに対応したジッタの計算を行うための前処理、メッセージロス算出----------
            create_perf_test_time_for_jitter_txt(h,i,j,time_output_path)#メッセージロストの行をperf_test_time.txtから削除しperf_test_time_for_jitter.txtを作成
            #----------ジッタの算出----------
            #calc_jitter_of_perf_and_record(i,j,time_output_path)    #perf_test_time.txtとrecord_time.txtの評価
            #calc_jitter_of_record_and_play(time_output_path)        #record_time.txtとplay_time.txtの評価
print("メッセージロス・ジッタの算出終了")

#-----メッセージロスの結果をlatex用に出力-----
#latex_product = (DDS,rate,reliability,durability)
for i in range(len(latex_product)):
    latex_param = list(latex_product[i])
    mml.make_latextable(latex_param,message_loss_output_path)
print("latex用の出力完了")

#評価にかかった時間を出力
end = datetime.datetime.now()
evaluation_time = end - start
print(f"評価にかかった時間は{evaluation_time}です")