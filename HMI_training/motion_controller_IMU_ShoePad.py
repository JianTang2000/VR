"""
Sensor data acquisition
Model inference
Send motion commands
"""

import torch
from torchvision import transforms
import torch.nn as nn
import time
import numpy as np
import serial
from threading import Thread

from util import UdpComms as U
import IMU.core as imu

sock = U.UdpComms(udpIP="192.168.0.110", portTX=8000, portRX=8001, enableRX=True, suppressWarnings=True)
motion_command = ["forward", "stop"]
use_shoe_and_IMU = True
use_IMU_only = False  # 纯转向仅需要 IMU


def sen_msg(msg):
    print(f"sending msg {msg}......")
    sock.SendData(str(msg))  # Send this string to other application


class V1_Backbone(nn.Module):
    def __init__(self):
        super(V1_Backbone, self).__init__()

        self.first_layers = nn.Sequential(
            nn.Conv2d(1, 50, kernel_size=(1, 5), stride=1, padding="valid"),
            nn.BatchNorm2d(50),
            nn.ReLU(),
            nn.Conv2d(50, 50, (1, 3), 1, padding="same"),
            nn.BatchNorm2d(50),
            nn.ReLU(),

            # nn.Linear(4608, 50),
            nn.MaxPool2d(1, 2),
            nn.Dropout(p=0.2),

            nn.Conv2d(50, 40, (1, 5), stride=1, padding="valid"),
            nn.ReLU(),
            # nn.BatchNorm2d(40),
            # nn.Linear(4608, 50),
            nn.MaxPool2d(1, 2),
            nn.Dropout(p=0.2),

            nn.Conv2d(40, 20, (1, 3), stride=1, padding="valid"),
            # nn.BatchNorm2d(40),
            nn.ReLU(),
            nn.Dropout(p=0.2),
        )

        self.sec_layers = nn.Sequential(
            nn.Linear(300, 200),
            nn.Dropout(p=0.4),
            nn.Linear(200, 50),
            nn.Dropout(p=0.4),
        )

    def forward(self, _input):
        x = self.first_layers(_input)
        x = x.view(x.size()[0], -1)
        x = self.sec_layers(x)
        return x


class V1_Net(V1_Backbone):
    def __init__(self):
        super().__init__()
        self.lin3 = nn.Linear(50, 2)

    def forward(self, inp):
        x = super().forward(inp)
        x = self.lin3(x)
        return x


class V1:
    def __init__(self):
        # self.device = torch.device("cuda:0")
        self.device = torch.device("cpu")
        self.model = torch.load(r'../materials/85_best.pkl', map_location='cpu')
        self.model.eval()

    def predict_img(self, input_data):
        """
        input_data : insure it has shape = 20*30
        """
        input_data = transforms.ToTensor()(input_data)
        input_data = torch.unsqueeze(input_data, dim=0)
        inputs = input_data.to(self.device, dtype=torch.float)
        outputs = self.model(inputs)
        _, preds = torch.max(outputs.data, 1)
        ret = preds.cpu().numpy()
        return ret


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


if __name__ == "__main__":
    deviceName_left = "COM9"  # 鞋垫串口
    total_time = 30
    port = "COM7"  # windows
    # port = "/dev/ttyUSB0"  # linux
    baudrate = 921600
    if use_IMU_only:
        try:
            hf_imu = serial.Serial(port=port, baudrate=baudrate, timeout=0.5)
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
            imu_thread = ImuThread("imu_thread", hf_imu)
            imu_thread.setDaemon(True)  # 子线程会与当前线程一起关闭
            imu_thread.start()
        # 保持 IMU 线程存活
        while True:
            time.sleep(10)
    if use_shoe_and_IMU:
        try:
            v1 = V1()
            hf_imu = serial.Serial(port=port, baudrate=baudrate, timeout=0.5)
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
            imu_thread = ImuThread("imu_thread", hf_imu)
            imu_thread.setDaemon(True)  # 子线程会与当前线程一起关闭
            imu_thread.start()
            # 启动鞋垫+IMU数据收集,每采集30长度送进网络一次
            s_left = serial.Serial(deviceName_left, 115200, timeout=1.0)
            time.sleep(1)
            while True:
                left_data = []
                IMU_data = []  # 存放成 12*N的形式
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
                                # get one IMU data when one shoePad data collected!
                                tmp_imu_data = imu.get_one_data(hf_imu)
                                IMU_data.append(",".join(tmp_imu_data))
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
                                # get one IMU data when one shoePad data collected!
                                tmp_imu_data = imu.get_one_data(hf_imu)
                                IMU_data.append(",".join(tmp_imu_data))

                                ad_ls_2 = []
                                for i in range(23, 39, 2):
                                    ad = byte_ls_left[i][2:] + byte_ls_left[i + 1][2:]  # 获取AD值
                                    ad_ls_2.append(ad)
                                # f_left.write(",".join(ad_ls_2) + "\n")
                                left_data.append(",".join(ad_ls_2))
                                # get one IMU data when one shoePad data collected!
                                tmp_imu_data = imu.get_one_data(hf_imu)
                                IMU_data.append(",".join(tmp_imu_data))
                                current_time += 2
                        except Exception:
                            print("something wrong and skip...")
                            continue
                assert len(left_data) is 30
                assert len(IMU_data) is 30
                print(f"collect one IMU+shoe data cost {time.time() - t1_s} ,send to network and UDP sender")
                # 拼成网络输入的格式
                for i in left_data:
                    if i != "":
                        f1 = int(i.split(",")[0])
                        f2 = int(i.split(",")[1])
                        f3 = int(i.split(",")[2])
                        f4 = int(i.split(",")[3])
                        f5 = int(i.split(",")[4])
                        f6 = int(i.split(",")[5])
                        f7 = int(i.split(",")[6])
                        f8 = int(i.split(",")[7])
                for i in IMU_data:
                    if i != "":
                        f9 = float(i.split(",")[0])
                        f10 = float(i.split(",")[1])
                        f11 = float(i.split(",")[2])
                        f12 = float(i.split(",")[3])
                        f13 = float(i.split(",")[4])
                        f14 = float(i.split(",")[5])
                        f15 = float(i.split(",")[6])
                        f16 = float(i.split(",")[7])
                        f17 = float(i.split(",")[8])
                        f18 = float(i.split(",")[9])
                        f19 = float(i.split(",")[10])
                        f20 = float(i.split(",")[11])
                i_data_class = np.vstack([f1, f2, f3, f4, f5, f6, f7, f8, f9, f10,
                                          f11, f12, f13, f14, f15, f16, f17, f18, f19, f20])  # shape = (8+12)*30
                res = v1.predict_img(i_data_class)
                sen_msg(motion_command[int(res[0])])
