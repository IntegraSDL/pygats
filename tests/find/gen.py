from PIL import Image, ImageDraw, ImageFont


def crop_image(img, w, h):
    img_crop = img.crop((0, 0, w, h))
    return img_crop


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
    return img
