"""
pyGATs is python3 library which combines power of pyautogui, opencv,
tesseract, markdown and other staff to automate end-to-end and exploratory
testing.
"""
import time
import sys
import string
import random
import inspect
import pathlib
from typing import Optional, List
import pyautogui
import pyperclip
from PIL import Image, ImageChops
import cv2 as cv
import numpy as np
import mss
from colorama import init, Fore
import yaml

init(autoreset=True)

TESTS_PASSED = []
TESTS_FAILED = []
STEP_INDEX = 0
ACTION_INDEX = 0
SCREENSHOTS_ON = True
SCREENSHOT_INDEX = 0
OUTPUT_PATH = pathlib.Path('output')
SNAPSHOT_PATH = None
SNAPSHOT_INDEX = 0
SUITE_NAME = ''
DOCSTRING = {}


class Context:  # pylint: disable=too-few-public-methods
    """
    Context stores information about
    """
    formatter = None
    timeout = 0

    def __init__(self, formatter, timeout=0):
        self.formatter = formatter
        self.timeout = timeout


class TestException(Exception):
    """
    Test exception class stores msg when error occurs
    """
    def __init__(self, msg):
        self.message = msg


def run_action(ctx: Context, action=None, **kwargs):
    """
    The function that determines start of the action

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        action (function): Function that performs the necessary steps
    """
    global STEP_INDEX
    global OUTPUT_PATH
    global ACTION_INDEX
    ACTION_INDEX += 1
    if DOCSTRING['Actions'] == 'default' or not DOCSTRING['Actions']:
        ctx.formatter.print_header(3, f'Действие {ACTION_INDEX}')
    else:
        try:
            ctx.formatter.print_header(3, DOCSTRING['Actions'][ACTION_INDEX])
        except (KeyError, TypeError):
            ctx.formatter.print_header(3, f'Действие {ACTION_INDEX}')
    STEP_INDEX = 0
    if OUTPUT_PATH.parts[len(OUTPUT_PATH.parts) - 2] != SUITE_NAME:
        OUTPUT_PATH = pathlib.Path(*OUTPUT_PATH.parts[:-1])
    OUTPUT_PATH = pathlib.Path(OUTPUT_PATH, f'action_{ACTION_INDEX}')
    OUTPUT_PATH.mkdir(exist_ok=True)
    if action is not None:
        action(**kwargs)


def check(ctx: Context, msg: str, func=None):
    """
    Prints message as check block

    Args:
        ctx (Context): An object that contains information about the current
                    context.
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


def suite(ctx: Context, module):
    """
    function prints test suite name in reports

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        module (inspect.module): module with tests
    """
    module_name = pathlib.Path(module.__file__).name.removesuffix('.py')
    module_docstring = {}
    if module.__doc__:
        module_docstring = yaml.safe_load(module.__doc__)
        try:
            module_docstring['Header']
        except (KeyError, TypeError):
            module_docstring = {}
            module_docstring['Header'] = f'Тестовый набор {module_name}'
    else:
        module_docstring['Header'] = f'Тестовый набор {module_name}'
    global SUITE_NAME
    SUITE_NAME = module_name
    ctx.formatter.print_header(1, module_docstring['Header'])


def step(ctx: Context, msg: str):
    """
    function prints step name and starts new screenshot index

    Args:
        ctx (Context): An object that contains information about the current
                    context.
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
    img_path = pathlib.Path(
        OUTPUT_PATH, f'step-{STEP_INDEX}-{SCREENSHOT_INDEX}-passed.png')
    SCREENSHOT_INDEX += 1

    # Take the screenshot and store it on disk
    with mss.mss() as sct:
        if rect is None:
            img = np.array(sct.grab(sct.monitors[0]))
        else:
            monitor = {'left': rect[0], 'top': rect[1], 'width': rect[2], 'height': rect[3]}
            img = np.array(sct.grab(monitor))
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
        cv.imwrite(str(img_path), img)
    # Display the screenshot
    ctx.formatter.print_img(img_path.relative_to(img_path.parts[0]), 'Screenshot')
    return img


