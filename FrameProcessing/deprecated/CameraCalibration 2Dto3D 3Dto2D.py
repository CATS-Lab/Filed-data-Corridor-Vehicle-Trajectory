import numpy as np
import cv2 as cv
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
rms2, camera_matrix2, dist2, rvec2, tvec2 = cv.calibrateCamera([utmPts2], [imgPts2], size, None, None)
new_camera_matrix1, _ = cv.getOptimalNewCameraMatrix(camera_matrix1, dist1, size, 1, size)
new_camera_matrix2, _ = cv.getOptimalNewCameraMatrix(camera_matrix2, dist2, size, 1, size)


# World coordinate to pixel coordinate (to undistort picture)
dist1 = np.array([dist1])
imgPts1_new, _ = cv.projectPoints(np.array(utmPts1), np.float32(rvec1), np.float32(tvec1), camera_matrix1, None)
imgPts2_new, _ = cv.projectPoints(np.array(utmPts2), np.float32(rvec2), np.float32(tvec2), camera_matrix2, None)
#Drone2的特征点世界坐标用Drone1的相机参数反算得到Drone1坐标系下的像素坐标
imgPts_2to1, _ = cv.projectPoints(np.array(utmPts2), np.float32(rvec1), np.float32(tvec1), camera_matrix1, None)


# plot imgPts2_to1
img1 = cv.imread("F:/CATS_Lab/2022 ANL-UWisc SOW/DJI_20221111160315_0001_V undistort result.png")
# img = cv.copyMakeBorder(img1, 0,350,0,3100, cv.BORDER_CONSTANT, value=[255,255,255])
# for i in range(np.size(imgPts1,1)):
#     coor = (imgPts1[0][i][0], imgPts1[0][i][1])
#     cv.circle(img, coor, 3, (0, 255, 0), 1) #green
# for i in range(np.size(imgPts_2to1,0)):
#     coor = (imgPts_2to1[i][0][0], imgPts_2to1[i][0][1])
#     cv.circle(img, coor, 8, (0, 0, 255), 1) #red
# # cv.namedWindow('img', cv.WINDOW_NORMAL)
# # cv.imshow('img',img)
# # cv.waitKey(0)
# cv.imwrite("F:/CATS_Lab/2022 ANL-UWisc SOW/merge.png", img)


# def cal_distance(x1,x2,y1,y2):
#     return pow(pow(x1-x2,2) + pow(y1-y2,2) , 0.5)

# 计算像素坐标的误差
# error_imgPts1 = 0
# for i in range(np.size(imgPts1_new,0)):
#     error = cal_distance(imgPts1_new[i][0][0], imgPts1[0][i][0],
#                          imgPts1_new[i][0][1], imgPts1[0][i][1])
#     error_imgPts1 += error
# print('error_imgPts1', error_imgPts1/np.size(imgPts1_new,0))
#
# error_imgPts2 = 0
# for i in range(np.size(imgPts2_new,0)):
#     error = cal_distance(imgPts2_new[i][0][0], imgPts2[0][i][0],
#                          imgPts2_new[i][0][1], imgPts2[0][i][1])
#     error_imgPts2 += error
# print('error_imgPts2', error_imgPts2/np.size(imgPts2_new,0))


# Pixel coordinate to World coordinate 第一个参数是转化前坐标，第二个参数是转化后坐标
hom1, _ = cv.findHomography(imgPts1_new, utmPts1, cv.RANSAC, 5)
# hom2, _ = cv.findHomography(imgPts2_new, utmPts2, cv.RANSAC, 5)
#
def cvt_pos(u , v, mat):
    x = (mat[0][0]*u+mat[0][1]*v+mat[0][2])/(mat[2][0]*u+mat[2][1]*v+mat[2][2])
    y = (mat[1][0]*u+mat[1][1]*v+mat[1][2])/(mat[2][0]*u+mat[2][1]*v+mat[2][2])
    return (int(x), int(y))
