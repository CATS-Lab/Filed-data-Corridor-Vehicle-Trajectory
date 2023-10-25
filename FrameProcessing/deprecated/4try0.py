import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import time
import os
import re

start_time = time.time()

Save_main_addr = "/media/ubuntu/Seagate Expansion Drive/ANL/"
sourceFile1 = Save_main_addr + "3Undistort_Drone1/"
sourceFile2 = Save_main_addr + "3Undistort_Drone2/"
Save_addr = Save_main_addr + "4Merging/"

Drone1_empty = cv.imread(Save_main_addr + "Drone1stable_empty.jpg")
Drone2_empty = cv.imread(Save_main_addr + "Drone2stable_empty.jpg")

Drone1_time_list = []
Drone2_time_list = []

path_list1 = os.listdir(sourceFile1)
path_list1.sort()
path_list2 = os.listdir(sourceFile2)
path_list2.sort()

for imgFileName in path_list1:
    time = float(imgFileName[8:16])
    print(time)
    Drone1_time_list.append(time)
for imgFileName in path_list2:
    time = float(imgFileName[8:16])
    print(time)
    Drone2_time_list.append(time)

# 前面是把每个drone有的time写成列表

#time_list_total = list(set(Drone1_time_list).union(set(Drone2_time_list))) #并集
time_list_total = list(set(Drone1_time_list).intersection(set(Drone2_time_list))) #交集
time_list_total.sort()



# 20221111160316.7  用这个得到转换矩阵M0
img1 = cv.imread(sourceFile1 + '20221111160316.7.undistort.jpg')
img2 = cv.imread(sourceFile2 + '20221111160316.7.undistort.jpg')
# 合并
dim = (int(img2.shape[1]), int(img2.shape[0]))
img1 = cv.resize(img1, dim, interpolation=cv.INTER_AREA)

# SURF
surf = cv.xfeatures2d.SURF_create(1000, nOctaves=4, extended=False, upright=True)
gray1 = cv.cvtColor(img1, cv.COLOR_RGB2GRAY)
gray2 = cv.cvtColor(img2, cv.COLOR_RGB2GRAY)
kp1, describe1 = surf.detectAndCompute(gray1, None)
kp2, describe2 = surf.detectAndCompute(gray2, None)

# FLANN
FLANN_INDEX_KDTREE = 0
indexParams = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
searchParams = dict(checks=50)
flann = cv.FlannBasedMatcher(indexParams, searchParams)
match = flann.knnMatch(describe1, describe2, k=2)

good = []
for i, (m, n) in enumerate(match):
    if m.distance < 0.75 * n.distance:
        good.append(m)

MIN = 10
if len(good) > MIN:
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    ano_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    M0, mask = cv.findHomography(src_pts, ano_pts, cv.RANSAC, 5.0) #找到两个平面之间的转换矩阵


# 遍历文件，用同一个M0
for time in time_list_total:
    #找drone1有咩有
    if time in Drone1_time_list:
        img1 = cv.imread(sourceFile1 + '20221111' + str(time) + '.undistort.jpg')
    else:
        img1 = Drone1_empty
    #找drone2有没有
    if time in Drone2_time_list:
        img2 = cv.imread(sourceFile2 + '20221111' + str(time) + '.undistort.jpg')
    else:
        img2 = Drone2_empty

    #合并
    dim = (int(img2.shape[1]), int(img2.shape[0]))
    img1 = cv.resize(img1, dim, interpolation=cv.INTER_AREA)

    print('img1 Dimensions : ', img1.shape)
    print('img2 Dimensions : ', img2.shape)
    # plt.imshow(img1, ), plt.show()
    # plt.imshow(img2, ), plt.show()

    # SURF
    surf = cv.xfeatures2d.SURF_create(1000, nOctaves=4, extended=False, upright=True)
    gray1 = cv.cvtColor(img1, cv.COLOR_RGB2GRAY)
    gray2 = cv.cvtColor(img2, cv.COLOR_RGB2GRAY)

    kp1, describe1 = surf.detectAndCompute(gray1, None)
    kp2, describe2 = surf.detectAndCompute(gray2, None)

    # FLANN
    FLANN_INDEX_KDTREE = 0
    indexParams = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    searchParams = dict(checks=50)

    flann = cv.FlannBasedMatcher(indexParams, searchParams)
    match = flann.knnMatch(describe1, describe2, k=2)

    good = []
    for i, (m, n) in enumerate(match):
        if m.distance < 0.75 * n.distance:
            good.append(m)

    ##################################
    # RANSAC:findhomography
    MIN = 10
    if len(good) > MIN:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
        ano_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
        M, mask = cv.findHomography(src_pts, ano_pts, cv.RANSAC, 5.0) #找到两个平面之间的转换矩阵
        warpImg = cv.warpPerspective(img2, np.linalg.inv(M0), (img1.shape[1] + img2.shape[1], img2.shape[0]))
        direct = warpImg.copy()
        direct[0:img1.shape[0], 0:img1.shape[1]] = img1
    ###################################

        # cv.namedWindow("Result", cv.WINDOW_NORMAL)
        # cv.imshow("Result",warpImg)
        rows, cols = img1.shape[:2]
        left = 0
        right = cols

        for col in range(0, cols):
            if img1[:, col].any() and warpImg[:, col].any():  # 开始重叠的最左端
                left = col
            break

        for col in range(cols - 1, 0, -1):
            if img1[:, col].any() and warpImg[:, col].any():  # 重叠的最右一列
                right = col
            break

        res = np.zeros([rows, cols, 3], np.uint8)

        for row in range(0, rows):
            for col in range(0, cols):
                if not img1[row, col].any():
                    res[row, col] = warpImg[row, col]
                elif not warpImg[row, col].any():
                    res[row, col] = img1[row, col]
                else:
                    srcImgLen = float(abs(col - left))
                    testImgLen = float(abs(col - right))
                    alpha = srcImgLen / (srcImgLen + testImgLen)
                    res[row, col] = np.clip(img1[row, col] * (1 - alpha) + warpImg[row, col] * alpha, 0, 255)

        warpImg[0:img1.shape[0], 0:img1.shape[1]] = res
        img3 = cv.cvtColor(direct, cv.COLOR_BGR2RGB)
        #plt.imshow(img3, ), plt.show()
        img4 = cv.cvtColor(warpImg, cv.COLOR_BGR2RGB)
        #plt.imshow(img4, ), plt.show()
        #cv.imwrite("simpletons.png", direct)
        cv.imwrite(Save_addr + '20221111' + str(time) + "bestowal.png", direct)
        #cv.imshow("pictures", img4)
    else:
        print("not enough matches!")