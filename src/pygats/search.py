from pathlib import Path
import cv2
from matplotlib import pyplot as plt
import pytesseract
from PIL import Image
import recog as rec
import pygats as pyg
from formatters import MarkdownFormatter as MD

ctx = pyg.Context(MD())


def find_text():
    img = cv2.imread("./src/pygats/test1.png")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 25))
    dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)
    edges = cv2.Canny(gray, 100, 200)
    plt.imshow(edges, cmap='gray')
    plt.show()
    contours, hierarchy = cv2.findContours(
        dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )
    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(thresh1, None)
    image_with_sift = cv2.drawKeypoints(thresh1, keypoints, None)
    plt.imshow(cv2.cvtColor(image_with_sift, cv2.COLOR_BGR2RGB))
    plt.title('SIFT Features')
    plt.show()
    print(f"Найдено контуров: {len(contours)}")
    im2 = img.copy()
    cv2.imwrite("./src/pygats/after.png", im2)
    search_folder = Path('./src/pygats/search_folder')
    search_folder.mkdir(parents=True, exist_ok=True)
    with open("./tests/find/result.txt", "w+") as file:
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cropped = im2[y:y + h, x:x + w]
            text = pytesseract.image_to_string(cropped, "rus")
            print(f"Распознанный текст: '{text}'")
            file.write(text)
            cv2.imwrite(f"./src/pygats/search_folder/{cnt}.png", cropped)
        file.close()


def pygats_search():
    file = open("tests/find/words.ru.txt")
    texts = []
    good_result = 0
    failed_count = 0
    text_count = 0
    lines = file.readlines()
    for line in lines:
        if not line.strip():
            continue
        text_count += 1
        try:
            text = rec.SearchedText(line.strip(), "rus", None)
            texts.append(text)
            img = Image.open("./src/pygats/test1.png")
            rec.check_text(ctx, img, text)
            good_result += 1
        except pyg.TestException:
            failed_count += 1
        if text_count >= 9:
            break
    print("успешно распознанных слов: ", good_result, "\n", "не распознанных слов: ", failed_count)


find_text()
