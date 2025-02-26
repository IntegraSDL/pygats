"""
module with data classes.
"""

from dataclasses import dataclass
import re
from typing import Optional, Union
import hdbscan
import pyautogui
import pytesseract
import mss
import numpy as np
import cv2 as cv
from Levenshtein import ratio
from PIL import Image
from pygats.pygats import step, passed, failed


@dataclass
class SearchedText:
    """
    Data class to store text content, language and crop area to be passed
    as parameters for Tesseract function
    """
    content: str
    lang: str
    area: str


@dataclass
class ROI:
    """
    Data class to store coordinates of region of interest
    x (int), y (int): coordinates of top-left point of rectangle where
    text resides
    w (int), h (int): width and height of rectangle where text resides
    """
    x: int
    y: int
    w: int
    h: int

    def rectangle_center_coords(self):
        """
        return center of the rectangle

        Returns:
                tuple: coordinates of the rectangle center
        """
        return self.x + self.w / 2, self.y + self.h / 2


@dataclass
class KeypointsCluster:
    """
    Data class for storing a cluster of keypoints, labels, and rectangle coordinates.
    keypoints (list): A list of keypoints representing the cluster.
    labels (list): A list of labels associated with the keypoints.
    coord_rect (list): Coordinates of the rectangle that bounds the cluster.
                                     Expected format is (x_min, y_min, x_max, y_max).

    Methods:
        __repr__(): Returns a string representation of the KeypointCluster instance,
                    including keypoints, labels, and rectangle coordinates.
    """
    keypoints: list
    labels: list
    coord_rect: tuple

    def __repr__(self):
        return (f"keypoints={self.keypoints,}\n"
                f"labels={self.labels}\n"
                f"coord_rect={self.coord_rect}")


def find_cropped_text(ctx, img: Image, txt: SearchedText,
                      skip: Optional[int] = 0, one_word: Optional[bool] = False):
    """
    Find text in image. Several passes are used.
    First time found area with text on image and then
    every area passed through recognition again to improve recognition results

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        img (Image): image to search text in
        txt (SearchedText): text to search
        skip (int, optional): number of occurrences of the text to skip.
        one_word (bool, optional): flag if only one word has been searched.

    Returns:
        (roi, found):
            roi(ROI): region of interest
            found (bool): whether the text is found in the image

    """
    recognized_data = pytesseract.image_to_data(img, txt.lang).split('\n')
    recognized_lines = combine_lines(recognized_data, one_word)
    roi, found = ROI(-1, -1, -1, -1), False
    for pos, content in recognized_lines:
        if content.find(txt.content) != -1:
            ctx.formatter.print_para('Найден текст ' + content)
            roi, found = pos, True
            if skip <= 0:
                break
            skip -= 1
    return roi, found


def find_text_on_screen(ctx, txt, skip=0, one_word=False):
    """
    Function finds text on the screen

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        txt (pygats.recog.SearchedText): text to find
        skip (int, optional): amount of findings which should be skipped
        one_word (bool, optional): search only one world

    Returns:
        (roi, found):
            roi(ROI): region of interest
            found (bool): whether the text is found in the image
    """
    step(ctx, f'Поиск текста {txt.content} на экране ...')
    with mss.mss() as sct:
        img = np.array(sct.grab(sct.monitors[0]))
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        img = Image.fromarray(img)
    roi, found = find_text(ctx, img, txt, skip, False, one_word)
    if found:
        return roi, found
    return find_text(ctx, img, txt, skip, True, one_word)


def check_text(ctx, img: Image, txt):
    """Checks if text (txt) exists on image (img) printed with language (lang)

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        img (Image): image to find text
        txt (pygats.recog.SearchedText): text to search

    """
    step(ctx,
         f'Проверка отображения текста {txt.content} на изображении {img}...')
    _, found = find_text(ctx, img, txt)
    if not found:
        _, found = find_text(ctx, img, txt, extend=True)
        if not found:
            failed(msg=f'{txt.content} не найден на изображении')
    passed(ctx)


def check_text_on_screen(ctx, txt):
    """Checks if text (txt) exists on the screen

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        txt (pygats.recog.SearchedText): text to search on screenshot
    """
    step(ctx, f'Проверка отображения текста {txt.content} на экране ...')
    with mss.mss() as sct:
        img = np.array(sct.grab(sct.monitors[0]))
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        img = Image.fromarray(img)
    _, found = find_text(ctx, img, txt)
    if not found:
        _, found = find_text(ctx, img, txt, extend=True)
        if not found:
            failed(msg=f'{txt.content} не найден на экране')
    passed(ctx)


def move_to_text(ctx, txt, skip=0):
    """Finds text on the screen and moves the cursor to it

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        txt (pygats.recog.SearchedText): text to be searched and clicked
        skip (int): amount of text should be skipped
    """
    step(ctx, f'Переместить курсор на текст {txt.content}')
    roi, found = find_text_on_screen(
        ctx, txt, skip, True)
    if not found:
        failed(msg=f'{txt.content} не найден на экране')
    ctx.formatter.print_para(f'{roi.x} {roi.y} {roi.w} {roi.h}')
    center_x, center_y = roi.rectangle_center_coords()
    pyautogui.moveTo(center_x, center_y)
    passed(ctx)


def click_text(ctx, txt, button='left', skip=0):
    """Finds text on screen and press mouse button on it

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        txt (pygats.recog.SearchedText): text to be searched and clicked
        button (string, optional): left, right, middle
        skip (int): amount of text should be skipped
    """
    step(ctx, f'Нажать текст {txt.content} на экране кнопкой {button}...')
    roi, found = find_text_on_screen(
        ctx, txt, skip, True)
    if not found:
        failed(msg=f'{txt.content} не найден на экране')

    ctx.formatter.print_para(f'{roi.x} {roi.y} {roi.w} {roi.h}')
    center_x, center_y = roi.rectangle_center_coords()
    pyautogui.moveTo(center_x, center_y)
    pyautogui.mouseDown(center_x, center_y, button)
    pyautogui.mouseUp(center_x, center_y, button)
    passed(ctx)


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
        list: list of (ROI, text) tuples

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
        roi = ROI(*map(int, split_line_1[6:10]))
        text = split_line_1[11]
        if not one_word:
            for j in range(i + 1, len(lines) - 1):
                split_line_2 = lines[j].split('\t')
                if abs(roi.y - int(split_line_2[7])) < 5 and len(split_line_2[11].strip()) > 0:
                    roi.w += int(split_line_2[8])
                    text += ' ' + split_line_2[11]
        result.append((roi, text))
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
        (x_offset, y_offset, img_crop):
            x_offset (int), y_offset (int): offset by x and y coordinates
            img_crop (Image): The cropped image area
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
    x_offset = crop_coord[0]
    y_offset = crop_coord[1]
    img_crop = img.crop(crop_coord)
    return x_offset, y_offset, img_crop


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
        (x_offset, y_offset, img_crop):
            x_offset (int), y_offset (int): offset by x and y coordinates
            img_crop (Image): The cropped image area
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
    return crop_image(*crop_area_params.get(crop_area)) if crop_area_params.get(crop_area)\
        else (0, 0, img)


def find_text(ctx, img: Image, txt, skip=0, extend=False, one_word=False):  # pylint: disable=R0917
    """Function finds text in image with Tesseract

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        img (Image): image where text will be recognized
        txt (pygats.recog.SearchedText): text which fill be searched
        skip (int): amount of skipped finding
        extend (bool, optional): extended crop area
        one_word (bool, optional): one word to search

    Returns:
        (roi,found):
            roi(ROI): region of interest
            found (bool): whether the text is found in the image
    """
    x_offset, y_offset, img = find_crop_image(img, txt.area, extend=extend)
    recognized = pytesseract.image_to_data(img, txt.lang).split('\n')
    lines = combine_lines(recognized, one_word)
    roi, found = ROI(-1, -1, -1, -1), False
    for pos, content in lines[1:]:
        if content.find(txt.content) != -1:
            ctx.formatter.print_para('Найден текст ' + content)
            roi = ROI(pos.x + x_offset, pos.y + y_offset, pos.w, pos.h)
            found = True
            if skip <= 0:
                break
            skip -= 1
        else:
            if pos.x + pos.y != 0:
                cropped = img.crop(
                    (pos.x, pos.y,
                        pos.x + pos.w,
                        pos.y + pos.h))
                roi, found = find_cropped_text(
                    ctx, cropped, txt, 0, one_word)
                if found:
                    return ROI(roi.x + pos.x, roi.y + pos.y, roi.w, roi.h), found
    return roi, found


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
    recognized_data = pytesseract.image_to_data(img, lang).split('\n')
    result = combine_lines(recognized_data)
    return list(set(result))


def find_fuzzy_text(recognized_list, search: str):
    """Fuzzy search of text in list using Levenshtein ratio
    Return value is list of tuples with following format:

    Args:
        recognized_list (list[tuple]): list of text to match with pattern (format: ROI,text)
        search (str): substring to search

    Returns:
        (roi,text, substring):
            roi(ROI): region of interest
            text (str): full text which resides in rectangle
    """
    result = []
    search_len = len(search)
    for roi, content in recognized_list:
        r = ratio(search, content, score_cutoff=0.5)
        text = content
        if r > 0.0:
            result.append((roi, content))
        elif len(text) > search_len:
            for i in range(len(text) - search_len):
                slice_for_search = text[i:i + search_len]
                r = ratio(search, slice_for_search, score_cutoff=0.8)
                if r > 0.0:
                    result.append((roi, content))
    return list(set(result))


def find_regexp_text(recognized_list: list, pattern):
    """Find text in list by regexp
    Return value is list of tuples with following format

    Args:
        recognized_list (list): list of text to match with pattern.(format tuple: ROI,text)
        pattern (str): regexp pattern to match

    Returns:
        (roi,text, substring):
            roi(ROI): region of interest
            text (str): full text which resides in rectangle
            substring (str): substring found in text
    """
    result = []
    for roi, content in recognized_list:
        match = re.findall(pattern, content)
        if len(match) > 0:
            result.append((roi, content, tuple(match)))
    return list(set(result))


def contrast(img: Image):
    """Function that determines the minimum and
    maximum brightness and contrast values on the image itself.
    The metrics are calculated using the YCbCr color model.
    Image.convert supports all possible conversions between “L”, “RGB” and “CMYK”.
    https://pillow.readthedocs.io/en/latest/reference/Image.html#PIL.Image.Image.convert

    Args:
        img (Image): Pil.Image that is converted from the BGR color space to YUV

    Returns:
        (contr):
            contr (float): contrast value on the image
    """
    MAX_CONTRAST = 21
    MIN_CONTRAST = 1
    image = np.array(img.convert('YCbCr'))
    Y = image[:, :, 0]
    br_min, br_max = np.min(Y), np.max(Y)
    contr = round((br_max + 0.05) / (br_min + 0.05), 3)
    # https://www.w3.org/TR/WCAG21/
    # According to WCAG, the contrast is defined in the range from 1 to 21
    contr = min(MAX_CONTRAST, max(MIN_CONTRAST, contr))
    return float(contr)


