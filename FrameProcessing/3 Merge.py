import cv2
import numpy as np
import os
import utm

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
        utm_ = utm.from_latlon(lat, lon)
        utm_x = utm_[0]
        utm_y = utm_[1]
        # utm_zone = utm_[2]
        # utm_band = utm_[3]
        utmPtsl.append([utm_x,utm_y,0])
        # lat, lon = utm.to_latlon(utm_x, utm_y, utm_zone, utm_band)
    utmPts = np.asarray(utmPtsl, dtype=np.float32)
    return utmPts

utmPts1 = GPS2UTM(Drone1_GPS_info)
utmPts2 = GPS2UTM(Drone2_GPS_info)

imgPts1 = np.array([Drone1_imgPts])
imgPts2 = np.array([Drone2_imgPts])

# Camera Calibration
size = (3835, 2151)
rms1, camera_matrix1, dist1, rvec1, tvec1 = cv2.calibrateCamera([utmPts1], [imgPts1], size, None, None)
new_camera_matrix1, _ = cv2.getOptimalNewCameraMatrix(camera_matrix1, dist1, size, 1, size)


# World coordinate to pixel coordinate (to undistort picture)
# imgPts1_new, _ = cv2.projectPoints(np.array(utmPts1), np.float32(rvec1), np.float32(tvec1), camera_matrix1, None)
# imgPts2_new, _ = cv2.projectPoints(np.array(utmPts2), np.float32(rvec2), np.float32(tvec2), camera_matrix2, None)
#Drone2的特征点世界坐标用Drone1的相机参数反算得到Drone1坐标系下的像素坐标
imgPts_2to1, _ = cv2.projectPoints(np.array(utmPts2), np.float32(rvec1), np.float32(tvec1), camera_matrix1, None)
hom2to1, _ = cv2.findHomography(imgPts2, imgPts_2to1, cv2.RANSAC, 5)


Save_main_addr = "/media/ubuntu/ANL/Data/"
sourceFile1 = Save_main_addr + "2PicStable_Drone1/"
sourceFile2 = Save_main_addr + "2PicStable_Drone2/"
Save_addr = Save_main_addr + "3Merging/"


Drone1_time_list = []
Drone2_time_list = []
Merged_time_list = []

path_list1 = os.listdir(sourceFile1)
path_list1.sort()
path_list2 = os.listdir(sourceFile2)
path_list2.sort()

for imgFileName in path_list1:
    time = float(imgFileName[8:16])
    Drone1_time_list.append(time)
for imgFileName in path_list2:
    time = float(imgFileName[8:16])
    Drone2_time_list.append(time)

for imgFileName in os.listdir(Save_addr):
    time = float(imgFileName[8:16])
    Merged_time_list.append(time)


# 前面是把每个drone有的time写成列表
time_list_total = list(set(Drone1_time_list).union(set(Drone2_time_list))) #并集
#time_list_total = list(set(Drone1_time_list).intersection(set(Drone2_time_list))) #交集
time_list_total.sort()

k = 0
# 遍历文件，用同一个M0
for time in time_list_total:
    #判断有没有合并过
    if time not in Merged_time_list:
        print(time, k, "/", len(time_list_total))
        k += 1

        #找drone1有咩有
        if time in Drone1_time_list:
            img1 = cv2.imread(sourceFile1 + '20221111' + str(time) + '.stable.jpg')
            if time in Drone2_time_list:
                img2 = cv2.imread(sourceFile2 + '20221111' + str(time) + '.stable.jpg')
                # 如果都有的合并方法
                img2 = cv2.copyMakeBorder(img2, 0, 350, 0, 3450, cv2.BORDER_CONSTANT, value=[0, 0, 0])
                move_img = cv2.warpPerspective(img2, hom2to1, (img2.shape[1], img2.shape[0]))

                final = move_img.copy()
                rows, cols, channel = img1.shape
                final[0:rows, 0:cols-100] = img1[0:rows, 0:cols-100]

                a, b = 1500, 3250
                part_move_img = move_img[a:rows, b:cols]
                final[a:rows, b:cols] = part_move_img

            else:
                #有1没有2
                final = cv2.copyMakeBorder(img1, 0, 350, 0, 3450, cv2.BORDER_CONSTANT, value=[0, 0, 0])
        else:
            #有2没有1
            img2 = cv2.imread(sourceFile2 + '20221111' + str(time) + '.stable.jpg')
            img2 = cv2.copyMakeBorder(img2, 0, 350, 0, 3450, cv2.BORDER_CONSTANT, value=[0, 0, 0])
            final = cv2.warpPerspective(img2, hom2to1, (img2.shape[1], img2.shape[0]))

        cv2.imwrite(Save_addr + '20221111' + str(time) + ".merge.jpg", final)

