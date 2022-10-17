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
    # config.enable_stream(rs.stream.color, 640, 360, rs.format.bgr8, 30)  # faster
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)  # fov smaller

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

    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_OCEAN)
    # 彩色图  ,  彩色深度图 3,  矩阵形式的深度信息图 720*1280(黑白)（也可以可视化）（乘以了scale所以是距离值）
    # 边界（双目测距无法检查的位置）没有深度信息，是黑色，深度数值为0
    return color_image, depth_colormap, depth_image_matrix


def main():
    """
    640, 480 -- img size
    """
    rectangle_color = (0, 0, 0)  # 黑色 (0, 0, 0)
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
        # # 计算某个区域深度block的非零元素的均值
        # _y_min_block = 350 - 10  # 矩形区域上方坐标（最上=0，最下=720）
        # _y_max_block = 350 + 10  # 矩形区域下方坐标
        # method_name(_depth_colormap, _depth_image_matrix, distance_min, rectangle_color, txt_color, _y_max_block, _y_min_block)
        # _y_min_block = 400 - 10  # 矩形区域上方坐标（最上=0，最下=720）
        # _y_max_block = 400 + 10  # 矩形区域下方坐标
        # method_name(_depth_colormap, _depth_image_matrix, distance_min, rectangle_color, txt_color, _y_max_block, _y_min_block)
        # _y_min_block = 450 - 10  # 矩形区域上方坐标（最上=0，最下=720）
        # _y_max_block = 450 + 10  # 矩形区域下方坐标
        # method_name(_depth_colormap, _depth_image_matrix, distance_min, rectangle_color, txt_color, _y_max_block, _y_min_block)
        # show
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


def method_name(_depth_colormap, _depth_image_matrix, distance_min_, rectangle_color, txt_color, y_max_block_, y_min_block_):
    # distance_min_ = 0.01
    object_box1 = _depth_image_matrix[y_min_block_:y_max_block_, 2:89].astype(float)
    # print(object_box1.size)
    no_depth_area1 = round(np.count_nonzero(object_box1 < distance_min_) / object_box1.size, 2)
    dist1 = compute_mean(object_box1)
    object_box2 = _depth_image_matrix[y_min_block_:y_max_block_, 93:180].astype(float)
    no_depth_area2 = round(np.count_nonzero(object_box2 < distance_min_) / object_box2.size, 2)
    dist2 = compute_mean(object_box2)
    object_box3 = _depth_image_matrix[y_min_block_:y_max_block_, 184:271].astype(float)
    no_depth_area3 = round(np.count_nonzero(object_box3 < distance_min_) / object_box3.size, 2)
    dist3 = compute_mean(object_box3)
    object_box4 = _depth_image_matrix[y_min_block_:y_max_block_, 275:362].astype(float)
    no_depth_area4 = round(np.count_nonzero(object_box4 < distance_min_) / object_box4.size, 2)
    dist4 = compute_mean(object_box4)
    object_box5 = _depth_image_matrix[y_min_block_:y_max_block_, 366:453].astype(float)
    no_depth_area5 = round(np.count_nonzero(object_box5 < distance_min_) / object_box5.size, 2)
    dist5 = compute_mean(object_box5)
    object_box6 = _depth_image_matrix[y_min_block_:y_max_block_, 457:544].astype(float)
    no_depth_area6 = round(np.count_nonzero(object_box6 < distance_min_) / object_box6.size, 2)
    dist6 = compute_mean(object_box6)
    object_box7 = _depth_image_matrix[y_min_block_:y_max_block_, 548:638].astype(float)
    no_depth_area7 = round(np.count_nonzero(object_box7 < distance_min_) / object_box7.size, 2)
    dist7 = compute_mean(object_box7)
    print("==>", dist1, dist2, dist3, dist4, dist5, dist6, dist7)
    print("==>", no_depth_area1, no_depth_area2, no_depth_area3, no_depth_area4, no_depth_area5, no_depth_area6, no_depth_area7)
    # put info on the img
    cv2.rectangle(_depth_colormap, (2, y_min_block_), (89, y_max_block_), rectangle_color, 1)
    cv2.rectangle(_depth_colormap, (93, y_min_block_), (180, y_max_block_), rectangle_color, 1)
    cv2.rectangle(_depth_colormap, (184, y_min_block_), (271, y_max_block_), rectangle_color, 1)
    cv2.rectangle(_depth_colormap, (275, y_min_block_), (362, y_max_block_), rectangle_color, 1)
    cv2.rectangle(_depth_colormap, (366, y_min_block_), (453, y_max_block_), rectangle_color, 1)
    cv2.rectangle(_depth_colormap, (457, y_min_block_), (544, y_max_block_), rectangle_color, 1)
    cv2.rectangle(_depth_colormap, (548, y_min_block_), (638, y_max_block_), rectangle_color, 1)
    txt = str(round(dist1, 2)) + "," + str(no_depth_area1)
    cv2.putText(_depth_colormap, txt, (2, int((y_min_block_ + y_max_block_) / 2)), 0, 0.5, txt_color, 1, 4)
    txt = str(round(dist2, 2)) + "," + str(no_depth_area2)
    cv2.putText(_depth_colormap, txt, (93, int((y_min_block_ + y_max_block_) / 2)), 0, 0.5, txt_color, 1, 4)
    txt = str(round(dist3, 2)) + "," + str(no_depth_area3)
    cv2.putText(_depth_colormap, txt, (184, int((y_min_block_ + y_max_block_) / 2)), 0, 0.5, txt_color, 1, 4)
    txt = str(round(dist4, 2)) + "," + str(no_depth_area4)
    cv2.putText(_depth_colormap, txt, (275, int((y_min_block_ + y_max_block_) / 2)), 0, 0.5, txt_color, 1, 4)
    txt = str(round(dist5, 2)) + "," + str(no_depth_area5)
    cv2.putText(_depth_colormap, txt, (366, int((y_min_block_ + y_max_block_) / 2)), 0, 0.5, txt_color, 1, 4)
    txt = str(round(dist6, 2)) + "," + str(no_depth_area6)
    cv2.putText(_depth_colormap, txt, (457, int((y_min_block_ + y_max_block_) / 2)), 0, 0.5, txt_color, 1, 4)
    txt = str(round(dist7, 2)) + "," + str(no_depth_area7)
    cv2.putText(_depth_colormap, txt, (548, int((y_min_block_ + y_max_block_) / 2)), 0, 0.5, txt_color, 1, 4)


if __name__ == "__main__":
    main()
