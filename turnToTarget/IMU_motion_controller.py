# -*- encoding: utf-8 -*-
"""
先启动 audio encoder ,这时没有audio产生, 再启动 Unity & IMU controller, audio 和 yaw controller 几乎同时开始工作
IMU 读取 heading 并控制 Unity player 转动, 这个运动控制在多种测试中是通用的
启动-- 初始化角度归零 -- 用IMU监控user的实时heading, 并发送yaw到Unity
IMU初始化角度归零要热启动，也就是先插线，然后启动个几次 （中间不要抽掉线）,充分的完整自我矫正之后。 再开始正式的测试。
"""

import time
import serial
from threading import Thread
from statistics import mean

# custom packages
from util import UdpComms as U
import IMU.core as imu  # 这行需要更改,并且其中的串口名称也需要与具体设备适配

# #######################这部分是超参数#########################

sock = U.UdpComms(udpIP="127.0.0.1", portTX=8000, portRX=8001, enableRX=True, suppressWarnings=True)  # 发送到Unity, IP写Unity 所在主机IP
IMU_port = "COM7"  # windows
IMU_baudrate = 921600


# ###############################################################
def sen_msg(msg):
    print(f"sending msg {msg}......")
    sock.SendData(str(msg))  # Send this string to other application


class ImuThread(Thread):
    def __init__(self, thread_name):
        super(ImuThread, self).__init__(name=thread_name)
        self.previous_yaw = None
        self.count_100 = 0  # 用来初始化归零 简单的说就是取前100个值均值为原点
        self.init_yaw = False  # 用来初始化归零
        self.yaw_start_value = None  # 用来初始化归零

    def run(self) -> None:
        time.sleep(0.5)  # 稍微等待一下, 保证 audio feedback 和 motion controller 同时开始工作
        print("IMU子线程启动...")
        port = IMU_port  # IMU硬件端口和波特率
        baudrate = IMU_baudrate  # IMU硬件端口和波特率
        try:
            _hf_imu = serial.Serial(port=port, baudrate=baudrate, timeout=0.5)
            if _hf_imu.isOpen():
                print("serial open success...")
            else:
                _hf_imu.open()
                print("serial open success...")
        except Exception as e:
            print("Exception:" + str(e))
            print("serial open fail")
            exit(0)
        else:
            yaw_init_list = []
            while True:
                _tmp_imu_data = imu.get_one_data(_hf_imu)
                # print(f"time cost for get one data is  {time.time() - t1} and yaw is ---- {_tmp_imu_data[8]} -----", )
                yaw = round(float(_tmp_imu_data[8]), 4)
                if self.count_100 <= 100:
                    yaw_init_list.append(yaw)
                    self.count_100 += 1
                    continue
                else:
                    if not self.init_yaw:
                        self.yaw_start_value = mean(yaw_init_list[50:])
                        self.init_yaw = True
                        continue
                    else:
                        spin_msg = "yaw_" + str(yaw - self.yaw_start_value)  # 这个报文结构在Unity UPD 接收段会有特定的解析代码
                        self.previous_yaw = yaw
                        sen_msg(spin_msg)
                        time.sleep(0.05)  # IMU 频率很高,没必要这么高的速率，这里控制到 20 FPS


if __name__ == "__main__":
    imu_thread = ImuThread("imu_thread")
    imu_thread.setDaemon(True)  # 子线程会与当前线程一起关闭
    imu_thread.start()
    while True:
        time.sleep(100)  # 保持主线程活着，不然子线程跟着挂了
