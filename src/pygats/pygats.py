"""
pyGATs tis python3 library which combines power of pyautogui, opencv, tesseract,
markdown and other staff to automate end-to-end and exploratorytesting.
"""
import time
import sys
import subprocess
import os
import string
import random
import inspect
import re
import pyautogui
import pyperclip
import pytesseract
from PIL import Image
from Levenshtein import ratio
import cv2 as cv
import numpy as np

PLATFORM = ''
TESTS_PASSED = []
TESTS_FAILED = []
STEP_INDEX = 0
SCREENSHOT_INDEX = 0
OUTPUT_PATH = 'output'
SUITE_NAME = ''

class Context: # pylint: disable=too-few-public-methods
    """Context stores information about"""
    formatter = None
    def __init__(self, frmtr):
        self.formatter = frmtr


class TestException(Exception):
    """
    Test exception class stores msg and screenshot when error occurs
    """
    def __init__(self, img, msg):
        self.image = img
        self.message = msg


def platform_specific_image(img):
    """
    function returns platform specific path to the image. If screenshot has
    platform specifics it shoult be separated in different images. Name of
    image contains platform name picName.PLATFORM.ext
    """
    if PLATFORM != '':
        splitted = img.split('.')
        if len(splitted) == 2:
            specific_image_path = splitted[0]+'.'+PLATFORM + '.' + splitted[1]
            if os.path.exists(specific_image_path):
                return specific_image_path
    return img


def begin_test(ctx, msg):
    """
    Begin of test. Dump msg as name of the test
    """
    global STEP_INDEX
    ctx.formatter.print_header(3, msg)
    STEP_INDEX = 0
    # img_path = os.path.join(OUTPUT_PATH, 'initial-state.png')
    # pyautogui.screenshot(img_path)
    # relative_path = img_path.split(os.path.sep)
    # tmp_path = os.path.join('', *relative_path[1:])
    # print('Начальное состояние')
    # print()
    # print(f'![Начальное состояние]({tmp_path})')


def check(ctx, msg, func=None):
    """
    Prints message as check block
    """
    ctx.formatter.print_para(f'{msg}')
    if func is not None:
        ctx.formatter.print_code(inspect.getsource(func))
        return func()
    return None


def suite(ctx, name, desc):
    """
    function prints test suite name in reports
    """
    global SUITE_NAME
    print()
    SUITE_NAME = name
    ctx.formatter.print_header(2, desc)


def step(ctx, msg):
    """
    function prints step name and starts new screenshot index
    """
    global STEP_INDEX, SCREENSHOT_INDEX
    STEP_INDEX += 1
    SCREENSHOT_INDEX = 0
    msg = f'Step {STEP_INDEX}: {msg}'
    ctx.formatter.print_para(msg)


def screenshot(ctx, rect=None):
    """Function takes screenshot limited by rect rectangle
    Return value is PIL.Image
    image is stored in output path as screenshotIndex
    """
    global SCREENSHOT_INDEX
    img_path = os.path.join(
        OUTPUT_PATH, f'step-{STEP_INDEX}-{SCREENSHOT_INDEX}-passed.png')
    SCREENSHOT_INDEX += 1
    img = pyautogui.screenshot(img_path, region=rect)
    relative_path = img_path.split(os.path.sep)
    tmp_path = os.path.join('', *relative_path[1:])
    ctx.formatter.print_img(tmp_path)
    return img


def log_image(img, msg='Снимок экрана'):
    """Function log img with msg into report
    image is stored in output path as screenshotIndex
    """
    global SCREENSHOT_INDEX
    img_path = os.path.join(
        OUTPUT_PATH, f'step-{STEP_INDEX}-{SCREENSHOT_INDEX}-passed.png')
    SCREENSHOT_INDEX += 1
    img.save(img_path)
    relative_path = img_path.split(os.path.sep)
    tmp_path = os.path.join('', *relative_path[1:])
    print(f'![{msg}]({tmp_path})')
    print()
    return img


