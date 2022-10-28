"""
获取RGBD sensor img 制作图片数据集
"""
import cv2
import time
from rgbdSensor import alignedRgbdAcquisition

date = time.strftime("%Y-%m-%d-%H-%M-%S-%f")
print(f"collecting imgs to build dataset at {str(date)}")
count = 0
while count < 1000:
    count += 1
    date = time.strftime("%Y-%m-%d-%H-%M-%S-%f")
    name = str(date) + "-Num-" + str(count) + ".jpg"
    _color_image, _depth_colormap, _depth_image_matrix = alignedRgbdAcquisition.get_img_depth()
    cv2.imwrite(name, _color_image)
    print(f"{count} / 1000")
