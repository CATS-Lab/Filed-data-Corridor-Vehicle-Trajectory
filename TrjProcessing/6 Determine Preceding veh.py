import pandas as pd
import numpy as np
from tqdm import tqdm

df = pd.read_csv("Data/Data3_lane_xy_va.csv")
veh_info = pd.read_csv("Data/Veh_info3.csv")
df['Pre_id'] = np.nan
df['Pre_v'] = np.nan
df['delta_d'] = np.nan

# the sort rule of all edge (all lane in same edge sare same rule)
sort_info = {}
sort_info['1_0'] = ['x_pix', True]
sort_info['2_1'] = ['x_pix', True]
sort_info['3_2'] = ['x_pix', True]
sort_info['4_3'] = ['x_pix', True]

sort_info['0_1'] = ['x_pix', False]
sort_info['1_2'] = ['x_pix', False]
sort_info['2_3'] = ['x_pix', False]
sort_info['3_4'] = ['x_pix', False]

sort_info['9_2'] = ['y_pix', True]
sort_info['2_6'] = ['y_pix', True]
sort_info['10_3'] = ['y_pix', True]
sort_info['3_7'] = ['y_pix', True]

sort_info['5_1'] = ['y_pix', False]
sort_info['1_8'] = ['y_pix', False]
sort_info['7_3'] = ['y_pix', False]
sort_info['3_10'] = ['y_pix', False]

net = np.load('net.npy', allow_pickle=True).item()

edge_list = list(net.keys())
edge_list.remove('node1')
edge_list.remove('node2')
edge_list.remove('node3')


def cal_distance(x1, x2, y1, y2):
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


grouped = df.groupby(['edge', 'lane'])

for t in tqdm(df['t_sec'].unique()):
    df_t = df[df['t_sec'] == t]
    for edge in edge_list:
        for lane in net[edge].keys():
            df_t_lane = df_t[(df_t['edge'] == edge) & (df_t['lane'] == lane)]
            if len(df_t_lane) < 2:
                continue

            # sort the veh in same lane
            df_t_lane = df_t_lane.sort_values(sort_info[edge][0], ascending=sort_info[edge][1])
            c = 0
            for i in df_t_lane.index:
                if c == 0:
                    df.loc[i, 'Pre_id'] = -1  # This is the first veh in the lane
                else:
                    veh_id = df.loc[i, 'id']
                    # if len(veh_info[veh_info['id'] == veh_id]) > 7 :
                    pre_veh_id = df.loc[c, 'id']

                    df.loc[i, 'Pre_id'] = pre_veh_id
                    df.loc[i, 'Pre_v'] = df.loc[c, 'v']

                    try:
                        pre_veh_len = float(veh_info.loc[veh_info['id'] == pre_veh_id]['length'].iloc[0])
                    except (NameError, IndexError):
                        pre_veh_len = 5

                    try:
                        veh_len = float(veh_info.loc[veh_info['id'] == veh_id]['length'].iloc[0])
                    except (NameError, IndexError):
                        veh_len = 5

                    x1 = df.loc[i, 'x_utm']
                    x2 = df.loc[c, 'x_utm']
                    y1 = df.loc[i, 'y_utm']
                    y2 = df.loc[c, 'y_utm']
                    df.loc[i, 'delta_d'] = round(cal_distance(x1, x2, y1, y2) - 0.5 * (pre_veh_len + veh_len), 3)
                c = i

df.to_csv(path_or_buf="/media/ubuntu/ANL/Data3_lane_xy_va_pre.csv", index=False)
