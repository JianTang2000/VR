import shutil
import os

import tools


def reduce_img(p=0.1):
    todo_path = r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\Unity-0811-gray-newbed-no-reduce"
    save_path = r'C:\Users\jiant\Desktop\data\V&R-objectDetectionData\Unity-0811-gray-newbed-reduced'
    files = os.listdir(todo_path)
    files = [i for i in files if i.endswith('.jpg')]
    for file in files:
        if tools.random_true(p):
            img_path = os.path.join(todo_path, file)
            img_path_new = os.path.join(save_path, file)
            shutil.copy(img_path, img_path_new)
        else:
            pass


def reduce_train_img_label(p=0.1):
    """
    按照比例减少训练图片和对应的标签
    """
    todo_img_path = r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\train-on-server\fig1-realData-AP-train-40\images\train"
    todo_label_path = r'C:\Users\jiant\Desktop\data\V&R-objectDetectionData\train-on-server\fig1-realData-AP-train-40\labels\train'
    files = os.listdir(todo_img_path)
    del_file_name_list = []
    for file in files:
        if tools.random_true(p):
            del_file_name_list.append(file)
            os.remove(os.path.join(todo_img_path, file))
        else:
            pass
    for file in del_file_name_list:
        txt_name = file.replace(".jpg", ".txt")
        os.remove(os.path.join(todo_label_path, txt_name))


def del_non_img_label():
    img_path = r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\train-on-server\fig1-realData-AP-train-20\images\train"
    label_path = r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\train-on-server\fig1-realData-AP-train-20\labels\train"
    imgs = os.listdir(img_path)
    labels = os.listdir(label_path)
    for label in labels:
        if imgs.__contains__(label.replace(".txt", ".jpg")):
            pass
        else:
            os.remove(os.path.join(label_path, label))


def copy_rename_files(new_name_start="1003-paper-1-", use_rate=1):
    """
    把 todo_path 的带txt和jpg的文件copy并rename再放到save_path里, 使用比例为 0-1 --> 0-100%
    """
    todo_path = r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\labeled\real-0816-dark-night-WallPaper-5classes"
    save_path = r'C:\Users\jiant\Desktop\data\V&R-objectDetectionData\tmp'
    files = os.listdir(todo_path)
    txts = [i for i in files if i.endswith("txt")]
    for txt in txts:
        if tools.random_true(use_rate):
            if txt != "classes.txt":
                txt_full_path = os.path.join(todo_path, txt)
                new_txt_name = new_name_start + txt
                new_txt_full_path = os.path.join(save_path, new_txt_name)
                shutil.copy(txt_full_path, new_txt_full_path)

                jpg_full_path = os.path.join(todo_path, txt.replace(".txt", ".jpg"))
                new_jpg_name = new_name_start + txt.replace(".txt", ".jpg")
                new_jpg_full_path = os.path.join(save_path, new_jpg_name)
                shutil.copy(jpg_full_path, new_jpg_full_path)


def copy_rename_files_all(new_name_start="1003-paper-1-"):
    """
    把 todo_path 的带txt和jpg的文件copy并rename再放到save_path里, 使用比例为 0-1 --> 0-100%
    """
    todo_path = r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\labeled\real-0816-dark-night-WallPaper-5classes"
    save_path = r'C:\Users\jiant\Desktop\data\V&R-objectDetectionData\tmp'
    files = os.listdir(todo_path)
    for file in files:
        txt_full_path = os.path.join(todo_path, file)
        new_txt_name = new_name_start + file
        new_txt_full_path = os.path.join(save_path, new_txt_name)
        shutil.copy(txt_full_path, new_txt_full_path)


