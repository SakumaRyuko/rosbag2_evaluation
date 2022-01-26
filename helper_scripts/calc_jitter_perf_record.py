def qSort(a):
    if len(a) in (0, 1):
        return a

    p = a[-1]
    l = [x for x in a[:-1] if x <= p]
    r = [x for x in a[:-1] if x >  p]

    return qSort(l) + [p] + qSort(r)

import matplotlib.pyplot as plt
import sys
import generate_cmd as gc

record_param = list(gc.get_record_product()[int(sys.argv[1])]) #argv[1]番目のrecordのパラメータ
perf_test_param = list(gc.get_perf_test_product()[int(sys.argv[2])]) # argv[2]番目のperf_testのパラメータ

time_output_path = sys.argv[3]

#eval.pyで生成したunix時間のテキストファイルを配列に保存
with open(f'{time_output_path}/perf_test_time_for_jitter.txt',mode='r',encoding='UTF-8') as f:
	str_list_p = f.readlines()

with open(f'{time_output_path}/record_time.txt',mode='r',encoding='UTF-8') as f:
	str_list_r = f.readlines()

#行数(データ数)を確認し、異なっているなら、エラー文を出力しexit
num_of_perf = len(str_list_p)
num_of_record = len(str_list_r)
if num_of_perf != num_of_record:
	print("perf_test_time_for_jitter.txtとrecord_time.txtのデータ数が異なるため、ジッタの計算が行えません")
	exit(0)

#最初の5要素を削除
del str_list_p[0:5]
del str_list_r[0:5]

#文字列を数値に変換
int_ary_p = []
int_ary_r = []
for i in range(len(str_list_p)):
	int_ary_p.append(int(str_list_p[i]))
for i in range(len(str_list_r)):
	int_ary_r.append(int(str_list_r[i]))

#時間差を求める
dif_p = []
dif_r = []
for i in range(len(str_list_p)-1):
	dif_p.append(int_ary_p[i+1]-int_ary_p[i])
for i in range(len(str_list_r)-1):
	dif_r.append(int_ary_r[i+1]-int_ary_r[i])

#データを1000000で割ってミリ秒にする
for i in range(len(dif_p)):
	dif_p[i] = float(dif_p[i]/1000000)
for i in range(len(dif_r)):
	dif_r[i] = float(dif_r[i]/1000000)

#recordの時間差とperf_testの時間差の差を取り、ジッタを求める
jitter = []
for i in range(len(dif_r)):
	jitter.append(dif_r[i] - dif_p[i])

#データ数をカウント
num_jitter = len(jitter)

#ジッタのプロット
fig = plt.figure()
y = jitter
x = []
for i in range(num_jitter):
	x.append(i+1)

plt.plot(x,y)
plt.xlabel("index")
plt.ylabel("ms")
plt.title("Jitter_of_rosbag2_record")
plt.grid(True)
plt.axhline(0,0,len(x),color='K')
plt.savefig(f"{time_output_path}/jitter_of_rosbag2_record.png")
#plt.show()


#jitterに絶対値をかける
abs_sum = 0
abs_ary =[]
for i in range(num_jitter):
	abs_ary.append(abs(jitter[i])) 
'''
abs_aryを昇順でソートする
abs_sort = qSort(abs_ary)
print(abs_sort)

abs_sortの95パーセンタイル以上の、外れ値となりやすい要素を削除
per = (num_sub*95)/100
del abs_sort[int(per):num_sub-1]
print(abs_sort)
'''
#ジッタの絶対値の合計と平均を求める
for i in range(len(abs_ary)):
	abs_sum += abs_ary[i]

abs_ave = abs_sum/len(abs_ary)

# with open('Jitter')
# print('play from rosbag2 record')
# print('total number of data',num_jitter)
# print('total of jitter：',abs_sum)
# print('average of jitter：',abs_ave)
# print('\n')
