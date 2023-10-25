#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import re
import pandas as pd
import datetime
from tqdm import tqdm

frames = 29.97
time_step = 0.1
path = "/home/ubuntu/Documents/yolov7-object-tracking/runs/detect/object_tracking3/labels/"  # 文件夹的路径
filelist = os.listdir(path)
filelist.sort()
data_list = []

data = pd.DataFrame()
i = 0

for file in tqdm(filelist):
    file_name = re.split("\.|\_", file)
    time = datetime.datetime.strptime(file_name[0], "%Y%m%d%H%M%S")
    millisec = int(file_name[1])

    d = pd.read_table(path + file, sep='\s', names=['id', 'class', 'x_pix', 'y_pix', 'w_pix', 'h_pix'])
    frame_time = time + datetime.timedelta(hours=0, minutes=0, seconds=round(millisec / 10, 1))
    d.insert(2, 'time', frame_time)
    data = pd.concat([data, d])

data.x_pix *= 7290
data.y_pix *= 2510
data.w_pix *= 7290
data.h_pix *= 2510

data.x_pix = data.x_pix.round(3)
data.y_pix = data.y_pix.round(3)
data.w_pix = data.w_pix.round(3)
data.h_pix = data.h_pix.round(3)

data.to_csv(path_or_buf="/media/ubuntu/ANL/" + "Data3.csv", columns=['id', 'time', 'x_pix', 'y_pix', 'w_pix', 'h_pix'], index=False)