#
# utmPts1_new = []
# for i in range(np.size(imgPts1,1)):
#     u, v = imgPts1[0][i][0], imgPts1[0][i][1]
#     x, y = cvt_pos(u, v, hom1)
#     utmPts1_new.append([x,y])
# utmPts1_new = np.asarray(utmPts1_new, dtype=np.float32)
#
# utmPts2_new = []
# for i in range(np.size(imgPts2,1)):
#     u, v = imgPts2[0][i][0], imgPts2[0][i][1]
#     x, y = cvt_pos(u, v, hom2)
#     utmPts2_new.append([x,y])
# utmPts2_new = np.asarray(utmPts2_new, dtype=np.float32)
#
# # 计算世界坐标的误差
# error = 0
# for i in range(np.size(utmPts1,0)):
#     error = cal_distance(utmPts1[i][0], utmPts1_new[i][0],
#                          utmPts1[i][1], utmPts1_new[i][1])
#     error += error
# print('error_utmPts1', error/np.size(utmPts1,0))
#
# error = 0
# for i in range(np.size(utmPts2,0)):
#     error = cal_distance(utmPts2[i][0], utmPts2_new[i][0],
#                          utmPts2[i][1], utmPts2_new[i][1])
#     error += error
# print('error_utmPts2', error/np.size(utmPts2,0))

# Drone2特征点的坐标用Drone1的参数转了Drone1的像素坐标系统下后，这个像素坐标再转Drone2特征点的世界坐标（还是用1的参数），
# Drone2的特征点世界坐标用Drone1的相机参数反算得到Drone1坐标系下的像素坐标是imgPts_2to1
# imgPts_2to1转成世界坐标 utm_212
# utm_212 = []
# for i in range(np.size(imgPts_2to1,0)):
#     u, v = imgPts_2to1[i][0][0], imgPts_2to1[i][0][1]
#     x, y = cvt_pos(u, v, hom1)
#     utm_212.append([x,y])
# utm_212 = np.asarray(utm_212, dtype=np.float32)
# error = 0
# for i in range(np.size(utmPts2,0)):
#     error = cal_distance(utmPts2[i][0], utm_212[i][0],
#                          utmPts2[i][1], utm_212[i][1])
#     error += error
# print('error_utm_212', error/np.size(utmPts2,0))


# 用utmPts_new计算点的距离，Drone1的特征点1和Drone2的特征点8的距离,Google地图显示309.76m,
# a,b =0, 7
# print('像素转utm的距离是', cal_distance(utmPts1_new[a][0],utmPts2_new[b][0],utmPts1_new[a][1],utmPts2_new[b][1]))
# print('真实GPS转utm的距离是', cal_distance(utmPts1[a][0],utmPts2[b][0],utmPts1[a][1],utmPts2[b][1]))
# print('utm_212的距离是', cal_distance(utmPts1[a][0],utm_212[b][0],utmPts1[a][1],utm_212[b][1]))
# 像素转utm的距离是 308.4493475434824
# GPS转utm的距离是 309.37346590528733
# utm_212的距离是 310.40862685337856


# 如果能接受上面这些误差，可以想办法把Drone2的图也转成Drone1的，作为merge结果
# 已知Drone2特征点在自身像素坐标系下的结果
# 之前得到了Drone2特征点在Drone1像素坐标系下的结果
# 这两个坐标系得到转化矩阵，用来把Drone2的图也转过去
hom2to1, _ = cv.findHomography(imgPts2, imgPts_2to1, cv.RANSAC, 5)
img2 = cv.imread("F:/CATS_Lab/2022 ANL-UWisc SOW/20221111160315.9.undisto.jpg")
img2 = cv.copyMakeBorder(img2, 0,350, 0,3450, cv.BORDER_CONSTANT, value=[0,0,0])
move_img = cv.warpPerspective(img2, hom2to1, (img2.shape[1], img2.shape[0]))

move_img1 = move_img.copy()
rows, cols = img1.shape[:2]
move_img1[0:rows, 0:cols] = img1

a, b = 1500, 3250
part_move_img = move_img[a:rows, b:cols]
move_img1[a:rows, b:cols] = part_move_img

cv.imwrite("F:/CATS_Lab/2022 ANL-UWisc SOW/merge2.png", move_img1)