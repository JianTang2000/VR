def angle(w, h):
    w_max = 1280  # 1280  # img width
    h_max = 720  # 720  # img height
    az_max = 69.46  # 70
    el_max = 42.63  # 42
    x = (w_max / 2 - w) / w_max
    y = (h_max / 2 - h) / h_max
    az = round(-az_max * 1 / 2 * 2 * x, 2)  # -(左边) , 0 中间 +(right)
    el = round(el_max * 1 / 2 * 2 * y, 2)  # -view_H , view_H(top)
    return az, el


if __name__ == "__main__":
    print(angle(1280, 20))
    print(angle(500, 20))
    print(angle(0, 20))
