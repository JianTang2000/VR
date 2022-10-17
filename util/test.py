import numpy as np
import imageio

image = imageio.imread(r'C:\Users\jiant\Pictures\bed\bed_1.png')
# If you want to see the actual colors instead of just grey images,
# you need to retain all three channels and set the values on the other channels to zero.
# For example, to get the red component, set the green and blue channel values to 0,
# as shown below:
red_image = image.copy()
red_image[:, :, 0] = 0
red_image[:, :, 2] = 0
blue_img = image.copy()
blue_img[:, :, 1] = 0
blue_img[:, :, 2] = 0
green_img = image.copy()
green_img[:, :, 0] = 0
green_img[:, :, 1] = 0
blue_single = blue_img[:, :, 0]
red_single = red_image[:, :, 1]
green_single = green_img[:, :, 2]
print(blue_single[248:253, 598:603])
print(red_single[248:253, 598:603])
print(green_single[248:253, 598:603])
cv2.imshow('B', blue_img)
cv2.imshow('G', red_image)
cv2.imshow('R', green_img)
cv2.waitKey(-1)
cv2.destroyAllWindows()