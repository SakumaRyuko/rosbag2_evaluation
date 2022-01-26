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
 
time_output_path = sys.argv[1]

#eval.pyで生成したunix時間のテキストファイルを配列に保存
with open(f'{time_output_path}/perf_test_time_for_jitter.txt',mode='r',encoding='UTF-8') as f:
	str_list_p = f.readlines()

with open(f'{time_output_path}/record_time.txt',mode='r',encoding='UTF-8') as f:
	str_list_r = f.readlines()

#行数(データ数)を確認し、異なっているなら、エラー文を出力しexit

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

#record毎の時間差から、perf_testの時間差を引く
jitter = []
for i in range(len(dif_r)-1):
	jitter.append(dif_r[i] - dif_p[i])

#dif_pをファイルに出力
with open(f"./play_jitter/play_jitter_{dt_str}.txt", 'w') as fp:
	for i in dif_p:
		fp.write("%s\n" %i)


#データ数をカウント
num_data = len(dif_p)

#ジッタのプロット
fig = plt.figure()
y = dif_p
x = []
for i in range(num_data):
	x.append(i+1)

plt.plot(x,y)
plt.xlabel("index")
plt.ylabel("ms")
plt.title("Jitter_of_rosbag2_play")
plt.grid(True)
plt.axhline(0,0,len(x),color='K')
plt.savefig(f"./play_jitter/jitter_of_play_{dt_str}.png")
plt.show()


#difに絶対値をかける
abs_sum = 0
abs_ary =[]
for i in range(num_data):
	abs_ary.append(abs(dif_p[i])) 
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

print('play from rosbag2 record')
print('total number of data',num_data)
print('total of jitter：',abs_sum)
print('average of jitter：',abs_ave)
print('\n')
'''
print('play from Rosbag2 record')
print('データ総数',num_data)
print('ジッタの合計：',abs_sum)
print('ジッタの平均：',abs_ave)
print('\n')
'''