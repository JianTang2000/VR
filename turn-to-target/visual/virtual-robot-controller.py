# -*- encoding: utf-8 -*-
# 此代码运行在 机器人 robot上！
# 从Unity拿到 virtual robot 的视野画面+当前heading
# 用Object detection (raspberry 上) 检查画面中的target，
# 计算target的angle和robot heading 的差值
# 根据 差值 发送运动指令到Unity直到对齐，同时播放声音

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

angle_error = 2.5  # 误差在此范围内则认为已经对齐
reached_distance = 0.5  # 距离在次距离内则认为已经到达了目标

use_audio_feedback = True
feedback_mod = "continuous spatial cues"  # 3种反馈方式选一种
# feedback_mod = "continuous verbal"
# feedback_mod = "once verbal"
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
