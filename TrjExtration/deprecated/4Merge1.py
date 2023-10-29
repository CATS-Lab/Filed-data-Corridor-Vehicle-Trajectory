import cv2
import numpy as np
import os

Save_main_addr = "/media/ubuntu/Seagate Expansion Drive/ANL/"
sourceFile1 = Save_main_addr + "3Undistort_Drone1/"
sourceFile2 = Save_main_addr + "3Undistort_Drone2/"
Save_addr = Save_main_addr + "4Merging/"

Drone1_empty = cv2.imread(Save_main_addr + "Drone1stable_empty.jpg")
Drone2_empty = cv2.imread(Save_main_addr + "Drone2stable_empty.jpg")


# img1 = cv2.imread(sourceFile1 + "20221111160316.0.undistort.jpg")
# img2 = cv2.imread(sourceFile2 + "20221111160316.0.undistort.jpg")
# image = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)

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

# 遍历文件，用同一个M0
for time in time_list_total:
    #找drone1有咩有
    if time in Drone1_time_list:
        img1 = cv2.imread(sourceFile1 + '20221111' + str(time) + '.undistort.jpg')
    else:
        img1 = Drone1_empty
    #找drone2有没有
    if time in Drone2_time_list:
        img2 = cv2.imread(sourceFile2 + '20221111' + str(time) + '.undistort.jpg')
    else:
        img2 = Drone2_empty

    #合并
    # rotate
    image = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
    rows, cols, channel = img2.shape
    M = cv2.getRotationMatrix2D((cols/2, rows/2), 0.8, 1) #参数：旋转中心 旋转度数 scale  # 0.9
    rotated_img2 = cv2.warpAffine(img2, M, (cols, rows))
    #print(rows, cols)

    # move
    move_x, move_y = 3226, 239   # 3220, 233
    M = np.float32([[1, 0, move_x], [0, 1, move_y]])
    rotated_img2 = cv2.warpAffine(rotated_img2, M, (image.shape[1] + int(move_x*1.01), image.shape[0] + int(move_y*1.1)) )

    # add two img
    rows, cols = img1.shape[:2]
    roi = rotated_img2[0:rows, 0:cols]
    dst = cv2.addWeighted(img1, 1, roi, 0, 0)
    add_img = rotated_img2.copy()
    add_img[0:rows, 0:cols] = dst

    a, b = 1500, 3250
    part_rotated_img2 = rotated_img2[a:rows, b:cols]
    add_img[a:rows, b:cols] = part_rotated_img2

    # show and save
    # cv2.namedWindow('add_img', 0)
    # cv2.imshow("add_img", add_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    cv2.imwrite(Save_addr + '20221111' + str(time) + "bestowal.png", add_img)