def take_snapshot(ctx: Context) -> str:
    """Function takes a snapshot to further detect changes on the screen

    Args:
        ctx (Context): An object that contains information about the current
                    context.

    Returns:
        img_path (PosixPath): path to snapshot
    """
    step(ctx, 'Создание снимка для поиска изменений на экране')
    global SNAPSHOT_PATH
    global SNAPSHOT_INDEX
    SNAPSHOT_PATH = pathlib.Path(OUTPUT_PATH, "compare")
    SNAPSHOT_PATH.mkdir(exist_ok=True)
    img_path = pathlib.Path(SNAPSHOT_PATH, f'snapshot-{SNAPSHOT_INDEX}.png')
    with mss.mss() as sct:
        img = np.array(sct.grab(sct.monitors[0]))
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
        cv.imwrite(str(img_path), img)
    SNAPSHOT_INDEX += 1
    ctx.formatter.print_img(img_path.relative_to(img_path.parts[0]), 'Снимок экрана')
    return img_path


def compare_snapshots(ctx: Context, first_img: str, second_img: str) -> tuple or None:
    """Function for comparing two images

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        first_img (str): path to first snapshot for compare
        second_img (str): path to second snapshot for compare

    Returns:
        tupple or None: coordinates of the change detection area
    """
    step(ctx, 'Поиск изменений между снимками ...')
    ctx.formatter.print_img(first_img.relative_to(first_img.parts[0]), 'Первый снимок')
    ctx.formatter.print_img(second_img.relative_to(second_img.parts[0]), 'Второй снимок')
    first = Image.open(first_img)
    second = Image.open(second_img)
    result = ImageChops.difference(first, second)
    if result.getbbox() is not None:
        relative_path = first_img.split('-')
        first_index = relative_path[len(relative_path) - 1].split('.')[0]
        relative_path = second_img.split('-')
        second_index = relative_path[len(relative_path) - 1].split('.')[0]
        result_path = pathlib.Path(SNAPSHOT_PATH, f'result-{first_index}-{second_index}.png')
        result.save(result_path)
        ctx.formatter.print_img(result_path.relative_to(result_path.parts[0]), 'Найдены изменения')
        ctx.formatter.print_bold('Найдены изменения')
        return result.getbbox()
    ctx.formatter.print_bold('Изменения не найдены')
    return None


def log_image(ctx: Context, img: Image, msg: Optional[str] = 'Снимок экрана'):
    """
    Function log img with msg into report
    image is stored in output path as screenshotIndex

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        img (Image): image to be logged
        msg (str, optional): description of the screenshot.
        Defaults to 'Снимок экрана'.  # noqa: DAR003

    Returns:
        PIL.Image: input image
    """
    global SCREENSHOT_INDEX
    img_path = pathlib.Path(
        OUTPUT_PATH, f'step-{STEP_INDEX}-{SCREENSHOT_INDEX}-passed.png')
    SCREENSHOT_INDEX += 1
    img.save(img_path)
    ctx.formatter.print_img(img_path.relative_to(img_path.parts[0]), msg)
    return img


def passed(ctx: Context):
    """
    function prints passed information after test case

    Args:
        ctx (Context): An object that contains information about the current
                    context.
    """
    if SCREENSHOTS_ON:
        time.sleep(ctx.timeout)
        img_path = pathlib.Path(OUTPUT_PATH, f'step-{STEP_INDEX}-passed.png')
        with mss.mss() as sct:
            img = np.array(sct.grab(sct.monitors[0]))
            img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
            cv.imwrite(str(img_path), img)
        ctx.formatter.print_img(img_path.relative_to(img_path.parts[0]), 'Успешно')
    ctx.formatter.print_bold('Успешно')


def failed(msg: Optional[str] = 'Тест не успешен'):
    """
    function generates exception while error occurs

    Args:
        msg (Optional[str]): failed text

    Raises:
        TestException: raise exception in case of test failed
    """
    raise TestException(msg)


def check_image(ctx: Context, img_path: str, timeout: Optional[int] = 1):
    """Check if image is located on screen. Timeout in second waiting image
    to occurs

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        img_path (str): path to image for check on screen
        timeout (Optional[int]): timeout in seconds to check if image occurs
    """
    step(ctx, f'Проверка отображения {img_path} ...')
    while timeout > 0:
        if locate_on_screen(ctx, img_path) is not None:
            passed(ctx)
            return
        timeout -= 1
        time.sleep(1)


def locate_on_screen(ctx: Context, img_path: str):
    """Function return coord of path to image located on screen.
    If not found returns None

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        img_path (str): path to image to find

    Returns:
        (x,y): coordinates path for image on screen
    """
    try:
        coord = pyautogui.locateOnScreen(img_path, confidence=0.5)
    except (pyautogui.ImageNotFoundException, OSError):
        failed(msg='Изображение не найдено')
    ctx.formatter.print_para(f'Изображение найдено в координатах {coord}')
    return coord


