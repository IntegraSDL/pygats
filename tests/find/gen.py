from pathlib import Path
import time
from PIL import Image, ImageDraw, ImageFont
from pygats.search import pygats_search

def crop_image(img, w, h):
    img_crop = img.crop((0, 0, w, h))
    return img_crop


def wrapper():
    folder_result = Path(f'tests/find/result.txt')
    start = time.time()
    pygats_search()
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
        img = crop_image(img, 600, 600)
    font = ImageFont.truetype(f'tests/find/fonts/{font}.ttf', size=size)
    draw_text = ImageDraw.Draw(img)
    draw_text.text((w, h), text, font=font, fill=('#000000'))
    img.save('tests/find/1.png')
    img = Image.open('tests/find/1.png')
    img.show()


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

def color_shade_gen(step: tuple = (1, 1, 1), size: tuple = (1920, 1080)):
    """Function generates images with different shades of color

    Args:
        step (int, optional): Tuple that determines the frequency of creating shades of color
        size (tuple, optional): Specifying the size of the image to be created
    """
    folder_path = Path(f'tests/find/color_shades')
    folder_path.mkdir(parents=True, exist_ok=True)
    for rgb in ColorShadeIterator(step):
        new_image_data = [rgb] * (size[0] * size[1])
        new_img = Image.new('RGB', size)
        new_img.putdata(new_image_data)
        new_img.save(f"{folder_path}/color:{rgb}.png", 'PNG')

wrapper()