"""
pyGATs is python3 library which combines power of pyautogui, opencv,
tesseract, markdown and other staff to automate end-to-end and exploratory
testing.
"""
import time
import sys
import os
import string
import random
import inspect
from typing import Optional, List
import pyautogui
import pyperclip
from PIL import Image, ImageChops
import cv2 as cv
import numpy as np

from pygats.formatters import print_color_text

PLATFORM = ''
TESTS_PASSED = []
TESTS_FAILED = []
STEP_INDEX = 0
SCREENSHOTS_ON = True
SCREENSHOT_INDEX = 0
OUTPUT_PATH = 'output'
SNAPSHOT_PATH = ''
SNAPSHOT_INDEX = 0
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


def platform_specific_image(image_path: str) -> str:
    """
    function returns platform specific path to the image. If screenshot has
    platform specifics it should be separated in different images. Name of
    image contains platform name picName.PLATFORM.ext

    Args:
        image_path (str): path to image

    Returns:
        str: path to image
    """
    if PLATFORM == '':
        return image_path

    path_parts = image_path.split('.')
    if len(path_parts) == 2:
        specific_image_path = path_parts[0] + '.' + PLATFORM + '.' + path_parts[1]
        if os.path.exists(specific_image_path):
            return specific_image_path

    return image_path


def begin_test(ctx: Context, msg: str):
    """
    Begin of test. Dump msg as name of the test

    Args:
        ctx (Context): context of test execution
        msg (str): message to print at the beginning of test case
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


def check(ctx: Context, msg: str, func=None):
    """
    Prints message as check block

    Args:
        ctx (Context): context of test execution
        msg (str): message to print at the beginning of test case
        func: pointer to function to be printed and called
        during test  # noqa: DAR003

    Returns:
        type or None: func() result or None

    """
    ctx.formatter.print_para(f'{msg}')
    if func is not None:
        ctx.formatter.print_code(inspect.getsource(func))
        return func()
    return None


def suite(ctx: Context, name: str, desc: str):
    """
    function prints test suite name in reports

    Args:
        ctx (Context): context of test execution
        name (str): name of test suite
        desc (str): description of test suite to be printed
    """
    global SUITE_NAME
    print()
    SUITE_NAME = name
    ctx.formatter.print_header(2, desc)


def step(ctx: Context, msg: str):
    """
    function prints step name and starts new screenshot index

    Args:
        ctx (Context): context
        msg (str): message to print
    """
    global STEP_INDEX, SCREENSHOT_INDEX
    STEP_INDEX += 1
    SCREENSHOT_INDEX = 0
    msg = f'Step {STEP_INDEX}: {msg}'
    ctx.formatter.print_para(msg)


def screenshot(ctx: Context, rect: Optional[tuple] = None):
    """Takes a screenshot, optionally limited to the rectangle
    defined by `rect`.

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        rect (Optional[tuple]): A tuple of four integers
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


def take_snapshot(ctx: Context) -> str:
    """Function takes a snapshot to further detect changes on the screen

    Args:
        ctx (Context): An object that contains information about the current
                    context.

    Returns:
        tmp_path (str): path to snapshot
    """
    step(ctx, 'Создание снимка для поиска изменений на экране')
    global SNAPSHOT_PATH
    global SNAPSHOT_INDEX
    SNAPSHOT_PATH = os.path.join(OUTPUT_PATH, "compare")
    try:
        os.makedirs(SNAPSHOT_PATH)
    except FileExistsError:
        pass
    img_path = os.path.join(SNAPSHOT_PATH, f'snapshot-{SNAPSHOT_INDEX}.png')
    pyautogui.screenshot(img_path)
    relative_path = img_path.split(os.path.sep)
    tmp_path = os.path.join('', *relative_path[1:])
    SNAPSHOT_INDEX += 1
    print()
    print(f'![Снимок экрана]({tmp_path})')
    print()
    return tmp_path


def compare_snapshots(ctx: Context, first_image: str, second_image: str) -> tuple or None:
    """Function for comparing two images

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        first_image (str): path to first snapshot for compare
        second_image (str): path to second snapshot for compare

    Returns:
        tupple or None: coordinates of the change detection area
    """
    step(ctx, 'Поиск изменений между снимками ...')
    print()
    print(f'![Первый снимок]({first_image})')
    print()
    print(f'![Второй снимок]({second_image})')
    print()
    first = Image.open(os.path.join('./output', first_image))
    second = Image.open(os.path.join('./output', second_image))
    result = ImageChops.difference(first, second)
    if result.getbbox() is not None:
        relative_path = first_image.split('-')
        first_index = relative_path[len(relative_path) - 1].split('.')[0]
        relative_path = second_image.split('-')
        second_index = relative_path[len(relative_path) - 1].split('.')[0]
        result_path = os.path.join(SNAPSHOT_PATH, f'result-{first_index}-{second_index}.png')
        result.save(result_path)
        relative_path = result_path.split(os.path.sep)
        tmp_path = os.path.join('', *relative_path[1:])
        print(f'![Найдены изменения]({tmp_path})')
        print()
        print('**Найдены изменения**')
        print()
        return result.getbbox()
    print()
    print('**Изменения не найдены**')
    print()
    return None


