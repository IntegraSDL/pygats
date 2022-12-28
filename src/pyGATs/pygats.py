import pyautogui
import time
import sys
import subprocess
import os
import signal
import string
import random
import inspect
import pytesseract
from PIL import Image
from Levenshtein import median, ratio
import re
import cv2 as cv
import numpy as np

platform = ''
TestsPassed = []
TestsFailed = []
StepIndex = 0
ScreenshotIndex = 0
OutputPath = 'output'
suiteName = ''


class TestException(Exception):
    def __init__(self, img, msg):
        self.image = img
        self.message = msg


def platformSpecificImage(img):
    if platform != '':
        splitted = img.split('.')
        if len(splitted) == 2:
            specificImagePath = splitted[0]+'.'+platform + '.' + splitted[1]
            if os.path.exists(specificImagePath):
                return specificImagePath
    return img


def test(msg):
    """
    Begin of test. Dump msg as name of the test
    """
    global StepIndex
    global suiteName
    print()
    print(f'### {msg}')
    print()
    StepIndex = 0
    imgPath = os.path.join(OutputPath, 'initial-state.png')
    pyautogui.screenshot(imgPath)
    relativePath = imgPath.split(os.path.sep)
    tmpPath = os.path.join('', *relativePath[1:])
    print(f'Начальное состояние')
    print()
    print(f'![Начальное состояние]({tmpPath})')


def check(msg, f=None):
    print()
    print(f'{msg}')
    if f is not None:
        print('```')
        print(inspect.getsource(f))
        print('```')
        return f()
    return None


def suite(name, desc):
    global suiteName
    print()
    suiteName = name
    print(f'## {desc}')


def step(msg, img=None):
    global StepIndex
    StepIndex += 1
    ScreenshotIndex = 0
    print()
    print(f'Шаг {StepIndex}: {msg}')
    print()


def screenshot(rect=None):
    """Function takes screenshot limited by rect rectangle
    Return value is PIL.Image
    image is stored in output path as screenshotIndex
    """
    global ScreenshotIndex
    imgPath = os.path.join(
        OutputPath, f'step-{StepIndex}-{ScreenshotIndex}-passed.png')
    ScreenshotIndex += 1
    img = pyautogui.screenshot(imgPath, region=rect)
    relativePath = imgPath.split(os.path.sep)
    tmpPath = os.path.join('', *relativePath[1:])
    print(f'![Снимок экрана]({tmpPath})')
    print()
    return img


def logImage(img, msg='Снимок экрана'):
    """Function log img with msg into report
    image is stored in output path as screenshotIndex
    """
    global ScreenshotIndex
    imgPath = os.path.join(
        OutputPath, f'step-{StepIndex}-{ScreenshotIndex}-passed.png')
    ScreenshotIndex += 1
    img.save(imgPath)
    relativePath = imgPath.split(os.path.sep)
    tmpPath = os.path.join('', *relativePath[1:])
    print(f'![{msg}]({tmpPath})')
    print()
    return img


def passed():
    global suiteName
    imgPath = os.path.join(OutputPath, f'step-{StepIndex}-passed.png')
    pyautogui.screenshot(imgPath)
    relativePath = imgPath.split(os.path.sep)
    tmpPath = os.path.join('', *relativePath[1:])
    print(f'![Успешно]({tmpPath})')
    print()
    print('**Успешно**')
    print()


def failed(img=pyautogui.screenshot(), msg='Тест не успешен'):
    raise TestException(img, msg)


def checkImage(img, timeout=1):
    """Check if image is located on screen. Timeout in second waiting image to occure"""
    img = platformSpecificImage(img)
    step(f'Проверка отображения {img} ...')
    try:
        while timeout > 0:
            if locateOnScreen(img) is not None:
                passed()
                return
            timeout -= 1
            time.sleep(1)
    except:
        print('Exception')
        failed(img, 'Изображение не найдено')
    failed(img, 'Изображение не найдено')


def locateOnScreen(img):
    """Function return coord of image located on screen. If not found returnes None"""
    img = platformSpecificImage(img)
    coord = pyautogui.locateOnScreen(img, confidence=0.5)
    print(f'Изображение найдено в координатах {coord}')
    return coord


def moveToCoord(x, y):
    """Function moves mouse to coord x,y"""
    step(f'Переместить указатель мыши в координаты {x},{y}')
    pyautogui.moveTo(x, y)
    passed()


