# imagenet-object-localization-challenge 数据从这里下载
# https://www.kaggle.com/competitions/imagenet-object-localization-challenge/data
# 而不是用代码下载

"""
将.xml转成.txt  结果是相对大小
指定 xml的位置 , 不会对这个路径下的文件进行任何增删改操作
指定 jpg位置, 不会对这个路径下的文件进行任何增删改操作 （只会处理.JPEG图片，且是三通道的照片，其他舍弃）
指定 生成的文件位置 ，会在指定位置生成：次级文件夹/train.txt/test.txt,可直接用于 yolov3/4的训练。还有val 绝对大小,每次rerun自动清空
指定 train/test划分比例， 8/2 开 即  = 0.8     取值 0到1之间，闭区间
指定 空白样本丢弃率 ，对每一个本应生成空白.txtx的样本以一定概率丢弃它们，未丢弃的会继续生成空白.txt。  取值 0到1之间，闭区间
指定 key-value 的dict , 多个类可以指定为同一个数字, 如果某个xml没有dict中定义的关键字,则生成空白.txt ,如果某张.jp没有.xml，则不生成txt

"""
import shutil
import os
import random
from lxml import etree
import numpy as np
import json
from PIL import Image


def random_true(prob):
    p = ([prob, 1 - prob])
    return np.random.choice([True, False], p=p)


def get_xml_text(root, pattern):
    return list(map(lambda x: x.text, root.xpath(pattern)))


def xml_to_txt(path, pic_name, save_dir, abs=True):
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    tree = etree.parse(path)
    root = tree.getroot()
    infos = {}
    for _pattern in ('width', 'height', 'name', 'xmin', 'ymin', 'xmax', 'ymax'):
        pattern = f'//{_pattern}'
        infos[_pattern] = get_xml_text(root, pattern)

    names = infos['name']
    width, height = int(infos['width'][0]), int(infos['height'][0])
    if abs:
        xmins = np.array(list(map(int, infos['xmin']))) / width
        ymins = np.array(list(map(int, infos['ymin']))) / height
        xmaxs = np.array(list(map(int, infos['xmax']))) / width
        ymaxs = np.array(list(map(int, infos['ymax']))) / height
    else:
        xmins = np.array(list(map(int, infos['xmin'])))
        ymins = np.array(list(map(int, infos['ymin'])))
        xmaxs = np.array(list(map(int, infos['xmax'])))
        ymaxs = np.array(list(map(int, infos['ymax'])))

    xs = list(map(lambda x: '%.6f' % x, ((xmaxs + xmins) / 2).tolist()))
    ys = list(map(lambda x: '%.6f' % x, ((ymaxs + ymins) / 2).tolist()))

    ws = list(map(lambda x: '%.6f' % x, ((xmaxs - xmins).tolist())))
    hs = list(map(lambda x: '%.6f' % x, ((ymaxs - ymins).tolist())))

    _names, _xs, _ys, _ws, _hs = [[] for _ in range(5)]
    for i, name in enumerate(names):
        if name in dic:
            _names.append(dic[name])
            _xs.append(xs[i])
            _ys.append(ys[i])
            _ws.append(ws[i])
            _hs.append(hs[i])

    if _names:
        res = np.column_stack((_names, _xs, _ys, _ws, _hs)).tolist()
        res = [' '.join(_res) + '\n' for _res in res]
    else:
        res = ['\n']

    # 以一定比例抛弃空白txt
    if res == ['\n']:
        if random_true(drop_rate):
            with open(os.path.join(save_dir, '{pic_name}.txt'.format(pic_name=pic_name)), 'w') as f:
                f.writelines(res)
        else:
            print('drop')
    else:
        with open(os.path.join(save_dir, '{pic_name}.txt'.format(pic_name=pic_name)), 'w') as f:
            f.writelines(res)
    return res


def good_img(path):
    img = Image.open(path)
    return len(img.split()) == 3