def passed():
    """
    function prints passed information after test case
    """
    img_path = os.path.join(OUTPUT_PATH, f'step-{STEP_INDEX}-passed.png')
    pyautogui.screenshot(img_path)
    relative_path = img_path.split(os.path.sep)
    tmp_path = os.path.join('', *relative_path[1:])
    print(f'![Успешно]({tmp_path})')
    print()
    print('**Успешно**')
    print()


def failed(img=pyautogui.screenshot(), msg='Тест не успешен'):
    """
    function generates excpetion while error occurs
    """
    raise TestException(img, msg)


def check_image(ctx, img, timeout=1):
    """Check if image is located on screen. Timeout in second waiting image to occure"""
    img = platform_specific_image(img)
    step(ctx, f'Проверка отображения {img} ...')
    try:
        while timeout > 0:
            if locate_on_screen(img) is not None:
                passed()
                return
            timeout -= 1
            time.sleep(1)
    except: # pylint: disable=bare-except
        print('Exception')
        failed(img, 'Изображение не найдено')
    failed(img, 'Изображение не найдено')


def locate_on_screen(img):
    """Function return coord of image located on screen. If not found returnes None"""
    img = platform_specific_image(img)
    coord = pyautogui.locateOnScreen(img, confidence=0.5)
    print(f'Изображение найдено в координатах {coord}')
    return coord


def move_to_coord(ctx, x, y):
    """Function moves mouse to coord x,y"""
    step(ctx, f'Переместить указатель мыши в координаты {x},{y}')
    pyautogui.moveTo(x, y)
    passed()


def move_to(ctx, img):
    """Function move mouse to img"""
    img = platform_specific_image(img)
    step(ctx, f'Переместить указатель мыши на изображение {img} ...')
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


def click_right_button(ctx):
    """function clicks right mouse button"""
    step(ctx, 'Нажать правую кнопку мыши ...')
    pyautogui.click(button='right')
    print(f'Текущая позиция указателя мыши {pyautogui.position()}')
    passed()


def click_left_button(ctx):
    """function clicks left button of mouse"""
    step(ctx, 'Нажать левую кнопку мыши ...')
    pyautogui.click(button='left')
    print(f'Текущая позиция указателя мыши {pyautogui.position()}')
    passed()


def click(ctx, btn, area=''):
    """function clicks button in area"""
    btn = platform_specific_image(btn)
    area = platform_specific_image(area)
    step(ctx, f'Нажать кнопку мыши {btn} ...')
    if area == '':
        center = pyautogui.locateCenterOnScreen(btn, confidence=0.8)
        print(f'Кнопка найдена с центром в координатах {center}')
    else:
        print(" area " + area)
        area_location = pyautogui.locateOnScreen(area, confidence=0.9)
        if area_location is None:
            failed(area, 'Изображение не найдено')
        box = pyautogui.locate(btn, area, confidence=0.8)
        if box is None:
            failed(area, 'Изображение не найдено')

        x = area_location.left + box.left + box.width/2
        y = area_location.top + box.top + box.height/2
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


def ctrl_with_key(ctx, key):
    """
    function presses key with ctrl key
    """
    step(ctx, f'Нажать клавишу ctrl+{key}')
    pyautogui.hotkey('ctrl', key)
    passed()


def alt_with_key(ctx, key):
    """
    function presses alt+key
    """
    step(ctx, f'Нажать клавишу alt+{key}')
    pyautogui.hotkey('alt', key)
    passed()


def drag_to(ctx, x, y):
    """
    drag something to coordinates x, y
    """
    step(ctx, f'Переместить в координаты {x}, {y} ...')
    pyautogui.dragTo(x, y, button='left', duration=0.5)
    passed()