def moveTo(img):
    """Function move mouse to img"""
    img = platformSpecificImage(img)
    step(f'Переместить указатель мыши на изображение {img} ...')
    center = pyautogui.locateCenterOnScreen(img, confidence=0.8)
    if center is None:
        failed(img, 'Изображение не найдено')
    if sys.platform == 'darwin':
        pyautogui.moveTo(center.x/2, center.y/2)
    else:
        pyautogui.moveTo(center.x, center.y)
    print(f'Текущая позиция указателя мыши {pyautogui.position()}')
    passed()
    return True


def clickRightButton():
    step('Нажать правую кнопку мыши ...')
    pyautogui.click(button='right')
    print(f'Текущая позиция указателя мыши {pyautogui.position()}')
    passed()


def clickLeftButton():
    step('Нажать левую кнопку мыши ...')
    pyautogui.click(button='left')
    print(f'Текущая позиция указателя мыши {pyautogui.position()}')
    passed()


def click(btn, area=''):
    btn = platformSpecificImage(btn)
    area = platformSpecificImage(area)
    step(f'Нажать кнопку мыши {btn} ...')
    if area == '':
        center = pyautogui.locateCenterOnScreen(btn, confidence=0.8)
        print(f'Кнопка найдена с центром в координатах {center}')
    else:
        print(" area " + area)
        areaLocation = pyautogui.locateOnScreen(area, confidence=0.9)
        if areaLocation is None:
            failed(area, 'Изображение не найдено')
        box = pyautogui.locate(btn, area, confidence=0.8)
        if box is None:
            failed(area, 'Изображение не найдено')

        x = areaLocation.left + box.left + box.width/2
        y = areaLocation.top + box.top + box.height/2
        center = pyautogui.Point(x, y)
    if center is None:
        failed(btn, 'Изображение не найдено')

    print(f'Перемещаем указатель мыши в координаты {center}')
    if sys.platform == 'darwin':
        pyautogui.moveTo(center.x/2, center.y/2)
    else:
        pyautogui.moveTo(center.x, center.y)
    # pyautogui.dragTo()
    pyautogui.click()
    passed()


def ctrlWithKey(key):
    step(f'Нажать клавишу ctrl+{key}')
    pyautogui.hotkey('ctrl', key)
    passed()


def altWithKey(key):
    step(f'Нажать клавишу alt+{key}')
    pyautogui.hotkey('alt', key)
    passed()


def dragTo(x, y):
    step(f'Переместить в координаты {x}, {y} ...')
    pyautogui.dragTo(x, y, button='left', duration=0.5)
    passed()


def move(x, y):
    step(f'Относительное перемещение указателя мыши x={x}, y={y} ...')
    print(f'из координат {pyautogui.position()}')
    pyautogui.move(x, y)
    print(f'новые координаты {pyautogui.position()}')
    passed()


def keyboard(message):
    step(f'Набрать на клавиатуре и нажать <Enter>: {message} ...')
    pyautogui.write(message, 0.1)
    pyautogui.press('enter')
    passed()


def press(key, n=1):
    """Function press keys n times"""
    step(f'Нажать {key} {n} раз')
    for i in range(n):
        pyautogui.press(key)


def typewrite(message):
    step(f'Набрать на клавиатуре {message} ...')
    pyautogui.write(message)
    passed()


def setUp(exec, outLog, errLog):
    print(f'## Подготовка стенда к работе')
    print(f'{exec} ...')
    env = os.environ.copy()
    testProc = subprocess.Popen(
        [exec], stderr=errLog, stdout=outLog, env=env, cwd=os.path.dirname(exec))
    time.sleep(1)
    if testProc is not None:
        passed()
    return testProc


def tearDown(testProc):
    print('## Завершение работы стенда')
    altWithKey('f4')
    testProc.kill()
    passed()


def printTestSummary(passed, failed):
    print()
    print(f'## Результаты тестирования')
    print(f'Тесты завершенные успешно:')
    for t in passed:
        print('* ', t)
    print()
    print(f'Тесты завершенные неуспешно:')
    for t in failed:
        print('* ', t)
    print()
    print('**Всего выполнено**')
    print()
    print(
        'Успешно: {:04d} / Неуспешно: {:04d}'.format(len(passed), len(failed)))
    print()


