# pytesseract boxes 
import cv2 as cv
import pytesseract
"https://programmersought.com/article/896710504463/"

img = cv.imread("./src/pygats/test1.png")

img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

hImg, wImg, _ = img.shape

boxes = pytesseract.image_to_boxes(img)
for b in boxes.splitlines():
    b = b.split(' ')
    print(b)
    x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
    cv.rectangle(img, (x, hImg - y), (w, hImg - h), (0, 0, 255), 2)

cv.imshow("img", img)
cv.waitKey(0)
