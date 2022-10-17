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
import IMU.core as imu  # 这行需要更改,并且其中的串口名称也需要与具体设备适配

print(f"串口打开成功，准备加载数据")
sock = U.UdpComms(udpIP="192.168.0.110", portTX=8000, portRX=8001, enableRX=True, suppressWarnings=True)
motion_command = ["backward", "forward", "stop"]
use_shoe = False  # 是否使用鞋垫 (纯转向仅需要 IMU)
use_IMU = True  # 是否使用鞋垫 (纯转向仅需要 IMU)


def sen_msg(msg):
    print(f"sending msg {msg}......")
    sock.SendData(str(msg))  # Send this string to other application


class V1_Backbone(nn.Module):
    def __init__(self):
        super(V1_Backbone, self).__init__()

        self.first_layers = nn.Sequential(
            nn.Conv2d(1, 50, kernel_size=(1, 5), stride=1, padding="valid"),
            # nn.BatchNorm2d(50),
            nn.ReLU(),
            nn.Conv2d(50, 50, (1, 3), 1, padding="same"),
            # nn.BatchNorm2d(50),
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
            nn.Linear(320, 200),
            nn.Dropout(p=0.4),
        )

    def forward(self, input):
        x = self.first_layers(input)
        x = x.view(x.size()[0], -1)
        x = self.sec_layers(x)
        return x


class V1_Net(V1_Backbone):
    def __init__(self):
        super().__init__()
        self.lin3 = nn.Linear(200, 3)

    def forward(self, inp):
        x = super().forward(inp)
        x = self.lin3(x)
        return x


class V1:
    def __init__(self):
        # self.device = torch.device("cuda:0")
        self.device = torch.device("cpu")
        self.model = torch.load(r'../materials/best_184e_50_0818.pkl', map_location='cpu')
        self.model.eval()

    def predict_img(self, input_data):
        """
        input_data : insure it has shape = 8*50
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


def getSerialData(_s_left):
    start_time = time.time()
    data_1s = [[], [], [], [], [], [], [], []]
    count = 0
    while count < 50:
        received_data_left = _s_left.read(_s_left.inWaiting())
        if not received_data_left == "":
            try:
                byte_ls_left = [hex(int(i)) for i in received_data_left]

                if len(byte_ls_left) == 20:
                    ad_ls = []
                    for i in range(3, 19, 2):
                        ad = byte_ls_left[i][2:] + byte_ls_left[i + 1][2:]  # 获取AD值
                        ad_ls.append(float(ad))
                    for i in range(8):
                        data_1s[i].append(ad_ls[i])
                    count += 1

                if len(byte_ls_left) == 40:
                    ad_ls = []
                    for i in range(3, 19, 2):
                        ad = byte_ls_left[i][2:] + byte_ls_left[i + 1][2:]  # 获取AD值
                        ad_ls.append(float(ad))
                    for i in range(8):
                        data_1s[i].append(ad_ls[i])
                    count += 1
                    if count < 50:
                        ad_ls_2 = []
                        for i in range(23, 39, 2):
                            ad = byte_ls_left[i][2:] + byte_ls_left[i + 1][2:]  # 获取AD值
                            ad_ls_2.append(float(ad))
                        for i in range(8):
                            data_1s[i].append(ad_ls_2[i])
                        count += 1
            except Exception:
                continue
        time.sleep(interval_time)
    middle_time = time.time()
    if len(data_1s[0]) == 50:
        # print("收集+处理数据时间:"+str(middle_time-start_time))
        return np.vstack(data_1s)
    else:
        return -1


class ImuThread(Thread):
    def __init__(self, thread_name):
        super(ImuThread, self).__init__(name=thread_name)
        self.previous_yaw = None

    def run(self) -> None:
        time.sleep(3)
        print("IMU子线程启动")
        while use_IMU:
            yaw = imu.get_current_yaw()
            # print("航向角:" + str(yaw))
            current_yaw = yaw
            spin_msg = get_spin(self.previous_yaw, current_yaw)  # 获取这一次里是该左/右/不转
            self.previous_yaw = current_yaw
            sen_msg(spin_msg)
            time.sleep(0.1)


if __name__ == "__main__":
    if use_IMU:
        imu_thread = ImuThread("imu_thread")
        imu_thread.setDaemon(True)  # 子线程会与当前线程一起关闭
        imu_thread.start()
    if use_shoe:
        deviceName_left = "COM9"  # 鞋垫串口
        hz = 50  # 赫兹
        interval_time = 1 / hz
        s_left = serial.Serial(deviceName_left, 115200, timeout=1.0)
        time.sleep(1)
        v1 = V1()
        while True:
            data_ls = getSerialData(s_left)
            res = v1.predict_img(data_ls)
            sen_msg(motion_command[int(res[0])])
            # sen_msg(motion_command[int(2)])
    else:
        while True:
            time.sleep(10)
