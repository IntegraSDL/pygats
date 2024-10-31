import time
from PIL import Image, ImageDraw, ImageFont
import color_gen


def crop_image(img, w, h):
    img_crop = img.crop((0, 0, w, h))
    return img_crop


def wrapper():
    start = time.time()
    gen("blue", 350, 350, 'Arial_Bold', 150, "File")
    seconds = int(time.time() - start)
    seconds = seconds % (24 * 3600)
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    with open('tests/find/result.txt', 'a') as file:
        file.write('Время выполнения: %02d:%02d:%02d\n' % (hours, minutes, seconds))


def gen(filename, w, h, font='', size=16, text='', crop=False):
    global count
    img = Image.open(f'tests/find/background/{filename}.jpg')
    if crop:
        img = crop_image(img, 350, 50)
    font = ImageFont.truetype(f'tests/find/fonts/{font}.ttf', size=size)
    draw_text = ImageDraw.Draw(img)
    colors = color_gen.color_generator()
    for fill_color in colors:
        draw_text.text((w, h), text, font=font, fill=fill_color)
        img.save(f'tests/find/fill_colors/{fill_color[1:]}.jpg')
    #img = Image.open('tests/find/1.jpg')
    return img

wrapper()