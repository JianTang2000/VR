import math
import time
from openal import *
import numpy as np


def random_true(prob):
    p = ([prob, 1 - prob])
    return np.random.choice([True, False], p=p)


def compute_mean(array_in, N=2):
    """
    计算 array_in (ndarray) 中 非零 元素的均值 , 保留 N 位小数
    """
    exist = (array_in != 0)
    mean_value = array_in.sum() / exist.sum()
    return round(mean_value, N)


def compute_mean_min(array_in, min_v, N=2):
    """
    计算 array_in (ndarray) 中 > min_v 元素的均值 , 保留 N 位小数
    """
    exist = (array_in >= min_v)
    _a = array_in[exist].sum()
    _b = exist.sum()
    mean_value = _a / _b
    return round(mean_value, N)


def pi_format(degree: float):
    """
    角度转弧度 , 如 90° = 1/2 pi
    """
    # math.degrees(x)
    return math.radians(degree)


def play_by_direction(lr_direction, listener, source1, sleep_time=0.15):
    """
    lr_direction  -90左边, +90右边
    """
    _el = 0  # 永远在水平面,只考虑水平面
    _distance = 1  # 距离恒定，没有距离变化效应
    _az = - lr_direction  # pyopenal中，x负数在右边，而 xyz2AZEL 中负数在左边，所以换一下符号  #_az>0在左边
    # play by pyOpenAL
    openal_z = _distance * math.cos(pi_format(_el)) * math.cos(pi_format(_az))
    openal_y = _distance * math.sin(pi_format(_el))
    openal_x = _distance * math.cos(pi_format(_el)) * math.sin(pi_format(_az))
    listener.move_to((openal_x, openal_y, openal_z))
    source1.play()
    while source1.get_state() == AL_PLAYING:
        time.sleep(sleep_time)  # 放完睡眠一个时间


if __name__ == "__main__":
    list1 = [1, 1, 1, 1, 1, 1]
    list2 = [0.3, 1, 1, 1, 1, 1]
    a = np.vstack([list1, list2])
    print(a)
    print(a.shape)
    print(compute_mean_min(a, 0.4))