def log_image(img: Image, msg: Optional[str] = 'Снимок экрана'):
    """
    Function log img with msg into report
    image is stored in output path as screenshotIndex

    Args:
        img (Image): image to be logged
        msg (str, optional): description of the screenshot.
        Defaults to 'Снимок экрана'.  # noqa: DAR003

    Returns:
        PIL.Image: input image
    """
    global SCREENSHOT_INDEX
    image_path = os.path.join(
        OUTPUT_PATH, f'step-{STEP_INDEX}-{SCREENSHOT_INDEX}-passed.png')
    SCREENSHOT_INDEX += 1
    img.save(image_path)
    relative_path = image_path.split(os.path.sep)
    tmp_path = os.path.join('', *relative_path[1:])
    print(f'![{msg}]({tmp_path})')
    print()
    return img


def passed():
    """
    function prints passed information after test case
    """
    if SCREENSHOTS_ON:
        image_path = os.path.join(OUTPUT_PATH, f'step-{STEP_INDEX}-passed.png')
        pyautogui.screenshot(image_path)
        relative_path = image_path.split(os.path.sep)
        tmp_path = os.path.join('', *relative_path[1:])
        print(f'![Успешно]({tmp_path})')
    print()
    print('**Успешно**')
    print()


def failed(img=pyautogui.screenshot(), msg: Optional[str] = 'Тест не успешен'):
    """
    function generates exception while error occurs

    Args:
        img (PIL.Image, optional): image or screenshot
        msg (Optional[str]): failed text

    Raises:
        TestException: raise exception in case of test failed
    """
    raise TestException(img, msg)


def check_image(ctx: Context, img_path: str, timeout: Optional[int] = 1):
    """Check if image is located on screen. Timeout in second waiting image
    to occurs

    Args:
        ctx (Context): context
        img_path (str): path to image for check on screen
        timeout (Optional[int]): timeout in seconds to check if image occurs
    """
    img_path = platform_specific_image(img_path)
    step(ctx, f'Проверка отображения {img_path} ...')
    # try:
    while timeout > 0:
        if locate_on_screen(img_path) is not None:
            passed()
            return
        timeout -= 1
        time.sleep(1)
    # except:  # pylint: disable=bare-except
    #     print('Exception')
    #     failed(img_path, 'Изображение не найдено')
    # failed(img_path, 'Изображение не найдено')


def locate_on_screen(img_path: str):
    """Function return coord of path to image located on screen.
    If not found returns None

    Args:
        img_path (str): path to image to find

    Returns:
        (x,y): coordinates path for image on screen
    """
    img_path = platform_specific_image(img_path)
    coord = pyautogui.locateOnScreen(img_path, confidence=0.5)
    print(f'Изображение найдено в координатах {coord}')
    return coord


def move_to_coord(ctx: Context, x: int, y: int):
    """Function moves mouse to coord x,y

    Args:
        ctx (Context): context
        x (int): x coordinate
        y (int): y coordinate
    """
    step(ctx, f'Переместить указатель мыши в координаты {x},{y}')
    pyautogui.moveTo(x, y)
    passed()


def move_to(ctx: Context, img_path: str):
    """Function move mouse to img_path

    Args:
        ctx (Context): context
        img_path (str): path to image for move to

    """
    img_path = platform_specific_image(img_path)
    step(ctx, f'Переместить указатель мыши на изображение {img_path} ...')
    center = pyautogui.locateCenterOnScreen(img_path, confidence=0.8)
    if center is None:
        failed(img_path, 'Изображение не найдено')
    if sys.platform == 'darwin':
        pyautogui.moveTo(center.x / 2, center.y / 2)
    else:
        pyautogui.moveTo(center.x, center.y)
    print(f'Текущая позиция указателя мыши {pyautogui.position()}')
    passed()


def click_right_button(ctx: Context):
    """function clicks right mouse button

    Args:
        ctx (Context): context
    """
    step(ctx, 'Нажать правую кнопку мыши ...')
    pyautogui.click(button='right')
    print(f'Текущая позиция указателя мыши {pyautogui.position()}')
    passed()


