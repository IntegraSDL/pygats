from pathlib import Path
import time
from PIL import Image, ImageDraw, ImageFont


def crop_image(img, w, h):
    img_crop = img.crop((0, 0, w, h))
    return img_crop


def wrapper():
    start = time.time()
    gen("white", 350, 350, 'TimesNewRoman', 32, "File")
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
    draw_text.text((w, h), text, font=font, fill=('#000000'))
    img.save('tests/find/1.jpg')
    img = Image.open('tests/find/1.jpg')


def color_shade_gen(rgb: tuple, step: int, size: tuple = (1920, 1080), crop=False):
    """Function generates images with different shades of color

    Args:
        rgb (list): List of color values in the rgb color model
        step (int): Step that determines the frequency of creating shades of color
        size (tuple): Specifying the size of the image to be created
        crop (bool, optional): Parameter responsible for cropping the image Defaults to False.
    """
    new_image = Image.new('RGB', size, rgb)
    new_image.save("tests/find/new_image.png", 'PNG')
    img = Image.open("tests/find/new_image.png")
    folder_path = Path(f'tests/find/color_shades')
    folder_path.mkdir(parents=True, exist_ok=True)
    if crop:
        img = crop_image(img, 350, 350)
    img = img.convert("RGB")
    datas = img.getdata()
    for color in range(0, 256, step):
        new_image_data = []
        for item in datas:
            if item[0]>200 and item[1]<80 and item[2]<80:
                new_image_data.append((color, 0, 0)) # Red color
            elif item[1] > 200 and item[0] < 80 and item[2] < 80:
                new_image_data.append((0, color, 0)) # Green color
            elif item[2] > 200 and item[0] < 80 and item[1] < 80:
                new_image_data.append((0, 0, color)) # Blue color
        new_img = Image.new('RGB', img.size)
        new_img.putdata(new_image_data)
        new_img.save(f"tests/find/color_shades/color{color}.png", 'PNG')

# if item[0]>200 and item[1]<80 and item[2]<80:
#     new_image_data.append((255, 0, 0)) # 1. Красный цвет
# elif item[1] > 200 and item[0] < 80 and item[2] < 80:
#     new_image_data.append((0, 255, 0)) # 2. Зеленый цве
# elif item[0] > 200 and item[1] > 200 and item[2] < 80:
#     new_image_data.append((255, 255, 0)) # 4. Желтый цвет
# elif item[1] > 150 and item[2] > 200 and item[0] < 80:
#     new_image_data.append((66, 170, 255)) # 5. Голубой цвет
# elif item[0] > 100 and item[2] > 200 and item[1] < 80:
#     new_image_data.append((139,0,255)) # 6. Фиолетовый цвет
# elif item[0] > 200 and item[1] > 200 and item[2] > 200:
#     new_image_data.append((255, 255, 255)) # 7. Белый цвет
# elif item[0] < 80 and item[1] < 80 and item[2] < 80:
#     new_image_data.append((0, 0, 0)) # 8. Черный цвет
# else:
#     new_image_data.append(item)