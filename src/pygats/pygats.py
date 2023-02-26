"""
pyGATs tis python3 library which combines power of pyautogui, opencv,
tesseract, markdown and other staff to automate end-to-end and exploratory
testing.
"""
import time
import sys
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


class Context:  # pylint: disable=too-few-public-methods
    """
    Context stores information about
    """
    formatter = None

    def __init__(self, formatter):
        self.formatter = formatter


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
    platform specifics it should be separated in different images. Name of
    image contains platform name picName.PLATFORM.ext

    Args:
        img (string): path to image

    Returns:
        string: path to image
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

    Args:
        ctx (Context): context of test execution
        msg (string): message to print at the beginning of test case
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

    Args:
        ctx (Context): context of test execution
        msg (string): message to print at the beginning of test case
        func (function Optional): function to be printed and called
                during test

    Returns:
        type or None: func() result or None

    """
    ctx.formatter.print_para(f'{msg}')
    if func is not None:
        ctx.formatter.print_code(inspect.getsource(func))
        return func()
    return None


def suite(ctx, name, desc):
    """
    function prints test suite name in reports

    Args:
        ctx (Context): context of test execution
        name (string): name of test suite
        desc (string): description of test suite to be printed
    """
    global SUITE_NAME
    print()
    SUITE_NAME = name
    ctx.formatter.print_header(2, desc)


def step(ctx, msg):
    """
    function prints step name and starts new screenshot index

    Args:
        ctx (Context): context
        msg (string): message to print
    """
    global STEP_INDEX, SCREENSHOT_INDEX
    STEP_INDEX += 1
    SCREENSHOT_INDEX = 0
    msg = f'Step {STEP_INDEX}: {msg}'
    ctx.formatter.print_para(msg)


def screenshot(ctx, rect=None):
    """Takes a screenshot, optionally limited to the rectangle
    defined by `rect`.

    Args:
        ctx (object): An object that contains information about the current
                    context.
        rect (tuple, optional): A tuple of four integers
            that defines the area of the screenshot to capture.
            x (int): x coordinate
            y (int): y coordinate
            width (int): width of rect
            height (int): height of rect

    Returns:
        PIL.Image: The screenshot as a PIL.Image object.

    Notes:
        The screenshot is also stored in the output path as `screenshotIndex`.
    """
    global SCREENSHOT_INDEX
    img_path = os.path.join(
        OUTPUT_PATH, f'step-{STEP_INDEX}-{SCREENSHOT_INDEX}-passed.png')
    SCREENSHOT_INDEX += 1

    # Take the screenshot and store it on disk
    img = pyautogui.screenshot(img_path, region=rect)
    # Get the relative path to the screenshot file
    relative_path = img_path.split(os.path.sep)
    tmp_path = os.path.join('', *relative_path[1:])
    # Display the screenshot
    ctx.formatter.print_img(tmp_path)
    return img


def log_image(img, msg='Снимок экрана'):
    """
    Function log img with msg into report
    image is stored in output path as screenshotIndex

    Args:
        img (PIL.Image): image to be logged
        msg (str, optional): description of the screenshot.
            Defaults to 'Снимок экрана'.

    Returns:
        PIL.Image: input image
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
    function generates exception while error occurs

    Args:
        img (PIL.Image, optional): image or screenshot
        msg (string, optional): failed text

    Raises:
        TestException: raise exception in case of test failed
    """
    raise TestException(img, msg)


def check_image(ctx, img, timeout=1):
    """Check if image is located on screen. Timeout in second waiting image
    to occurs

    Args:
        ctx (Context): context
        img (PIL.Image): image to check on screen
        timeout (int): timeout in seconds to check if image occurs
    """
    img = platform_specific_image(img)
    step(ctx, f'Проверка отображения {img} ...')
    # try:
    while timeout > 0:
        if locate_on_screen(img) is not None:
            passed()
            return
        timeout -= 1
        time.sleep(1)
    # except:  # pylint: disable=bare-except
    #     print('Exception')
    #     failed(img, 'Изображение не найдено')
    # failed(img, 'Изображение не найдено')


def locate_on_screen(img):
    """Function return coord of image located on screen.
    If not found returns None

    Args:
        img (PIL.Image): image to find

    Returns:
        (x,y): coordinates image on screen
    """
    img = platform_specific_image(img)
    coord = pyautogui.locateOnScreen(img, confidence=0.5)
    print(f'Изображение найдено в координатах {coord}')
    return coord


def move_to_coord(ctx, x, y):
    """Function moves mouse to coord x,y

    Args:
        ctx (Context): context
        x (int): x coordinate
        y (int): y coordinate
    """
    step(ctx, f'Переместить указатель мыши в координаты {x},{y}')
    pyautogui.moveTo(x, y)
    passed()


def move_to(ctx, img):
    """Function move mouse to img

    Args:
        ctx (Context): context
        img (PIL.Image): image to move to

    """
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


def click_right_button(ctx):
    """function clicks right mouse button

    Args:
        ctx (Context): context
    """
    step(ctx, 'Нажать правую кнопку мыши ...')
    pyautogui.click(button='right')
    print(f'Текущая позиция указателя мыши {pyautogui.position()}')
    passed()


def click_left_button(ctx):
    """function clicks left button of mouse

    Args:
        ctx (Context): context
    """
    step(ctx, 'Нажать левую кнопку мыши ...')
    pyautogui.click(button='left')
    print(f'Текущая позиция указателя мыши {pyautogui.position()}')
    passed()


def click(ctx, btn, area=''):
    """function clicks button in area

    Args:
        ctx (Context): context
        btn (string): path to button image to press
        area (string, optional): path to area of image to print
    """
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

    Args:
        ctx (Context): context
        key (char): key to press CTRL+key
    """
    step(ctx, f'Нажать клавишу ctrl+{key}')
    pyautogui.hotkey('ctrl', key)
    passed()