def click_left_button(ctx: Context, clicks: Optional[int] = 1):
    """function clicks left button of mouse

    Args:
        ctx (Context): context
        clicks (Optional[int]): number of clicks
    """
    step(ctx, 'Нажать левую кнопку мыши ...')
    pyautogui.click(button='left', clicks=clicks, interval=0.2)
    print(f'Текущая позиция указателя мыши {pyautogui.position()}')
    passed()


def click(ctx: Context, button_path: str, area: Optional[str] = ''):
    """function clicks button in area

    Args:
        ctx (Context): context
        button_path (str): path to button image to press
        area (Optional[str]): path to area of image to print
    """
    button_path = platform_specific_image(button_path)
    area = platform_specific_image(area)
    fail_message = 'Изображение не найдено'
    step(ctx, f'Нажать кнопку мыши {button_path} ...')
    if area == '':
        center = pyautogui.locateCenterOnScreen(button_path, confidence=0.8)
        print(f'Кнопка найдена с центром в координатах {center}')
    else:
        print(" area " + area)
        area_location = pyautogui.locateOnScreen(area, confidence=0.9)
        if area_location is None:
            failed(area, fail_message)
        box = pyautogui.locate(button_path, area, confidence=0.8)
        if box is None:
            failed(area, fail_message)

        x = area_location.left + box.left + box.width / 2
        y = area_location.top + box.top + box.height / 2
        center = pyautogui.Point(x, y)
    if center is None:
        failed(button_path, fail_message)

    print(f'Перемещаем указатель мыши в координаты {center}')
    if sys.platform == 'darwin':
        pyautogui.moveTo(center.x / 2, center.y / 2)
    else:
        pyautogui.moveTo(center.x, center.y)
    # pyautogui.dragTo()
    pyautogui.click()
    passed()


def scroll(ctx: Context, clicks: Optional[int] = 1):
    """mouse wheel scroll function

    Args:
        ctx (Context): context
        clicks (Optional[int]): number of turns of mouse wheel, if it's positive scroll to up,
                                if it's negative to down
    """
    step(ctx, 'Прокрутка колеса мыши ...')
    pyautogui.scroll(clicks=clicks)
    passed()


def ctrl_with_key(ctx: Context, key: str):

    """
    function presses key with ctrl key

    Args:
        ctx (Context): context
        key (str): key to press CTRL + key
    """
    step(ctx, f'Нажать клавишу ctrl + {key}')
    pyautogui.hotkey('ctrl', key)
    passed()


def alt_with_key(ctx: Context, key: str):
    """
    function presses alt+key

    Args:
        ctx (Context): context
        key (str): key to press ALT + key
    """
    step(ctx, f'Нажать клавишу alt+{key}')
    pyautogui.hotkey('alt', key)
    passed()


def drag_to(ctx: Context, x: int, y: int):
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


def move(ctx: Context, x: int, y: int):
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


def press(ctx: Context, key: str, n: Optional[int] = 1):
    """Function press keys n times

    Args:
        ctx (Context): context
        key (str): key to press
        n (Optional[int]): amount of time to press
    """
    step(ctx, f'Нажать {key} {n} раз')
    for _ in range(n):
        pyautogui.press(key)


