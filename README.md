# Bi-scale Car-following Model Calibration for Corridor Based on Trajectory

## Introduction

Hey there! In this repo, you'll find a tool that our group put together to transform video data we captured with two drones into CSV-based car-following trajectories. We got our footage from Park St in Madison, Wisconsin. We're using this transformed trajectory data to test out a bi-scale calibration approach for car-following models. We've been working on a paper that describes the detailed methods behind this tool, and we're planning to upload it to arXiv soon. Once our paper gets the green light, we'll be sharing the video data here too. Stay tuned!

![alt text](images/study_area_of_data_set.jpg)
The studied area of the data collected from Park St in Madison, Wisconsin

## Installation

Here are the prerequisites for using this repo:

1. **Python 3**: Ensure you have a Python 3 environment set up.
2. **Required Packages**: Install all necessary packages listed in the `requirements.txt` file.
3. **YOLOv7**: If you're keen on executing the detection component, YOLOv7 needs to be installed.

## Usage

To use this repo, run each Python script in the order we introduced in this section. As you proceed through each Python script, always verify the paths for both the input and output files. This ensures that everything runs smoothly.

The process of vehicle trajectory extraction and cleaning contains two parts: trajectory extraction and trajectory processing. Please find the details of each steps in our paper.

### Trajectory extraction

All code in this steps is under folder "TrjExtraction".

Step (1): Selects keyframes from the vedio. (./TrjExtraction/1 ExtractFrame.py)

Step (1): Stabilizes all frames by matching the feature points. (./TrjExtraction/2 PicStable.py)

Step (2): Merges the frames from different drones and gets the full scope of the target range. (./TrjExtraction/3 Merge.py)

Step (3): Detects and tracks the vehicle using locally trained YOLOv7 (25) and DeepSORT (26), then get the initial trajectory data of all vehicles in pixel coordinate. (This step required YOLOv7, we will update the code for this step soon)

### Trajectory processing

All code in this steps is under folder "TrjProcessing".

Step (0): Converts the trajectories to csv format. (./TrjProcessing/0 trackresult2csv.py)

Sept (1): Determine the edges of each lanes in the map. (./TrjProcessing/1 Determine edge and lane.py)

Step (2): Transfers the coordinate trajectory to Universal Transverse Mercator Grid System (UTM) coordinate trajectory. (./TrjProcessing/2 Pixel2Global xy.py)

Step (3): Removes position offsets and then smoothed the trajectory. (./TrjProcessing/3 Trj Clean.py)

Step (4): Calculates the vehicle speed, acceleration, and position. (./TrjProcessing/4 Determine va.py, ./TrjProcessing/5 Veh_info.py, ./TrjProcessing/6 Determine Preceding veh.py)

### Data

We will provide the processed data soon. Data attributes are shown below.
| **Attribute** | **Unit** | **Description** |
| --- | --- | --- |
| id | - | Id of vehicles |
| time | - | Time in the format of YYYYMMDDHHMM.S. |
| x\_pix | pixel | The horizontal pixel coordinate of vehicle |
| y\_pix | pixel | The vertical pixel coordinate of vehicle |
| w\_pix | pixel | The width of an object in pixels. |
| h\_pix | pixel | The height of an object in pixels. |
| edge | - | The position of edge or intersection. |
| lane | - | The position of lane at given edge. If the vehicle is in an intersection, lane is 0. |
| x\_utm | m | The UTM x-coordinate of vehicle |
| y\_utm | m | The UTM y-coordinate of vehicle |
| t\_sec | sec | The record time in seconds |
| v | m/s | Speed of the vehicle |
| a | $m/s^-2$ | Acceleration of the vehicle |
| pre\_id | - | Vehicle id of the previous vehicle |
| pre\_v | m/s | Speed of the previous vehicle |
| delta\_d | m | Distance between the outer contours of the subject vehicle and the preceding vehicle |

## Developers

Developer: Keke Long (klong23@wisc.edu).

Code reviewer: Hang Zhou (hzhou364@wisc.edu).

If you have any questions, please feel free to contact CATS Lab in UW-Madison. We're here to help!

## Citation

Long, K., Shi, H., Chen, Z., Liang, Z., Li, X., & de Souza, F. (2024). Bi-scale car-following model calibration based on corridor-level trajectory. Transportation Research Part E: Logistics and Transportation Review, 186, 103497.
