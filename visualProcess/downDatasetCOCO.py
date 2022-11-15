import argparse
import json
import os
import shutil

import fiftyone as fo
import fiftyone.zoo as foz
import numpy as np
from tqdm import tqdm


def random_true(prob):
    p = ([prob, 1 - prob])
    return np.random.choice([True, False], p=p)


def download_coco():
    dataset = foz.load_zoo_dataset(
        "coco-2017",
        split="train",
        max_samples=50000,
        shuffle=True,
    )

    session = fo.launch_app(dataset)

    dataset = foz.load_zoo_dataset(
        "coco-2017",
        split="train",
        label_types=["detections"],
        classes=["apple", "sandwich", "cup", "bowl", "spoon", "knife", "bottle", "sink", "refrigerator",
                 "dining table", "chair", "couch", "bed", "book", "cell phone", "person", "toilet"],
        max_samples=50000,
    )

    session.dataset = dataset


# json to yolo txt
parser = argparse.ArgumentParser()
parser.add_argument('--json_path', default=r'C:\Users\jiant\fiftyone\coco-2017\train\labels.json', type=str, help="input: coco format(json)")
parser.add_argument('--save_path', default=r'C:\Users\jiant\fiftyone\coco-2017\train\yoloFormat', type=str, help="specify where to save the output dir of labels")
arg = parser.parse_args()

coco_classes_all = ["person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
                    "traffic light",
                    "fire hydrant",
                    "stop sign",
                    "parking meter",
                    "bench",
                    "bird",
                    "cat",
                    "dog",
                    "horse",
                    "sheep",
                    "cow",
                    "elephant",
                    "bear",
                    "zebra",
                    "giraffe",
                    "backpack",
                    "umbrella",
                    "handbag",
                    "tie",
                    "suitcase",
                    "frisbee",
                    "skis",
                    "snowboard",
                    "sports ball",
                    "kite",
                    "baseball bat",
                    "baseball glove",
                    "skateboard",
                    "surfboard",
                    "tennis racket",
                    "bottle",
                    "wine glass",
                    "cup",
                    "fork",
                    "knife",
                    "spoon",
                    "bowl",
                    "banana",
                    "apple",
                    "sandwich",
                    "orange",
                    "broccoli",
                    "carrot",
                    "hot dog",
                    "pizza",
                    "donut",
                    "cake",
                    "chair",
                    "couch",
                    "potted plant",
                    "bed",
                    "dining table",
                    "toilet",
                    "tv",
                    "laptop",
                    "mouse",
                    "remote",
                    "keyboard",
                    "cell phone",
                    "microwave",
                    "oven",
                    "toaster",
                    "sink",
                    "refrigerator",
                    "book",
                    "clock",
                    "vase",
                    "scissors",
                    "teddy bear",
                    "hair drier",
                    "toothbrush"]
wanted_classes = ["apple", "sandwich", "cup", "bowl", "spoon", "knife", "bottle", "sink", "refrigerator",
                  "dining table", "chair", "couch", "bed", "book", "cell phone", "person", "toilet"]
wanted_id = [47, 48, 41, 45, 44, 43, 39, 71, 72, 60, 56, 57, 59, 73, 67, 0, 61]
custom_classes = ["apple", "sandwich", "cup", "bowl", "spoon", "knife", "bottle", "sink", "refrigerator",
                  "table", "chair", "couch", "bed", "cloth", "book", "cell phone", "person", "toilet",
                  "Door handle", "step", "White cane"]
txt_dir_path = r"C:\Users\jiant\fiftyone\coco-2017\train\yoloFormat"
img_dir_path = r"C:\Users\jiant\fiftyone\coco-2017\train\data"
img_save_path = r"C:\Users\jiant\fiftyone\coco-2017\train\yoloFormatIMG"


def convert(size, box):
    dw = 1. / (size[0])
    dh = 1. / (size[1])
    x = box[0] + box[2] / 2.0
    y = box[1] + box[3] / 2.0
    w = box[2]
    h = box[3]

    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)