def alt_with_key(ctx, key):
    """
    function presses alt+key

    Args:
        ctx (Context): context
        key (char): key to press ALT+key
    """
    step(ctx, f'Нажать клавишу alt+{key}')
    pyautogui.hotkey('alt', key)
    passed()


def drag_to(ctx, x, y):
    """
    drag something to coordinates x, y

    Args:
        ctx (Context): context
        x (int): coordinates to move mouse pointer
        y (int): coordinates to move mouse pointer
    """
    step(ctx, f'Переместить в координаты {x}, {y} ...')
    pyautogui.dragTo(x, y, button='left', duration=0.5)
    passed()


def move(ctx, x, y):
    """
    function moves mouse pointer to x,y coordinates

    Args:
        ctx (Context): context
        x (int): coordinates to move mouse pointer
        y (int): coordinates to move mouse pointer
    """
    step(ctx, f'Относительное перемещение указателя мыши x={x}, y={y} ...')
    print(f'из координат {pyautogui.position()}')
    pyautogui.move(x, y)
    print(f'новые координаты {pyautogui.position()}')
    passed()


def keyboard(ctx, message):
    """
    function types message on keyboard with 0.1 sec delay of each symbol
    At the end <Enter> is pressed

    Args:
        ctx (Context): context
        message (string): text to type on keyboard
    """
    step(ctx, f'Набрать на клавиатуре и нажать <Enter>: {message} ...')
    pyautogui.write(message, 0.1)
    pyautogui.press('enter')
    passed()


def press(ctx, key, n=1):
    """Function press keys n times

    Args:
        ctx (Context): context
        key (char): key to press
        n (int): amount of time to press
    """
    step(ctx, f'Нажать {key} {n} раз')
    for _ in range(n):
        pyautogui.press(key)


def typewrite(ctx, message, lang='eng'):
    """function types keys on keyboard

    Args:
        ctx (Context): context
        message (string): text to typewrite
        lang (string): language in tesseract format

    """
    if lang != 'eng':
        clipboard = pyperclip.paste()
        pyperclip.copy(message)
        pyautogui.hotkey('ctrl', 'v')
        pyperclip.copy(clipboard)
        passed()
    else:
        step(ctx, f'Набрать на клавиатуре {message} ...')
        pyautogui.write(message)
        passed()


def print_test_summary(list_passed, list_failed):
    """Functions print tests summary for executed suites

    Args:
        list_passed (list): list of test passed
        list_failed (list): list of test failed
    """
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
    # pylint: disable=consider-using-f-string
    print(
        'Успешно: {:04d} / Неуспешно: {:04d}'.format(
            len(list_passed), len(list_failed)))
    print()


