"""
module with data classes.
"""

from dataclasses import dataclass
import pytesseract
import re
import pyperclip
import pytesseract
from Levenshtein import ratio


@dataclass
class SearchedText:
    """
    Data class to store text with lang to be passed as parameters
    for Tesseract function
    """
    text: str
    lang: str


def find_cropped_text(img, txt, skip=0, one_word = False):
    """
    Find text in image. Several passes are used.
    First time found area with text on image and then
    every area passed through recognition again to improve recognition results

    Args:
        img (PIL.Image): image to search text in
        txt (pygats.recog.SearchedText): text to search
        skip (int, optional): number of occurrences of the text to skip.

    Returns:
        (left, top, width, height, found):
            left (int): left coordinate of the text bounding box
            top (int): top coordinate of the text bounding box
            width (int): width of the text bounding box
            height (int): height of the text bounding box
            found (bool): whether the text is found in the image

    """
    recognized = pytesseract.image_to_data(img, txt.lang).split('\n')
    if one_word is False:
        combine_words_in_lines(recognized)
    ret_tuple = (-1, -1, -1, -1, False)
    for line in recognized[1:]:
        splitted = line.split('\t')
        if len(splitted) == 12 and splitted[11].find(txt.text) != -1:
            print(f'Найден текст {splitted[11]}')
            ret_tuple = (int(splitted[6]), int(splitted[7]), int(
                splitted[8]), int(splitted[9]), True)
            if skip <= 0:
                break
            skip -= 1
    return ret_tuple


def find_text_on_screen(ctx, txt, skip=0, inv=False, one_word = False):
    """
    Function finds text on the screen

    Args:
        ctx (Context): context
        txt (pygats.recog.SearchedText): text to find
        skip (int, optional): amount of findings which should be skipped
        inv (bool, optional): colour inversion of picture
        one_word (bool, optional): search only one world

    Returns:
        (left, top, width, height, found):
            left (int): left coordinate of the text bounding box
            top (int): top coordinate of the text bounding box
            width (int): width of the text bounding box
            height (int): height of the text bounding box
            found (bool): whether the text is found in the image
    """
    step(ctx, f'Поиск текста {txt.text} на экране ...')
    img = pyautogui.screenshot()
    return find_text(img, txt, skip, inv, one_word)


def check_text(ctx, img, txt):
    """Checks if text (txt) exists on image (img) printed with language (lang)

    Args:
        ctx (Context): context
        img (PIL.Image): image to find text
        txt (pygats.recog.SearchedText): text to search

    """
    step(ctx, f'Проверка отображения текста {txt.text} на изображении {img}...')
    _, _, _, _, flag = find_text(img, txt)
    if flag:
        passed()
        return
    failed(img, f'{txt.text} не найден на изображении')


def check_text_on_screen(ctx, txt):
    """Checks if text (txt) exists on the screen

    Args:
        ctx (Context): context
        txt (pygats.recog.SearchedText): text to search on screenshot
    """
    step(ctx, f'Проверка отображения текста {txt.text} на экране ...')
    img = pyautogui.screenshot()
    _, _, _, _, flag = find_text(img, txt)
    if not flag:
        failed(img, f'{txt.text} не найден на экране')
    passed()


def click_text(ctx, txt, button='left', skip=0, inv=False):
    """Finds text on screen and press mouse button on it

    Args:
        ctx (Context): execution context
        txt (pygats.recog.SearchedText): text to be searched and clicked
        button (string, optional): left, right, middle
        skip (int): amount of text should be skipped
    """
    step(ctx, f'Нажать текст {txt.text} на экране кнопкой {button}...')
    x, y, width, height, found = find_text_on_screen(ctx,
                                                    txt,
                                                    skip,
                                                    inv,
                                                    True)
    if not found:
        failed(msg=f'{txt.text} не найден на экране')

    print(x, y, width, height)
    center_x = x + width/2
    center_y = y + height/2
    pyautogui.moveTo(center_x, center_y)
    pyautogui.mouseDown(center_x, center_y, button)
    pyautogui.mouseUp(center_x, center_y, button)
    passed()


def recognize_text_with_data(img, lang):
    """Functions recognize all texts on the image with Tesseract

    Args:
        img (PIL.Image): input image to recognize text
        lang (string): language in tesseract format

    Returns:
        list: recognized text
    """
    return pytesseract.image_to_data(img, lang)


def combine_words_in_lines(lines):
    """Functions combines words recognized on screen into lines

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
        There is magic number 5 to understand if words on the same line.
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


def find_text(img, txt, skip=0, inv = False, one_word = False):
    """Function finds text in image with Tesseract

    Args:
        img (PIL.Image): image where text will be recognized
        text (pygats.recog.SearchedText): text which fill be searched
        skip (int): amount of skipped finding

    Returns:
        (x,y,w,h,text):
            x (int), y (int): coordinates of top-left point of rectangle where
               text resides
            w (int), h (int): width and height of rectangle where text resides
            text (string): full text which resides in rectangle

    """
    cv_image = np.array(img)
    img_gray = cv.cvtColor(cv_image, cv.COLOR_BGR2GRAY)
    if inv:
        thresh = cv.adaptiveThreshold(img_gray, 255,
                                      cv.ADAPTIVE_THRESH_MEAN_C, \
                                      cv.THRESH_BINARY_INV, 11, 2)
    else:
        thresh = cv.adaptiveThreshold(img_gray, 255,
                                      cv.ADAPTIVE_THRESH_MEAN_C, \
                                      cv.THRESH_BINARY, 11, 2)
    recognized = pytesseract.image_to_data(thresh, txt.lang).split('\n')
    if one_word is False:
        combine_words_in_lines(recognized)
    ret_tuple = (-1, -1, -1, -1, False)
    for line in recognized[1:]:
        splitted = line.split('\t')
        if len(splitted) == 12:
            if splitted[11].find(txt.text) != -1:
                print("Найден текст " + splitted[11])
                ret_tuple = (int(splitted[6]), int(splitted[7]), int(
                    splitted[8]), int(splitted[9]), True)
                if skip <= 0:
                    break
                skip -= 1
            else:
                if int(splitted[6]) + int(splitted[7]) != 0:
                    cropped = Image.fromarray(thresh).crop((int(splitted[6]), int(splitted[7]),
                                        int(splitted[6])+int(splitted[8]),
                                        int(splitted[7])+int(splitted[9])))
                    cropped_tuple = find_cropped_text(cropped, txt, 0, one_word)
                    if cropped_tuple[4]:
                        return (cropped_tuple[0]+int(splitted[6]),
                                cropped_tuple[1]+int(splitted[7]),
                                cropped_tuple[2],
                                cropped_tuple[3],
                                cropped_tuple[4])
    return ret_tuple


def recognize_text(img, lang):
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
    l_search = len(search)
    for item in recognized_list:
        r = ratio(search, item[4], score_cutoff=0.5)
        if r > 0.0:
            result.append(item)
        else:
            s = item[4]
            if len(s) > l_search:
                for i in range(0, len(s)-l_search):
                    slice_for_search = s[i:i+l_search]
                    r = ratio(search, slice_for_search, score_cutoff=0.8)
                    if r > 0.0:
                        result.append(item)
    return list(set(result))


def find_regexp_text(recognized_list, pattern):
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

