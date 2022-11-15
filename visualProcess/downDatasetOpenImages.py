import fiftyone as fo
import fiftyone.zoo as foz
import os
import shutil
import numpy as np
import pandas as pd


def random_true(prob):
    p = ([prob, 1 - prob])
    return np.random.choice([True, False], p=p)


def download_open_image():
    dataset = foz.load_zoo_dataset(
        "open-images-v6",
        split="train",
        label_types=["detections"],
        classes=["Door handle", "Stairs"],
        max_samples=5000,
        shuffle=True,
    )

    session = fo.launch_app(dataset)

    session.dataset = dataset


txt_dir_path = r"C:\Users\jiant\fiftyone\open-images-v6\train\labels\yoloFormatTxt"
detection_csv_path = r"C:\Users\jiant\fiftyone\open-images-v6\train\labels\detections.csv"
img_all_path = r"C:\Users\jiant\fiftyone\open-images-v6\train\data"
img_copy_path = r"C:\Users\jiant\fiftyone\open-images-v6\train\labels\yoloFormatImage"

class_name = ["Apple", "Sandwich", "Cup", "Bowl", "Spoon", "Knife", "Bottle", "Sink", "Refrigerator", "Table", "Chair", "Couch", "Bed",
              "Cloth", "Book", "Mobile Phone", "Person", "Toilet", "Door Handle", "Stairs"]
# data_raw = {"classesName": ["Apple",
#                             "Sandwich", "Sandwich", "Sandwich",
#                             "Cup", "Cup", "Cup", "Cup",
#                             "Bowl", "Bowl",
#                             "Spoon",
#                             "Knife", "Knife",
#                             "Bottle", "Bottle",
#                             "Sink",
#                             "Refrigerator",
#                             "Table", "Table", "Table", "Table",
#                             "Chair",
#                             "Couch", "Couch", "Couch", "Couch",
#                             "Bed",
#                             "Cloth", "Cloth", "Cloth", "Cloth", "Cloth", "Cloth", "Cloth", "Cloth", "Cloth", "Cloth",
#                             "Book",
#                             "Mobile Phone",
#                             "Person", "Person", "Person", "Person", "Person",
#                             "Toilet",
#                             "Door Handle",
#                             "Stairs"],
#             "idName": ["/m/014j1m",
#                        "/m/0l515", "/m/0cdn1", "/m/06pcq", "/m/09tvcd",
#                        "/m/02p5f1q", "/m/02jvh9", "/m/07v9_z",
#                        "/m/03hj559", "/m/04kkgm",
#                        "/m/0cmx8",
#                        "/m/04ctx", "/m/058qzx",
#                        "/m/04dr76w", "/m/0271t ",
#                        "/m/0130jx",
#                        "/m/040b_t",
#                        "/m/04bcr3", "/m/04p0qw", "/m/078n6m", "/m/0h8n5zk",
#                        "/m/01mzpv",
#                        "/m/02crq1", "/m/026qbn5", "/m/03m3pdh", "/m/0703r8",
#                        "/m/03ssj5",
#                        "/m/09j2d", "/m/01bfm9", "/m/01d40f", "/m/01n4qj", "/m/01xygc", "/m/01xyhv", "/m/01cmb2", "/m/02wv6h6", "/m/032b3c", "/m/0h8mhzd",
#                        "/m/0bt_c3",
#                        "/m/050k8",
#                        "/m/01g317", "/m/04yx4", "/m/03bt1vf", "/m/01bl7v", "/m/05r655",
#                        "/m/09g1w",
#                        "/m/03c7gz",
#                        "/m/01lynh"]}


# data_raw = {"classesName": ["Cloth",
#                             "Door Handle",
#                             "Stairs"],
#             "idName": ["/m/01n4qj",
#                        "/m/03c7gz",
#                        "/m/01lynh"]}

data_raw = {"classesName": ["Door Handle",
                            "Stairs"],
            "idName": ["/m/03c7gz",
                       "/m/01lynh"]}

df = pd.DataFrame(data_raw)


def extract_txt():
    raw_data = pd.read_csv(detection_csv_path)
    img_id_list = os.listdir(img_all_path)
    summary_list = [0 for i in range(len(class_name))]  # 统计all图中各类框个数
    max_step = len(img_id_list)
    current_step = 1
    for img_id in img_id_list:
        current_step += 1
        if current_step % 10 == 0:
            print(f"{current_step}/{max_step}")
        hard_img = False
        summary_list_tmp = [0 for i in range(len(class_name))]  # 统计一张图中各类有关键obj的框个数
        file_data = ""
        img_id_no_end = img_id.replace(".jpg", "")
        img_id_txt_end = img_id.replace(".jpg", ".txt")
        csv_data_i = raw_data.loc[raw_data.ImageID == img_id_no_end]
        for index, row in csv_data_i.iterrows():
            label_name = row['LabelName']
            x_min = row['XMin']
            x_max = row['XMax']
            y_min = row['YMin']
            y_max = row['YMax']
            IsOccluded = int(row['IsOccluded'])
            IsTruncated = int(row['IsTruncated'])
            IsGroupOf = int(row['IsGroupOf'])
            IsDepiction = int(row['IsDepiction'])
            IsInside = int(row['IsInside'])
            x = (float(x_min) + float(x_max)) / 2
            y = (float(y_min) + float(y_max)) / 2
            w = float(x_max) - float(x_min)
            h = float(y_max) - float(y_min)
            # 找到 label 对应的 classes ID
            if not df[df["idName"] == label_name].empty:
                index_int = int(df[df["idName"] == label_name].index.values)
                index_class_name = str(df.iloc[index_int, 0])
                if IsGroupOf == 1 or IsDepiction == 1 or IsInside == 1:
                    hard_img = True
                    break
                index_class_20 = class_name.index(index_class_name)
                summary_list_tmp[index_class_20] = summary_list_tmp[index_class_20] + 1
                new_line = str(index_class_20) + " " + str(x) + " " + str(y) + " " + str(w) + " " + str(h) + "\n"
                file_data += new_line
            else:
                continue
            # for j in range(20):
            #     if label_name == class_id[j]:
            #         if IsGroupOf == 1 or IsDepiction == 1 or IsInside == 1:
            #             hard_img = True
            #             break
            #         summary_list_tmp[j] = summary_list_tmp[j] + 1
            #         new_line = str(j) + " " + str(x) + " " + str(y) + " " + str(w) + " " + str(h) + "\n"
            #         file_data += new_line
            #         break
        # boxes太多,大于15的图片不想要，扔掉
        if sum(summary_list_tmp) > 15:
            hard_img = True
        if file_data != "" and not hard_img:
            for i in range(20):
                summary_list[i] = summary_list[i] + summary_list_tmp[i]
            with open(os.path.join(txt_dir_path, img_id_txt_end), "w", ) as f:
                f.write(file_data)
    print(class_name)
    print(summary_list)
    print("Done!")


def copy_img_by_txt():
    txts = os.listdir(txt_dir_path)
    for txt in txts:
        img_name = txt.replace(".txt", ".jpg")
        img_path = os.path.join(img_all_path, img_name)
        img_path_new = os.path.join(img_copy_path, img_name)
        shutil.copy(img_path, img_path_new)


if __name__ == "__main__":
    # download_open_image()
    extract_txt()
    copy_img_by_txt()
