import os
import shutil

txt_dir_path = r"C:\Users\jiant\OneDrive\SJTU\7data\indoor-scene\1111-public\all_in_one\coco-all-TXT and Image"
new_idr = r"C:\Users\jiant\OneDrive\SJTU\7data\indoor-scene\1111-public\all_in_one\001_coco-by-classes"
tpm_dir = r"C:\Users\jiant\OneDrive\SJTU\7data\indoor-scene\1111-public\all_in_one\002_tmp"


def select_img_by_id(id_obj=7):
    txts = os.listdir(txt_dir_path)
    txts = [i for i in txts if i.endswith("txt")]
    for txt in txts:
        with open(os.path.join(txt_dir_path, txt), "r") as f:
            for line in f:
                if int(line.split(" ")[0]) == id_obj:
                    old = os.path.join(txt_dir_path, txt.replace("txt", "jpg"))
                    new = os.path.join(new_idr, txt.replace("txt", "jpg"))
                    shutil.copy(old, new)
                    break
    print("Done")


def copy_txt():
    imgs = os.listdir(tpm_dir)
    for img in imgs:
        txt_p = os.path.join(txt_dir_path, img.replace("jpg", "txt"))
        new = os.path.join(tpm_dir, img.replace("jpg", "txt"))
        shutil.copy(txt_p, new)


if __name__ == "__main__":
    # select_img_by_id()
    copy_txt()
