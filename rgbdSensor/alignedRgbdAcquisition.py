# -*- encoding: utf-8 -*-
"""
aligned-rgbd-acquisition-fps-test.py
测试硬件设备在all不同变量组合下的表现
=====变量：img_size    -- edit about line-47 to change img_size
1 640, 360   -- 更小的设备不支持了
2 960, 540
3 1280, 720
=====变量：电源
1  type-c 33w 5V-3A 直插供电
2  电池 12.0V 11.5 11 11 10.5   ---再低就要机器人就要充电了
=====变量：操作系统
1  Ubuntu 20.04.5 LTS   -- 这个经典的的操作系统
2  Raspberry Pi OS   -- 机器人用的这个操作系统
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

# config.enable_stream(rs.stream.depth, 640, 360, rs.format.z16, 30)
# config.enable_stream(rs.stream.depth, 640, 360, rs.format.z16, 30)
config.enable_stream(rs.stream.depth, 640, 360, rs.format.z16, 30)

config.enable_stream(rs.stream.color, 640, 360, rs.format.bgr8, 30)
# config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
# config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)


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

# Create an align object
# rs.align allows us to perform alignment of depth frames to others frames
# The "align_to" is the stream type to which we plan to align depth frames.
align_to = rs.stream.color
align = rs.align(align_to)


def get_img_depth():
    """
    实时获取当前的RGB和depth图；
    像素级别对齐
    返回: 彩色图 720*1280*3 ;彩色深度图 720*1280*3;矩阵形式的深度信息图 720*1280(黑白)（也可以可视化）（乘以了scale所以是距离值）
    """
    # Get frameset of color and depth
    frames = pipeline.wait_for_frames()
    # Align the depth frame to color frame
    aligned_frames = align.process(frames)
    # Get aligned frames
    aligned_depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
    color_frame = aligned_frames.get_color_frame()
    # Validate that both frames are valid
    if not aligned_depth_frame or not color_frame:
        print("depth or RGB input not found!")

    # compute distance to a pixel
    depth_image = np.asanyarray(aligned_depth_frame.get_data())
    depth_image_matrix = depth_image * depth_scale
    color_image = np.asanyarray(color_frame.get_data())

    # depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), 2)
    # 彩色图  ,  彩色深度图 3,  矩阵形式的深度信息图 720*1280(黑白)（也可以可视化）（乘以了scale所以是距离值）
    # 边界（双目测距无法检查的位置）没有深度信息，是黑色，深度数值为0
    return color_image, depth_colormap, depth_image_matrix


def main():
    """
    640, 480 -- img size
    """
    distance_min = 0.12  # 小于该值的深度值应等于0,即此处深度计算失效
    vis = True
    while True:
        t1 = time.time()
        _color_image, _depth_colormap, _depth_image_matrix = get_img_depth()
        print("================> frame update GAP = ", time.time() - t1)
        # cv2.line(_color_image, (320, 0), (320, 480), (0, 255, 0), 2)
        _height = _depth_image_matrix.shape[0]
        _width = _depth_image_matrix.shape[1]
        print(f"=====acquired img has shape {_height} * {_width}==================================")
        object_box1 = _depth_image_matrix[200:210, 100:120].astype(float)
        no_depth_area1 = round(np.count_nonzero(object_box1 < distance_min) / object_box1.size, 2)
        dist1 = compute_mean(object_box1)
        print(f"=====acquired img dist at [200:210, 100:120] is {dist1}, and no_depth area is {no_depth_area1}%")
        if vis:
            cv2.namedWindow('RGB')
            cv2.namedWindow('Depth')
            cv2.imshow('RGB', _color_image)
            cv2.imshow('Depth', _depth_colormap)
            key = cv2.waitKey(1)


def compute_mean(array_in, N=2):
    """
    计算 array_in (ndarray) 中 非零 元素的均值 , 保留 N 位小数
    """
    exist = (array_in != 0)
    mean_value = array_in.sum() / exist.sum()
    return round(mean_value, N)


if __name__ == "__main__":
    main()
