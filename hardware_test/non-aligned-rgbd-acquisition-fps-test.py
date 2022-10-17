# -*- encoding: utf-8 -*-
"""
non-aligned-rgbd-acquisition-fps-test.py
和 aligned-rgbd-acquisition-fps-test.py 一样测试，区别是这里图片不需要对齐操作，理论上会快很多
"""

import time
import pyrealsense2 as rs
import numpy as np
import cv2

# Create a pipeline
pipeline = rs.pipeline()
# Create a config and configure the pipeline to stream
#  different resolutions of color and depth streams
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

# config.enable_stream(rs.stream.depth, 640, 360, rs.format.z16, 30)
# config.enable_stream(rs.stream.depth, 640, 360, rs.format.z16, 30)
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

# config.enable_stream(rs.stream.color, 640, 360, rs.format.bgr8, 30)
# config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

# supported size
# Depth
# 320x240
# 640x480
# 1024x768
#
# Color
# 640x360
# 640x480
# 960x540
# 1280x720

# Start streaming
profile = pipeline.start(config)

# Getting the depth sensor's depth scale (see rs-align example for explanation)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print("Depth Scale is: ", depth_scale)

# We will be removing the background of objects more than   !!!!!!
#  clipping_distance_in_meters meters away
clipping_distance_in_meters = 1  # 1 meter
clipping_distance = clipping_distance_in_meters / depth_scale


def compute_mean(array_in, N=2):
    """
    计算 array_in (ndarray) 中 非零 元素的均值 , 保留 N 位小数
    """
    exist = (array_in != 0)
    mean_value = array_in.sum() / exist.sum()
    return round(mean_value, N)


vis = False
distance_min = 0.12  # 小于该值的深度值应等于0,即此处深度计算失效
while True:
    t1 = time.time()
    frames = pipeline.wait_for_frames()
    img = frames.get_color_frame()
    img = np.asanyarray(img.get_data())
    img1 = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # 这个可以用来可视化 R G B 吗 ？
    dst = np.hstack((img, img1))
    rgb_img = img

    depth = frames.get_depth_frame()
    depth_image = np.asanyarray(depth.get_data())  # 这个颜色非常的僵硬，看不清，所以转一下
    depth_image_matrix = depth_image * depth_scale
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), 2)

    print("================> frame update GAP = ", time.time() - t1)
    _height = depth_image_matrix.shape[0]
    _width = depth_image_matrix.shape[1]
    _height2 = rgb_img.shape[0]
    _width2 = rgb_img.shape[1]
    print(f"=====acquired D-frame has shape {_height} * {_width} and rgb-frame has shape {_height2} * {_width2}")
    object_box1 = depth_image_matrix[200:210, 100:120].astype(float)
    no_depth_area1 = round(np.count_nonzero(object_box1 < distance_min) / object_box1.size, 2)
    dist1 = compute_mean(object_box1)
    print(f"=====acquired img dist at [200:210, 100:120] is {dist1}, and no_depth area is {no_depth_area1}%")

    if vis:
        cv2.namedWindow('RGB')
        cv2.namedWindow('Depth')
        cv2.imshow('RGB', rgb_img)
        cv2.imshow('Depth', depth_colormap)
        key = cv2.waitKey(1)