def split_train_test():
    todo_path = r"C:\Users\jiant\Desktop\data\indoor-scene\chair"
    save_path = r'C:\Users\jiant\Desktop\data\indoor-scene\chair-train'
    if not os.path.isdir(os.path.join(save_path, r'images\train')):
        os.makedirs(os.path.join(save_path, r'images\train'))
    if not os.path.isdir(os.path.join(save_path, r'images\val')):
        os.makedirs(os.path.join(save_path, r'images\val'))
    if not os.path.isdir(os.path.join(save_path, r'labels\train')):
        os.makedirs(os.path.join(save_path, r'labels\train'))
    if not os.path.isdir(os.path.join(save_path, r'labels\val')):
        os.makedirs(os.path.join(save_path, r'labels\val'))
    shutil.rmtree(os.path.join(save_path, r'images\train'))
    os.mkdir(os.path.join(save_path, r'images\train'))
    shutil.rmtree(os.path.join(save_path, r'images\val'))
    os.mkdir(os.path.join(save_path, r'images\val'))
    shutil.rmtree(os.path.join(save_path, r'labels\train'))
    os.mkdir(os.path.join(save_path, r'labels\train'))
    shutil.rmtree(os.path.join(save_path, r'labels\val'))
    os.mkdir(os.path.join(save_path, r'labels\val'))

    files_all = os.listdir(todo_path)
    files = [i for i in files_all if i.startswith("rgb") and i.endswith('.jpg')]
    txts = [i for i in files_all if i.startswith("rgb") and i.endswith('.txt')]
    files = [i for i in files if i.replace(".jpg", ".txt") in txts]
    for file in files:
        if tools.random_true(0.7):
            img_path = os.path.join(todo_path, file)
            img_path_new = os.path.join(os.path.join(save_path, r'images\train'), file)
            label_path = os.path.join(todo_path, file.replace('.jpg', '.txt'))
            label_path_new = os.path.join(os.path.join(save_path, r'labels\train'), file.replace('.jpg', '.txt'))
            shutil.copy(img_path, img_path_new)
            shutil.copy(label_path, label_path_new)
        else:
            img_path = os.path.join(todo_path, file)
            img_path_new = os.path.join(os.path.join(save_path, r'images\val'), file)
            label_path = os.path.join(todo_path, file.replace('.jpg', '.txt'))
            label_path_new = os.path.join(os.path.join(save_path, r'labels\val'), file.replace('.jpg', '.txt'))
            shutil.copy(img_path, img_path_new)
            shutil.copy(label_path, label_path_new)


def copy_txt_to_img(use_rate=1):
    label_path = r"C:\Users\jiant\Desktop\tmp\l"
    img_path = r'C:\Users\jiant\Desktop\tmp\10'
    labels = os.listdir(label_path)
    imgs = os.listdir(img_path)
    for img in imgs:
        txt_name = img.replace(".jpg", ".txt")
        if labels.__contains__(txt_name):
            txt_path = os.path.join(img_path, txt_name)
            shutil.copy(os.path.join(label_path, txt_name), txt_path)


def txt_classes_num_summary():
    """
    指定类名,  文件路径名（txt 和 img 放一起）
    """
    classes_name = ['ball', 'bed', 'sofa', 'chair', 'couch']
    classes_count = [0 for i in classes_name]
    file_path = r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\labeled\00selected-to-use-V&R-5-classes-no-man\1-real"
    files = os.listdir(file_path)
    txts = [i for i in files if i.endswith("txt")]
    imgs = [i.replace(".txt", ".jpg") for i in txts]
    print(f" ======> img file num (with related txt) = {len(imgs)}")
    for txt in txts:
        with open(os.path.join(file_path, txt), 'r') as f1:
            lines = f1.readlines()  # read each line
        txt_context = [i.replace("\n", "") for i in lines if i != '\n']
        print("txt file name is :", txt)
        print("raw txt is :", lines)
        print("clearn txt is :", txt_context)
        # break
        for cont in txt_context:
            box = cont.split(" ")
            box = [float(i) for i in box]
            classes_count[int(box[0])] += 1
        # print(classes_count)
        # break
    print(classes_name)
    print(classes_count)


if __name__ == "__main__":
    # reduce_img(p=0.1)
    # copy_rename_files_all()
    split_train_test()
    # txt_classes_num_summary()
    # copy_txt_to_img()
    # reduce_train_img_label(p=0.18)
    # del_non_img_label()