def move(ctx, x, y):
    """
    function moves mouse pointer to x,y coordinates
    """
    step(ctx, f'Относительное перемещение указателя мыши x={x}, y={y} ...')
    print(f'из координат {pyautogui.position()}')
    pyautogui.move(x, y)
    print(f'новые координаты {pyautogui.position()}')
    passed()


def keyboard(ctx, message):
    """
    function types message on keboard with 0.1 sec delay of each simbol
    At the end <Enter> is pressed
    """
    step(ctx, f'Набрать на клавиатуре и нажать <Enter>: {message} ...')
    pyautogui.write(message, 0.1)
    pyautogui.press('enter')
    passed()


def press(ctx, key, n=1):
    """Function press keys n times"""
    step(ctx, f'Нажать {key} {n} раз')
    for _ in range(n):
        pyautogui.press(key)


def typewrite(ctx, message, lang='eng'):
    """function types keys on keboard"""
    if lang != 'eng':
        buffer = pyperclip.paste()
        pyperclip.copy(message)
        pyautogui.hotkey('ctrl', 'v')
        pyperclip.copy(buffer)
        passed()
    else:
        step(ctx, f'Набрать на клавиатуре {message} ...')
        pyautogui.write(message)
        passed()


def setup_test_env(cmd, out_log, err_log):
    """Setup test environment (run cmd) before execute test cases"""
    print('## Подготовка стенда к работе')
    print(f'{cmd} ...')
    env = os.environ.copy()
    dirName = os.path.dirname(cmd)
    if dirName == '':
        dirName = os.path.expanduser('~')
    with subprocess.Popen(
        [cmd], stderr=err_log,
        stdout=out_log, env=env,
        cwd=dirName) as testProc:
        time.sleep(1)
        if testProc is not None:
            passed()
        return testProc


def teardown_test_env(ctx, test_proc):
    """Tear down test suite after all test cases done"""
    print('## Завершение работы стенда')
    alt_with_key(ctx, 'f4')
    test_proc.kill()
    passed()


def print_test_summary(list_passed, list_failed):
    """Functions print tests summary for executed suites"""
    print()
    print('## Результаты тестирования')
    print('Тесты завершенные успешно:')
    for t in list_passed:
        print('* ', t)
    print()
    print('Тесты завершенные неуспешно:')
    for t in list_failed:
        print('* ', t)
    print()
    print('**Всего выполнено**')
    print()
    print(
        'Успешно: {:04d} / Неуспешно: {:04d}'.format(len(list_passed), len(list_failed))) # pylint: disable=consider-using-f-string
    print()


def check_text(ctx, img, txt, lang):
    """Checks if text (txt) exists on image (img) printed with language (lang) """
    step(ctx, f'Проверка отображения текста {txt} на изображении {img}...')
    _, _, _, _, flag = findText(img, txt, lang=lang)
    if flag:
        passed()
        return
    failed(img, f'{txt} не найден на изображении')


def check_text_on_screen(ctx, txt, lang):
    """Checks if text (txt) exists on the screen"""
    step(ctx, f'Проверка отображения текста {txt} на экране ...')
    img = pyautogui.screenshot()
    _, _, _, _, flag = findText(img, txt, lang=lang)
    if not flag:
        failed(img, f'{txt} не найден на экране')
    passed()


def clickText(ctx, text, lang, button='left', skip=0):
    """Finds text on screen and press mouse button on it"""
    step(ctx, f'Нажать текст {text} экране кнопкой {button}...')
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
    """Functions recognize all texts on the image with Tesseract"""
    return pytesseract.image_to_data(img, lang)

# DEPRICATED: this function will be removed
# def recognizeText(img, lang):
#    return pytesseract.image_to_string(img, lang=lang)


