import cv2
import os
from rgbdSensor import alignedStreamNoDot

video_dir = 'yuanqi_video.avi'
# 帧率
fps = 30
# 图片尺寸
img_size = (640, 360)

# fourcc = cv2.cv.CV_FOURCC('M','J','P','G')#opencv2.4
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
videoWriter = cv2.VideoWriter(video_dir, fourcc, fps, img_size)

count = 0
while count < 2000:
    print("saving at ", count)
    _color_image, _, _, _, _ = alignedStreamNoDot.get_img_depth_ir(align_ir=True)
    videoWriter.write(_color_image)
    count += 1

videoWriter.release()