def check_text(ctx, img, txt, lang):
    """Checks if text (txt) exists on image (img) printed with language (lang)

    Args:
        ctx (Context): context
        img (PIL.Image): image to find text
        txt (string): text to search
        lang (string): language in tesseract

    """
    step(ctx, f'Проверка отображения текста {txt} на изображении {img}...')
    _, _, _, _, flag = findText(img, txt, lang=lang)
    if flag:
        passed()
        return
    failed(img, f'{txt} не найден на изображении')


def check_text_on_screen(ctx, txt, lang):
    """Checks if text (txt) exists on the screen

    Args:
        ctx (Context): context
        txt (string): text to search on screenshot
        lang (string): language in tesseract format
    """
    step(ctx, f'Проверка отображения текста {txt} на экране ...')
    img = pyautogui.screenshot()
    _, _, _, _, flag = findText(img, txt, lang=lang)
    if not flag:
        failed(img, f'{txt} не найден на экране')
    passed()


def click_text(ctx, text, lang, button='left', skip=0):
    """Finds text on screen and press mouse button on it

    Args:
        ctx (Context): execution context
        text (string): text to be searched and clicked
        lang (string): language in tesseract format
        button (string, optional): left, right, middle
        skip (int): amount of text should be skipped
    """
    step(ctx, f'Нажать текст {text} на экране кнопкой {button}...')
    x, y, width, height, found = findTextOnScreen(ctx, text, lang, skip)
    if not found:
        failed(msg=f'{text} не найден на экране')

    print(x, y, width, height)
    center_x = x + width/2
    center_y = y + height/2
    pyautogui.moveTo(center_x, center_y)
    pyautogui.mouseDown(center_x, center_y, button)
    pyautogui.mouseUp(center_x, center_y, button)
    passed()


def recognizeTextWithData(img, lang):
    """Functions recognize all texts on the image with Tesseract

    Args:
        img (PIL.Image): input image to recognize text
        lang (string): languange in tesseract format

    Returns:
        list: recognized text
    """
    return pytesseract.image_to_data(img, lang)


def combine_words_in_lines(lines):
    """Functions combines words recognized on screan into lines

    Args:
        lines (List): Returns result containing box boundaries, confidences,
            and other information.

    Returns:
        list: combined lines

    Notes:
        Now this function just add other words to the left most. No box rect is
        adjusted.

    Todo:
        * This function should adjust rect (width) of left most word when added
        new word to it.
    """
    for i in range(1, len(lines)-1):
        splitted = lines[i].split('\t')
        if len(splitted) != 12:
            return
        y = int(splitted[7])
        for j in range(i+1, len(lines)-1):
            splitted2 = lines[j].split('\t')
            if abs(y-int(splitted2[7])) < 5 and len(splitted2[11].strip()) > 0:
                lines[i] += ' ' + splitted2[11]


def combine_lines(lines):
    """Function translate lines from Tesseract output format into
    result tuple

    Args:
        lines (List): Returns result containing box boundaries, confidences,
            and other information.

    Returns:
        list: combined tuples

    Notes:
        There is magic number 5 to undersdand if words on the same line.
        It should be reworked in future.

    Todo:
        * This function should be reworked in future with
          combine_words_in_lines. Need one function to combine words in
          sentences.
    """
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
    """Function finds text in image with Tesseract

    Args:
        img (PIL.Image): image where text will be recognized
        text (string): text which fill be searched
        lang (string): language of text (tesseract-ocr)
        skip (int): amount of skipped finding

    Returns:
        (x,y,w,h,text):
            x (int), y (int): coordinates of top-left point of rectangle where
               text resides
            w (int), h (int): width and height of rectangle where text resides
            text (string): full text which resides in rectangle

    """
    recognized = pytesseract.image_to_data(img, lang).split('\n')
    combine_words_in_lines(recognized)
    ret_tuple = (-1, -1, -1, -1, False)
    for line in recognized[1:]:
        splitted = line.split('\t')
        if len(splitted) == 12:
            if splitted[11].find(text) != -1:
                print("Найден текст " + splitted[11])
                ret_tuple = (int(splitted[6]), int(splitted[7]), int(
                    splitted[8]), int(splitted[9]), True)
                if skip <= 0:
                    break
                skip -= 1
            else:
                if int(splitted[6]) + int(splitted[7]) != 0:
                    cropped = img.crop((int(splitted[6]), int(splitted[7]),
                                        int(splitted[6])+int(splitted[8]),
                                        int(splitted[7])+int(splitted[9])))
                    cropped_tuple = find_cropped_text(cropped, text, lang)
                    if cropped_tuple[4]:
                        return (cropped_tuple[0]+int(splitted[6]),
                                cropped_tuple[1]+int(splitted[7]),
                                cropped_tuple[2],
                                cropped_tuple[3],
                                cropped_tuple[4])
    return ret_tuple


