# conda activate py36
# https://luzhimin.blog.csdn.net/article/details/114523558?spm=1001.2014.3001.5502
import cv2
import numpy as np
from tqdm import tqdm
import argparse
import os
import time

# get param
parser = argparse.ArgumentParser(description='')
parser.add_argument('-v', type=str, default='')  # 指定输入视频路径位置（参数必选）
parser.add_argument('-o', type=str, default='')  # 指定输出视频路径位置（参数必选）
parser.add_argument('-n', type=int, default=-1)  # 指定处理的帧数（参数可选）, 不设置使用视频实际帧

# eg: python3 stable.py -v=video/01.mp4 -o=video/01_stable.mp4 -n=100 -p=6

args = parser.parse_args()

input_path = args.v
output_path = args.o
number = args.n


class Stable:
    # 处理视频文件路径
    __input_path = None
    __output_path = None
    __number = number

    # surf 特征提取
    __surf = {
        # surf算法
        'surf': None,
        # 提取的特征点
        'kp': None,
        # 描述符
        'des': None,
        # 过滤后的特征模板
        'template_kp': None
    }

    # capture
    __capture = {
        # 捕捉器
        'cap': None,
        # 视频大小
        'size': None,
        # 视频总帧
        'frame_count': None,
        # 视频帧率
        'fps': None,
        # 视频
        'video': None,
    }

    # 配置
    __config = {
        # 要保留的最佳特征的数量
        'key_point_count': 1000,
        # Flann特征匹配
        'index_params': dict(algorithm=0, trees=5),
        'search_params': dict(checks=50),
        'ratio': 0.8,
    }

    # 当前处理帧数
    __current_frame = 0

    # 需要处理帧数
    __handle_count = 0

    # 帧队列
    __frame_queue = None

    # 需要写入的帧队列
    __write_frame_queue = None

    # 特征提取列表
    __surf_list = []

    def __init__(self):
        pass

    # 初始化capture
    def __init_capture(self):
        self.__capture['cap'] = cv2.VideoCapture(self.__video_path)
        self.__capture['size'] = (int(self.__capture['cap'].get(cv2.CAP_PROP_FRAME_WIDTH)),
                                  int(self.__capture['cap'].get(cv2.CAP_PROP_FRAME_HEIGHT)))

        self.__capture['fps'] = self.__capture['cap'].get(cv2.CAP_PROP_FPS)

        self.__capture['video'] = cv2.VideoWriter(self.__output_path, cv2.VideoWriter_fourcc(*"mp4v"),
                                                  self.__capture['fps'], self.__capture['size'])

        self.__capture['frame_count'] = int(self.__capture['cap'].get(cv2.CAP_PROP_FRAME_COUNT))

        if number == -1:
            self.__number = self.__capture['frame_count']
        else:
            self.__number = min(self.__number, self.__capture['frame_count'])

    # 初始化surf
    def __init_surf(self):

        ## first_frame 用来对其的标准
        # 用自身视频的第一帧
        self.__capture['cap'].set(cv2.CAP_PROP_POS_FRAMES, 0)
        state, first_frame = self.__capture['cap'].read()
        # 用给定视频的第一帧
        # first_frame_capture = cv2.VideoCapture("/media/ubuntu/GFWLeidos/ANL/ParkSt_DroneVideo/Drone1/DJI_20221111163858_0002_V.MP4")
        # state, first_frame = first_frame_capture.read()
        # cv2.imwrite("/media/cats/GFWLeidos/ANL/ParkSt_DroneVideo/Drone1/DJI_20221111160315_0001_V.png", first_frame)

        ## last_frame
        # 用自身视频的第一帧
        # self.__capture['cap'].set(cv2.CAP_PROP_POS_FRAMES, 0)
        # state, last_frame = self.__capture['cap'].read()
        # 用自身视频的最后一帧
        self.__capture['cap'].set(cv2.CAP_PROP_POS_FRAMES, self.__capture['frame_count'] - 5)
        state, last_frame = self.__capture['cap'].read()
        # 用给定视频的第一帧
        # last_frame_capture = cv2.VideoCapture("/media/cats/GFWLeidos/ANL/ParkSt_DroneVideo/Drone1/DJI_20221111163858_0002_V.MP4")
        # state, last_frame = last_frame_capture.read()


        self.__surf['surf'] = cv2.xfeatures2d.SURF_create(self.__config['key_point_count'],1,1,1,1)
        self.__surf['kp'], self.__surf['des'] = self.__surf['surf'].detectAndCompute(first_frame, None)
        kp, des = self.__surf['surf'].detectAndCompute(last_frame, None)

        # 快速临近匹配
        flann = cv2.FlannBasedMatcher(self.__config['index_params'], self.__config['search_params'])
        matches = flann.knnMatch(self.__surf['des'], des, k=2)

        good_match = []
        for m, n in matches:
            if m.distance < self.__config['ratio'] * n.distance:
                good_match.append(m)

        self.__surf['template_kp'] = []
        for f in good_match:
            self.__surf['template_kp'].append(self.__surf['kp'][f.queryIdx])

        self.__capture['cap'].set(cv2.CAP_PROP_POS_FRAMES, 0)


    # 释放
    def __release(self):
        self.__capture['video'].release()
        self.__capture['cap'].release()

    # 处理
    def __process(self):

        print('Total frame =',self.__capture['frame_count'])
        current_frame = 1
        self.__capture['cap'].set(cv2.CAP_PROP_POS_FRAMES, 0)
        process_bar = tqdm(self.__number, position=current_frame)

        while current_frame <= self.__number:
            # 抽帧
            success, frame = self.__capture['cap'].read()
            if not success: return

            # 计算
            frame = self.detect_compute(frame)

            # 写帧
            self.__capture['video'].write(frame)
            current_frame += 1
            process_bar.update(1)

    # 视频稳像
    def stable(self, input_path, output_path, number):
        self.__video_path = input_path
        self.__output_path = output_path
        self.__number = number
        self.__init_capture()
        self.__init_surf()
        self.__process()
        self.__release()

    # 特征点提取
    def detect_compute(self, frame):

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 计算特征点
        kp, des = self.__surf['surf'].detectAndCompute(frame_gray, None)

        # 快速临近匹配
        flann = cv2.FlannBasedMatcher(self.__config['index_params'], self.__config['search_params'])
        matches = flann.knnMatch(self.__surf['des'], des, k=2)

        # 计算单应性矩阵
        good_match = []
        for m, n in matches:
            if m.distance < self.__config['ratio'] * n.distance:
                good_match.append(m)

        # 特征模版过滤
        p1, p2 = [], []
        for f in good_match:
            if self.__surf['kp'][f.queryIdx] in self.__surf['template_kp']:
                p1.append(self.__surf['kp'][f.queryIdx].pt)
                p2.append(kp[f.trainIdx].pt)

        # 单应性矩阵
        H, _ = cv2.findHomography(np.float32(p2), np.float32(p1), cv2.RHO)

        # 透视变换
        output_frame = cv2.warpPerspective(frame, H, self.__capture['size'], borderMode=cv2.BORDER_CONSTANT)

        return output_frame


if __name__ == '__main__':

    if not os.path.exists(input_path):
        print(f'[ERROR] File "{input_path}" not found')
        exit(0)
    else:
        print(f'[INFO] Video "{input_path}" stable begin')

    s = Stable()
    s.stable(input_path, output_path, number)

    print('[INFO] Done.')
    exit(0)