if __name__ == '__main__':

    # ############################## 请手动在这里配置
    # key请写成和XML的key完全一致。如XML中有个标签是person，那么key就写成person
    #   仅仅转换dic中存在的key，XML中存在的其他key不会被转换,如XML中存在person和wheel两类，那么仅仅转换person，忽略wheel
    # value写key对应的数字label。多个key可以对应同一个label
    # classes_id = ["n07930864", "n04263257", "n04597913", "n03658185", "n04557648", "n04070727", "n03201208", "n04099969", "n04344873", "n04350905", "n02992529",
    #               "n04447861"]
    # classes_names = ["cup", "soup bowl", "wooden spoon", "paper knife", "water bottle", "refrigerator", "dining table", "rocking chair", "studio couch", "suit of clothes", "cellphone",
    #                  "toilet seat"]
    # classes_id = ["n03595614", "n04070727", "n02992529"]
    # classes_names = ["T-shirt", "refrigerator", "cellphone"]
    # n04479046 trench coat （风衣）
    dic = {'n04479046': 13}

    # ####请手动在这里配置  img 存放位置
    img_dir = r'C:\Users\jiant\fiftyone\imagenet-object-localization-challenge\ILSVRC\imgs-shoudong'
    # ####请手动在这里配置  xml 存放位置
    anno_dir = r'C:\Users\jiant\fiftyone\imagenet-object-localization-challenge\ILSVRC\xml-shoudong'
    # ####请手动在这里配置  生成文件的目录 （会自动生成次级目录）
    save_path = r'C:\Users\jiant\fiftyone\imagenet-object-localization-challenge\ILSVRC\yoloFormatTxt'

    # 请手动在这里配置 丢弃比例
    # 如果某个xml里没有你需要的key，会生成一个空白的txt，这样的.txt你想保留多少？ 0代表全部不要，1代表全部保留，0.5代表保留50%
    drop_rate = 0
    train_rate = 0.1

    # 生成img存放的位置, jpg和txt都会放在这里，清空已存在（之前run过）生成的历史文件
    img_save_dir = os.path.join(save_path, 'img')
    label_save_dir = os.path.join(save_path, 'label')
    img_val_GT = os.path.join(save_path, 'img_val_GT')
    # img_val_GT  和 val.txt 不相等，是因为 blank sample 的 drop_rate 导致的，属于正常情况

    if not os.path.isdir(img_save_dir):
        os.makedirs(img_save_dir)
    if not os.path.isdir(label_save_dir):
        os.makedirs(label_save_dir)
    if not os.path.isdir(img_val_GT):
        os.makedirs(img_val_GT)

    print("going to delete and then make dir :", img_save_dir)
    shutil.rmtree(img_save_dir)
    os.mkdir(img_save_dir)
    print("going to delete and then make dir :", label_save_dir)
    shutil.rmtree(label_save_dir)
    os.mkdir(label_save_dir)
    print("going to delete and then make dir :", img_val_GT)
    shutil.rmtree(img_val_GT)
    os.mkdir(img_val_GT)
    print("going to delete XXX.txt")
    try:
        os.remove(os.path.join(save_path, 'train.txt'))
    except BaseException:
        print("delete txt failed!, but it is ok if u run this for the first time")
    try:
        os.remove(os.path.join(save_path, 'test.txt'))
    except BaseException:
        print("delete txt failed!, but it is ok if u run this for the first time")
    try:
        os.remove(os.path.join(save_path, 'val.txt'))
    except BaseException:
        print("delete txt failed!, but it is ok if u run this for the first time")
    try:
        os.remove(os.path.join(save_path, 'name.txt'))
    except BaseException:
        print("delete txt failed!, but it is ok if u run this for the first time")

    print("going to check channels...")
    all_files = os.listdir(img_dir)
    bad_files = [i for i in all_files if not good_img(os.path.join(img_dir, i))]
    print("bad img (not 3 channels) number = ", len(bad_files))

    # 找出那些 ! 有xml没jpg 的 和 有jpg没xml的
    img_dir_file = os.listdir(img_dir)
    anno_dir_file = os.listdir(anno_dir)
    img_dir_names = [name.replace('.JPEG', '') for name in img_dir_file if name.endswith('.JPEG')]
    anno_dir_names = [name.replace('.xml', '') for name in anno_dir_file if name.endswith('.xml')]
    good_set_have_img_xml_no_end = set(img_dir_names) & set(anno_dir_names)
    good_set_have_img_xml = [i + ".JPEG" for i in good_set_have_img_xml_no_end if True]
    print("good img (have_img_xml) number = ", len(good_set_have_img_xml))

    # 把all img 拷贝到存放位置
    print("copying img...")
    fileName1 = os.listdir(img_dir)
    fileName1 = set(fileName1) - set(bad_files)  # diff
    fileName1 = set(fileName1) | set(good_set_have_img_xml)  # Union
    print("used img (finally choose) number = ", len(fileName1))
    for name in fileName1:
        file_i = os.path.join(img_dir, name)
        file_d = os.path.join(img_save_dir, name)
        file_d2 = os.path.join(img_val_GT, name)
        shutil.copy(file_i, file_d)
        shutil.copy(file_i, file_d2)

    print("init XXX.txt ...")
    # 生成train test 的 txt
    pic_names = [name.split('.')[0] for name in os.listdir(img_save_dir) if
                 os.path.isfile(os.path.join(img_save_dir, name))]
    xml_names = [name.split('.')[0] for name in os.listdir(anno_dir) if os.path.isfile(os.path.join(anno_dir, name))]
    pic_names_no_xml = [name for name in pic_names if name not in xml_names]
    pic_names = [name for name in pic_names if name in xml_names]
    print('num of img without xml = ', len(pic_names_no_xml), ', will do nothing on them')
    print('num of img with xml = ', len(pic_names), ', will convert them')
    # random
    for _ in range(10):
        random.shuffle(pic_names)
    num_total = len(pic_names)
    num_train = int(num_total * train_rate)
    train_names = pic_names[:num_train]
    val_names = pic_names[num_train:]

    for i, name in enumerate(train_names):
        xml_to_txt(anno_dir + '\\' + name + '.xml',
                   name,
                   img_save_dir)
        print(f'\rsucceed convert xml to txt（train part）: {i} / {num_train} ...', end='')

    for i, name in enumerate(val_names):
        xml_to_txt(anno_dir + '\\' + name + '.xml',
                   name,
                   img_save_dir)
        print(f'\rsucceed convert xml to txt（test part）: {i + num_train} / {num_total} ...', end='')

    for i, name in enumerate(val_names):
        xml_to_txt(anno_dir + '\\' + name + '.xml',
                   name,
                   img_val_GT, abs=False)
        print(f'\rsucceed convert xml to txt（test part , abd = False）: {i + num_train} / {num_total} ...', end='')

    # 删掉那些有jpg 但没有txt的图片 ，因为有些xml被 drop 了
    fileName1 = os.listdir(img_val_GT)
    pic_names = [name.replace('.JPEG', '') for name in fileName1 if name.endswith('.JPEG')]
    txt_names = [name.replace('.txt', '') for name in fileName1 if name.endswith('.txt')]
    pic_names_no_txt = [name for name in pic_names if name not in txt_names]
    for name in pic_names_no_txt:
        file_d = os.path.join(img_val_GT, (name + '.JPEG'))
        os.remove(file_d)

    # 删掉那些有jpg 但没有txt的图片 ，因为有些xml被 drop 了
    fileName1 = os.listdir(img_save_dir)
    pic_names = [name.replace('.JPEG', '') for name in fileName1 if name.endswith('.JPEG')]
    txt_names = [name.replace('.txt', '') for name in fileName1 if name.endswith('.txt')]
    pic_names_no_txt = [name for name in pic_names if name not in txt_names]
    for name in pic_names_no_txt:
        file_d = os.path.join(img_save_dir, (name + '.JPEG'))
        os.remove(file_d)

    # 生成train test 的 name 文件, 仅留下  有jpg & txt 的
    fileName1 = os.listdir(img_save_dir)
    pic_names = [name.replace('.JPEG', '') for name in fileName1 if name.endswith('.JPEG')]
    with open(os.path.join(save_path, 'train.txt'), 'w') as f:
        f.writelines([r'to_train/img/' + n + '.JPEG\n' for n in train_names if n in pic_names])
    with open(os.path.join(save_path, 'val.txt'), 'w') as f:
        f.writelines([r'to_train/img/' + n + '.JPEG\n' for n in val_names if n in pic_names])

    # 生成 names 名字
    j = json.dumps(dic)
    with open(os.path.join(save_path, 'name.txt'), 'w') as f:
        f.writelines(j)

    print('going to final step')

    # ## 将 jpg 和 txt 分开存放,没错,就是这么蛋疼
    # fileName1 = os.listdir(img_save_dir)
    # txt_names = [name for name in fileName1 if name.endswith('.txt')]
    # for name in txt_names:
    #     file_i = os.path.join(img_save_dir, name)
    #     file_d = os.path.join(os.path.join(save_path, "label"), name)
    #     shutil.copy(file_i, file_d)
    # for name in txt_names:
    #     file_d = os.path.join(img_save_dir, name)
    #     os.remove(file_d)

    print('ok for everything')