def extract_coco():
    json_file = arg.json_path  # COCO Object Instance 类型的标注
    ana_txt_save_path = arg.save_path  # 保存的路径

    data = json.load(open(json_file, 'r'))
    if not os.path.exists(ana_txt_save_path):
        os.makedirs(ana_txt_save_path)

    id_map = {}  # coco数据集的id不连续！重新映射一下再输出！
    for i, category in enumerate(data['categories']):
        id_map[category['id']] = i

    # 通过事先建表来降低时间复杂度
    max_id = 0
    for img in data['images']:
        max_id = max(max_id, img['id'])
    img_ann_dict = [[] for i in range(max_id + 1)]
    for i, ann in enumerate(data['annotations']):
        img_ann_dict[ann['image_id']].append(i)

    for img in tqdm(data['images']):
        filename = img["file_name"]
        img_width = img["width"]
        img_height = img["height"]
        img_id = img["id"]
        head, tail = os.path.splitext(filename)
        ana_txt_name = head + ".txt"  # 对应的txt名字，与jpg一致
        f_txt = open(os.path.join(ana_txt_save_path, ana_txt_name), 'w')
        # 这里可以直接查表而无需重复遍历
        for ann_id in img_ann_dict[img_id]:
            ann = data['annotations'][ann_id]
            box = convert((img_width, img_height), ann["bbox"])
            f_txt.write("%s %s %s %s %s\n" % (id_map[ann["category_id"]], box[0], box[1], box[2], box[3]))
        f_txt.close()


def print_obj_id():
    for w in wanted_classes:
        print(coco_classes_all.index(w))


def leave_out_txt():
    """
    把不包括关键物体的txt删掉
    """

    txts = os.listdir(txt_dir_path)
    for txt in txts:
        contains_obj = False
        with open(os.path.join(txt_dir_path, txt)) as f:
            label_i = f.read().split('\n')
            label_i = [i for i in label_i if i != ""]
        for box in label_i:
            id_i = box.split(" ")[0]
            if int(id_i) in wanted_id:
                contains_obj = True
                continue
        if not contains_obj:
            os.remove(os.path.join(txt_dir_path, txt))


def leave_out_boxes():
    txts = os.listdir(txt_dir_path)
    for txt in txts:
        file_data = ""
        with open(os.path.join(txt_dir_path, txt), "r") as f:
            for line in f:
                if int(line.split(" ")[0]) in wanted_id:
                    file_data += line
        with open(os.path.join(txt_dir_path, txt), "w", ) as f:
            f.write(file_data)


def leave_out_txt_hard():
    """
    wanted_classes = ["apple", "sandwich", "cup", "bowl", "spoon", "knife", "bottle", "sink", "refrigerator",
                  "dining table", "chair", "couch", "bed", "book", "cell phone", "person", "toilet"]
    wanted_id = [47, 48, 41, 45, 44, 43, 39, 71, 72, 60, 56, 57, 59, 73, 67, 0, 61]
    一张图中boxes数量超过 15 的扔掉
    """
    txts = os.listdir(txt_dir_path)
    for txt in txts:
        person_count = 0
        with open(os.path.join(txt_dir_path, txt)) as f:
            label_i = f.read().split('\n')
            label_i = [i for i in label_i if i != ""]
        for box in label_i:
            id_i = int(box.split(" ")[0])
            if id_i == 0:
                person_count += 1
        if person_count > 4:
            print("img remove due to person count > 4...")
            os.remove(os.path.join(txt_dir_path, txt))
        elif len(label_i) > 15:
            print("img remove due to boxes count > 15...")
            os.remove(os.path.join(txt_dir_path, txt))
        else:
            if person_count > 2 and len(label_i) <= 5 and random_true(0.8):  # 当全是人的时候
                print("img remove due to person and random ...")
                os.remove(os.path.join(txt_dir_path, txt))