def recognizeText(img, lang):
    """Function recognizes text in image with Tesseract and combine
    lines to tuple and return lists

    Args:
        img (PIL.Image): image where text will be recognized
        lang (string): language of text (tesseract-ocr)

    Returns:
        (x,y,w,h,text):
            x (int), y (int): coordinates of top-left point of rectangle where
               text resides
            w (int), h (int): width and height of rectangle where text resides
            text (string): full text which resides in rectangle

    Notes:
        This is wrapper function to pytesseract.image_to_data. Results of
        image_to_data are combined to lines.
    """
    recognized = pytesseract.image_to_data(img, lang).split('\n')
    result = combine_lines(recognized)
    return list(set(result))


def find_fuzzy_text(recognized_list, search):
    """Fuzzy search of text in list using Levenshtein ratio
    Return value is list of tuples with following format:

    Args:
        recognized_list (list): list of text to match with pattern
        search (string): substring to search

    Returns:
        (x,y,w,h,text, substring):
            x (int), y (int): coordinates of top-left point of rectangle where
               text resides
            w (int), h (int): width and height of rectangle where text resides
            text (string): full text which resides in rectangle
            substring (string): substring found in text
    """
    result = []
    lSearch = len(search)
    for item in recognized_list:
        r = ratio(search, item[4], score_cutoff=0.5)
        if r > 0.0:
            result.append(item)
        else:
            s = item[4]
            if len(s) > lSearch:
                for i in range(0, len(s)-lSearch):
                    slice_for_search = s[i:i+lSearch]
                    r = ratio(search, slice_for_search, score_cutoff=0.8)
                    if r > 0.0:
                        result.append(item)
    return list(set(result))


def findRegExpText(recognized_list, pattern):
    """Find text in list by regexp
    Return value is list of tuples with following format

    Args:
        recognized_list (list): list of text to match with pattern
        pattern (string): regex pattern to match

    Returns:
        (x,y,w,h,text, substring):
            x (int), y (int): coordinates of top-left point of rectangle where
               text resides
            w (int), h (int): width and height of rectangle where text resides
            text (string): full text which resides in rectangle
            substring (string): substring found in text
    """
    result = []
    for item in recognized_list:
        m = re.findall(pattern, item[4])
        if len(m) > 0:
            item += tuple(m)
            result.append(item)
    return list(set(result))


def find_cropped_text(img, text, lang, skip=0):
    """
    Find text in image. Several passes are used.
    First time found area with text on image and then
    every area passed through recongintion again to improve recognition results

    Args:
        img (PIL.Image): image to search text in
        text (str): text to search
        lang (str): language code of the text
        skip (int, optional): number of occurrences of the text to skip.

    Returns:
        (left, top, width, height, found):
            left (int): left coordinate of the text bounding box
            top (int): top coordinate of the text bounding box
            width (int): width of the text bounding box
            height (int): height of the text bounding box
            found (bool): whether the text is found in the image

    """
    recognized = pytesseract.image_to_data(img, lang).split('\n')
    combine_words_in_lines(recognized)
    ret_tuple = (-1, -1, -1, -1, False)
    for line in recognized[1:]:
        splitted = line.split('\t')
        if len(splitted) == 12 and splitted[11].find(text) != -1:
            print(f'Найден текст {splitted[11]}')
            ret_tuple = (int(splitted[6]), int(splitted[7]), int(
                splitted[8]), int(splitted[9]), True)
            if skip <= 0:
                break
            skip -= 1
    return ret_tuple