def move_to_coord(ctx: Context, x: int, y: int):
    """Function moves mouse to coord x,y

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        x (int): x coordinate
        y (int): y coordinate
    """
    step(ctx, f'Переместить указатель мыши в координаты {x},{y}')
    pyautogui.moveTo(x, y)
    passed(ctx)


def move_to(ctx: Context, img_path: str):
    """Function move mouse to img_path

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        img_path (str): path to image for move to

    """
    step(ctx, f'Переместить указатель мыши на изображение {img_path} ...')
    try:
        center = pyautogui.locateCenterOnScreen(img_path, confidence=0.8)
    except pyautogui.ImageNotFoundException:
        failed(msg='Изображение не найдено')
    if center is None:
        failed('Изображение не найдено')
    if sys.platform == 'darwin':
        pyautogui.moveTo(center.x / 2, center.y / 2)
    else:
        pyautogui.moveTo(center.x, center.y)
        ctx.formatter.print_para(f'Текущая позиция указателя мыши {pyautogui.position()}')
    passed(ctx)


def click_right_button(ctx: Context):
    """function clicks right mouse button

    Args:
        ctx (Context): An object that contains information about the current
                    context.
    """
    step(ctx, 'Нажать правую кнопку мыши ...')
    pyautogui.click(button='right')
    ctx.formatter.print_para(f'Текущая позиция указателя мыши {pyautogui.position()}')
    passed(ctx)


def click_left_button(ctx: Context, clicks: Optional[int] = 1):
    """function clicks left button of mouse

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        clicks (Optional[int]): number of clicks
    """
    step(ctx, 'Нажать левую кнопку мыши ...')
    pyautogui.click(button='left', clicks=clicks, interval=0.2)
    ctx.formatter.print_para(f'Текущая позиция указателя мыши {pyautogui.position()}')
    passed(ctx)


def click(ctx: Context, button_path: str, area: Optional[str] = ''):
    """function clicks button in area

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        button_path (str): path to button image to press
        area (Optional[str]): path to area of image to print
    """
    fail_message = 'Изображение не найдено'
    step(ctx, f'Нажать кнопку мыши {button_path} ...')
    if area == '':
        try:
            center = pyautogui.locateCenterOnScreen(button_path, confidence=0.8)
        except pyautogui.ImageNotFoundException:
            failed(msg='Изображение не найдено')
        ctx.formatter.print_para(f'Кнопка найдена с центром в координатах {center}')
    else:
        ctx.formatter.print_para(' area ' + area)
        try:
            area_location = pyautogui.locateOnScreen(area, confidence=0.9)
        except pyautogui.ImageNotFoundException:
            failed(msg='Изображение не найдено')
        if area_location is None:
            failed(fail_message)
        try:
            box = pyautogui.locate(button_path, area, confidence=0.8)
        except pyautogui.ImageNotFoundException:
            failed(msg='Изображение не найдено')
        if box is None:
            failed(fail_message)

        x = area_location.left + box.left + box.width / 2
        y = area_location.top + box.top + box.height / 2
        center = pyautogui.Point(x, y)
    if center is None:
        failed(msg=fail_message)
    ctx.formatter.print_para(f'Перемещаем указатель мыши в координаты {center}')
    if sys.platform == 'darwin':
        pyautogui.moveTo(center.x / 2, center.y / 2)
    else:
        pyautogui.moveTo(center.x, center.y)
    pyautogui.click()
    passed(ctx)


def scroll(ctx: Context, clicks: Optional[int] = 1):
    """mouse wheel scroll function

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        clicks (Optional[int]): number of turns of mouse wheel, if it's positive scroll to up,
                                if it's negative to down
    """
    step(ctx, 'Прокрутка колеса мыши ...')
    pyautogui.scroll(clicks=clicks)
    passed(ctx)


def ctrl_with_key(ctx: Context, key: str):

    """
    function presses key with ctrl key

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        key (str): key to press CTRL + key
    """
    step(ctx, f'Нажать клавишу ctrl + {key}')
    pyautogui.hotkey('ctrl', key)
    passed(ctx)


def alt_with_key(ctx: Context, key: str):
    """
    function presses alt+key

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        key (str): key to press ALT + key
    """
    step(ctx, f'Нажать клавишу alt+{key}')
    pyautogui.hotkey('alt', key)
    passed(ctx)


