import numpy as np
import cv2 as cv
import utm
import pandas as pd
import datetime
import re
from tqdm import tqdm

#%% Drone 1
# 经纬度坐标 #维度，经度
Drone1_GPS_info = np.float64([
[43.07345658033848, -89.40063053980529],
[43.07311704755464, -89.40056863064746],
[43.0731843668088, -89.40077368397719],
[43.072837730935674, -89.40065474737953],
[43.07217521708628, -89.40060601485285],
[43.07202717247519, -89.40097762598936],
[43.0731607524848, -89.39999719756588],
[43.073188523667504, -89.40130920580263],
])
# 像素坐标
Drone1_imgPts = np.float32([
[620,1024],
[1340,922],
[1193,1248],
[1926,1049],
[3353,949],
[3702,1545],
[1232,33],
[1191,2110],
])

#%% Drone 2
# 经纬度坐标 #维度，经度
Drone2_GPS_info = np.float64([
[43.07217521708628, -89.40060601485285],
[43.07202717247519, -89.40097762598936],
[43.07156488096945, -89.4010451306886],
[43.07100327890835, -89.40038683025702],
[43.070949815570124, -89.40058049922119],
[43.07098248144149, -89.4011368300587],
[43.07087891141097, -89.40146388464368],
[43.070689791802266, -89.40108214544868],
])
# 像素坐标
Drone2_imgPts = np.float32([
[153,700],
[480,1273],
[1475,1354],
[2636,310],
[2755,609],
[2707,1467],
[2947,1971],
[3321,1356],
])


#%% 经纬度转UTM
def GPS2UTM(GPS_info):
    utmPtsl = []
    for i in range(len(GPS_info)):
        lat, lon = GPS_info[i,0], GPS_info[i,1]
        utm_ = utm.from_latlon(lat, lon) # from_latlon(latitude, longitude, force_zone_number=None, force_zone_letter=None)
        utm_x = utm_[0]
        utm_y = utm_[1]
        utm_zone = utm_[2]
        utm_band = utm_[3]
        utmPtsl.append([utm_x,utm_y,0])
        # print("utm_x: %s, utm_y: %s, utm_zone: %s, utm_band: %s" % (utm_x, utm_y, utm_zone, utm_band))
        # lat, lon = utm.to_latlon(utm_x, utm_y, utm_zone, utm_band)
    utmPts = np.asarray(utmPtsl, dtype=np.float32)
    return utmPts

utmPts1 = GPS2UTM(Drone1_GPS_info)
utmPts2 = GPS2UTM(Drone2_GPS_info)

imgPts1 = np.array([Drone1_imgPts])
imgPts2 = np.array([Drone2_imgPts])


# Camera Calibration
size = (3835, 2151)
rms1, camera_matrix1, dist1, rvec1, tvec1 = cv.calibrateCamera([utmPts1], [imgPts1], size, None, None)
new_camera_matrix1, _ = cv.getOptimalNewCameraMatrix(camera_matrix1, dist1, size, 1, size)

# Pixel coordinate to World coordinate 第一个参数是转化前坐标，第二个参数是转化后坐标
hom1, _ = cv.findHomography(imgPts1, utmPts1, cv.RANSAC, 5)


def cvt_pos(u , v, mat):
    x = (mat[0][0]*u+mat[0][1]*v+mat[0][2])/(mat[2][0]*u+mat[2][1]*v+mat[2][2])
    y = (mat[1][0]*u+mat[1][1]*v+mat[1][2])/(mat[2][0]*u+mat[2][1]*v+mat[2][2])
    return (round(x,2) - 300000, round(y,2) - 4770000)


d = pd.read_csv("/media/ubuntu/ANL/Data3_lane.csv")
d = d.loc[:, ~d.columns.str.contains('^Unnamed')]
d["x_utm"] = np.nan
d["y_utm"] = np.nan
d["t_sec"] = np.nan

# pixel to utm, add t_sec
with tqdm(total=len(d)) as pbar:
    for i, row in d.iterrows():
        d.at[i, 'x_utm'], d.at[i, 'y_utm'] = cvt_pos(getattr(row, 'x_pix'), getattr(row, 'y_pix'), hom1)
        t = d.at[i, 'time']
        time1 = datetime.datetime.strptime(re.split("\.|\_", t)[0], "%Y-%m-%d %H:%M:%S")
        millisec = int(re.split("\.|\_", t)[1][0])
        frame_time = time1 + datetime.timedelta(hours=0, minutes=0, seconds=round(millisec / 10, 1))
        d.at[i, 't_sec'] = (frame_time - datetime.datetime(2022, 11, 11, 16)).total_seconds()
        pbar.update(1)

d['lane'] = d['lane'].astype(int)
d.x_utm = d.x_utm.round(3)
d.y_utm = d.y_utm.round(3)

d.to_csv(path_or_buf="/media/ubuntu/ANL/Data3_lane_xy.csv", index=False)