def checkText(img, txt, lang):
    step(f'Проверка отображения текста {txt} на изображении {img}...')
    x, y, width, height, flag = findText(img, txt, lang=lang)
    if flag:
        passed()
        return
    failed(img, f'{txt} не найден на изображении')


def checkTextOnScreen(txt, lang):
    step(f'Проверка отображения текста {txt} на экране ...')
    img = pyautogui.screenshot()
    x, y, width, height, flag = findText(img, txt, lang=lang)
    if not flag:
        failed(img, f'{txt} не найден на экране')
    passed()
    return


def clickText(text, lang, button='left', skip=0):
    step(f'Нажать текст {text} экране кнопкой {button}...')
    x, y, width, height, found = findTextOnScreen(text, lang, skip)
    if not found:
        failed(msg=f'{text} не найден на экране')

    print(x, y, width, height)
    centerX = x + width/2
    centerY = y + height/2
    pyautogui.moveTo(centerX, centerY)
    pyautogui.mouseDown(centerX, centerY, button)
    pyautogui.mouseUp(centerX, centerY, button)
    passed()


def recognizeTextWithData(img, lang):
    return pytesseract.image_to_data(img, lang)

# DEPRICATED: this function will be removed
# def recognizeText(img, lang):
#    return pytesseract.image_to_string(img, lang=lang)


def combineWordsInLines(lines):
    for i in range(1, len(lines)-1):
        splitted = lines[i].split('\t')
        if len(splitted) != 12:
            return
        y = int(splitted[7])
        for j in range(i+1, len(lines)-1):
            splitted2 = lines[j].split('\t')
            if abs(y - int(splitted2[7])) < 5:
                if len(splitted2[11].strip()) > 0:
                    lines[i] += ' ' + splitted2[11]
    return


def combineLines(lines):
    result = []
    for i in range(1, len(lines)-1):
        splitted = lines[i].split('\t')
        if len(splitted) != 12:
            return
        x = int(splitted[6])
        y = int(splitted[7])
        w = int(splitted[8])
        h = int(splitted[9])
        text = splitted[11]
        for j in range(i+1, len(lines)-1):
            splitted2 = lines[j].split('\t')
            if abs(y - int(splitted2[7])) < 5:
                if len(splitted2[11].strip()) > 0:
                    w += int(splitted[8])
                    text += ' ' + splitted2[11]
        result.append((x, y, w, h, text))
    return result


def findText(img, text, lang, skip=0):
    recognized = pytesseract.image_to_data(img, lang).split('\n')
    combineWordsInLines(recognized)
    retTup = (-1, -1, -1, -1, False)
    for line in recognized[1:]:
        splitted = line.split('\t')
        if len(splitted) == 12:
            if splitted[11].find(text) != -1:
                print("Найден текст " + splitted[11])
                x = int(splitted[6]) + int(splitted[8])/2
                y = int(splitted[7]) + int(splitted[9])/2
                retTup = (int(splitted[6]), int(splitted[7]), int(
                    splitted[8]), int(splitted[9]), True)
                if skip <= 0:
                    break
                skip -= 1
            else:
                if int(splitted[6]) + int(splitted[7]) != 0:
                    cropped = img.crop((int(splitted[6]), int(splitted[7]), int(
                        splitted[6])+int(splitted[8]), int(splitted[7])+int(splitted[9])))
                    croppedTup = findTextCropped(cropped, text, lang)
                    if croppedTup[4]:
                        return (croppedTup[0]+int(splitted[6]), croppedTup[1]+int(splitted[7]), croppedTup[2], croppedTup[3], croppedTup[4])
    return retTup


def recognizeText(img, lang):
    recognized = pytesseract.image_to_data(img, lang).split('\n')
    result = combineLines(recognized)
    return list(set(result))


def findFuzzyText(recognizedList, search):
    """Fuzzy search of text in list using Levenshtein ratio
    Return value is list of tuples with following format:
    (x,y,w,h,text)
    x,y       - coordinates of top-left point of rectangle where text resides
    w,h       - width and height of rectangle where text resides
    text      - full text which resides in rectangle
    """
    result = []
    lSearch = len(search)
    for l in recognizedList:
        r = ratio(search, l[4], score_cutoff=0.5)
        if r > 0.0:
            result.append(l)
        else:
            s = l[4]
            if len(s) > lSearch:
                for i in range(0, len(s)-lSearch):
                    slice = s[i:i+lSearch]
                    r = ratio(search, slice, score_cutoff=0.8)
                    if r > 0.0:
                        result.append(l)
    return list(set(result))