def drag_to(ctx: Context, x: int, y: int):
    """
    drag something to coordinates x, y

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        x (int): coordinates to move mouse pointer
        y (int): coordinates to move mouse pointer
    """
    step(ctx, f'Переместить в координаты {x}, {y} ...')
    pyautogui.dragTo(x, y, button='left', duration=0.5)
    passed(ctx)


def move(ctx: Context, x: int, y: int):
    """
    function moves mouse pointer to x,y coordinates

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        x (int): coordinates to move mouse pointer
        y (int): coordinates to move mouse pointer
    """
    step(ctx, f'Относительное перемещение указателя мыши x={x}, y={y} ...')
    ctx.formatter.print_para(f'из координат {pyautogui.position()}')
    pyautogui.move(x, y)
    ctx.formatter.print_para(f'новые координаты {pyautogui.position()}')
    passed(ctx)


def press(ctx: Context, key: str, n: Optional[int] = 1):
    """Function press keys n times

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        key (str): key to press
        n (Optional[int]): amount of time to press
    """
    step(ctx, f'Нажать {key} {n} раз')
    for _ in range(n):
        pyautogui.press(key)


def typewrite(ctx: Context, message: str, lang: Optional[str] = 'eng'):
    """function types keys on keyboard

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        message (str): text to typewrite
        lang (Optional[str]): language in tesseract format

    """
    if lang != 'eng':
        clipboard = pyperclip.paste()
        pyperclip.copy(message)
        pyautogui.hotkey('ctrl', 'v')
        pyperclip.copy(clipboard)
        passed(ctx)
    else:
        step(ctx, f'Набрать на клавиатуре {message} ...')
        pyautogui.write(message)
        passed(ctx)


def print_test_summary(ctx: Context, list_passed: List, list_failed: List):
    """Functions print tests summary for executed suites

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        list_passed (List): list of test passed
        list_failed (List): list of test failed
    """
    # pylint: disable=consider-using-f-string
    ctx.formatter.print_header(2, 'Результаты тестирования')
    ctx.formatter.print_para(Fore.GREEN + 'Тесты завершенные успешно:' + Fore.RESET)
    for t in list_passed:
        ctx.formatter.print_list(Fore.GREEN + t + Fore.RESET)
    ctx.formatter.print_para(Fore.RED + '\nТесты завершенные неуспешно:' + Fore.RESET)
    for t in list_failed:
        ctx.formatter.print_list(Fore.RED + t + Fore.RESET)
    print()
    ctx.formatter.print_bold('Всего выполнено')
    ctx.formatter.print_para(
        'Успешно: {:04d} / Неуспешно: {:04d}'.format(
            len(list_passed), len(list_failed)))


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


def find_contours(ctx: Context, img_path: str, fltr=repeater):
    """
    Function finds contours by cv and filter them with filter

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        img_path (str): path to image where contours will be searched
        fltr (function, optional): filter which will be used on contours
        results  # noqa: DAR003

    Returns:
        list of points: list of points filtered
    """
    step(ctx, 'Поиск контуров с применением селектора')
    img = cv.imread(img_path)
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    edges = cv.Canny(img_gray, 50, 100)
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))
    edges = cv.dilate(edges, kernel, iterations=1)
    contours, _ = cv.findContours(
        image=edges, mode=cv.RETR_TREE, method=cv.CHAIN_APPROX_NONE)
    return fltr(contours)


