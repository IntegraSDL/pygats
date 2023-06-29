"""
module with data classes.
"""

from dataclasses import dataclass
import re
from typing import Optional
import pyautogui
import pytesseract
from Levenshtein import ratio
from PIL import Image
from pygats.pygats import step, passed, failed


@dataclass
class SearchedText:
    """
    Data class to store text, lang and crop area to be passed as parameters
    for Tesseract function
    """
    text: str
    lang: str
    area: str


def find_cropped_text(img, txt, skip=0, one_word=False):
    """
    Find text in image. Several passes are used.
    First time found area with text on image and then
    every area passed through recognition again to improve recognition results

    Args:
        img (PIL.Image): image to search text in
        txt (pygats.recog.SearchedText): text to search
        skip (int, optional): number of occurrences of the text to skip.
        one_word (bool, optional): flag if only one word has been searched.

    Returns:
        (left, top, width, height, found):
            left (int): left coordinate of the text bounding box
            top (int): top coordinate of the text bounding box
            width (int): width of the text bounding box
            height (int): height of the text bounding box
            found (bool): whether the text is found in the image

    """
    recognized = pytesseract.image_to_data(img, txt.lang).split('\n')
    recog_tuple = combine_lines(recognized, one_word)
    ret_tuple = (-1, -1, -1, -1, False)
    for line in recog_tuple:
        if line[4].find(txt.text) != -1:
            print("Найден текст " + line[4])
            ret_tuple = (
                line[0], line[1], line[2], line[3], True)
            if skip <= 0:
                break
            skip -= 1
    return ret_tuple


