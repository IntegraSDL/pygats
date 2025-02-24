from PIL import Image
import hdbscan
import numpy as np
import recog as rec
import cv2 as cv

query_image = Image.open("./tests/find/background/test-01.jpg")
train_image = Image.open("./tests/find/background/test-02.jpg")

keypoints_1, descriptors_1, coord_list_1 = rec.find_keypoints(query_image)
keypoints_2, descriptors_2, coord_list_2 = rec.find_keypoints(train_image)

unique_keypoints1 = []
unique_keypoints2 = []

for kp1 in keypoints_1:
    x1, y1 = kp1.pt
    uniq = True
    for kp2 in keypoints_2:
        x2, y2 = kp2.pt
        if abs(x1-x2) < 1 and abs(y1-y2)<1:
            uniq = False
            break
    if uniq:
        unique_keypoints1.append(kp1)

for kp2 in keypoints_2:
    x2, y2 = kp2.pt
    uniq = True
    for kp1 in keypoints_1:
        x1, y1 = kp1.pt
        if abs(x2-x1) < 1 and abs(y2-y1)<1:
            uniq = False
            break
    if uniq:
        unique_keypoints2.append(kp2)

query_image = np.array(query_image)
train_image = np.array(train_image)
query_image = cv.drawKeypoints(query_image, unique_keypoints1, query_image,(255, 0, 0) )
query_image = cv.drawKeypoints(query_image, unique_keypoints2, query_image,(0, 0, 255) )


result_h = cv.hconcat([query_image, train_image])
cv.imshow('Horizontal Concatenation', result_h)
cv.waitKey(0)