import cv2
import numpy as np

# Create a black image
img = np.zeros((512, 512, 3), np.uint8)

while True:
    cv2.imshow('Window', img)
    cv2.circle(img, (10, 20), 15, (0, 0, 255), -1)

    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

# # Draw a polygon
# pts = np.array([[10, 5], [20, 30], [70, 20], [50, 10]], np.int32)
# pts = pts.reshape((-1, 1, 2))
#
#
# # Display the image
# cv2.imshow("img", img)
#
# cv2.waitKey(0)
