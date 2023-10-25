# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from decimal import Decimal
#import geopandas
from shapely import geometry
import pyproj
import re

class KalmanFilter(object):
    def __init__(self,F,H,gps_var,pre_var):
        self.F =F # 预测时的矩阵
        self.H = H # 测量时的矩阵
        self.n=self.F.shape[0]
        self.Q = np.zeros((self.n,self.n))
        self.Q[2,2]=pre_var
        self.Q[3,3]=pre_var
        self.R = np.zeros((n,n))
        self.R[0,0]=gps_var
        self.R[1,1]=gps_var
        self.R[2,2]=gps_var
        self.R[3,3]=gps_var
        self.P = np.eye(self.n)
        self.B = np.zeros((self.n, 1))
        self.state=0

    #第一次传入时设置观测值为初始估计值
    def set_state(self,x,y,time_stamp):
        self.X = np.zeros((self.n, 1))
        self.speed_x=0
        self.speed_y=0
        self.X=np.array([[x],[y],[self.speed_x],[self.speed_y]])
        self.pre_X=self.X
        self.time_stamp=time_stamp
        self.duration=0

    def process(self,x,y,time_stamp):
        if self.state==0:
            self.set_state(x,y,time_stamp)
            self.state=1
            return x,y

        self.duration=(time_stamp-self.time_stamp)#.seconds
        self.time_stamp=time_stamp
        self.Z = np.array([[x],[y],[self.speed_x],[self.speed_y]])
        #更新时长
        self.F[0,2]=self.duration
        self.F[1,3]=self.duration
        self.predict()
        self.update()
        return self.X[0,0],self.X[1,0]

    # 预测
    def predict(self, u = 0):
        # 实现公式x(k|k-1)=F(k-1)x(k-1)+B(k-1)u(k-1)
        self.X = np.dot(self.F, self.X) + np.dot(self.B, u)
        # 实现公式P(k|k-1)=F(k-1)P(k-1)F(k-1)^T+Q(k-1)
        self.P = np.dot(np.dot(self.F, self.P), self.F.T) + self.Q

    # 状态更新,使用观测校正预测
    def update(self):
        # 新息公式y(k)=z(k)-H(k)x(k|k-1)
        y = self.Z - np.dot(self.H, self.X)
        # 新息的协方差S(k)=H(k)P(k|k-1)H(k)^T+R(k)
        S = self.R + np.dot(self.H, np.dot(self.P, self.H.T))
        # 卡尔曼增益K=P(k|k-1)H(k)^TS(k)^-1 # linalg.inv(S)用于求S矩阵的逆
        K = np.dot(np.dot(self.P, self.H.T), np.linalg.inv(S))
        print('K=',K)
        # 状态更新，实现x(k)=x(k|k-1)+Ky(k)
        self.X = self.X + np.dot(K, y)
        #计算速度
        self.speed_x=(self.X[0,0]-self.pre_X[0,0])/self.duration
        self.speed_y=(self.X[1,0]-self.pre_X[1,0])/self.duration
        self.pre_X=self.X
        print(self.X)
        # 定义单位阵
        I = np.eye(self.n)
        # 估计值vs真实值 协方差更新
        # P(k)=[I-KH(k)]P(k|k-1)
        self.P = np.dot(I - np.dot(K, self.H), self.P)


# data=pd.read_table(r'E:\data\Taxi数据\T-drive Taxi Trajectories\release\taxi_log_2008_by_id\12.txt',delimiter=',',header=None)
# data.columns=['id','time','lon','lat']
# data['time']=pd.to_datetime(data['time'])
# data=data.sort_values(by='time')
# data=data.reset_index()
# data.columns=['label','id','time','lon','lat']
# data=data.drop_duplicates(subset="time")
# data['lon']= data['lon'].astype(float)
# data['lat']= data['lat'].astype(float)
#
# # -------中位数法-------
# n=4
# data1=data[['lon','lat']].rolling(n,min_periods=1,axis=0).median()
# data=pd.concat([data[['label','id','time']],data1],axis=1)
# data['geometry']=data.apply(lambda x: geometry.Point(x.lon,x.lat),axis=1)
# data=geopandas.GeoDataFrame(data)
# data.crs = pyproj.CRS.from_user_input('EPSG:4326')
# data=data.to_crs(crs="EPSG:2385")
# data['geometry']=data['geometry'].astype(str)
# data['x']=data['geometry'].apply(lambda x: float(re.findall(r'POINT \((.*?) ',x)[0]))
# data['y']=data['geometry'].apply(lambda x: float(re.findall(r'\d (.*?)\)',x)[0]))
# data.to_csv(r'C:\Users\fff507\Desktop\before.csv',index=False)


d = pd.read_csv("/media/ubuntu/ANL/Data1_lane_xy.csv")
d = d[d['id'] == 6]

# ------卡尔曼滤波------
# 状态变量的个数,x,y,speed_x,speed_y
n = 4
F = np.eye(n)
H = np.eye(n)
# 速度噪声的方差
pre_var = 10
# 坐标测量噪声的方差
gps_var = 10
gps_kalman=KalmanFilter(F=F,H=H,gps_var=gps_var,pre_var=pre_var)
lon_list=[]
lat_list=[]
for index,row in d.iterrows():
    lon,lat=gps_kalman.process(x=row['x_utm'],y=row['y_utm'],time_stamp=row['t_sec'])
    lon_list.append(lon)
    lat_list.append(lat)
print(lon_list)
d['new_lon'] = lon_list
d['new_lat'] = lat_list
d['geometry'] = d.apply(lambda x:geometry.Point(x.new_lon,x.new_lat),axis=1)
# data = geopandas.GeoDataFrame(d)
# data.crs = pyproj.CRS.from_user_input('EPSG:2385')
# data = data.to_crs(crs="EPSG:4326")
d['geometry'] = d['geometry'].astype(str)
d['new_lon'] = d['geometry'].apply(lambda x: float(re.findall(r'POINT \((.*?) ',x)[0]))
d['new_lat'] = d['geometry'].apply(lambda x: float(re.findall(r'\d (.*?)\)',x)[0]))

fig= plt.figure(figsize=(20,20), dpi=200)
ax1 = fig.add_subplot(111)
ax1.plot(d['x_utm'], d['y_utm'], '-*',label='before')
ax1.plot(d['new_lon'], d['new_lat'], '-o',label='after',alpha=0.5)
ax1.set_xlabel('UTM X Coordinate (m)')
ax1.set_ylabel('UTM Y Coordinate (m)')
#plt.gca().set_aspect(1)
plt.legend()
plt.show()
d.to_csv("/media/ubuntu/ANL/after.csv", index=False)
