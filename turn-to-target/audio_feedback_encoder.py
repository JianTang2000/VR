# -*- encoding: utf-8 -*-
# turn-2-target test, 根据当前IMU的angle 和 target angle 的差，生成 不同类型的 cues 反馈 播放
# 需要 material 文件夹下的 wav音频文件
# 需要 根据主机IP更改IP

import win32com.client
from flask_cors import CORS
from gevent import pywsgi
from flask import Flask, request, Response
import jsonpickle
import time
import math
from openal import *
from openal.al import *
from queue import Queue
import threading
import random

app = Flask(__name__)
CORS(app, resources=r'/*')
# #######################这部分是超参数#########################
ip = str("192.168.0.102")  # IP 和 Unity 所在主机 IP要一致
port = str(8211)  # port 和 Unity 侧请求的port要一致
feedback_mod = "continuous spatial cues"  # 3种反馈方式选一种
# feedback_mod = "continuous verbal"
# feedback_mod = "once verbal"
angle_error = 2.5  # 误差在此范围内则认为已经对齐
reached_distance = 0.5  # 距离在次距离内则认为已经到达了目标
cue_sleep_gap = 0.05  # 单位为秒, spatial cues model下,这里休眠的越小，则播放的audio频率越高
list_angles = [34, 30, 20, 10, -10, -20, -30, -34, 34, 30, 20, 10, -10, -20, -30, -34, 34, 30, 20, 10, -10, -20, -30, -34]
# ###############################################################
said_once = False
directions = ["左", "右", "前", "后", "左前", "右前", "左后", "右后"]
# spatial cues 正弦波声
source300 = oalOpen("../materials/300.wav")  # 对应direction 3
source500 = oalOpen("../materials/500.wav")  # 对应direction 2
source700 = oalOpen("../materials/700.wav")  # 对应direction 1
source1100 = oalOpen("../materials/1100.wav")  # 对应direction 0
_listener = oalGetListener()


def play_by_distance(lr_direction, listener, source1, distance=1):
    """
    发出 spatial 声音 通用 function
    lr_direction  -90左边, +90右边, 0 中间
    """
    _el = 0  # 永远在水平面
    _distance = distance
    _az = - lr_direction  # pyopenal中，x负数在右边，而 xyz2AZEL 中负数在左边，所以换一下符号  # _az 》0 在左边
    # play by pyOpenAL
    openal_z = _distance * math.cos(math.radians(_el)) * math.cos(math.radians(_az))
    openal_y = _distance * math.sin(math.radians(_el))
    openal_x = _distance * math.cos(math.radians(_el)) * math.sin(math.radians(_az))
    listener.move_to((openal_x, openal_y, openal_z))
    source1.play()
    while source1.get_state() == AL_PLAYING:
        time.sleep(cue_sleep_gap)  # spatial cues model下,这里休眠的越小，则播放的audio频率越高


def play_by_angle(player_rotation_y, direction_lr, angle, remaining_distance, speak_thread):
    """
    当路距离 <= 0.5时 足够接近物体，直接提示 已到达，目的地在XX角度 ” ;
    距离还比较远时，根绝 feedback mod 生成相应的audio feedback 并播放
    :param player_rotation_y: player 当前 heading
    :param direction_lr: 目标点 方位
    :param angle:  目标点 角度
    :param remaining_distance:  目标点距离
    :param speak_thread: 发声线程
    :return:
    """
    global said_once
    if remaining_distance <= reached_distance:
        if abs(float(angle)) <= angle_error:
            speak_thread.Speak(f"arrived, target in front of you.")
            return
        else:
            speak_thread.Speak(f"arrived, target on your {direction_lr.strip()} side.")
            return
    else:
        if feedback_mod == "continuous spatial cues":
            if abs(float(angle)) <= angle_error:
                play_by_distance(0, _listener, source300)
                return
            else:
                side_int = -90 if direction_lr.strip() == "left" else 90
                play_by_distance(side_int, _listener, source700)
                return

        elif feedback_mod == "continuous verbal":
            if abs(float(angle)) <= angle_error:
                speak_thread.Speak(f"ahead")
                return
            else:
                spoken_context = direction_lr.strip() + f", {int(float(angle))} degrees"
                speak_thread.Speak(spoken_context)
                return
        else:
            if not said_once:
                if abs(float(angle)) <= angle_error:
                    speak_thread.Speak(f"ahead")
                    said_once = True
                    return
                else:
                    spoken_context = direction_lr.strip() + f", {int(float(angle))} degrees"
                    speak_thread.Speak(spoken_context)
                    said_once = True
                    return


def nav_play(player_position, steering_target, player_rotation_y, remaining_distance, corners_length, direction, speak_thread):
    direction_lr = direction.split(" ")[1]  # # 9.999968 right
    angle = direction.split(" ")[0]
    player_rotation_y = float(player_rotation_y)
    remaining_distance = float(remaining_distance)
    corners_length = int(corners_length)
    player_position = player_position.strip(')(').split(',')  # (0.1, 1.0, 4.8)
    steering_target = steering_target.strip(')(').split(',')  # (0.0, 1.0, 2.3)
    print(f"angle = {angle}, direction = {direction_lr}, player yaw = {player_rotation_y}, remaining dis = {remaining_distance}")
    play_by_angle(player_rotation_y, direction_lr, angle, remaining_distance, speak_thread)


def consume_stream2(threadName, qq1, speak_thread):
    while True:
        try:
            if not qq1.empty():
                context_1 = qq1.get()
                player_position = context_1[0]
                steering_target = context_1[1]
                player_rotation_y = context_1[2]
                remaining_distance = context_1[3]
                corners_length = context_1[4]
                direction = context_1[5]  # 9.999968 right
                nav_play(player_position, steering_target, player_rotation_y, remaining_distance, corners_length, direction, speak_thread)
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
        self.speak_thread = win32com.client.Dispatch('SAPI.SPVOICE')

    def run(self):
        print('消费线程启动了......')
        consume_stream2(self.name, self.qq1, self.speak_thread)


qq = Queue(2)


@app.route('/userInterface', methods=["POST"])
def detect():
    r = request
    player_position = r.form["player_position"]
    steering_target = r.form["steering_target"]
    player_rotation_y = r.form["player_rotation_y"]
    remaining_distance = r.form["remaining_distance"]
    corners_length = r.form["corners_length"]
    direction = r.form["direction"]
    # print("++++++++++++++ direction is ", direction)
    context_1 = [player_position, steering_target, player_rotation_y, remaining_distance, corners_length, direction]
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
    random.shuffle(list_angles)
    print(list_angles)
    speak_main = win32com.client.Dispatch('SAPI.SPVOICE')
    speak_main.Speak('程序开始运行!')  # 这两行必须有,不然speak会报错
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