def combineWordsInLines(lines):
    """Functions combines words recognized on screan into lines"""
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
    """Function translate lines from Tesseract output format into result tuple"""
    result = []
    for i in range(1, len(lines)-1):
        splitted = lines[i].split('\t')
        if len(splitted) != 12:
            return result
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
    """Function finds text in image with Tesseract"""
    recognized = pytesseract.image_to_data(img, lang).split('\n')
    combineWordsInLines(recognized)
    retTup = (-1, -1, -1, -1, False)
    for line in recognized[1:]:
        splitted = line.split('\t')
        if len(splitted) == 12:
            if splitted[11].find(text) != -1:
                print("Найден текст " + splitted[11])
                #x = int(splitted[6]) + int(splitted[8])/2
                #y = int(splitted[7]) + int(splitted[9])/2
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
                        return (croppedTup[0]+int(splitted[6]),
                                croppedTup[1]+int(splitted[7]),
                                croppedTup[2],
                                croppedTup[3],
                                croppedTup[4])
    return retTup


def recognizeText(img, lang):
    """Function recognizes text in image with Tesseract and combine
    lines to tuple and return lists
    """
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
                    slice_for_search = s[i:i+lSearch]
                    r = ratio(search, slice_for_search, score_cutoff=0.8)
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
    """Find text in image. Several passes are used.
    First time found area with text on image and then
    every area passed through recongintion again to improve recognition results"""
    recognized = pytesseract.image_to_data(img, lang).split('\n')
    combineWordsInLines(recognized)
    retTup = (-1, -1, -1, -1, False)
    for line in recognized[1:]:
        splitted = line.split('\t')
        if len(splitted) == 12:
            if splitted[11].find(text) != -1:
                print(f'Найден текст {splitted[11]}')
                #x = int(splitted[6]) + int(splitted[8])/2
                #y = int(splitted[7]) + int(splitted[9])/2
                retTup = (int(splitted[6]), int(splitted[7]), int(
                    splitted[8]), int(splitted[9]), True)
                if skip <= 0:
                    break
                skip -= 1
    return retTup


def findTextOnScreen(ctx, text, lang, skip=0):
    """Function finds text on the screen"""
    step(ctx, f'Поиск текста {text} на экране ...')
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


def findContours(ctx, img, fltr=repeater):
    """Function finds contours by cv and filter them with filter"""
    step(ctx, 'Поиск контуров с применением селектора')
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
    """Generate randomized string of acsii letters"""
    letters = string.ascii_letters + ' _' + string.digits
    return ''.join(random.choice(letters) for _ in range(stringLength))


def run(funcs, counter=1, output='output'):
    """Execute test suite (list of test cases) one by one"""
    global OUTPUT_PATH
    try:
        os.makedirs(output)
    except: # pylint: disable=bare-except
        pass
    for _ in range(counter):
        for f in funcs:
            testName = f.__name__
            try:
                os.makedirs(os.path.join(output, SUITE_NAME, testName))
            except: # pylint: disable=bare-except
                pass
            try:
                OUTPUT_PATH = os.path.join(output, SUITE_NAME, testName)
                f()
                TESTS_PASSED.append(os.path.join(SUITE_NAME, testName))
                imgPath = os.path.join(
                    output, SUITE_NAME, testName, 'test-passed.png')
                pyautogui.screenshot(imgPath)
                relativePath = imgPath.split(os.path.sep)
                tmpPath = os.path.join('', *relativePath[1:])
                print(f'![Тест пройден]({tmpPath})')
                print()
                print('**Тест пройден**')
            except TestException as e:
                imgPath = os.path.join(
                    output, SUITE_NAME, testName, 'test-failed.png')
                pyautogui.screenshot(imgPath)
                print(f'\n> Error : {e.message}\n')
                relativePath = imgPath.split(os.path.sep)
                tmpPath = os.path.join('', *relativePath[1:])
                print(f'![Тест не пройден]({tmpPath})')
                print()
                print('**Тест не пройден**')
                TESTS_FAILED.append(os.path.join(SUITE_NAME, testName))

    print_test_summary(TESTS_PASSED, TESTS_FAILED)
