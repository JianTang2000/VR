#!/usr/bin/env python
# -*- coding:utf-8 -*-
import serial
import struct
import math
import platform
import serial.tools.list_ports
import time

from IMU import core

# shoePad
test_time = 3  # 测试总时间以秒为单位
hz = 50  # 鞋垫赫兹
total_time = test_time * hz
deviceName_left = "COM9"
deviceName_right = "COM4"
IMU_port = "COM7"
baudrate = 921600
left_file = r"../materials/jt_0826_IMU&ShoePad_stand_1.txt"
right_file = "../materials/jt_0825_test_stand_1.txt"
left_data = []
right_data = []
IMU_data = []  # 存放成 12*N的形式

if __name__ == "__main__":
    """
    HZ = 50
    ideal time cost = 20s
    total_time = 1000
    data collect done! now saving data...
    time cost is  32.9069550037384s
    so real performance is : sample 30 points in 1 second
    """

    current_time = 0
    # 打开串口
    s_left = serial.Serial(deviceName_left, 115200, timeout=1.0)
    # s_right = serial.Serial(deviceName_right, 115200, timeout=1.0)
    time.sleep(1)
    try:
        hf_imu = serial.Serial(port=IMU_port, baudrate=baudrate, timeout=0.5)
        if hf_imu.isOpen():
            print("serial open success...")
        else:
            hf_imu.open()
            print("serial open success...")
    except Exception as e:
        print("Exception:" + str(e))
        print("serial open fail")
        exit(0)
    else:
        t1_s = time.time()
        while current_time < total_time:
            # collect shoePad & IMU data {total_time} times
            # 接受到的数据，左右脚分别解析
            received_data_left = s_left.read(s_left.inWaiting())
            # received_data_right = s_right.read(s_right.inWaiting())
            received_data_right = 0
            if not (received_data_left == "" and received_data_right == ""):
                try:
                    # 每个字节分离开来
                    byte_ls_left = [hex(int(i)) for i in received_data_left]
                    # byte_ls_right = [hex(int(i)) for i in received_data_right]
                    # print(str(len(byte_ls_left)) + "《========》" + str(byte_ls_left))
                    # print("#####################################################################")
                    # print(byte_ls_right)
                    # print("0000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
                    # 有效的数据记录
                    if len(byte_ls_left) == 20:
                        ad_ls = []
                        for i in range(3, 19, 2):
                            ad = byte_ls_left[i][2:] + byte_ls_left[i + 1][2:]  # 获取AD值
                            ad_ls.append(ad)
                        # f_left.write(",".join(ad_ls) + "\n")
                        left_data.append(",".join(ad_ls))
                        # get one IMU data when one shoePad data collected!
                        tmp_imu_data = core.get_one_data(hf_imu)
                        IMU_data.append(",".join(tmp_imu_data))
                        # print current process...
                        current_time += 1
                        if current_time % 100 == 0:
                            print(current_time)

                    # 长度为两倍也认为是有效的数据，原因是程序处理需要一定时间，然而sleep_time就已经和串口的频率统一了，因此有可能一次有两个数据需要等待处理
                    if len(byte_ls_left) == 40:
                        ad_ls = []
                        for i in range(3, 19, 2):
                            ad = byte_ls_left[i][2:] + byte_ls_left[i + 1][2:]  # 获取AD值
                            ad_ls.append(ad)
                        # f_left.write(",".join(ad_ls) + "\n")
                        left_data.append(",".join(ad_ls))
                        # get one IMU data when one shoePad data collected!
                        tmp_imu_data = core.get_one_data(hf_imu)
                        IMU_data.append(",".join(tmp_imu_data))

                        ad_ls_2 = []
                        for i in range(23, 39, 2):
                            ad = byte_ls_left[i][2:] + byte_ls_left[i + 1][2:]  # 获取AD值
                            ad_ls_2.append(ad)
                        # f_left.write(",".join(ad_ls_2) + "\n")
                        left_data.append(",".join(ad_ls_2))
                        # get one IMU data when one shoePad data collected!
                        tmp_imu_data = core.get_one_data(hf_imu)
                        IMU_data.append(",".join(tmp_imu_data))
                        current_time += 2
                        if current_time % 100 == 0:
                            print(current_time)

                    # 右脚同理
                    '''
                    if len(byte_ls_right) == 20:
                        ad_ls = []
                        for i in range(3, 19, 2):
                            ad = byte_ls_right[i][2:] + byte_ls_right[i + 1][2:]  # 获取AD值
                            ad_ls.append(ad)
                        f_right.write(",".join(ad_ls) + "\n")

                    if len(byte_ls_right) == 40:
                        ad_ls = []
                        for i in range(3, 19, 2):
                            ad = byte_ls_right[i][2:] + byte_ls_right[i + 1][2:]  # 获取AD值
                            ad_ls.append(ad)
                        f_right.write(",".join(ad_ls) + "\n")
                        ad_ls_2 = []
                        for i in range(23, 39, 2):
                            ad = byte_ls_right[i][2:] + byte_ls_right[i + 1][2:]  # 获取AD值
                            ad_ls_2.append(ad)
                        f_right.write(",".join(ad_ls_2) + "\n")
                    '''
                except Exception:
                    print("something wrong and skip...")
                    continue
        print("data collect done! now saving data...")
        print("ideal time cost is ", test_time)
        print("time cost is ", time.time() - t1_s)
        f_left = open(left_file, 'w+')
        assert len(left_data) == len(IMU_data)
        for i in range(len(IMU_data)):
            line_i = left_data[i] + "," + IMU_data[i] + "\n"
            f_left.write(line_i)
        f_left.close()
        print("Done for everything!")
