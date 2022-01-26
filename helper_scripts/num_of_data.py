with open('./time_output/0126_17:52:55/rmw_cyclonedds_cpp/qos=best_effort:volatile/nd=false:mcs=guide:spp=default/Array1k:rate=100/pub_time_before_del.txt','r') as f:
    print(len(f.readlines()))
