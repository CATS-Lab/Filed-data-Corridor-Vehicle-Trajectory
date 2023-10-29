# Match two image
from __future__ import print_function
import cv2
import os
import glob
import numpy as np

MAX_FEATURES = 1000
GOOD_MATCH_PERCENT = 0.15

def alignImages(im1, im2):

    # Convert images to grayscale
    im1Gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
    im2Gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)

    # Detect ORB features and compute descriptors.
    orb = cv2.ORB_create(MAX_FEATURES)
    keypoints1, descriptors1 = orb.detectAndCompute(im1Gray, None)
    keypoints2, descriptors2 = orb.detectAndCompute(im2Gray, None)

    # Match features.
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(descriptors1, descriptors2, None)

    # Sort matches by score
    matches.sort(key=lambda x: x.distance, reverse=False)

    # Remove not so good matches
    numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
    matches = matches[:numGoodMatches]

    # Draw top matches
    # imMatches = cv2.drawMatches(im1, keypoints1, im2, keypoints2, matches, None)
    # cv2.imwrite("matches.jpg", imMatches)

    # Extract location of good matches
    points1 = np.zeros((len(matches), 2), dtype=np.float32)
    points2 = np.zeros((len(matches), 2), dtype=np.float32)

    for i, match in enumerate(matches):
        points1[i, :] = keypoints1[match.queryIdx].pt
        points2[i, :] = keypoints2[match.trainIdx].pt

    # Find homography
    h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)

    # Use homography
    height, width, channels = im2.shape
    im1Reg = cv2.warpPerspective(im1, h, (width, height))

    return im1Reg, h


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
        imReg, h = alignImages(im, imReference) #estimated homography
        cv2.imwrite(Save_addr + imgFileName[:-3] + "stable.jpg", imReg)
        print("Saving aligned image : ", imgFileName[:-3] + "stable.jpg")
        #print("Estimated homography : \n",  h)
