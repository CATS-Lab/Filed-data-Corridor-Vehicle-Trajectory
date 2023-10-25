import pandas as pd
d = pd.read_csv("/media/ubuntu/ANL/Data1_lane_xy.csv")
num_veh = len(d['id'].unique())
for veh_id in d['id'].unique():
    d_veh = d[d['id'] == veh_id]
    # 然后检查接下来是不是每个时间点都有值
    d_veh_t_list = d_veh['t_sec'].tolist()
    for i in range(len(d_veh_t_list)-1):
        if round(d_veh_t_list[i+1] - d_veh_t_list[i], 1) > 0.1:
            print(veh_id, d_veh_t_list[i], '不连续')