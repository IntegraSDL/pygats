from pathlib import Path
import time
from PIL import Image, ImageDraw, ImageFont
import pygats.recog as rec

def crop_image(img, w, h):
    img_crop = img.crop((0, 0, w, h))
    return img_crop


def wrapper():
    folder_result = Path(f'tests/find/result.txt')
    start = time.time()
    #gen("white", 350, 350, 'TimesNewRoman', 32, "File")
    seconds = int(time.time() - start)
    seconds = seconds % (24 * 3600)
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    with open(folder_result, 'a') as file:
        file.write('Время выполнения: %02d:%02d:%02d\n' % (hours, minutes, seconds))


def gen(filename, w, h, font='', size=16, text='', crop=False):
    global count
    img = Image.open(f'tests/find/background/{filename}.jpg')
    if crop:
        img = crop_image(img, 350, 50)
    font = ImageFont.truetype(f'tests/find/fonts/{font}.ttf', size=size)
    draw_text = ImageDraw.Draw(img)
    draw_text.text((w, h), text, font=font, fill=('#000000'))
    img.save('tests/find/1.jpg')
    img = Image.open('tests/find/1.jpg')


class ColorShadeIterator:
    def __init__(self, step):
        self.step = step
        self.limit = (255, 255, 255)
        self.rgb = (0, 0, 0)

    def __iter__(self):
        return self
 
    def __next__(self):
        shade = self.rgb
        for rgb, lim in zip(shade, self.limit):
            if rgb > lim:
                raise StopIteration
        self.rgb = tuple(rgb + lim for rgb, lim in zip(shade, self.step))
        return shade


def color_shade_gen(step: tuple = (1, 1, 1), size: tuple = (1920, 1080), contr=False, contrast_value: float = 21.0):
    """Function generates images with different shades of color

    Args:
        step (tuple): Tuple that determines the frequency of creating shades of color (default is (1, 1, 1)).
        size (tuple): Specifying the size of the image to be created (default is (1920, 1080)).
        contr (Optional, bool): Flag indicating whether to apply contrast filtering (default is False).
        contrast_value (Optional, float): Target contrast value for filtering (default is 21.0).
    
    Returns:
        list: A list of generated colors.
    """
    folder_path = Path('tests/find/color_shades')
    folder_path.mkdir(parents=True, exist_ok=True)
    generated_colors = []
    for rgb in ColorShadeIterator(step):
        contrast = rec.contrast_metrics(rgb, (255, 255, 255))
        if contr:
            if contrast_value == contrast[2]:
                new_image_data = [rgb] * (size[0] * size[1])
                new_img = Image.new('RGB', size)
                new_img.putdata(new_image_data)
                generated_colors.append(rgb)
                new_img.save(folder_path / f"color_{rgb}.png", 'PNG')
                print(f"{rgb} удовлетворяет условию")
        else:
            new_image_data = [rgb] * (size[0] * size[1])
            new_img = Image.new('RGB', size)
            new_img.putdata(new_image_data)
            generated_colors.append(rgb)
            new_img.save(folder_path / f"color_{rgb}.png", 'PNG')
    return generated_colors


def sorting_colors(contrast_value: float = 21.0):
    rgb_tuple = []
    for r in range(256):
        for g in range(256):
            for b in range(256):
                color = [r, g, b]
                contrast = rec.contrast_metrics(color, (255, 255, 255))
                if contrast_value == contrast[2]:
                    rgb_tuple.append(color)
    print(rgb_tuple)
                    

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb