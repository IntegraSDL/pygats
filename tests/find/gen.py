import time
from PIL import Image, ImageDraw, ImageFont
from . import color_gen


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
    colors = color_gen.color_generator()
    for fill_color in colors:
        draw_text.text((w, h), text, font=font, fill=fill_color)
        print(f"Drawing text with color: {fill_color}")
        img.save(f'tests/find/fill_colors/{fill_color[1:]}.jpg', quality=95)
    return img

def bg_changer(crop=False):
    img = Image.open('tests/find/1.jpg')
    img = img.convert("RGB")
    datas = img.getdata()
    new_image_data = []
    for item in datas:
        if item[0]>200 and item[1]<80 and item[2]<80:
            new_image_data.append((255, 0, 0)) # 1. Красный цвет
        elif item[1] > 200 and item[0] < 80 and item[2] < 80:
            new_image_data.append((0, 255, 0)) # 2. Зеленый цвет
        elif item[2] > 200 and item[0] < 80 and item[1] < 80:
            new_image_data.append((0, 0, 255)) # 3. Синий цвет
        elif item[0] > 200 and item[1] > 200 and item[2] < 80:
            new_image_data.append((255, 255, 0)) # 4. Желтый цвет
        elif item[1] > 150 and item[2] > 200 and item[0] < 80:
            new_image_data.append((66, 170, 255)) # 5. Голубой цвет
        elif item[0] > 100 and item[2] > 200 and item[1] < 80:
            new_image_data.append((139,0,255)) # 6. Фиолетовый цвет
        elif item[0] > 200 and item[1] > 200 and item[2] > 200:
            new_image_data.append((255, 255, 255)) # 7. Белый цвет
        elif item[0] < 80 and item[1] < 80 and item[2] < 80:
            new_image_data.append((0, 0, 0)) # 8. Черный цвет
        else:
            new_image_data.append(item)
    img.putdata(new_image_data)
    img.save("tests/find/2.jpg")
    img.show()