def draw_contours(img: Image, cnts: List[np.ndarray]) -> Image:
    """
    Draw contours on a PIL.Image instance.

    Args:
        img (Image): Input image on which to draw the contours.
        cnts (List[np.ndarray]): List of contours, represented
        as Numpy arrays.  # noqa: DAR003

    Returns:
        Image: Output image with contours drawn.

    Raises:
        TypeError: If `img` is not a `PIL.Image` instance.
        ValueError: If `cnts` is not a list of Numpy arrays.
    """
    if not isinstance(img, Image.Image):
        raise TypeError("img must be a PIL.Image instance")
    if not all(isinstance(cnt, np.ndarray) for cnt in cnts):
        raise ValueError("cnts must be a list of Numpy arrays")
    np_img = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
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
        >>> random_string(5, character_set='')
        'yzbVG'
    """
    if string_length <= 0:
        raise ValueError("string_length must be a positive integer")
    if not character_set:
        character_set = string.ascii_letters + ' _' + string.digits
    return ''.join(random.choice(character_set) for _ in range(string_length))


def create_stm(ctx: Context, funcs: List[str]):
    """
    Print а software test methodology based on docstring functions.

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        funcs (List[str]) list of function to be executed
        # noqa: DAR003
    """
    global DOCSTRING
    module = inspect.getmodule(funcs[0])
    suite(ctx, module)
    for f in funcs:
        DOCSTRING = yaml.safe_load(f.__doc__)
        ctx.formatter.print_header(2, DOCSTRING['Definition'])
        ctx.formatter.print_header(3, 'Порядок выполнения проверки:')
        for i in range(1, len(DOCSTRING['Actions']) + 1):
            ctx.formatter.print_list(DOCSTRING['Actions'][i])
        print()
        ctx.formatter.print_header(2, f"Ожидаемый результат: {DOCSTRING['Expected']}")


def docstring_handler(func):
    """
    Addition and modification of the docstring in case of missing elements

    Args:
        func (function): Function for getting a docstring

    Returns:
        dict: docstring of function
    """
    docstr = {}
    if func.__doc__:
        docstr = yaml.safe_load(func.__doc__)
        try:
            docstr['Definition']
        except (KeyError, TypeError):
            docstr['Definition'] = f'Тестовая функция {func.__name__}'
        try:
            docstr['Actions']
        except (KeyError, TypeError):
            docstr['Actions'] = 'default'
        try:
            docstr['Expected']
        except (KeyError, TypeError):
            docstr['Expected'] = 'Успешное выполнение тестовой функции'
    else:
        docstr['Definition'] = f'Тестовая функция {func.__name__}'
        docstr['Actions'] = 'default'
        docstr['Expected'] = 'Успешное выполнение тестовой функции'
    return docstr


def run(ctx: Context, funcs: List[str], counter: Optional[int] = 1,
        output: Optional[str] = 'output', screenshots_on: Optional[bool] = True):
    """
    Execute test suite (list of test cases) one by one.

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        funcs (List[str]) list of function to be executed
        counter (Optional[int]): amount to time test cases to be executed
        output (Optional[str]): path to store test results
        screenshots_on (Optional[bool]): create screenshots while running tests
        # noqa: DAR003
    """
    global OUTPUT_PATH
    global SCREENSHOTS_ON
    global DOCSTRING
    global ACTION_INDEX
    SCREENSHOTS_ON = screenshots_on
    p = pathlib.Path(output)
    p.mkdir(exist_ok=True)
    module = inspect.getmodule(funcs[0])
    suite(ctx, module)
    for _ in range(counter):
        for f in funcs:
            ACTION_INDEX = 0
            test_name = f.__name__
            DOCSTRING = docstring_handler(f)
            ctx.formatter.print_header(2, DOCSTRING['Definition'])
            if SCREENSHOTS_ON:
                p = pathlib.Path(output, SUITE_NAME, test_name)
                p.mkdir(parents=True, exist_ok=True)
            try:
                OUTPUT_PATH = pathlib.Path(output, SUITE_NAME, test_name)
                f()
                TESTS_PASSED.append(str(pathlib.Path(SUITE_NAME, test_name)))
                if SCREENSHOTS_ON:
                    img_path = pathlib.Path(
                        output, SUITE_NAME, test_name, 'test-passed.png')
                    with mss.mss() as sct:
                        img = np.array(sct.grab(sct.monitors[0]))
                        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
                        img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
                        cv.imwrite(str(img_path), img)
                    ctx.formatter.print_img(img_path.relative_to(img_path.parts[0]),
                                            'Тест пройден')
                ctx.formatter.print_header(2, f"Ожидаемый результат: {DOCSTRING['Expected']}")
                ctx.formatter.print_bold(Fore.GREEN + 'Тест пройден' + Fore.RESET)
            except TestException as e:
                if SCREENSHOTS_ON:
                    img_path = pathlib.Path(
                        output, SUITE_NAME, test_name, 'test-failed.png')
                    with mss.mss() as sct:
                        img = np.array(sct.grab(sct.monitors[0]))
                        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
                        img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
                        cv.imwrite(str(img_path), img)
                    ctx.formatter.print_img(img_path.relative_to(img_path.parts[0]),
                                            'Тест не пройден')
                ctx.formatter.print_header(2, f"Ожидаемый результат: {DOCSTRING['Expected']}")
                ctx.formatter.print_para(Fore.RED + '> Error : ' + e.message + Fore.RESET)
                ctx.formatter.print_bold(Fore.RED + 'Тест не пройден' + Fore.RESET)
                TESTS_FAILED.append(str(pathlib.Path(SUITE_NAME, test_name)))

    print_test_summary(ctx, TESTS_PASSED, TESTS_FAILED)
