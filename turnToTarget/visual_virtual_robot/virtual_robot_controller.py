# -*- encoding: utf-8 -*-
"""
此代码运行在 机器人 robot上
虚拟机器人移动,所以不需要启动 IMU_motion_controller.py
1 启动本脚本, 再启动 Unity (RGBsender.cs)


从Unity拿到 virtual robot 的视野画面
用Object detection (raspberry 上) 检查画面中的target，
计算target的angle和 0° 的差值
根据 差值 发送运动指令到Unity直到对齐，同时播放声音
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
from openal import *
from queue import Queue
import threading
import cv2
import numpy as np
import torch

from util import UdpComms as U
from turnToTarget.imu_method import audio_feedback_encoder

app = Flask(__name__)
CORS(app, resources=r'/*')
# #######################这部分是超参数#########################
target_obj_id = 0  # [ 'ball','bed','sofa','chair','couch' ]
img_size = 256
motion_command = ["backward", "forward", "stop", "left", "right"]
sock = U.UdpComms(udpIP="192.168.0.102", portTX=8000, portRX=8001, enableRX=True, suppressWarnings=True)
ip = str("192.168.0.103")  #
port = str(8411)  # port 和 Unity 侧请求的port要一致
feedback_mod = audio_feedback_encoder.feedback_mod
angle_error = audio_feedback_encoder.angle_error
reached_distance = audio_feedback_encoder.reached_distance
# ###############################################################
# spatial cues 正弦波声
source300 = audio_feedback_encoder.source300
source500 = audio_feedback_encoder.source500
source700 = audio_feedback_encoder.source700
source1100 = audio_feedback_encoder.source1100
_listener = oalGetListener()
qq = Queue(2)


def sen_msg(msg):
    print(f"sending msg {msg}......")
    sock.SendData(str(msg))  # Send this string to other application


def post_process_angle(results, obj_id=0):
    """
    找出 第一个 obj_id 物体的角度
    :param results:  a dict
    :param obj_id: 0 / 1 / 2 ...
    :return: "10.8 right"
    """
    xywh = [None for i in range(4)]
    found = False
    results.print()  # or .show(), .save()    # can disable print time cost and prediction
    ret_tensor = results.xywh
    ret_numpy = ret_tensor[0].numpy()
    for pred in ret_numpy:
        conf = float(pred[4])  # 0.98
        class_id = int(pred[5])  # 0,1,2,3
        if class_id == int(obj_id):
            xywh[0] = pred[0]
            xywh[1] = pred[1]
            xywh[2] = pred[2]
            xywh[3] = pred[3]
            found = True
            break
    if not found:
        return None
    w_max = 640  # 1280  # img width
    h_max = 360  # 720  # img height
    az_max = 69.46  # 70
    el_max = 42.63  # 42
    x = (w_max / 2 - xywh[0]) / w_max
    y = (h_max / 2 - xywh[1]) / h_max
    az = round(-az_max * 1 / 2 * 2 * x, 2)  # -(左边) , 0 中间 +(right)
    el = round(el_max * 1 / 2 * 2 * y, 2)  # -view_H , view_H(top)
    part_2 = " "
    part_3 = str(abs(az))
    part_1 = "left" if az <= 0 else "right"
    ret = part_3 + part_2 + part_1
    return ret  # "10.8 right"


def play_and_rotate_by_angle(direction_lr, angle, remaining_distance=100):
    """
    当路距离 <= 0.5时 足够接近物体，直接提示 已到达，目的地在XX角度 ” ;
    距离还比较远时，根绝 feedback mod 生成相应的audio feedback 并播放
    :param direction_lr: 目标点 方位
    :param angle:  目标点 角度
    :param remaining_distance:  目标点距离
    :return:
    """
    if remaining_distance <= reached_distance:
        # 这个场景在这里不应该发生
        raise NotImplementedError
    else:
        # 这里用机器人模拟人，假设机器人的反应速度为0且永远做出反应正确
        # 即在听完发声之后马上做出正确的rotating动作(模拟做出反应)--在每一次发声过程中停下等待(模拟倾听)
        abs_angle_float = abs(float(angle))
        if feedback_mod == "continuous spatial cues complex":
            if abs_angle_float <= angle_error:
                audio_feedback_encoder.play_by_distance(0, _listener, source300)  # 播放声音
                sen_msg(motion_command[2])  # ["backward", "forward", "stop", "left", "right"]
                return
            else:
                side_int = -90 if direction_lr.strip() == "left" else 90
                if abs_angle_float > 20:  # 超过一定阈值的改变频率,以便更清晰的区分
                    audio_feedback_encoder.play_by_distance(side_int, _listener, source1100)
                else:
                    audio_feedback_encoder.play_by_distance(side_int, _listener, source700)
                if side_int == -90:
                    sen_msg(motion_command[3])
                else:
                    sen_msg(motion_command[4])
                # 做完转向动作后,sleep一段时间后停下,模拟做一个转向动作需要的时间
                time.sleep(0.3)
                sen_msg(motion_command[2])
                return
        elif feedback_mod == "continuous verbal":
            raise NotImplementedError
        else:
            raise NotImplementedError


def robot_nav_play(cv2_rgb, v5_model_ins):
    results = v5_model_ins(cv2_rgb, size=img_size)
    direction = post_process_angle(results, target_obj_id)  # "10.8 right"
    if direction is None:
        return
    direction_lr = direction.split(" ")[1]
    angle = direction.split(" ")[0]
    print(f"==== post-process result is angle = {angle} on the {direction_lr}")
    play_and_rotate_by_angle(direction_lr, angle)


def consume_stream2(threadName, qq1, v5_model_ins, only_vis=False, vis_and_save=False):
    """
    消费线程的具体动作
    :param threadName:
    :param qq1:
    :param v5_model_ins:
    :param only_vis:  True 时 弹框展示 Unity player 视野RGB 图
    :param vis_and_save: True 时 Unity player 视野RGB 图 存文件
    :return:
    """
    while True:
        try:
            if not qq1.empty():
                context_1 = qq1.get()
                rgb_str = context_1[0]
                # convert string data to numpy array
                np_img = np.fromstring(rgb_str, np.uint8)
                # convert numpy array to image
                cv2_rgb = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
                count = 0
                if only_vis:
                    cv2.namedWindow('RGB')
                    cv2.imshow('RGB', cv2_rgb)
                    key = cv2.waitKey(1)
                elif vis_and_save:
                    date = time.strftime("%Y-%m-%d-%H-%M-%S")
                    name = str(date) + "-" + str(count) + ".jpg"
                    count += 1
                    cv2.imwrite(name, cv2_rgb)
                else:
                    robot_nav_play(cv2_rgb, v5_model_ins)
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
        self.model = torch.hub.load('/home/pi/jian/yolov5',
                                    'custom',
                                    path='/home/pi/jian/weights/exp62-n-PureVirtual-300-train+100 test/weights/best.pt',
                                    source='local',
                                    force_reload=True,
                                    device='cpu')

    def run(self):
        print('子线程启动了......')
        consume_stream2(self.name, self.qq1, self.model)


@app.route('/userInterface', methods=["POST"])
def detect():
    r = request
    # 获取深度图,但这里用不上所以不获取 -- 因为很耗时
    # depth_frame_str = r.form["depth_frame"]
    # depth_frame_ndarray = upsample(depth_frame_str, 640, 360, 5, 5, 0.5)
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
    print('=============================================================================')
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print('======================================================================================')
    print('=========server start running at: ', now, '=========')
    print('=========IP + Port    =   ', ip, ':', port, '=========')
    print('============================ ready to fly ============================================')
    server = pywsgi.WSGIServer((ip, int(port)), app)
    server.serve_forever()
