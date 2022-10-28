import cv2
import os
import numpy as np
import matplotlib.pyplot as plt


def variance_of_laplacian(img):
    # compute the Laplacian of the image and then return the focus
    # measure, which is simply the variance of the Laplacian
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # score_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    score_var = cv2.Laplacian(gray, cv2.CV_8U, ksize=3).var()
    # score_var = cv2.Laplacian(gray, cv2.CV_16S, ksize=3).var()
    return round(score_var, 4)


def hist_var():
    var_vague = []
    vague_imgs = os.listdir(r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\labeled\00selected-to-use-V&R-5-classes-no-man\tmp\classification\vague")
    for file in vague_imgs:
        full_path = os.path.join(r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\labeled\00selected-to-use-V&R-5-classes-no-man\tmp\classification\vague", file)
        img_file = cv2.imread(full_path)
        var_vague.append(variance_of_laplacian(img_file))
    print(var_vague)
    print(f"min value of vague var is {min(var_vague)}")
    print(f"max value of vague var is {max(var_vague)}")

    var_clear = []
    clear_imgs = os.listdir(r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\labeled\00selected-to-use-V&R-5-classes-no-man\tmp\classification\clear")
    for file in clear_imgs:
        full_path = os.path.join(r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\labeled\00selected-to-use-V&R-5-classes-no-man\tmp\classification\clear", file)
        img_file = cv2.imread(full_path)
        var_clear.append(variance_of_laplacian(img_file))
    print(var_clear)
    print(f"min value of clear var is {min(var_clear)}")
    print(f"max value of clear var is {max(var_clear)}")

    _var_vague = [i for i in var_vague if i < 200]
    _var_clear = [i for i in var_clear if i < 200]
    print(f"{len(_var_vague) / len(var_vague)} % vague imgs var smaller than 200")
    print(f"{len(_var_clear) / len(var_clear)} % vague imgs var smaller than 200")

    __var_vague = [i for i in _var_vague if i < 50]
    __var_clear = [i for i in _var_clear if i < 50]
    print(f"{len(__var_vague) / len(_var_vague)} % vague imgs var smaller than 50")
    print(f"{len(__var_clear) / len(_var_clear)} % vague imgs var smaller than 50")

    plt.hist(_var_vague, bins=50, alpha=0.5, label='var_vague')
    plt.hist(_var_clear, bins=50, alpha=0.5, label='var_clear')
    plt.legend(loc='upper right')
    plt.show()


def hist_var2():
    var_vague = []
    vague_imgs = os.listdir(r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\labeled\00selected-to-use-V&R-5-classes-no-man\tmp\classification2\vague")
    for file in vague_imgs:
        full_path = os.path.join(r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\labeled\00selected-to-use-V&R-5-classes-no-man\tmp\classification2\vague", file)
        img_file = cv2.imread(full_path)
        var_vague.append(variance_of_laplacian(img_file))
    print(var_vague)
    print(f"min value of vague var is {min(var_vague)}")
    print(f"max value of vague var is {max(var_vague)}")

    var_clear = []
    clear_imgs = os.listdir(r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\labeled\00selected-to-use-V&R-5-classes-no-man\tmp\classification2\clear")
    for file in clear_imgs:
        full_path = os.path.join(r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\labeled\00selected-to-use-V&R-5-classes-no-man\tmp\classification2\clear", file)
        img_file = cv2.imread(full_path)
        var_clear.append(variance_of_laplacian(img_file))
    print(var_clear)
    print(f"min value of clear var is {min(var_clear)}")
    print(f"max value of clear var is {max(var_clear)}")

    _var_vague = [i for i in var_vague if i < 200]
    _var_clear = [i for i in var_clear if i < 200]
    print(f"{len(_var_vague) / len(var_vague)} % vague imgs var smaller than 200")
    print(f"{len(_var_clear) / len(var_clear)} % vague imgs var smaller than 200")

    __var_vague = [i for i in _var_vague if i < 60]
    __var_clear = [i for i in _var_clear if i < 60]
    print(f"{len(__var_vague) / len(_var_vague)} % vague imgs var smaller than 60")
    print(f"{len(__var_clear) / len(_var_clear)} % vague imgs var smaller than 60")

    plt.hist(_var_vague, bins=50, alpha=0.5, label='var_vague')
    plt.hist(_var_clear, bins=50, alpha=0.5, label='var_clear')
    plt.legend(loc='upper right')
    plt.show()


def write_var_score():
    files = os.listdir(r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\labeled\00selected-to-use-V&R-5-classes-no-man\tmp\classification\clear")
    for f in files:
        img = cv2.imread(os.path.join(r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\labeled\00selected-to-use-V&R-5-classes-no-man\tmp\classification\clear", f))
        var_score = variance_of_laplacian(img)
        txt = str(var_score)
        cv2.putText(img, txt, (100, 80), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 100, 100), 4)  # 大小，颜色，粗细
        file_full_path = os.path.join(r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\labeled\00selected-to-use-V&R-5-classes-no-man\tmp2\classification\clear", f)
        cv2.imwrite(file_full_path, img)


if __name__ == "__main__":
    # test_img = cv2.imread(r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\labeled\00selected-to-use-V&R-5-classes-no-man/1003-paper-1-98.jpg")
    # print(variance_of_laplacian(test_img))
    hist_var()
    # hist_var2()
    # write_var_score()
