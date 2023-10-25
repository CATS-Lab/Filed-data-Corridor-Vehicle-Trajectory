import numpy as np
import cv2
import matplotlib.pyplot as plt
import utm
import os

#%% GPS to UTM
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
        # UTM转经纬度
        # lat, lon = utm.to_latlon(utm_x, utm_y, utm_zone, utm_band)
    utmPts = np.asarray(utmPtsl, dtype=np.float32)
    # plt.plot(utmPts[:,0], utmPts[:,1])
    # plt.title('utmPts 世界坐标')
    # plt.show()
    return utmPts

# %% Drone 1
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
    [620, 1024],
    [1340, 922],
    [1193, 1248],
    [1926, 1049],
    [3353, 949],
    [3702, 1545],
    [1232, 33],
    [1191, 2110],
])

# %% Drone 2
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
    [153, 700],
    [480, 1273],
    [1475, 1354],
    [2636, 310],
    [2755, 609],
    [2707, 1467],
    [2947, 1971],
    [3321, 1356],
])

GPS_info1 = Drone1_GPS_info
imgPts1 = np.array([Drone1_imgPts])
GPS_info2 = Drone2_GPS_info
imgPts2 = np.array([Drone2_imgPts])


Drone_num = 2 # The only place need to be changed

size = (3835, 2151)
Save_main_addr = "/media/ubuntu/Seagate Expansion Drive/ANL/"
if Drone_num == 1:
    sourceFile = Save_main_addr + "2PicStable_Drone1/"
    Save_addr  = Save_main_addr + "3Undistort_Drone1/"
    rms, camera_matrix, distCoeffs, rvec, tvec = cv2.calibrateCamera([GPS2UTM(GPS_info1)], [imgPts1], size, None, None) # Camera Calibration
    print("camera matrix1 =", camera_matrix)
elif Drone_num == 2:
    sourceFile = Save_main_addr + "2PicStable_Drone2/"
    Save_addr  = Save_main_addr + "3Undistort_Drone2/"
    rms, camera_matrix, distCoeffs, rvec, tvec = cv2.calibrateCamera([GPS2UTM(GPS_info2)], [imgPts2], size, None, None) # Camera Calibration
    print("camera matrix1 =", camera_matrix)


# Undistort frames
path_list = os.listdir(sourceFile)
path_list.sort()
#print(path_list)
for imgFileName in path_list:
    if imgFileName[0] != 'd':
        img = cv2.imread(sourceFile + imgFileName, cv2.IMREAD_COLOR)
        img_undistored = cv2.undistort(img, camera_matrix, distCoeffs)
        cv2.imwrite(Save_addr + imgFileName[:-10] + "undistort.jpg", img_undistored)
        print("Saving image : ", imgFileName[:-10] + "undistort.jpg")
        os.rename(os.path.join(sourceFile, imgFileName), os.path.join(sourceFile, "d" + imgFileName))