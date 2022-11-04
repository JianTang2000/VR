# -*- encoding: utf-8 -*-
"""
获取 RGB depth 和 IR 但是不要求对齐,对齐操作耗费计算资源,不对齐速度会快很多
"""

import time
import pyrealsense2 as rs
import numpy as np
import cv2

# #############################
open_dot = 1  # 红外圆形投影模式开关, 0关掉 1打开
# #############################
pipeline = rs.pipeline()
config = rs.config()
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

depth_sensor = device.query_sensors()[0]
if depth_sensor.supports(rs.option.emitter_enabled):
    depth_sensor.set_option(rs.option.emitter_enabled, open_dot)

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.depth, 640, 360, rs.format.z16, 30)
# config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)

config.enable_stream(rs.stream.color, 640, 360, rs.format.bgr8, 30)
# config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
# config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
config.enable_stream(rs.stream.infrared, 640, 360)  # 启动IR支持

# Start streaming
profile = pipeline.start(config)

# Getting the depth sensor's depth scale (see rs-align example for explanation)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print("Depth Scale is: ", depth_scale)


def compute_mean(array_in, N=6):
    """
    计算 array_in (ndarray) 中 非零 元素的均值 , 保留 N 位小数
    """
    exist = (array_in != 0)
    mean_value = array_in.sum() / exist.sum()
    return round(mean_value, N)


def get_img_depth_ir():
    frames = pipeline.wait_for_frames()
    img = frames.get_color_frame()  # 这里img是一个realsens的class
    img = np.asanyarray(img.get_data())  # 这里img是一个ndarray 比如 720*1280*3
    rgb_img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # img是BGR格式,不利于可视化,转成RGB

    depth = frames.get_depth_frame()
    depth_image = np.asanyarray(depth.get_data())
    depth_image_matrix = depth_image * depth_scale
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), 2)

    ir_frame = frames.first(rs.stream.infrared)  # 获取到IR帧
    ir_image = np.asanyarray(ir_frame.get_data())

    return rgb_img, depth_colormap, depth_image_matrix, ir_image


def main():
    distance_min = 0.12  # 小于该值的深度值应等于0,即此处深度计算失效
    vis = True
    first_print = False
    rectangle_color = (0, 155, 50)  # 黑色 (0, 0, 0)
    txt_color = (0, 255, 127)
    while True:
        t1 = time.time()
        _color_image, _depth_colormap, _depth_image_matrix, ir_image = get_img_depth_ir()
        if not first_print:
            print("================> frame update GAP = ", time.time() - t1)
            _height = _depth_image_matrix.shape[0]
            _width = _depth_image_matrix.shape[1]
            print(f"=====acquired img has shape {_height} * {_width}==================================")
            first_print = True
        # 在这里修改矩形框位置
        x_min = 300
        x_max = 400
        y_min = 200
        y_max = 300
        object_box1 = _depth_image_matrix[y_min:y_max, x_min:x_max].astype(float)
        no_depth_area1 = round(np.count_nonzero(object_box1 < distance_min) / object_box1.size, 2)
        dist1 = compute_mean(object_box1)
        print(f"=====acquired img dist at specific area is {dist1}, and no_depth area is {no_depth_area1}%")
        if vis:
            cv2.line(_color_image, (320, 0), (320, 360), (0, 222, 10), 2)
            cv2.line(_color_image, (0, 180), (640, 180), (0, 222, 10), 2)
            cv2.rectangle(_color_image, (x_min, y_min), (x_max, y_max), rectangle_color, 2)
            cv2.rectangle(_depth_colormap, (x_min, y_min), (x_max, y_max), rectangle_color, 2)
            txt = "distance = " + str(dist1)
            cv2.putText(_color_image, txt, (x_min - 5, y_min - 5), 0, 1, txt_color, 2, 4)
            cv2.putText(_depth_colormap, txt, (x_min - 5, y_min - 5), 0, 1, txt_color, 2, 4)
            cv2.namedWindow('RGB')
            cv2.namedWindow('Depth')
            cv2.namedWindow('ir')
            cv2.imshow('ir', ir_image)
            cv2.imshow('RGB', _color_image)
            cv2.imshow('Depth', _depth_colormap)
            key = cv2.waitKey(1)


if __name__ == "__main__":
    main()