def find_text_on_screen(ctx, txt, skip=0, one_word=False):
    """
    Function finds text on the screen

    Args:
        ctx (Context): context
        txt (pygats.recog.SearchedText): text to find
        skip (int, optional): amount of findings which should be skipped
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
    (x, y, w, h, found) = find_text(img, txt, skip, False, one_word)
    if found:
        return x, y, w, h, found
    return find_text(img, txt, skip, True, one_word)


def check_text(ctx, img: Image, txt):
    """Checks if text (txt) exists on image (img) printed with language (lang)

    Args:
        ctx (Context): context
        img (Image): image to find text
        txt (pygats.recog.SearchedText): text to search

    """
    step(ctx,
         f'Проверка отображения текста {txt.text} на изображении {img}...')
    _, _, _, _, found = find_text(img, txt)
    if not found:
        _, _, _, _, found = find_text(img, txt, extend=True)
        if not found:
            failed(img, f'{txt.text} не найден на изображении')
    passed()


def check_text_on_screen(ctx, txt):
    """Checks if text (txt) exists on the screen

    Args:
        ctx (Context): context
        txt (pygats.recog.SearchedText): text to search on screenshot
    """
    step(ctx, f'Проверка отображения текста {txt.text} на экране ...')
    img = pyautogui.screenshot()
    _, _, _, _, found = find_text(img, txt)
    if not found:
        _, _, _, _, found = find_text(img, txt, extend=True)
        if not found:
            failed(img, f'{txt.text} не найден на экране')
    passed()


def click_text(ctx, txt, button='left', skip=0):
    """Finds text on screen and press mouse button on it

    Args:
        ctx (Context): execution context
        txt (pygats.recog.SearchedText): text to be searched and clicked
        button (string, optional): left, right, middle
        skip (int): amount of text should be skipped
    """
    step(ctx, f'Нажать текст {txt.text} на экране кнопкой {button}...')
    x, y, width, height, found = find_text_on_screen(
        ctx, txt, skip, True)
    if not found:
        failed(msg=f'{txt.text} не найден на экране')

    print(x, y, width, height)
    center_x = x + width / 2
    center_y = y + height / 2
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


def combine_lines(lines, one_word=False):
    """Function translate lines from Tesseract output format into
    result tuple

    Args:
        lines (List): Returns result containing box boundaries, confidences,
            and other information.
        one_word (bool, optional): one word to search

    Returns:
        list: combined tuples

    Notes:
        There is magic number 5 to understand if words on the same line.
        It should be reworked in the future.

    Todo:
        * This function should be reworked in future with
          combine_words_in_lines. Need one function to combine words in
          sentences.
    """
    result = []
    for i in range(1, len(lines) - 1):
        split_line_1 = lines[i].split('\t')
        if len(split_line_1) != 12:
            return result
        x = int(split_line_1[6])
        y = int(split_line_1[7])
        w = int(split_line_1[8])
        h = int(split_line_1[9])
        text = split_line_1[11]
        if not one_word:
            for j in range(i + 1, len(lines) - 1):
                split_line_2 = lines[j].split('\t')
                if abs(y - int(split_line_2[7])) < 5 and len(split_line_2[11].strip()) > 0:
                    w += int(split_line_2[8])
                    text += ' ' + split_line_2[11]
        result.append((x, y, w, h, text))
    return result


def crop_image(img: Image, width: Optional[int] = 0, height: Optional[int] = 0,
               extend: Optional[bool] = False) -> Image:
    """
    Crops a portion of the input image based on the specified width and height multipliers.
    If width and height aren't specified return an original image

    Args:
        img (Image): The input image to crop.
        width (int, optional): The multiplier to determine the beginning of the crop area by width.
        height (int, optional): The multiplier to determine the beginning of the crop area by height
        extend (bool, optional): Whether to extend the crop area by a factor of 2.

    Returns:
        Image: The cropped image area.
    """
    img_width, img_height = img.size
    factor = 1
    if extend:
        crop_width = img_width // 4
        crop_height = img_height // 4
        factor = 2
    else:
        crop_width = img_width // 3
        crop_height = img_height // 3
    crop_coord = (crop_width * width,
                  crop_height * height,
                  crop_width * width + crop_width * factor,
                  crop_height * height + crop_height * factor)
    img_crop = img.crop(crop_coord)
    return img_crop


def find_crop_image(img: Image, crop_area: Optional[str] = 'all',
                    extend: Optional[bool] = False) -> Image:
    """
    Detects the crop area for the input image and crops the image based on the specified crop area.

    Args:
        img (Image): The input image to crop.
        crop_area (str, optional): The crop area to use. Defaults to 'all'. # noqa: DAR003
        extend (bool, optional): Whether to extend the crop area by a factor of 2.
        Defaults to False.

    Returns:
        Image: The cropped image area.
    """
    crop_area_params = {
        'center': (img, 1, 1, extend),
        'top-left': (img, 0, 0, extend),
        'left': (img, 0, 1, extend),
        'bottom-left': (img, 0, 2, extend),
        'top': (img, 1, 0, extend),
        'bottom': (img, 1, 2, extend),
        'top-right': (img, 2, 0, extend),
        'right': (img, 2, 1, extend),
        'bottom-right': (img, 2, 2, extend)
    }
    return crop_image(*crop_area_params.get(crop_area)) if crop_area_params.get(crop_area) else img


def find_text(img: Image, txt, skip=0, extend=False, one_word=False):
    """Function finds text in image with Tesseract

    Args:
        img (Image): image where text will be recognized
        txt (pygats.recog.SearchedText): text which fill be searched
        skip (int): amount of skipped finding
        extend (bool, optional): extended crop area
        one_word (bool, optional): one word to search

    Returns:
        (x,y,w,h,found):
            x (int), y (int): coordinates of top-left point of rectangle where
               text resides
            w (int), h (int): width and height of rectangle where text resides
            found (bool): whether the text is found in the image
    """
    img = find_crop_image(img, txt.area, extend=extend)
    recognized = pytesseract.image_to_data(img, txt.lang).split('\n')
    recog_tuple = combine_lines(recognized, one_word)
    ret_tuple = (-1, -1, -1, -1, False)
    for line in recog_tuple[1:]:
        if line[4].find(txt.text) != -1:
            print("Найден текст " + line[4])
            ret_tuple = (
                line[0], line[1], line[2], line[3], True)
            if skip <= 0:
                break
            skip -= 1
        else:
            if line[0] + line[1] != 0:
                cropped = img.crop(
                    (line[0], line[1],
                        line[0] + line[2],
                        line[1] + line[3]))
                x, y, w, h, found = find_cropped_text(
                    cropped, txt, 0, one_word)
                if found:
                    return (x + line[0], y + line[1], w, h, found)
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
        recognized_list (list[tuple]): list of text to match with pattern (format: x,y,w,h,text)
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
    search_len = len(search)
    for item in recognized_list:
        r = ratio(search, item[4], score_cutoff=0.5)
        text = item[4]
        if r > 0.0:
            result.append(item)
        elif len(text) > search_len:
            for i in range(0, len(text) - search_len):
                slice_for_search = text[i:i + search_len]
                r = ratio(search, slice_for_search, score_cutoff=0.8)
                if r > 0.0:
                    result.append(item)
    return list(set(result))


def find_regexp_text(recognized_list, pattern):
    """Find text in list by regexp
    Return value is list of tuples with following format

    Args:
        recognized_list (list[tuple]): list of text to match with pattern.(format: x,y,w,h,text)
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
        match = re.findall(pattern, item[4])
        if len(match) > 0:
            item += tuple(match)
            result.append(item)
    return list(set(result))
