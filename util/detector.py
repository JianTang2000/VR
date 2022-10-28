# import time
#
# import torch
# import cv2
#
# # Model
# model = torch.hub.load('/home/pi/VR-blind/yolov5', 'custom',
#                        path='/home/pi/VR-blind/yolov5/exp62-n-PureVirtual-300-train+100-test/weights/best.pt',
#                        source='local',
#                        device='cpu')
#
# # Images
# imgs = cv2.imread(r"vr-data/2022-10-22-16-21-52-0.jpg")
#
# # Inference
# while True:
#     t1 = time.time()
#     results = model(imgs, size=256)
#     ret_tensor = results.xyxy
#     ret = ret_tensor[0].numpy()
#     print(f"========> time cost is : {time.time() - t1}")

# Speed: 631.5ms pre-process, 19.2ms inference, 1.6ms NMS per image at shape (2, 3, 640, 640)


import time

import torch
import cv2

# Model
model = torch.hub.load(r'C:\Users\jiant\Desktop\code\yolov5', 'custom',
                       path=r'C:\Users\jiant\Desktop\data\V&R-objectDetectionData\results\exp62-n-PureVirtual-300-train+100-test\weights\best.pt',
                       source='local',
                       device='cpu')

# Images
imgs = cv2.imread(r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\train-on-server\figX-pure-virtual-train-884\images\train\0930_v_1_167.jpg")

# Inference
while True:
    t1 = time.time()
    results = model(imgs, size=256)
    ret_tensor = results.xyxy
    ret = ret_tensor[0].numpy()
    print(f"========> time cost is : {time.time() - t1}")

# Speed: 631.5ms pre-process, 19.2ms inference, 1.6ms NMS per image at shape (2, 3, 640, 640)
