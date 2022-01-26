import generate_cmd as gc
import os
# dt_str = gc.get_dt_str()
topics = gc.get_perf_test_topics()
nd_mcs_spp_array = gc.get_nd_mcs_spp_array()
num_of_publish = gc.get_perf_test_num_of_publish()
nd_ary = nd_mcs_spp_array[0]
mcs_ary = nd_mcs_spp_array[1]
spp_ary = nd_mcs_spp_array[2]
nd_mcs_spp_array_length = len(nd_ary)*len(mcs_ary)*len(spp_ary)

def tabular_def_cmd():
    cmd = "\\begin{tabular}{|c||"
    for i in range(nd_mcs_spp_array_length):
        cmd += "c|"
    cmd += "}\\hline\n"
    return cmd

def no_discovery_table():
    cmd = "no discovery "
    for i in range(len(nd_ary)):
        cmd += f"& \\multicolumn{{{len(mcs_ary)*len(spp_ary)}}}{{c|}}{{{nd_ary[i]}}} "
    cmd += "\\\\\\hline\n"
    return cmd

def max_cache_size_table():
    cmd = "max cache size "
    if len(mcs_ary) == 1:
        cmd += f"& \\multicolumn{{{nd_mcs_spp_array_length}}}{{c|}}{{{mcs_ary[0]}}} "
    else:
        for i in range(len(nd_ary)):
            for i in range(len(mcs_ary)):
                cmd += f"& \\multicolumn{{{len(spp_ary)}}}{{c|}}{{{mcs_ary[i]}}} "
    cmd += "\\\\\\hline\n"
    return cmd

def storage_preset_profile_table():
    cmd = "storage preset profile "
    if len(spp_ary) == 1:
        cmd += f"& \\multicolumn{{{nd_mcs_spp_array_length}}}{{c|}}{{{spp_ary[0]}}} "
    else:
        for i in range(len(nd_ary)*len(mcs_ary)):
            for j in range(len(spp_ary)):
                cmd += f"& {spp_ary[j]} "
    cmd += "\\\\\\hline\\hline\n"
    return cmd

def make_latextable(latex_param,m_path): #m_path=./time_output/時刻/number_of_lost_message
    dds = latex_param[0]
    rate = latex_param[1]
    reliability = latex_param[2]
    durability = latex_param[3]
    header_code = header_table(dds,rate,reliability,durability)
    body_code = body_table(dds,rate,reliability,durability,m_path)
    end_code = "\\end{tabular}\n\\end{table*}\n\n"
    #./time_output/時刻/number_of_message_lossのトピックごとのファイルから値を代入
    with open(f'{m_path}/all_latex_table_code', 'a') as f:
        for i in header_code:
            f.write("%s" %i)
        for i in body_code:
            f.write("%s" %i)
        f.write(end_code)
        # print(i)


def header_table(dds,rate,reliability,durability): #
    header_code = []
    #latex用に_を\_に直す
    dds = dds.replace('_','\\_')
    reliability = reliability.replace('_','\\_')
    #table
    begin_table = "\\begin{table*}\n\\centering\n"
    header_code.append(begin_table)
    #ラベル
    label = "\\label{Messageloss:"
    label += f"{dds},{rate},{reliability},{durability}"
    label += "}\n"
    header_code.append(label)
    #キャプション
    caption = "\\caption{Number of lost messages."
    caption += f" DDS is {dds}, Publish rate is {rate}, and QoS is {reliability}/{durability}"
    caption += "}\n"
    header_code.append(caption)
    #tabular
    header_code.append(tabular_def_cmd())
    #パラメータ(sppが一番下で固定)
    header_code.append(no_discovery_table())
    header_code.append(max_cache_size_table())
    header_code.append(storage_preset_profile_table())

    return header_code

def body_table(dds,rate,reliability,durability,m_path):
    body_code = []
    m_filepath = f"{m_path}/{dds},{rate},{reliability},{durability}," #m_path=./time_output/時刻/number_of_lost_message
    for i in range(len(topics)):
        topic_table = f"{topics[i]} "
        m_filename =  m_filepath + f"{topics[i]}.txt"
        with open(f'{m_filename}','r') as f:
            loss_result = f.readlines()
            # while loss_result:
            for j in range(nd_mcs_spp_array_length):
                if f"{num_of_publish}" in loss_result[j]: #全部ロストしていたら(ロスト数が、パブリッシュ回数と同じ)、そもそもレコードが上手くいってないのでfail
                    topic_table += f"& fail "
                else:
                    loss = loss_result[j].replace('\n','')
                    topic_table += f"& {loss} "
        topic_table += "\\\\\\hline\n"
        body_code.append(topic_table)
    return body_code
    #例:Array1k & 0 & 0 ... \\\hline
    #   Array4k & 0 & 0 ... \\\hline






# make_latextable("rmw_cyclonedds_cpp","50","best_effort","volatile",f"./time_output/{dt_str}")