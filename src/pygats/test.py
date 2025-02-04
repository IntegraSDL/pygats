from PIL import Image
import cv2 as cv
from matplotlib import pyplot as plt
import numpy as np
import recog as rec


img = Image.open("./tests/find/background/3_scada.png")

# Поиск ключевых точек
keypoints, descriptors, coord_list = rec.find_keypoints(img)

# Кластеризация по координатам
labels, centers = rec.rectangle_cluster(coord_list, K=10)

# # Визуализация
result_img = rec.draw_clustered_rectangles(10, coord_list, labels, img, keypoints )
