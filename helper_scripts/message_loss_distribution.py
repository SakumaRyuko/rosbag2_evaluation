import generate_cmd as gc
num_of_publish = gc.get_perf_test_num_of_publish()
def message_loss_dist(id_list,r,output_path,topic):
    #配列の値のr毎の個数を求める
    with open(f"{output_path}",'a') as f:
        if id_list == []:
            print(f"{topic}:{num_of_publish}個全てロストした。",file=f)
        else:
            id_devide_by_num_of_pub = list(map(lambda x: -(-x//r), id_list)) #rで割り、切り上げる
            message_loss_count = []
            for i in range(int(num_of_publish/r)): #パブリッシュ回数をrで割った回数、id_devide_by_num_of_pubの中のi+1の値(切り上げ後の値)の個数をカウントし,rから引きリストに追加
                message_loss_count.append(r-id_devide_by_num_of_pub.count(i+1))
            print(f"{topic}:{num_of_publish}回のパブリッシュの内、{r}毎のロスト数は{message_loss_count}",file=f)
    # return id_devide_by_num_of_pub


# print(4/3)
# print(4//3)
# a = [3,5,15,14,56,78,103] #0000112
# message_loss_rate(a,50)
