import cv2
import os
import datetime
import re

Save = False
error = 0

Drone_num = 2
VideoName = "DJI_20221111165056_0004_V"
error = 0.6
Save = True

Save_main_addr = "/media/ubuntu/ANL/Data/"
if Drone_num == 1:
    sourceFile = Save_main_addr + "ParkSt_DroneVideo/Drone1/"
    if Save:
        Save_addr = Save_main_addr + "1extractFrame_Drone1/"
    else:
        Save_addr = Save_main_addr + "1Drone1/"
elif Drone_num == 2:
    sourceFile = Save_main_addr + "ParkSt_DroneVideo/Drone2/"
    if Save:
        Save_addr = Save_main_addr + "1extractFrame_Drone2/"
    else:
        Save_addr = Save_main_addr + "1Drone2/"

video_path = os.path.join("", "", sourceFile + VideoName + '.MP4')

file_name = re.split(r'[_,\s]\s*', VideoName)
time = datetime.datetime.strptime(file_name[1], "%Y%m%d%H%M%S")

frames = 29.97
time_step = 0.1
ii = [round(n * time_step * frames) for n in list(range(50000))]

cap = cv2.VideoCapture(video_path)
total_frames_num = cap.get(7)

num_frame = 1
while (True):
    ret, frame = cap.read()
    if ret:
        if num_frame in ii:
            frame_time = time + datetime.timedelta(hours=0, minutes=0, seconds=round(num_frame / frames, 1))
            frame_time = frame_time + datetime.timedelta(hours=0, minutes=0, seconds=error)
            data_microsecond = frame_time.microsecond / 1000000
            date_stamp = datetime.datetime.strftime(frame_time, '%Y%m%d%H%M%S') + str(round(data_microsecond, 1))[1:]
            if Drone_num == 2:
                frame = cv2.flip(cv2.flip(frame, 0), 1)
            cv2.imwrite(Save_addr + date_stamp + '.jpg', frame)
        num_frame += 1
        cv2.waitKey(0)
    else:
        break
cap.release()
