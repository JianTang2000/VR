#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
采集鞋垫数据以训练模型
"""
import time
import serial
import struct
import platform
import math
import serial.tools.list_ports

test_time = 60  # 测试总时间以秒为单位
hz = 100  # 赫兹
total_time = test_time * hz
deviceName_left = "COM3"
deviceName_right = "COM4"
left_file = r"../materials/jt_0825_test_left.txt"
right_file = "../materials/jt_0825_test_right.txt"
left_data = []
right_data = []


# 每次打开串口都会覆盖写之前的数据，慎重！
def collect_shoe_data():
    current_time = 0
    # 打开串口
    s_left = serial.Serial(deviceName_left, 115200, timeout=1.0)
    # s_right = serial.Serial(deviceName_right, 115200, timeout=1.0)
    time.sleep(1)
    # 开始读取数据
    while current_time < total_time:
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
                    left_data.append(",".join(ad_ls) + "\n")
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
                    left_data.append(",".join(ad_ls) + "\n")
                    ad_ls_2 = []
                    for i in range(23, 39, 2):
                        ad = byte_ls_left[i][2:] + byte_ls_left[i + 1][2:]  # 获取AD值
                        ad_ls_2.append(ad)
                    # f_left.write(",".join(ad_ls_2) + "\n")
                    left_data.append(",".join(ad_ls_2) + "\n")
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

        # time.sleep(interval_time)
    print("saving data...")
    f_left = open(left_file, 'w+')
    for i in left_data:
        f_left.write(i)
    f_left.close()
    print("Done!")


if __name__ == "__main__":
    t1 = time.time()
    collect_shoe_data()
    print("time cost for data collection is ", time.time() - t1)
