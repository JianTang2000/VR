# 将数据转成ndarray
# 再将ndarray转成TIFF format image 并存文件

import numpy as np
import cv2
import tifffile
import os
from PIL import Image

files = os.listdir(r"C:\Users\jiant\Desktop\data\indoor-scene\Multimodal\noDot\pureRGB")
rgb_files = []
depth_matrix_files = []
for file in files:
    if file.startswith("rgb-") and file.endswith(".jpg"):
        rgb_files.append(file)
for rgb_file in rgb_files:
    name0 = rgb_file.replace("rgb-", "depth-")
    name1 = name0.replace(".jpg", ".npy")
    img_BGR = cv2.imread(os.path.join(r"C:\Users\jiant\Desktop\data\indoor-scene\Multimodal\noDot\pureRGB", rgb_file))
    img_RGB = cv2.cvtColor(img_BGR, cv2.COLOR_BGR2RGB)  # BGR -> RGB
    depth = np.load(os.path.join(r"C:\Users\jiant\Desktop\data\indoor-scene\Multimodal\noDot\NightStrongLight", name1))
    depth_cm = depth * 100  # 在uint16保存格式下，只保留了整数位
    depth_3_channels = np.expand_dims(depth_cm, axis=2)
    new_ndarray_channel4 = np.concatenate((img_RGB, depth_3_channels), axis=2)
    to_save = np.array(new_ndarray_channel4, dtype=np.uint16)
    new_name0 = rgb_file.replace(".jpg", ".tif")
    save_path = os.path.join(r"C:\Users\jiant\Desktop\data\indoor-scene\Multimodal\noDot\tiff", new_name0)
    tifffile.imwrite(save_path, to_save)

# img = cv2.imread(r"C:\Users\jiant\Desktop\data\indoor-scene\Multimodal\noDot\NightStrongLight\rgb-2022-11-04-22-39-17-24.jpg")
# img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # BGR -> RGB
# depth = np.load(r"C:\Users\jiant\Desktop\data\indoor-scene\Multimodal\noDot\NightStrongLight\depth-2022-11-04-22-39-17-24.npy")
# depth = depth * 100
# IR = np.load(r"C:\Users\jiant\Desktop\data\indoor-scene\Multimodal\noDot\NightStrongLight\AlignedIR-2022-11-04-22-39-17-24.npy")
# depth = np.expand_dims(depth, axis=2)
# # IR = np.expand_dims(IR, axis=2)
# # channel5 = np.concatenate((img, depth, IR), axis=2)
# channel4 = np.concatenate((img, depth), axis=2)
# to_save = np.array(channel4, dtype=np.uint16)
# tifffile.imwrite('temp.tif', to_save)
#
# image_stack = tifffile.imread('temp.tif')
# print(image_stack.shape)
# image_stack_cv2 = cv2.imread(r"temp.tif", -1)  # BGR
# print("OK")
#
#
#
# im = Image.open('temp.tif')
# im.verify()  # PIL verify
# print("OK")
#
# #
# # im.verify()  # PIL verify
# # print("OK")


# im = cv2.imread(r"C:\Users\jiant\Desktop\data\indoor-scene\Multimodal\noDot\demoTrain-tiff\images\train\rgb-2022-11-04-22-28-15-459.tif")  # BGR
# im2 = Image.open(r"C:\Users\jiant\Desktop\data\indoor-scene\Multimodal\noDot\pureRGB\rgb-2022-11-04-22-28-16-461.jpg")
# imCV2 = cv2.imread(r"C:\Users\jiant\Desktop\data\indoor-scene\Multimodal\noDot\pureRGB\rgb-2022-11-04-22-28-16-461.jpg")
# imCV2 = cv2.cvtColor(imCV2, cv2.COLOR_BGR2RGB)  # BGR -> RGB
# image_stack = tifffile.imread(r"C:\Users\jiant\Desktop\data\indoor-scene\Multimodal\noDot\demoTrain-tiff\images\train\rgb-2022-11-04-22-28-15-459.tif")
# depth_info = np.load(r"C:\Users\jiant\Desktop\data\indoor-scene\Multimodal\noDot\NightStrongLight\depth-2022-11-04-22-28-16-461.npy")
# print(image_stack[0, 0, :])
# aa = image_stack[:, :, 0:3]
# cv2.imshow('Depth', aa)
# key = cv2.waitKey(-1)
# print("OK")
