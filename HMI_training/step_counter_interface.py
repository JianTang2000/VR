"""
Sensor data acquisition
Model inference
Send motion commands
"""

import time
import numpy as np
import serial
from threading import Thread
from util import UdpComms as U
import IMU.core as imu

sock = U.UdpComms(udpIP="192.168.0.102", portTX=8000, portRX=8001, enableRX=True, suppressWarnings=True)
motion_command = ["forward", "stop"]
use_shoe_only = True


def sen_msg(msg):
    print(f"sending msg {msg}......")
    sock.SendData(str(msg))  # Send this string to other application


def get_spin(yaw_1, yaw_2):
    """
    直接返回当前 yaw, unity侧和现实中时刻保持一致的yaw
    :param yaw_1: previous_yaw
    :param yaw_2: current_yaw
    :return:
    """
    return "yaw_" + str(yaw_2)


class ImuThread(Thread):
    def __init__(self, thread_name, imu_ins):
        super(ImuThread, self).__init__(name=thread_name)
        self.previous_yaw = None
        self.imu_ins = imu_ins

    def run(self) -> None:
        while True:
            print("IMU子线程启动")
            try:
                # _hf_imu = serial.Serial(port=port, baudrate=baudrate, timeout=0.5)
                if self.imu_ins.isOpen():
                    print("serial open success...")
                else:
                    self.imu_ins.open()
                    print("serial open success...")
            except Exception as e:
                print("Exception:" + str(e))
                print("serial open fail")
                exit(0)
            else:
                _tmp_imu_data = imu.get_one_data(self.imu_ins)
                # print(f"time cost for get one data is  {time.time() - t1} and yaw is ---- {_tmp_imu_data[8]} -----", )
                # print("航向角:" + str(yaw))
                current_yaw = _tmp_imu_data[8]
                spin_msg = get_spin(self.previous_yaw, current_yaw)  # 获取这一次里是该左/右/不转
                self.previous_yaw = current_yaw
                sen_msg(spin_msg)
                time.sleep(0.1)  # send IMU at 10 Hz


def reshape_list(l):
    """

    :param l: [[1,2,3,4,5,6,7,8],...,[1,2,3,4,5,6,7,8]]  len = 10
    :return:  [[1,1,1,1,1,1,1,1,1,1],...,[1,1,1,1,1,1,1,1,1,1]]  len = 8
    """
    ret = [[], [], [], [], [], [], [], []]
    for i in range(10):
        for j in range(8):
            f_list[j].append(l[i][j])
    return ret


# f_list.shape = (sensor_number, window_size)
def get_foot_lift(in_list, window_size=10, sensor_number=8, threshold=1800):
    """

    :return:   foot lift   foot down   continue lift
    """
    # check the data
    if len(in_list) != sensor_number:
        raise Exception("f_list size should be same with sensor_number")
    for sensor_data in in_list:
        if len(sensor_data) != window_size:
            raise Exception("f_list[i] size should be same with window_size")

    global continue_lift  # 使用全局变量存储前一次的判断信息
    count = 0  # 统计一共有多少颗传感器满足要求

    for sensor_data in in_list:
        below_threshold = True
        for ad_value in sensor_data:
            if ad_value > threshold:
                below_threshold = False
                break
        if below_threshold:
            count += 1

    if count > sensor_number * 0.75 and not continue_lift:
        continue_lift = True
        print("foot lift")
        return "foot lift"
    elif count <= sensor_number * 0.75:
        continue_lift = False
        # print("foot down")
        return "foot down"

    return "continue lift"


if __name__ == "__main__":
    continue_lift = False  # 使用全局变量存储前一次的判断信息
    # deviceName_left = "/dev/ttyUSB0"  # linux
    deviceName_left = "COM9"  # 鞋垫串口 windows
    total_time = 10  # WINDOW_SIZE = 10
    baudrate = 921600
    if use_shoe_only:
        # 启动鞋垫+IMU数据收集,每采集30长度送进网络一次
        s_left = serial.Serial(deviceName_left, 115200, timeout=1.0)
        time.sleep(1)
        while True:
            left_data = []  # shall be [[8*1]] len = total_time
            current_time = 0
            t1_s = time.time()
            while current_time < total_time:
                received_data_left = s_left.read(s_left.inWaiting())
                received_data_right = 0
                if not (received_data_left == "" and received_data_right == ""):
                    try:
                        byte_ls_left = [hex(int(i)) for i in received_data_left]
                        # 有效的数据记录
                        if len(byte_ls_left) == 20:
                            ad_ls = []
                            for i in range(3, 19, 2):
                                ad = byte_ls_left[i][2:] + byte_ls_left[i + 1][2:]  # 获取AD值
                                ad_ls.append(ad)
                            # f_left.write(",".join(ad_ls) + "\n")
                            left_data.append(",".join(ad_ls))
                            # print current process...
                            current_time += 1
                        # 长度为两倍也认为是有效的数据，原因是程序处理需要一定时间，然而sleep_time就已经和串口的频率统一了，因此有可能一次有两个数据需要等待处理
                        if len(byte_ls_left) == 40:
                            ad_ls = []
                            for i in range(3, 19, 2):
                                ad = byte_ls_left[i][2:] + byte_ls_left[i + 1][2:]  # 获取AD值
                                ad_ls.append(ad)
                            # f_left.write(",".join(ad_ls) + "\n")
                            left_data.append(",".join(ad_ls))

                            ad_ls_2 = []
                            for i in range(23, 39, 2):
                                ad = byte_ls_left[i][2:] + byte_ls_left[i + 1][2:]  # 获取AD值
                                ad_ls_2.append(ad)
                            # f_left.write(",".join(ad_ls_2) + "\n")
                            left_data.append(",".join(ad_ls_2))
                            current_time += 2
                    except Exception:
                        print("something wrong and skip...")
                        continue
            assert len(left_data) is total_time
            print(f"collect one IMU+shoe data cost {time.time() - t1_s} ,send to network and UDP sender")
            # 拼成网络输入的格式
            f_list = reshape_list(left_data)
            pose_str = get_foot_lift(f_list, total_time, len(f_list))  # foot lift   foot down   continue lift
            if pose_str is "foot lift":
                sen_msg(motion_command[0])