def typewrite(ctx: Context, message: str, lang: Optional[str] = 'eng'):
    """function types keys on keyboard

    Args:
        ctx (Context): context
        message (str): text to typewrite
        lang (Optional[str]): language in tesseract format

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


def print_test_summary(list_passed: List, list_failed: List):
    """Functions print tests summary for executed suites

    Args:
        list_passed (List): list of test passed
        list_failed (List): list of test failed
    """
    # pylint: disable=consider-using-f-string
    print()
    print('## Результаты тестирования')
    print_color_text('Тесты завершенные успешно:', 'green')
    for t in list_passed:
        print_color_text('* ' + t, 'green')
    print()
    print_color_text('Тесты завершенные неуспешно:', 'red')
    for t in list_failed:
        print_color_text('* ' + t, 'red')
    print()
    print('**Всего выполнено**')
    print()
    print(
        'Успешно: {:04d} / Неуспешно: {:04d}'.format(
            len(list_passed), len(list_failed)))
    print()


def repeater(cnts: List):
    """
    This function is default selector for contours

    Args:
        cnts (List): list of points to be filtered

    Returns:
        list: unchanged list of points
    """
    return cnts


def filter_rect_sorted(cnts: List[np.ndarray]) -> List[np.ndarray]:
    """Filter and sort contours to get rectangles

    Args:
        cnts (List[np.ndarray]): list of contours

    Returns:
        List[np.ndarray]: list of filtered and sorted rectangles

    """
    def approx(x):
        """
        Approximate polygonal curves to rectangles

        Args:
            x (list): list of vertexes

        Returns:
            rect: rect which approximate polygonal curves
        """
        epsilon = 0.025 * cv.arcLength(x, True)
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

    cnts = list(filter(rect_filter, map(approx, cnts)))
    cnts = sorted(cnts, key=lambda x: abs(x.item(4) - x.item(0)) * abs
                  (x.item(5) - x.item(1)), reverse=True)
    return cnts


def find_contours(ctx: Context, image_path: str, fltr=repeater):
    """
    Function finds contours by cv and filter them with filter

    Args:
        ctx (Context): context of test run
        image_path (str): path to image where contours will be searched
        fltr (function, optional): filter which will be used on contours
        results  # noqa: DAR003

    Returns:
        list of points: list of points filtered
    """
    step(ctx, 'Поиск контуров с применением селектора')
    image = cv.imread(image_path)
    image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    edges = cv.Canny(image_gray, 50, 100)
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))
    edges = cv.dilate(edges, kernel, iterations=1)
    contours, _ = cv.findContours(
        image=edges, mode=cv.RETR_TREE, method=cv.CHAIN_APPROX_NONE)
    return fltr(contours)


def draw_contours(image: Image, cnts: List[np.ndarray]) -> Image:
    """
    Draw contours on a PIL.Image instance.

    Args:
        image (Image): Input image on which to draw the contours.
        cnts (List[np.ndarray]): List of contours, represented
        as Numpy arrays.  # noqa: DAR003

    Returns:
        Image: Output image with contours drawn.

    Raises:
        TypeError: If `img` is not a `PIL.Image` instance.
        ValueError: If `cnts` is not a list of Numpy arrays.
    """
    if not isinstance(image, Image.Image):
        raise TypeError("img must be a PIL.Image instance")
    if not all(isinstance(cnt, np.ndarray) for cnt in cnts):
        raise ValueError("cnts must be a list of Numpy arrays")
    np_img = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
    cv.drawContours(np_img, cnts, -1, (0, 255, 0), lineType=cv.LINE_AA)
    return Image.fromarray(cv.cvtColor(np_img, cv.COLOR_BGR2RGB))


def random_string(string_length: int, character_set: Optional[str] = None):
    """Generate a randomized string of characters.

    Args:
        string_length (int): The length of the generated string.
        character_set (Optional[str]): A string of characters to use
        when generating the random string. Defaults are  # noqa: DAR003
        ascii letters, digits and the underscore.  # noqa: DAR003

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


def run(funcs: List[str], counter: Optional[int] = 1, output: Optional[str] = 'output',
        screenshots_on: Optional[bool] = True):
    """
    Execute test suite (list of test cases) one by one

    Args:
        funcs (List[str]) list of function to be executed
        counter (Optional[int]): amount to time test cases to be executed
        output (Optional[str]): path to store test results
        screenshots_on (Optional[bool]): create screenshots while running tests
    """
    global OUTPUT_PATH
    global SCREENSHOTS_ON
    SCREENSHOTS_ON = screenshots_on
    try:
        os.makedirs(output)
    except FileExistsError:
        pass
    for _ in range(counter):
        for f in funcs:
            test_name = f.__name__
            try:
                os.makedirs(os.path.join(output, SUITE_NAME, test_name))
            except FileExistsError:
                pass
            try:
                OUTPUT_PATH = os.path.join(output, SUITE_NAME, test_name)
                f()
                TESTS_PASSED.append(os.path.join(SUITE_NAME, test_name))
                if SCREENSHOTS_ON:
                    img_path = os.path.join(
                        output, SUITE_NAME, test_name, 'test-passed.png')
                    pyautogui.screenshot(img_path)
                    relative_path = img_path.split(os.path.sep)
                    tmp_path = os.path.join('', *relative_path[1:])
                    print(f'![Тест пройден]({tmp_path})')
                print_color_text('\n**Тест пройден**', 'green')
            except TestException as e:
                if SCREENSHOTS_ON:
                    img_path = os.path.join(
                        output, SUITE_NAME, test_name, 'test-failed.png')
                    pyautogui.screenshot(img_path)
                    relative_path = img_path.split(os.path.sep)
                    tmp_path = os.path.join('', *relative_path[1:])
                    print(f'![Тест не пройден]({tmp_path})')
                print_color_text('\n> Error : ' + e.message + '\n', 'red')
                print_color_text('**Тест не пройден**', 'red')
                TESTS_FAILED.append(os.path.join(SUITE_NAME, test_name))

    print_test_summary(TESTS_PASSED, TESTS_FAILED)
