import torch
import cv2


def post_process_angle(results, obj_id=0):
    """
    找出 第一个 obj_id 物体的角度
    :param results:  a dict
    :param obj_id: 0 / 1 / 2 ...
    :return: "10.8 right"
    """
    xywh = [None for i in range(4)]
    found = False
    results.print()  # or .show(), .save()    # can disable print time cost and prediction
    ret_tensor = results.xywh
    ret_numpy = ret_tensor[0].numpy()
    for pred in ret_numpy:
        conf = float(pred[4])  # 0.98
        class_id = int(pred[5])  # 0,1,2,3
        if class_id == int(obj_id):
            xywh[0] = pred[0]
            xywh[1] = pred[1]
            xywh[2] = pred[2]
            xywh[3] = pred[3]
            found = True
            break
    if not found:
        return None
    w_max = 1058  # 1280  # img width
    h_max = 595  # 720  # img height
    az_max = 69.46  # 70
    el_max = 42.63  # 42
    x = (w_max / 2 - xywh[0]) / w_max
    y = (h_max / 2 - xywh[1]) / h_max
    az = round(-az_max * 1 / 2 * 2 * x, 2)  # -(左边) , 0 中间 +(right)
    el = round(el_max * 1 / 2 * 2 * y, 2)  # -view_H , view_H(top)
    part_2 = " "
    part_3 = str(abs(az))
    part_1 = "left" if az <= 0 else "right"
    ret = part_3 + part_2 + part_1
    return ret  # "10.8 right"


model = torch.hub.load(r'C:\Users\jiant\Desktop\code\yolov5', 'custom',
                       path=r'C:\Users\jiant\Desktop\data\V&R-objectDetectionData\results\exp62-n-PureVirtual-300-train+100-test\weights\best.pt',
                       source='local',
                       device='cpu')

img = cv2.imread(r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\ball-0.png")
results = model(img, size=256)
direction = post_process_angle(results, 0)  # "10.8 right"
direction_lr = direction.split(" ")[1]
angle = direction.split(" ")[0]
print(f"==== post-process result is angle = {angle} on the {direction_lr}")

img = cv2.imread(r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\ball-10.png")
results = model(img, size=640)
direction = post_process_angle(results, 0)  # "10.8 right"
direction_lr = direction.split(" ")[1]
angle = direction.split(" ")[0]
print(f"==== post-process result is angle = {angle} on the {direction_lr}")

img = cv2.imread(r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\ball-20.png")
results = model(img, size=256)
direction = post_process_angle(results, 0)  # "10.8 right"
direction_lr = direction.split(" ")[1]
angle = direction.split(" ")[0]
print(f"==== post-process result is angle = {angle} on the {direction_lr}")

img = cv2.imread(r"C:\Users\jiant\Desktop\data\V&R-objectDetectionData\ball-30.png")
results = model(img, size=256)
direction = post_process_angle(results, 0)  # "10.8 right"
direction_lr = direction.split(" ")[1]
angle = direction.split(" ")[0]
print(f"==== post-process result is angle = {angle} on the {direction_lr}")


