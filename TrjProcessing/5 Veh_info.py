import pandas as pd
import numpy as np
import random
from tqdm import tqdm


def cal_distance(x1,x2,y1,y2):
    return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def Cal_mean(ll,p): #排除10%的极大极小值
    ll.sort()
    z = len(ll)
    ll = ll[int(z*p):int(z*(1-0.5*p))]
    return np.nanmean(ll)


# 记录每辆车的开始结束edge，lane， trip_time
Veh_info = pd.DataFrame(columns=['id', 'length', 'start_time', 'trip_time', 'edge_start', 'edge_end'])
df = pd.read_csv("Data/Data3_lane_xy.csv")
veh_list = df['id'].unique()

# 车辆横着走的edge
e_list_1 = ['0_1','1_0', '1_2','2_1', '3_2','2_3', '3_4','4_3']
# 车辆竖着走的edge
e_list_2 = ['5_1', '1_8', '9_2', '2_6', '3_7', '7_3', '3_10', '10_3']

# pix转utm的平均缩放系数 = 任意两个点的utm距离/任意两个点的pix距离，两个点是取同一edge上的
r_list = []
net = np.load('net.npy', allow_pickle=True).item()
edge_list = list(net.keys())
for edge in edge_list:
    d = df[df['edge'] == edge]
    if len(d)>0:
        d.reset_index(drop=True, inplace=True)
        for k in range(max(len(d),50)):
            a = random.randint(0, len(d)-1)
            b = random.randint(0, len(d)-1)
            distance_utm = cal_distance(d.at[a, 'x_utm'], d.at[b, 'x_utm'], d.at[a, 'y_utm'], d.at[b, 'y_utm'])
            distance_pix = cal_distance(d.at[a, 'x_pix'], d.at[b, 'x_pix'], d.at[a, 'y_pix'], d.at[b, 'y_pix'])
            r_list.append(distance_utm/distance_pix)
r = np.nanmean(r_list)
print('pix转utm的平均缩放系数',r)


for veh in tqdm(veh_list, desc='Processing vehicles'):
    d = df[df['id'] == veh]

    # Cal t
    t = d['t_sec'].max()-d['t_sec'].min()

    # Cal 'edge_start', 'edge_end'
    i = d['t_sec'].idxmin()
    index = d.index.get_loc(i)
    edge_start = d.iloc[index].at['edge']
    if type(edge_start) != str:
        continue
    if edge_start == 'node':
        edge_start = edge_start + '_' + str(d.iloc[index].at['lane'])[0]
    i = d['t_sec'].idxmax()
    index = d.index.get_loc(i)
    edge_end = d.iloc[index].at['edge']
    if type(edge_end) != str:
        continue
    if edge_end == 'node':
        edge_end = edge_end + '_' + str(d.iloc[index].at['lane'])[0]

    # 如果车的行驶距离太短，起终点的edge一样，就不要了，在这个里筛选车辆不影响Data里算前车
    # if t <= 5 or (edge_start[0] == 'n' and edge_end[0] == 'n'):
    #     continue

    # Cal 'length'
    l_list = list(d[d['edge'].isin(e_list_1)]['w_pix']) + list(d[d['edge'].isin(e_list_2)]['h_pix'])
    if len(l_list):
        l = r * Cal_mean(l_list, 0.05)

    if edge_start != edge_end:
        Veh_info = Veh_info.append({'id': veh, 'length': round(l,2) ,'start_time': round(d['t_sec'].min(),1), 'trip_time': round(t,1), 'edge_start': edge_start, 'edge_end': edge_end}, ignore_index=True)

Veh_info.to_csv(path_or_buf="Data/Veh_info3.csv", index=False)

# import matplotlib.pyplot as plt
# Veh_info = pd.read_csv("/media/ubuntu/ANL/Veh_info.csv")
# plt.hist(Veh_info['length'], bins=30, normed=0, facecolor="blue", edgecolor="black", alpha=0.7)
# plt.title('distribution of vehicle length (meter)')
# plt.show()
