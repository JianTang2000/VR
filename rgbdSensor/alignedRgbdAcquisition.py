# -*- encoding: utf-8 -*-
"""
深度+RGB对齐获取
"""
import time

import cv2
import numpy as np
import pyrealsense2 as rs

# #############################
open_dot = 1  # 红外圆形投影模式开关, 0关掉 1打开
# img_size_W = 1280
# img_size_H = 720
img_size_W = 1280
img_size_H = 720
# #############################

pipeline = rs.pipeline()
config = rs.config()

pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

depth_sensor = device.query_sensors()[0]
if depth_sensor.supports(rs.option.emitter_enabled):
    depth_sensor.set_option(rs.option.emitter_enabled, open_dot)  # 红外圆形投影模式开关, 0关掉 1打开

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

# config.enable_stream(rs.stream.depth, 640, 360, rs.format.z16, 30)
config.enable_stream(rs.stream.depth, img_size_W, img_size_H, rs.format.z16, 30)

# config.enable_stream(rs.stream.color, 640, 360, rs.format.bgr8, 30)
# config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
config.enable_stream(rs.stream.color, img_size_W, img_size_H, rs.format.bgr8, 30)
config.enable_stream(rs.stream.infrared)  # 启动IR支持

# Start streaming
profile = pipeline.start(config)
# Getting the depth sensor's depth scale (see rs-align example for explanation)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print("Depth Scale is: ", depth_scale)

# Create an align object
align_to = rs.stream.color
align = rs.align(align_to)


def compute_mean(array_in, N=6):
    """
    计算 array_in (ndarray) 中 非零 元素的均值 , 保留 N 位小数
    """
    exist = (array_in != 0)
    mean_value = array_in.sum() / exist.sum()
    return round(mean_value, N)


def get_img_depth():
    """
    实时获取当前的RGB和depth图；
    像素级别对齐
    """
    frames = pipeline.wait_for_frames()
    aligned_frames = align.process(frames)
    aligned_depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
    color_frame = aligned_frames.get_color_frame()
    if not aligned_depth_frame or not color_frame:
        print("depth or RGB input not found!")
    depth_image = np.asanyarray(aligned_depth_frame.get_data())
    depth_image_matrix = depth_image * depth_scale  # 乘以了scale以得到单位为米的距离值 （边界（双目测距无法检查的位置）没有深度信息，是黑色，深度数值为0）
    color_image = np.asanyarray(color_frame.get_data())
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
    return color_image, depth_colormap, depth_image_matrix


def get_img_depth_ir(align_ir=False):
    frames = pipeline.wait_for_frames()
    ir_frame = frames.first(rs.stream.infrared)  # 获取到IR帧
    aligned_frames = align.process(frames)
    aligned_depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
    color_frame = aligned_frames.get_color_frame()
    # ir_frame = aligned_frames.get_infrared_frame() # 这个也没对齐，因为API中不提供IR对齐，要自己弄
    if not aligned_depth_frame or not color_frame or not ir_frame:
        print("depth or RGB or IR input not found!")
    # compute distance to a pixel
    depth_image = np.asanyarray(aligned_depth_frame.get_data())
    depth_image_matrix = depth_image * depth_scale  # 乘以了scale以得到单位为米的距离值 （边界（双目测距无法检查的位置）没有深度信息，是黑色，深度数值为0）
    color_image = np.asanyarray(color_frame.get_data())
    ir_image = np.asanyarray(ir_frame.get_data())
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
    aligned_ir = None
    if align_ir:
        aligned_ir, color_image = align_ir_rgb(ir_image, color_image)
    return color_image, depth_colormap, depth_image_matrix, ir_image, aligned_ir


def align_ir_rgb(ir_input, rgb_input):
    """
    work only for size (360, 640) or (640,1280)
    :param ir_input:
    :param rgb_input:
    :return:aligned ir and rgb
    """
    _height = rgb_input.shape[0]
    _width = rgb_input.shape[1]
    assert _height == 360 or _height == 720
    if _height == 360:
        cut_lef_right = ir_input[:, 86:(640 - 99)]
        cut_up_down = cut_lef_right[51:(360 - 55), :]
        ret_ir = cv2.resize(cut_up_down, dsize=(_width, _height))
    else:
        cut_lef_right = ir_input[:, 171:(1280 - 198)]
        cut_up_down = cut_lef_right[102:(780 - 110), :]
        ret_ir = cv2.resize(cut_up_down, dsize=(_width, _height))
    return ret_ir, rgb_input


def main():
    """实时获取sensor图片并弹框展示"""
    distance_min = 0.12  # 小于该值的深度值应等于0,即此处深度计算失效
    vis = True
    first_print = False
    rectangle_color = (0, 155, 50)  # 黑色 (0, 0, 0)
    txt_color = (0, 255, 127)
    while True:
        # 在这里修改矩形框位置
        x_min = 100
        x_max = 100 + 20
        y_min = 200
        y_max = 200 + 40
        t1 = time.time()
        color_image, depth_colormap, depth_image_matrix, ir_image, aligned_ir = get_img_depth_ir(align_ir=True)
        if not first_print:
            print("================> frame update GAP = ", time.time() - t1)
            _height = depth_image_matrix.shape[0]
            _width = depth_image_matrix.shape[1]
            print(f"=====acquired img has shape {_height} * {_width}==================================")
            print(f"mean = {x_max}+{x_min}/2 ={(x_max + x_min) / 2}")
            first_print = True
        object_box1 = depth_image_matrix[y_min:y_max, x_min:x_max].astype(float)
        no_depth_area1 = round(np.count_nonzero(object_box1 < distance_min) / object_box1.size, 2)
        dist1 = compute_mean(object_box1)
        print(dist1)
        # print(f"=====acquired img dist at specific area is {dist1}, and no_depth area is {no_depth_area1}%")
        if vis:
            cv2.line(color_image, (640, 0), (640, 720), (0, 255, 0), 2)
            cv2.line(color_image, (0, 575), (1280, 575), (0, 255, 0), 2)
            cv2.rectangle(color_image, (x_min, y_min), (x_max, y_max), rectangle_color, 2)
            cv2.rectangle(depth_colormap, (x_min, y_min), (x_max, y_max), rectangle_color, 2)
            txt = str(dist1)
            cv2.putText(color_image, txt, (x_min - 10, y_min - 10), 0, 1.5, txt_color, 2, 4)
            cv2.putText(depth_colormap, txt, (x_min - 10, y_min - 10), 0, 1.5, txt_color, 2, 4)

            cv2.namedWindow('RGB')
            cv2.namedWindow('Depth')
            cv2.namedWindow('ir')
            cv2.imshow('ir', aligned_ir)
            cv2.imshow('RGB', color_image)
            cv2.imshow('Depth', depth_colormap)
            key = cv2.waitKey(1)


if __name__ == "__main__":
    main()
