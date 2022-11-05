# 讲四通道的图存入TIFF格式的图片种
import numpy as np
import cv2
import tifffile

#
img = cv2.imread(r"C:\Users\jiant\Desktop\data\indoor-scene\Multimodal\noDot\NightStrongLight\rgb-2022-11-04-22-39-17-24.jpg")
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # BGR -> RGB
depth = np.load(r"C:\Users\jiant\Desktop\data\indoor-scene\Multimodal\noDot\NightStrongLight\depth-2022-11-04-22-39-17-24.npy")
IR = np.load(r"C:\Users\jiant\Desktop\data\indoor-scene\Multimodal\noDot\NightStrongLight\AlignedIR-2022-11-04-22-39-17-24.npy")
depth = np.expand_dims(depth, axis=2)
# IR = np.expand_dims(IR, axis=2)
# channel5 = np.concatenate((img, depth, IR), axis=2)
channel4 = np.concatenate((img, depth), axis=2)
print(123)

tifffile.imwrite('temp.tif', channel4)