def leave_out_img():
    """
    yoloFormatIMG 该文件夹需要手动新建
    """
    txts = os.listdir(txt_dir_path)
    imgs = os.listdir(img_dir_path)
    for txt in txts:
        if imgs.__contains__(txt.replace(".txt", '.jpg')):
            img_path = os.path.join(img_dir_path, txt.replace(".txt", '.jpg'))
            new_img_path = os.path.join(img_save_path, txt.replace(".txt", '.jpg'))
            shutil.copy(img_path, new_img_path)


def txt_to_custom_txt():
    """
    wanted_classes = ["apple", "sandwich", "cup", "bowl", "spoon", "knife", "bottle", "sink", "refrigerator",
                  "dining table", "chair", "couch", "bed", "book", "cell phone", "person", "toilet"]
    wanted_id = [47, 48, 41, 45, 44, 43, 39, 71, 72, 60, 56, 57, 59, 73, 67, 0, 61]
    """
    txts = os.listdir(txt_dir_path)
    for txt in txts:
        file_data = ""
        tmp = ""
        with open(os.path.join(txt_dir_path, txt), "r") as f:
            for line in f:
                if line != "\n":
                    if line.startswith("47"):
                        tmp = line.replace('47', '0', 1)
                    elif line.startswith("48"):
                        tmp = line.replace('48', '1', 1)
                    elif line.startswith("41"):
                        tmp = line.replace('41', '2', 1)
                    elif line.startswith("45"):
                        tmp = line.replace('45', '3', 1)
                    elif line.startswith("44"):
                        tmp = line.replace('44', '4', 1)
                    elif line.startswith("43"):
                        tmp = line.replace('43', '5', 1)
                    elif line.startswith("39"):
                        tmp = line.replace('39', '6', 1)
                    elif line.startswith("71"):
                        tmp = line.replace('71', '7', 1)
                    elif line.startswith("72"):
                        tmp = line.replace('72', '8', 1)
                    elif line.startswith("60"):
                        tmp = line.replace('60', '9', 1)
                    elif line.startswith("56"):
                        tmp = line.replace('56', '10', 1)
                    elif line.startswith("57"):
                        tmp = line.replace('57', '11', 1)
                    elif line.startswith("59"):
                        tmp = line.replace('59', '12', 1)
                    elif line.startswith("73"):
                        tmp = line.replace('73', '14', 1)
                    elif line.startswith("67"):
                        tmp = line.replace('67', '15', 1)
                    elif line.startswith("0"):
                        tmp = line.replace('0', '16', 1)
                    elif line.startswith("61"):
                        tmp = line.replace('61', '17', 1)
                    else:
                        raise ValueError
                    file_data += tmp

        with open(os.path.join(txt_dir_path, txt), "w", ) as f:
            f.write(file_data)


def summary_boxes():
    """
    这个需要在 txt_to_custom_txt() 之前summary
    """
    txts = os.listdir(txt_dir_path)
    classes_summary = [0 for i in range(len(wanted_classes))]
    for txt in txts:
        # print(txt)
        with open(os.path.join(txt_dir_path, txt), "r") as f:
            for line in f:
                id_int = int(line.split(" ")[0])
                if id_int not in wanted_id:
                    print(f"{txt} has bad id: {id_int}")
                else:
                    classes_summary[wanted_id.index(int(line.split(" ")[0]))] += 1
    print(wanted_classes)
    print(classes_summary)


if __name__ == '__main__':
    download_coco()
    # extract_coco()  # jason to txt
    # print_obj_id()
    # leave_out_txt()  # 删掉不带关键obj的txt
    # leave_out_boxes()  # 删掉不相关obj的boxes
    # leave_out_txt_hard()  # 删掉obj太多太困难的txt
    # leave_out_img()  # 把所有有txt的img放到新文件夹
    # summary_boxes()  # 对obj box 数量进行统计打印
    # txt_to_custom_txt()  # 把coco的classes id 改成自定义的class id
