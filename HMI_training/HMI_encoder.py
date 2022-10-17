"""
接收Unity HTTP发过来的path planning info
encoder 成对应的HMI
播放语言

也可以给 turn-in-space 做响应
"""
import time

from flask_cors import CORS
from gevent import pywsgi
from flask import Flask, request, Response
import jsonpickle
from openal import *
from queue import Queue
import threading
import win32com.client

from util import tools

ip = str("192.168.0.102")
port = str(8211)
app = Flask(__name__)
CORS(app, resources=r'/*')
qq = Queue(1)  # 防止速率不匹配造成的延迟累计
directions = ["左", "右", "前", "后",
              "左前", "右前", "左后", "右后"]
source300 = oalOpen(r"../materials/300.wav")  # 对应direction 3
source500 = oalOpen(r"../materials/500.wav")  # 对应direction 2
source700 = oalOpen(r"../materials/700.wav")  # 对应direction 1
source1100 = oalOpen(r"../materials/1100.wav")  # 对应direction 0
_listener = oalGetListener()


def encoder_and_play(player_position, steering_target, player_rotation_y,
                     remaining_distance, corners_length, direction, speak):
    """
    direction: 下一步的方向信息 50 right / 40 left
    remaining_distance: 终点剩余距离
    当路距离 <= 0.5时 足够接近物体,直接提示已到达,目的地在XX角度
    转向过大时 spoken audio
    otherwise spatial cues
    """
    thred = 5  # 声音在 1/2*thred内即OK
    angle = float(direction.split(" ")[0])
    direction = str(direction.split(" ")[1])
    if direction == "right" and abs(angle - 0) <= thred:
        direction = directions[2]  # 前方
    elif direction == "right" and abs(angle - 180) <= thred:
        direction = directions[3]  # 后方
    elif direction == "right" and angle >= 90:
        direction = directions[7]  # 右后
    elif direction == "right" and angle < 90:
        direction = directions[5]  # 右前
    elif direction == "left" and abs(angle - 0) <= thred:
        direction = directions[2]  # 前方
    elif direction == "left" and abs(angle - 180) <= thred:
        direction = directions[3]  # 后方
    elif direction == "left" and angle >= 90:
        direction = directions[6]  # 左后
    elif direction == "left" and angle < 90:
        direction = directions[4]  # 左前
    else:
        raise ValueError
    if float(remaining_distance) <= 0.5:
        speak.Speak(f"已到达目的地,目的地在您{direction}方")
        return
    else:
        # directions = ["左", "右", "前", "后","左前", "右前", "左后", "右后"]
        if direction == directions[4]:  # "左"
            tools.play_by_direction(-90, _listener, source700)
            return
        if direction == directions[5]:  # "右"
            tools.play_by_direction(90, _listener, source700)
            return
        if direction == directions[2]:  # "前"
            tools.play_by_direction(0, _listener, source300)
            return
        if direction == directions[3]:  # 后方
            speak.Speak(f"请向{direction}转")
            return
        if direction == directions[6]:  # 左后
            speak.Speak(f"请向{direction}转")
            return
        if direction == directions[7]:  # 右后
            speak.Speak(f"请向{direction}转")
            return


def consume_stream(threadName, qq1, speak):
    while True:
        try:
            if not qq1.empty():
                context_1 = qq1.get()
                player_position = context_1[0]
                steering_target = context_1[1]
                player_rotation_y = context_1[2]
                remaining_distance = context_1[3]
                corners_length = context_1[4]
                direction = context_1[5]
                encoder_and_play(player_position, steering_target, player_rotation_y,
                                 remaining_distance, corners_length, direction, speak)
        except RuntimeError:
            print(threadName, "====> consume_stream error occurs and skip to next frame!")


class myThread2(threading.Thread):
    def __init__(self, threadID, name, qq1):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.qq1 = qq1

    def run(self) -> None:
        print('消费线程启动了......')
        speak = win32com.client.Dispatch('SAPI.SPVOICE')
        consume_stream(self.name, self.qq1, speak)


# 192.168.0.101/userInterface
@app.route('/userInterface', methods=["POST"])
def detect():
    r = request
    player_position = r.form["player_position"]
    steering_target = r.form["steering_target"]
    player_rotation_y = r.form["player_rotation_y"]
    remaining_distance = r.form["remaining_distance"]
    corners_length = r.form["corners_length"]
    direction = r.form["direction"]
    print("=============================> direction is ", direction)
    context_1 = [player_position, steering_target, player_rotation_y, remaining_distance, corners_length, direction]
    if qq.full():
        qq.get()
        qq.put(context_1)
    else:
        qq.put(context_1)
    # build a response dict to send back to client
    response = {'message': 'data received'}
    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")


def main():
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


if __name__ == "__main__":
    speak = win32com.client.Dispatch('SAPI.SPVOICE')
    speak.Speak('程序开始运行!')  # 这两行必须有,不然speak会报错
    main()