def findRegExpText(recognizedList, regexp):
    """Find text in list by regexp
    Return value is list of tuples with following format
    (x,y,w,h,text, substring)
    x,y       - coordinates of top-left point of rectangle where text resides
    w,h       - width and height of rectangle where text resides
    text      - full text which resides in rectangle
    substring - substring found in text
    """
    result = []
    for l in recognizedList:
        m = re.findall(regexp, l[4])
        if len(m) > 0:
            l += tuple(m)
            result.append(l)
    return list(set(result))


def findTextCropped(img, text, lang, skip=0):
    recognized = pytesseract.image_to_data(img, lang).split('\n')
    combineWordsInLines(recognized)
    retTup = (-1, -1, -1, -1, False)
    for line in recognized[1:]:
        splitted = line.split('\t')
        if len(splitted) == 12:
            if splitted[11].find(text) != -1:
                print(f'Найден текст {splitted[11]}')
                x = int(splitted[6]) + int(splitted[8])/2
                y = int(splitted[7]) + int(splitted[9])/2
                retTup = (int(splitted[6]), int(splitted[7]), int(
                    splitted[8]), int(splitted[9]), True)
                if skip <= 0:
                    break
                skip -= 1
    return retTup


def findTextOnScreen(text, lang, skip=0):
    step(f'Поиск текста {text} на экране ...')
    img = pyautogui.screenshot()
    return findText(img, text, lang, skip)


def repeater(cnts):
    """This function is default selector for contours"""
    return cnts


def filterRectSorted(cnts):
    """Selector choose rect like contours and sort them by area descending"""
    def approxer(x):
        eps = 0.01 * cv.arcLength(x, True)
        return cv.approxPolyDP(x, eps, True)

    def rectFilter(x):
        if len(x) == 4:
            return True
        return False

    cnts2 = list(filter(rectFilter, map(approxer, cnts)))
    cnts2 = sorted(cnts2, key=lambda x: abs(x.item(4)-x.item(0))
                   * abs(x.item(5)-x.item(1)), reverse=True)
    return cnts2


def findContours(img, fltr=repeater):
    """Function finds contours by cv and filter them with filter"""
    step('Поиск контуров с применением селектора')
    npImg = np.array(img)
    gray = cv.cvtColor(npImg, cv.COLOR_BGR2GRAY)
    _, thresh = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)
    cnts, _ = cv.findContours(
        thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    return fltr(cnts)


def drawContours(img, cnts):
    """Function draw contours on PIL.Image"""
    npImg = np.array(img)
    cv.drawContours(npImg, cnts, -1, (0, 255, 0), 3)
    return Image.fromarray(npImg)


def randomString(stringLength):
    letters = string.ascii_letters + ' _' + string.digits
    return ''.join(random.choice(letters) for i in range(stringLength))


def run(funcs, counter=1, output='output'):
    global OutputPath, suiteName
    try:
        os.makedirs(output)
    except:
        pass
    for i in range(counter):
        for f in funcs:
            testName = f.__name__
            try:
                os.makedirs(os.path.join(output, suiteName, testName))
            except:
                pass
            try:
                OutputPath = os.path.join(output, suiteName, testName)
                f()
                TestsPassed.append(os.path.join(suiteName, testName))
                imgPath = os.path.join(
                    output, suiteName, testName, 'test-passed.png')
                pyautogui.screenshot(imgPath)
                relativePath = imgPath.split(os.path.sep)
                tmpPath = os.path.join('', *relativePath[1:])
                print(f'![Тест пройден]({tmpPath})')
                print()
                print(f'**Тест пройден**')
                pass
            except TestException as e:
                imgPath = os.path.join(
                    output, suiteName, testName, 'test-failed.png')
                pyautogui.screenshot(imgPath)
                print(f'\n> Error : {e.message}\n')
                relativePath = imgPath.split(os.path.sep)
                tmpPath = os.path.join('', *relativePath[1:])
                print(f'![Тест не пройден]({tmpPath})')
                print()
                print("**Тест не пройден**")
                TestsFailed.append(os.path.join(suiteName, testName))
                pass

    printTestSummary(TestsPassed, TestsFailed)
