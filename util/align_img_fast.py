# -*- encoding: utf-8 -*-
"""
获取对齐的 RGB-D 图片
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

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

if device_product_line == 'L500':
    config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
else:
    # config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
    config.enable_stream(rs.stream.color, 640, 360, rs.format.bgr8, 30)  # faster
    # config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)  # 这个 H FOV 会变小 所以不行

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
    rectangle_color = (0, 123, 123)  # 黑色 (0, 0, 0)
    txt_color = (0, 255, 127)
    distance_min = 0.12  # 小于该值的深度值应等于0,即此处深度计算失效
    while True:
        t1 = time.time()
        _color_image, _depth_colormap, _depth_image_matrix = get_img_depth()
        print("frame update GAP = ", time.time() - t1)
        # cv2.line(_color_image, (320, 0), (320, 480), (0, 255, 0), 2)
        print("============================================================")
        print("============================================================")
        _height = _depth_image_matrix.shape[0]
        _width = _depth_image_matrix.shape[1]
        print(f"=====acquired img has shape {_height} * {_width}==================================")

        _y_min_block = 220 - 5  # 矩形区域上方坐标（最上=0，最下=720）
        _y_max_block = 220 + 5  # 矩形区域下方坐标
        method_name(_depth_colormap, _color_image, _depth_image_matrix, distance_min, rectangle_color, txt_color, _y_max_block, _y_min_block)

        if True:
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


def method_name(_depth_colormap, _color_image, _depth_image_matrix, distance_min_, rectangle_color, txt_color, y_max_block_, y_min_block_):
    # distance_min_ = 0.01
    object_box1 = _depth_image_matrix[y_min_block_:y_max_block_, 315:325].astype(float)
    no_depth_area1 = round(np.count_nonzero(object_box1 < distance_min_) / object_box1.size, 2)
    dist1 = compute_mean(object_box1)
    # put info on the img
    cv2.rectangle(_depth_colormap, (315, y_min_block_), (325, y_max_block_), rectangle_color, 1)
    cv2.rectangle(_color_image, (315, y_min_block_), (325, y_max_block_), rectangle_color, 1)
    txt = str(round(dist1, 2)) + "," + str(no_depth_area1)
    cv2.putText(_depth_colormap, txt, (315, int((y_min_block_ + y_max_block_) / 2) - 10), 0, 1.5, txt_color, 2, 4)


if __name__ == "__main__":
    main()