def findTextOnScreen(ctx, text, lang, skip=0):
    """
    Function finds text on the screen

    Args:
        ctx (Context): context
        text (string): text to find
        lang (string): language of the text (tesseract-ocr)
        skip (int, optional): amount of findings which should be skipped

    Returns:
        (left, top, width, height, found):
            left (int): left coordinate of the text bounding box
            top (int): top coordinate of the text bounding box
            width (int): width of the text bounding box
            height (int): height of the text bounding box
            found (bool): whether the text is found in the image
    """
    step(ctx, f'Поиск текста {text} на экране ...')
    img = pyautogui.screenshot()
    return findText(img, text, lang, skip)


def repeater(cnts):
    """
    This function is default selector for contours

    Args:
        cnts (list): list of points to be filtered

    Returns:
        list: unchanged list of points
    """
    return cnts


def filter_rect_sorted(cnts):
    """Filter and sort contours to get rectangles

    Args:
        cnts (List[Numpy.ndarray]): list of contours

    Returns:
        List[Numpy.ndarray]: list of filtered and sorted rectangles

    """
    def approxer(x):
        """
        Approximate polygonal curves to rectangles

        Args:
            x (list): list of vertexes

        Returns:
            rect: rect which approximate polygonal curves
        """
        epsilon = 0.01 * cv.arcLength(x, True)
        return cv.approxPolyDP(x, epsilon, True)

    def rect_filter(x):
        """
        Filter contours that approximate to rectangles

        Args:
            x (list): list of vertexes

        Returns:
            bool: true if x is rectangle
        """
        return len(x) == 4

    cnts = list(filter(rect_filter, map(approxer, cnts)))
    cnts = sorted(cnts, key=lambda x: abs(x.item(4)-x.item(0))
                  * abs(x.item(5)-x.item(1)), reverse=True)
    return cnts


def find_contours(ctx, img, fltr=repeater):
    """
    Function finds contours by cv and filter them with filter

    Args:
        ctx (Context): context of test run
        img (PIL.Image): image where contours will be searched
        fltr (function, optional): filter which will be used on contours
            results

    Returns:
        list of points: list of points filtered
    """
    step(ctx, 'Поиск контуров с применением селектора')
    npImg = np.array(img)
    gray = cv.cvtColor(npImg, cv.COLOR_BGR2GRAY)
    _, thresh = cv.threshold(gray, 127, 255, cv.THRESH_BINARY)
    cnts, _ = cv.findContours(
        thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    return fltr(cnts)


def drawContours(img, cnts):
    """
    Draw contours on a PIL.Image instance.

    Args:
        img (PIL.Image): Input image on which to draw the contours.
        cnts (list of numpy.ndarray): List of contours, represented
            as Numpy arrays.

    Returns:
        PIL.Image: Output image with contours drawn.

    Raises:
        TypeError: If `img` is not a `PIL.Image` instance.
        ValueError: If `cnts` is not a list of Numpy arrays.
    """
    if not isinstance(img, Image.Image):
        raise TypeError("img must be a PIL.Image instance")
    if not all(isinstance(cnt, np.ndarray) for cnt in cnts):
        raise ValueError("cnts must be a list of Numpy arrays")
    npImg = np.array(img)
    cv.drawContours(npImg, cnts, -1, (0, 255, 0), 3)
    return Image.fromarray(npImg)


def random_string(string_length, character_set=None):
    """Generate a randomized string of characters.

    Args:
        string_length (int): The length of the generated string.
        character_set (string, optional): A string of characters to use
            when generating the random string. Defaults to ascii letters,
            digits and the underscore.

    Returns:
        str: A string of the specified length, consisting of characters from
            the character set.

    Raises:
        ValueError: If `string_length` is not a positive integer.

    Examples:
        >>> random_string(5)
        'W3t9_'
        >>> random_string(5, character_set='01')
        '10101'
    """
    if string_length <= 0:
        raise ValueError("string_length must be a positive integer")
    if character_set is None:
        character_set = string.ascii_letters + ' _' + string.digits
    return ''.join(random.choice(character_set) for _ in range(string_length))


def run(funcs, counter=1, output='output'):
    """
    Execute test suite (list of test cases) one by one

    Args:
        funcs (list of strings): list of function to be executed
        counter (int Optional): amount to time test cases to be executed
        output (string): path to store test results
    """
    global OUTPUT_PATH
    try:
        os.makedirs(output)
    except FileExistsError:
        pass
    for _ in range(counter):
        for f in funcs:
            testName = f.__name__
            try:
                os.makedirs(os.path.join(output, SUITE_NAME, testName))
            except FileExistsError:
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
