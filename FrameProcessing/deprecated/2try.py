# Match two image
from __future__ import print_function
import cv2
import os
import glob
import numpy as np


MAX_FEATURES = 1000
GOOD_MATCH_PERCENT = 0.15
def surf_kp(image):
    '''SIFT(surf)特征点检测(速度比sift快)'''
    height, width = image.shape[:2]
    size = (int(width), int(height))
    shrink = cv2.resize(image, size, interpolation=cv2.INTER_AREA)
    gray_image = cv2.cvtColor(shrink,cv2.COLOR_BGR2GRAY)
    surf = cv2.xfeatures2d_SURF.create()
    kp, des = surf.detectAndCompute(gray_image, None)
    return kp,des

def get_good_match(des1,des2):
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)
    return good

def siftImageAlignment(img1,img2):
   kp1,des1 = surf_kp(img1)
   kp2,des2 = surf_kp(img2)
   goodMatch = get_good_match(des1,des2)
   if len(goodMatch) > 4:
       ptsA= np.float32([kp1[m.queryIdx].pt for m in goodMatch]).reshape(-1, 1, 2)
       ptsB = np.float32([kp2[m.trainIdx].pt for m in goodMatch]).reshape(-1, 1, 2)
       ransacReprojThreshold = 4
       H, status =cv2.findHomography(ptsA,ptsB,cv2.RANSAC,ransacReprojThreshold);
       imgOut = cv2.warpPerspective(img2, H, (img1.shape[1],img1.shape[0]),flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
   return imgOut,H,status

if __name__ == '__main__':
    Drone_num = 1
    if Drone_num == 1:
        sourceFile = "/home/ubuntu/Documents/1extractFrame_Drone1/"
        Save_addr = "/home/ubuntu/Documents/2PicStable_Drone1/"
        refFileName = sourceFile+"20221111160315.1.jpg"
    elif Drone_num == 2:
        sourceFile = "/home/ubuntu/Documents/1extractFrame_Drone2/"
        Save_addr = "/home/ubuntu/Documents/2PicStable_Drone2/"

    imReference = cv2.imread(refFileName, cv2.IMREAD_COLOR)

    path_list = os.listdir(sourceFile)
    path_list.sort()
    #print(path_list)

    for imgFileName in path_list:
        im = cv2.imread(sourceFile + imgFileName, cv2.IMREAD_COLOR)
        result, _, _ = siftImageAlignment(imReference, im )
        allImg = np.concatenate((imReference, im , result), axis=1)
        cv2.imwrite(Save_addr + imgFileName[:-3] + "stable.jpg", result)
        print("Saving aligned image : ", imgFileName[:-3] + "stable.jpg")
        #print("Estimated homography : \n",  h)
