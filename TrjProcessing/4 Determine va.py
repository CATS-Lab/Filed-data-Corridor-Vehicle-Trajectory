import pandas as pd
import numpy as np
from tqdm import tqdm

# def cal_distance(x1,x2,y1,y2):
#     return np.sqrt((x1 - x2)**2 + (y1 - y2)**2)

df = pd.read_csv("/media/ubuntu/ANL/Data3_lane_xynew.csv")

def calculate_speed(df):
    # Use vectorization to calculate distance
    dx = np.diff(df['x_utm'])
    dy = np.diff(df['y_utm'])
    dt = np.diff(df['t_sec'])
    distance = np.sqrt(dx**2 + dy**2)
    speed = distance / dt
    speed = np.insert(speed, len(speed), np.nan)

    # Add speed column to dataframe
    df['v'] = speed.round(3)

    return df

def calculate_acceleration(df):
    # Calculate acceleration using difference between previous and current time steps
    acceleration = np.diff(df['v']) / np.diff(df['t_sec'])
    acceleration = np.insert(acceleration, len(acceleration), np.nan)

    # Add acceleration column to dataframe
    df['a'] = acceleration.round(3)

    return df

# Group data by vehicle ID and apply calculation functions
grouped = df.groupby('id').apply(calculate_speed)
grouped = grouped.groupby('id').apply(calculate_acceleration)

new_d = grouped.reset_index(drop=True)
new_d.to_csv(path_or_buf="/media/ubuntu/ANL/Data3_lane_xy_va.csv", index=False)