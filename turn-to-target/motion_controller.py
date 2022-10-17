"""
用IMU 控制 player旋转
"""

import time
import numpy as np
import serial
from threading import Thread
from statistics import mean

from util import UdpComms as U
import IMU.core as imu  # 这行需要更改,并且其中的串口名称也需要与具体设备适配

# IP写Unity UDP IP 和端口
sock = U.UdpComms(udpIP="127.0.0.1", portTX=8000, portRX=8001, enableRX=True, suppressWarnings=True)

motion_command = ["backward", "forward", "stop"]
use_shoe = False  # 是否使用鞋垫
use_IMU = True  # 是否使用鞋垫 (纯转向仅需要 IMU)


def sen_msg(msg):
    print(f"sending msg {msg}......")
    sock.SendData(str(msg))  # Send this string to other application


class ImuThread(Thread):
    def __init__(self, thread_name):
        super(ImuThread, self).__init__(name=thread_name)
        self.previous_yaw = None
        self.count_100 = 0
        self.init_yaw = False
        self.yaw_start_value = None

    def run(self) -> None:
        time.sleep(2)
        print("IMU子线程启动")
        # IMU硬件端口和波特率
        port = "COM3"  # windows
        # port = "/dev/ttyUSB0"  # linux
        baudrate = 921600
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
                        spin_msg = "yaw_" + str(yaw - self.yaw_start_value)
                        self.previous_yaw = yaw
                        sen_msg(spin_msg)
                        time.sleep(0.05)


if __name__ == "__main__":
    if use_IMU:
        imu_thread = ImuThread("imu_thread")
        imu_thread.setDaemon(True)  # 子线程会与当前线程一起关闭
        imu_thread.start()
    if use_shoe:
        raise NotImplementedError
    while True:
        time.sleep(100)
