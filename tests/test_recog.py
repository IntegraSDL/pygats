"""Module with library tests"""
from pathlib import Path
import pytest
import pygats.recog as rec
import pygats.pygats as pyg
from pygats.formatters import MarkdownFormatter as MD
from PIL import Image, ImageDraw, ImageFont
from tests.find import gen

@pytest.fixture(name='formatter', scope="session", autouse=True)
def fixture_formatter():
    """formatter fixture for markdown"""
    return MD()


@pytest.fixture(scope="session", autouse=True)
def fixture_create_ctx(formatter: MD):
    """ctx fixture for check for ctx creation"""
    global ctx
    ctx = pyg.Context(formatter)
    return ctx


@pytest.fixture(scope="function")
def words_for_bg():
    gen.bg_changer(True)
    file = open("tests/find/words.txt")
    lines = file.readlines()
    font = ImageFont.truetype(f'tests/find/fonts/Arial_Bold.ttf', size=60)
    texts = [] 
    for line in lines:
        if not line.strip():
            continue
        img = Image.open('tests/find/2.jpg')
        draw_text = ImageDraw.Draw(img)
        draw_text.text((50, 50),line.strip() , font=font, fill="#000000")
        text = rec.SearchedText(line.strip(), "eng", None)
        texts.append(text)
        img.save(f'tests/find/fill_colors/{line.strip()}.jpg', quality=95)
    print(texts)
    return texts 
  
        
def test_check_text_1(capsys, words_for_bg):
    successful_count = 0
    failed_count = 0
    fill_color = Path('tests/find/fill_colors')
    for expected_text in words_for_bg:
        image_path = fill_color / f"{expected_text.content}.jpg"
        print(f"Проверяем файл: {image_path}") 
        try:
            if image_path.exists():
                img = Image.open(image_path)
                result = rec.check_text(ctx, img, expected_text)
                print(f"Файл {image_path} найден.")
                if result:
                    successful_count += 1
                else:
                    failed_count += 1
        except pyg.TestException:
                print(f"Файл {image_path} не найден.")
                failed_count += 1
            
    print(f"Успешно распознанных слов: {successful_count}")
    print(f"Не распознанных слов: {failed_count}")