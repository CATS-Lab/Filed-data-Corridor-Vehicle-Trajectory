import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from math import sqrt, pow, acos
from tqdm import tqdm

def cal_distance(x1,x2,y1,y2):
    return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def angle_of_vector(v1, v2):
    pi = 3.1415
    vector_prod = v1[0] * v2[0] + v1[1] * v2[1]
    length_prod = sqrt(pow(v1[0], 2) + pow(v1[1], 2)) * sqrt(pow(v2[0], 2) + pow(v2[1], 2))
    cos = vector_prod * 1.0 / (length_prod * 1.0 + 1e-6)
    return (acos(cos) / pi) * 180

def CleanSharpAngle(x_list, y_list, angle_threshold):
    waste=[]
    x_new = x_list.copy()
    y_new = y_list.copy()
    for i in range(1, len(x_list)-2):
        a = np.array([x_list[i] - x_list[i-1], y_list[i] - y_list[i-1]])
        b = np.array([x_list[i] - x_list[i+1], y_list[i] - y_list[i+1]])
        angle = angle_of_vector(a, b)
        if angle < angle_threshold:
            x_new[i], y_new[i] = np.mean([x_list[i-1], x_list[i+1], x_list[i+2]]) , np.mean([y_list[i-1], y_list[i+1], y_list[i+2]])
            waste.append([x_list[i],y_list[i]])
    return x_new, y_new, np.array(waste)

def MovingAverage(input):
    output = {}
    size = len(input)
    w = np.array([3, 2, 1, -1])
    output[0] = np.dot(w, np.array([input[0], input[1], input[2], input[3]]))/ sum(w)
    w = np.array([4, 3, 2, 1])
    output[1] = np.dot(w, np.array([input[0], input[1], input[2], input[3]]))/ sum(w)
    for i in range(2, size - 2):
        w = np.array([1, 1, 1, 1, 1])
        output[i] = np.dot(w, np.array([input[i-2], input[i-1], input[i], input[i+1], input[i+2]]))/ sum(w)
    a, b, c, d = 4, 3, 2, 1
    w = np.array([4, 3, 2, 1])
    output[size-2] = (a*input[size - 1] + b*input[size - 2] + c*input[size - 3] + d*input[size - 4]) / (a+b+c+d)
    a, b, c, d = 3, 2, 1, -1
    w = np.array([3, 2, 1, -1])
    output[size-1] = (a*input[size - 1] + b*input[size - 2] + c*input[size - 3] + d*input[size - 4]) / (a+b+c+d)
    return output


df = pd.read_csv("/media/ubuntu/ANL/Data3_lane_xy.csv")
#时间步长设为1
df = df[df['t_sec'].apply(lambda x: x.is_integer())]

veh_list = df['id'].unique()
new_d = []
new_d = pd.DataFrame(new_d)
for veh in tqdm(veh_list, desc='Processing vehicles'):
    d = df[df['id'] == veh]
    if len(d) > 7:
        x_list = np.round(d['x_utm'].tolist(), 2)
        y_list = np.round(d['y_utm'].tolist(), 2)

        # Clean the points formed Sharp Angles
        x_new, y_new, waste = CleanSharpAngle(x_list, y_list, 140)

        # 不允许开倒车
        for i in range(0, len(x_list)-1):
            a = i
            b = a + 1
            distance_max = cal_distance(x_new[a], x_new[b], y_new[a], y_new[b])
            while b < len(x_list)-1:
                distance = cal_distance(x_new[a], x_new[b], y_new[a], y_new[b])
                if distance < distance_max and distance_max < 1:
                    x_new[a:b] = np.mean(x_new[a:b])
                    y_new[a:b] = np.mean(y_new[a:b])
                else:
                    distance_max = distance
                b += 1

        # Moving average
        x_new = list(MovingAverage(x_new).values())
        y_new = list(MovingAverage(y_new).values())
        d['x_utm'] = x_new
        d['y_utm'] = y_new
        d.x_utm = d.x_utm.round(3)
        d.y_utm = d.y_utm.round(3)

        new_d = pd.concat([new_d, d], axis=0)

new_d.to_csv(path_or_buf="/media/ubuntu/ANL/Data3_lane_xynew.csv", index=False)


