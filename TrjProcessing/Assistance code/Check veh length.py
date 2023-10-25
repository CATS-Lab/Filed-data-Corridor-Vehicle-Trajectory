# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import pandas as pd

path = "/home/ubuntu/Documents/yolov7-object-tracking/runs/detect/object_tracking2/"
file = "labels/20221111160221.8.merge.txt"
d = pd.read_table(path + file, sep='\s', names=['id','class','x_pix','y_pix','w_pix','h_pix'])

import cv2
import numpy as np
import matplotlib.pyplot as plt

w = 7290
h = 2510
img = cv2.imread("/home/ubuntu/Documents/yolov7-object-tracking/runs/detect/object_tracking/20221111160221.8.merge.jpg")

for i in range(len(d)):
    center_x = d.loc[i,'x_pix']*w
    center_y = d.loc[i,'y_pix']*h
    img = cv2.drawMarker(img, (int(center_x), int(center_y)), (0, 255, 255), markerType=cv2.MARKER_STAR, markerSize=20,thickness=10)
    bw = d.loc[i,'w_pix']*w
    bh = d.loc[i,'h_pix']*h
    # left top
    img = cv2.drawMarker(img, (int(center_x-bw*0.5), int(center_y-bh*0.5)), (0, 255, 255),
                         markerType=cv2.MARKER_STAR, markerSize=5, thickness=4)
    # right botton
    img = cv2.drawMarker(img, (int(center_x+bw*0.5), int(center_y+bh*0.5)), (0, 255, 255),
                         markerType=cv2.MARKER_STAR, markerSize=5, thickness=4)

plt.imshow(img)
plt.show()