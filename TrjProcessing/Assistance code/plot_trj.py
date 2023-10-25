import matplotlib.pyplot as plt
import pandas as pd

# 读取处理前的数据
df_before = pd.read_csv("/media/ubuntu/ANL/Data3_lane_xy.csv")
df_before = df_before[df_before['id'] == 6]  # 筛选出id为6的数据

# 读取处理后的数据
df_after = pd.read_csv("/media/ubuntu/ANL/Data3_lane_xynew.csv")
df_after = df_after[df_after['id'] == 6]  # 筛选出id为6的数据

# 绘制处理前和处理后的轨迹
fig, ax = plt.subplots(figsize=(10, 8))
ax.plot(df_before['x_utm'], df_before['y_utm'], color='blue', label='before')
ax.plot(df_after['x_utm'], df_after['y_utm'], color='orange', label='after')
ax.set_title('Vehicle Trajectory (ID=6) Before and After Processing')
ax.set_xlabel('UTM X Coordinate (m)')
ax.set_ylabel('UTM Y Coordinate (m)')
ax.legend()
plt.show()
