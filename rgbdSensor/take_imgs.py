"""
获取RGBD sensor img 制作图片数据集
"""
import os
import time

import cv2
import numpy as np

import alignedRgbdAcquisition


def save_video(video_dir='1115-10-40-rgb.avi', ir_dir='1115-10-40-ir.avi'):
    fps = 30
    img_size = (1280, 720)
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    videoWriter = cv2.VideoWriter(video_dir, fourcc, fps, img_size)
    videoWriter_ir = cv2.VideoWriter(ir_dir, fourcc, fps, img_size, 0)  # 灰色
    count = 0
    max_count = 30 * 60 * 2
    while count < max_count:
        print(f"saving at {count} / {max_count} ")
        _color_image, _, _, _, ir = alignedRgbdAcquisition.get_img_depth_ir(align_ir=True)
        videoWriter.write(_color_image)
        videoWriter_ir.write(ir)
        count += 1
    videoWriter.release()
    videoWriter_ir.release()


def save_single_img(desc="-fu-20"):
    """
    desc="-fu-20"
    desc="-yang-20"
    desc="-ping-20"
    """
    count = 0
    _color_image, _depth_colormap, _depth_image_matrix, ir_image, aligned_ir_image = alignedRgbdAcquisition.get_img_depth_ir(align_ir=True)
    # 8秒弹框展示时间，在这段时间里对齐物体
    while count < 30 * 8:
        _color_image, _depth_colormap, _depth_image_matrix, ir_image, aligned_ir_image = alignedRgbdAcquisition.get_img_depth_ir(align_ir=True)
        cv2.namedWindow('RGB')
        cv2.imshow('RGB', _color_image)
        key = cv2.waitKey(1)
        count += 1
    print("  start to take img ! ... ")
    _color_image, _depth_colormap, _depth_image_matrix, ir_image, aligned_ir_image = alignedRgbdAcquisition.get_img_depth_ir(align_ir=True)
    date = time.strftime("%Y-%m-%d-%H-%M-%S")  # 每秒存一次
    rgb_name = "0-rgb-" + str(date) + "-" + str(desc) + ".jpg"
    depth_rgb_name = "1-depthRGB-" + str(date) + "-" + str(desc) + ".jpg"
    depth_name = "2-depth-" + str(date) + "-" + str(desc) + ".npy"
    ir_name = "3-ir-" + str(date) + "-" + str(desc) + ".npy"
    AlignedIR_name = "4-AlignedIR-" + str(date) + "-" + str(desc) + ".npy"
    cv2.imwrite(rgb_name, _color_image)
    cv2.imwrite(depth_rgb_name, _depth_colormap)
    np.save(depth_name, _depth_image_matrix)
    np.save(ir_name, ir_image)
    np.save(AlignedIR_name, aligned_ir_image)


def save_img():
    """每间隔一秒存一张图"""
    save_dir = r"C:\Users\jt\OneDrive\SJTU\7data\indoor-scene\1111-private"
    count_current = 0
    while True:
        count_current += 1
        _color_image, _depth_colormap, _depth_image_matrix, ir_image, aligned_ir_image = alignedRgbdAcquisition.get_img_depth_ir(align_ir=True)
        date = time.strftime("%Y-%m-%d-%H-%M-%S")  # 每秒存一次
        rgb_name = "0-rgb-" + str(date) + "-" + str(count_current) + ".jpg"
        depth_rgb_name = "1-depthRGB-" + str(date) + "-" + str(count_current) + ".jpg"
        depth_name = "2-depth-" + str(date) + "-" + str(count_current) + ".npy"
        ir_name = "3-ir-" + str(date) + "-" + str(count_current) + ".npy"
        AlignedIR_name = "4-AlignedIR-" + str(date) + "-" + str(count_current) + ".npy"
        cv2.imwrite(os.path.join(save_dir, rgb_name), _color_image)
        cv2.imwrite(os.path.join(save_dir, depth_rgb_name), _depth_colormap)
        np.save(os.path.join(save_dir, depth_name), _depth_image_matrix)
        np.save(os.path.join(save_dir, ir_name), ir_image)
        np.save(os.path.join(save_dir, AlignedIR_name), aligned_ir_image)
        print("current at ", count_current)
        cv2.namedWindow('RGB')
        cv2.imshow('RGB', _color_image)
        key = cv2.waitKey(1)
        time.sleep(0.92)


if __name__ == "__main__":
    save_img()
    # save_single_img(desc="-fu-20")
    # save_video(video_dir='1115-10-40-rgb.avi', ir_dir='1115-10-40-ir.avi')
