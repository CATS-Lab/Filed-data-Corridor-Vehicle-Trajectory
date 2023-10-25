from __future__ import print_function
import cv2
import os
import numpy as np
Save_main_addr = "/media/ubuntu/ANL/Data/"
Drone_num = 2
if Drone_num == 1:
    sourceFile = Save_main_addr + "1extractFrame_Drone1/"
    Save_addr  = Save_main_addr + "2PicStable_Drone1/"
    #refFileName = sourceFile + "d20221111160315.1.jpg"
    #refFileName = Save_main_addr + "20221111163145.5.stable.black.jpg"
    #refFileName = Save_main_addr + "20221111164400.0.stable.black.jpg"
    #refFileName = Save_main_addr + "20221111165010.0.stable.black.jpg"
    refFileName = Save_main_addr + "20221111165334.0.stable.black.jpg"

elif Drone_num == 2:
    sourceFile = Save_main_addr + "1extractFrame_Drone2/"
    Save_addr  = Save_main_addr + "2PicStable_Drone2/"
    #refFileName = sourceFile + "d20221111160221.8.jpg"
    #refFileName = Save_addr + "20221111163214.3.stable.jpg"
    #refFileName = Save_main_addr + 'D2stableform/' + '20221111163214.0.stable.jpg'
    #refFileName = Save_main_addr + 'D2stableform/' + '20221111164412.0.stable.jpg'
    refFileName = Save_main_addr + 'D2stableform/' + '20221111165010.5.stable.jpg'

img2 = cv2.imread(refFileName, cv2.IMREAD_COLOR)
img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

path_list = os.listdir(sourceFile)
path_list.sort()
#print(path_list)
MAX_FEATURES = 1000
for imgFileName in path_list:
    if imgFileName[0] != 'd':
        img1 = cv2.imread(sourceFile + imgFileName, cv2.IMREAD_COLOR)
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)

        sift = cv2.xfeatures2d_SURF.create(2000)
        kp1, dp1 = sift.detectAndCompute(img1_gray, None)
        kp2, dp2 = sift.detectAndCompute(img2_gray, None)

        # Find nearest neighbor approximate matching
        index_params = dict(algorithm=0, trees=5)
        search_params = dict(checks=100)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(dp1, dp2, k=2)

        # Calculate effective point
        matchesMask = [[0, 0] for i in range(len(matches))]

        # coff to design effective kp nums
        coff = 0.2
        good = []
        for i, (m, n) in enumerate(matches):
            if m.distance < coff * n.distance:
                matchesMask[i] = [1, 0]
                good.append(m)

        # Find homography
        if len(good) > 3:
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
            h, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        # Use homography
        height, width, channels = img2.shape
        result = cv2.warpPerspective(img1, h, (width, height))
        #cv2.imshow("result", result)

        cv2.imwrite(Save_addr + imgFileName[:-3] + "stable.jpg", result)
        print("Saving image : ", imgFileName[:-3] + "stable.jpg")
        # processed pic rename with a 'd' ahead
        os.rename(os.path.join(sourceFile, imgFileName), os.path.join(sourceFile, "d" + imgFileName))

        # 存临时文件 画对比图
        # cv2.imwrite('./stable_try_result/' + imgFileName[:-3] + "stable.jpg", result) # 临时文件夹
        # good = np.expand_dims(good, 1)
        # img_out = cv2.drawMatchesKnn(img1, kp1, img2, kp2, good[:200], None, flags=2)
        # cv2.imwrite('./stable_try_result/compare' + imgFileName[:-3] + "stable.jpg", img_out)