def find_keypoints(img: Image):
    """Function that uses the SIFT algorithm to find keypoints in an image.
    The function returns three values, one of which contains the coordinates of the key points,
    which simplifies further use of the data.

    Args:
        img (Image): Pil.Image which is used to search for keypoints

    Returns:
        (keypoints, descriptors, coord_list):
            keypoints (tuple): The detected keypoints
            descriptors (numpy.ndarray): Computed descriptors
            coord_list (numpy.ndarray): Array of coordinates of keypoints
    """
    if img.mode == "L":
        gray = np.array(img)
    else:
        gray = cv.cvtColor(np.array(img), cv.COLOR_BGR2GRAY)
    sift = cv.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(gray, None)
    coord_list = []
    for kp in keypoints:
        x, y = kp.pt
        coord_list.append([x, y])
    coord_list = np.array(coord_list)
    return keypoints, descriptors, coord_list


def hdbscan_cluster(keypoints: tuple, coord_list: np.ndarray, min_cluster_size: Optional[int] = 5,  # pylint: disable=R0914, R0917
                    min_samples: Union[int, float] = None,
                    cluster_selection_epsilon: Optional[float] = 0.0,
                    margins: Optional[tuple] = (0, 0)):
    """Function that performs clusterization of keypoints using their coordinates and HDBSCAN
    The function is used for found coordinates and keypoints.
    https://scikit-learn.org/stable/modules/generated/sklearn.cluster.HDBSCAN.html#r6f313792b2b7-5

    Args:
        keypoints (tuple): Distinctive points in an image
        coord_list (np.ndarray): Array of coordinates of keypoints
        min_cluster_size (int): Min number of samples that allows to consider a group as a cluster;
        min_samples (int | float): Calculate the distance between a point and its nearest neighbor
        cluster_selection_epsilon (float): Distance threshold
        margins (tuple): Tuple of values for symmetrical boundary changes along x, y

    Returns:
        (clusters):
            clusters(list): list of cluster objects containing detailed information about
            labels, keypoints and rectangles

    """
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        cluster_selection_epsilon=cluster_selection_epsilon,
        gen_min_span_tree=True
    )
    clusterer.fit(coord_list)
    labels = clusterer.labels_
    clusters = []
    for label in set(labels):
        if label != -1:
            cluster_points = coord_list[labels == label]
            keypoints_in_cluster = []
            labels_in_cluster = []
            if len(cluster_points) > 0:
                x_coordinates = [point[0] for point in cluster_points]
                y_coordinates = [point[1] for point in cluster_points]
                x_min = int(min(x_coordinates))
                y_min = int(min(y_coordinates))
                x_max = int(max(x_coordinates))
                y_max = int(max(y_coordinates))
                coord_rect = (x_min - margins[0], y_min - margins[1],
                              x_max + margins[0], y_max + margins[1])
                for kp in keypoints:
                    x, y = kp.pt
                    if x_min <= x <= x_max and y_min <= y <= y_max:
                        keypoints_in_cluster.append(kp)
                        labels_in_cluster.append(int(label))
                cluster = KeypointsCluster(keypoints_in_cluster, labels_in_cluster, coord_rect)
                clusters.append(cluster)
    return clusters


def image_difference(img_1: Image, img_2: Image):
    """Function that calculates the difference between two images and returns the coordinates of
    rectangles enclosing the areas where these differences are observed.

    Args:
        img_1 (Image): First image
        img_2 (Image): Second image

    Returns:
        (coord_rect):
            coord_rect(tuple): Tuple with the coordinates of all the bounding boxes
            that enclose the regions of difference between the two images

    """
    gray_1 = cv.cvtColor(np.array(img_1), cv.COLOR_BGR2GRAY)
    gray_2 = cv.cvtColor(np.array(img_2), cv.COLOR_BGR2GRAY)
    diff = cv.absdiff(gray_1, gray_2)
    _, thresh = cv.threshold(diff, 30, 255, cv.THRESH_BINARY)
    contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    coord_rect = []
    for contour in contours:
        (x, y, w, h) = cv.boundingRect(contour)
        coord = (x, y, x + w, y + h)
        coord_rect.append(coord)
    return tuple(coord_rect)
