import cv2
import os
import datetime
import re

Save = False
error = 0

# Drone_num = 2
# VideoName = "DJI_20221111160610_0002_V"
# error = +0.3
# Save = True
##
# Drone_num = 1
# VideoName = "DJI_20221111160704_0002_V"
# error = -0.3
# Save = True
##
# Drone_num = 2
# VideoName = "DJI_20221111160959_0003_V"
# error = 0.1
# Save = True
##
# Drone_num = 1
# VideoName = "DJI_20221111161052_0003_V"
# error = 0.4
# Save = True
##
# Drone_num = 2
# VideoName = "DJI_20221111161348_0004_V"
# error = -0.2
# Save = True
##
# Drone_num = 1
# VideoName = "DJI_20221111161441_0004_V"
# error = 0.1
# Save = True
##
# Drone_num = 2
# VideoName = "DJI_20221111161737_0005_V"
# error = -0.5
# Save = True
##
# Drone_num = 1
# VideoName = "DJI_20221111161830_0005_V"
# error = -0.2
# Save = True
##
# Drone_num = 2
# VideoName = "DJI_20221111162125_0006_V"
# error = 0.2
# Save = True
##
# Drone_num = 1
# VideoName = "DJI_20221111162218_0006_V"
# error = 0.5
# Save = True
##
# Drone_num = 2
# VideoName = "DJI_20221111162514_0007_V"
# error = 0
# Save = True
#
# Drone_num = 1
# VideoName = "DJI_20221111162607_0007_V"
# error = 0.1
# Save = True
##
# Drone_num = 2
# VideoName = "DJI_20221111162903_0008_V"
# error = -0.4
# Save = True
##
# Drone_num = 1
# VideoName = "DJI_20221111162956_0008_V"
# error = -0.1
# Save = True
##
# Drone_num = 2
# VideoName = "DJI_20221111163201_0009_V" # cannot find reference frame from Drone 1
# Save = True
##
# Drone_num = 1
# VideoName = "DJI_20221111163509_0001_V"
# error = -0.4
# Save = True
##
# Drone_num = 2
# VideoName = "DJI_20221111163549_0010_V"
# error = 0.6
# Save = True
##
# Drone_num = 1
# VideoName = "DJI_20221111163858_0002_V"  # cannot find reference frame from Drone 2, 但是相对于上一个drone1的时间差
# error = -0.7
# Save = True
##
# Drone_num = 2
# VideoName = "DJI_20221111163930_0001_V"
# error = 0.4
# Save = True
##
# Drone_num = 1
# VideoName = "DJI_20221111164246_0003_V"
# error = 0
# Save = True
##
# Drone_num = 2
# VideoName = "DJI_20221111164319_0002_V" #没问题
# error = 0
# Save = True
##
# Drone_num = 1
# VideoName = "DJI_20221111164635_0004_V" #没问题
# error = -0.3
# Save = True
##
# Drone_num = 2
# VideoName = "DJI_20221111164707_0003_V"
# error = 0.8
# Save = True
##
# Drone_num = 1
# VideoName = "DJI_20221111165024_0005_V"
# error = -0.5
# Save = True
##
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
ii = [round(n*time_step*frames) for n in list(range(50000))]

cap = cv2.VideoCapture(video_path)
total_frames_num = cap.get(7)

num_frame = 1
while (True):
    ret, frame = cap.read()
    if ret:
        if num_frame in ii:
            frame_time = time + datetime.timedelta(hours=0, minutes=0, seconds=round(num_frame/frames,1))
            frame_time = frame_time + datetime.timedelta(hours=0, minutes=0, seconds= error) #修改误差
            data_microsecond = frame_time.microsecond / 1000000
            date_stamp = datetime.datetime.strftime(frame_time, '%Y%m%d%H%M%S') + str(round(data_microsecond,1))[1:]
            if Drone_num == 2:
                frame = cv2.flip(cv2.flip(frame, 0), 1) #旋转
            cv2.imwrite(Save_addr + date_stamp + '.jpg', frame)  # 保存
            print("保存文件" + date_stamp + '对应帧' + str(num_frame) + '/' + str(total_frames_num))
        num_frame += 1
        cv2.waitKey(0)
    else:
        print("所有帧都已经保存完成")
        break
cap.release()


