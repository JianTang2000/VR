# -*- encoding: utf-8 -*-
"""
此代码运行在 机器人 robot上
人亲自移动

1 先启动 本脚本 ,这时没有audio产生,
2 再启动 Unity （RGBsender.cs） & IMU_motion_controller.py,
    audio发声 和 IMU_motion_controller 将几乎同时开始工作
    Object detection 得到角度差，播放声音，人转动
"""
import sys

sys.path.append(r"../../..")
sys.path.append(r"../..")
sys.path.append(r"..")

from flask_cors import CORS
from gevent import pywsgi
from flask import Flask, request, Response
import jsonpickle
import time
from queue import Queue
import threading
import numpy as np
import cv2
import torch
import datetime

from turnToTarget.visual_virtual_robot import virtual_robot_controller
from turnToTarget.imu_method import audio_feedback_encoder

app = Flask(__name__)
CORS(app, resources=r'/*')
# #######################这部分是超参数#########################
ip = str("192.168.0.105")  #
port = str(8211)  # port 和 Unity 侧请求的port要一致
target_obj_id = virtual_robot_controller.target_obj_id
img_size = virtual_robot_controller.img_size
# feedback mod 等其他超参 在 audio_feedback_encoder.py中修改
# ###############################################################
qq = Queue(1)


def human_nav_play(cv2_rgb, v5_model_ins):
    results = v5_model_ins(cv2_rgb, size=img_size)
    direction = virtual_robot_controller.post_process_angle(results, target_obj_id)  # "10.8 right"
    if direction is None:
        return
    direction_lr = direction.split(" ")[1]
    angle = direction.split(" ")[0]
    print(f"==== post-process result is angle = {angle} on the {direction_lr}")
    audio_feedback_encoder.play_by_angle(None, direction_lr, angle)


def consume_stream2(threadName, qq1, v5_model_ins, only_vis=False, vis_and_save=True):
    count_save_num = 0
    while True:
        try:
            if not qq1.empty():
                context_1 = qq1.get()
                rgb_str = context_1[0]
                # convert string data to numpy array
                np_img = np.fromstring(rgb_str, np.uint8)
                # convert numpy array to image
                cv2_rgb = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
                if only_vis:
                    cv2.namedWindow('RGB')
                    cv2.imshow('RGB', cv2_rgb)
                    key = cv2.waitKey(1)
                elif vis_and_save:
                    date = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')
                    name = str(date).replace(",", "-") + "-" + str(count_save_num) + ".jpg"
                    cv2.imwrite(name, cv2_rgb)
                else:
                    human_nav_play(cv2_rgb, v5_model_ins)
        except RuntimeError:
            print(threadName, "queue1 error occurs and skip for next frame!")
            raise NotImplementedError


class myThread2(threading.Thread):
    """
    一个子线程,用Queue存储Unity侧的反馈，由于两端速率不一致，Queue会自动扔掉旧数据，保证目前get到的都是新数据
    """

    def __init__(self, threadID, name, qq1):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.qq1 = qq1
        # self.model = torch.hub.load(r'C:\Users\jt\Desktop\work\yolov5', 'custom',
        #                             path=r'C:\Users\jt\Desktop\data\weights\exp62-n-PureVirtual-300-train+100 test\weights\best.pt',
        #                             source='local',
        #                             device='cpu')
        self.model = torch.hub.load('/home/pi/jian/yolov5', 'custom',
                                    path='/home/pi/jian/weights/exp62-n-PureVirtual-300-train+100 test/weights/best.pt',
                                    source='local', force_reload=True,
                                    device='cpu')

    def run(self):
        print('消费线程启动了......')
        consume_stream2(self.name, self.qq1, self.model)


@app.route('/userInterface', methods=["POST"])
def detect():
    r = request
    rgb_str = request.files['rgb'].read()
    context_1 = [rgb_str]
    if qq.full():
        qq.get()
        qq.put(context_1)
    else:
        qq.put(context_1)
    # build a response dict to send back to client
    # encode response using jsonpickle
    response = {'message': 'data received'}
    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")


if __name__ == '__main__':
    thread11 = myThread2(11, "thread_get_queue_cam", qq)
    thread11.start()

    print('===========================================================================')
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print('===================================================================================')
    print('=========server start running at: ', now, '=========')
    print('=========IP + Port    =   ', ip, ':', port, '=========')
    print('============================ ready to fly =========================================')
    server = pywsgi.WSGIServer((ip, int(port)), app)
    server.serve_forever()
