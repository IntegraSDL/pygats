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
    gen.color_shade_gen((210, 0, 0), 5, (1280,1280), True)
    file = open("tests/find/words.txt")
    lines = file.readlines()
    font = ImageFont.truetype(f'tests/find/fonts/Arial_Bold.ttf', size=27)
    texts = [] 
    colors = Path('tests/find/color_shades')
    colors_and_texts = Path(f'tests/find/fill_colors')
    colors_and_texts.mkdir(parents=True, exist_ok=True)
    for photo in colors.glob('*'):
        img = Image.open(photo)
        for line in lines:
            if not line.strip():
                continue
            new_img = img.copy()
            draw_text = ImageDraw.Draw(new_img)
            draw_text.text((100, 100),line.strip(), font=font, fill="#000000")
            text = rec.SearchedText(line.strip(), "eng", None)
            texts.append(text)
            subfolder_name = photo.name[:8]
            folder_path = Path(f'tests/find/fill_colors/{subfolder_name}')
            folder_path.mkdir(parents=True, exist_ok=True)
            new_img.save(f'tests/find/fill_colors/{subfolder_name}/{line.strip()}.png', quality=100)
    return texts
  

def test_check_text_1(words_for_bg, capsys):
    successful_count = 0
    failed_count = 0
    fill_color = Path(f'tests/find/fill_colors')
    for folders in fill_color.glob('*'):
        image_count = 0
        assert folders.is_dir()
        for expected_text in words_for_bg:
            image_path = folders / f"{expected_text.content}.png"
            print(f"Проверяем файл: {image_path}")
            image_count += 1 
            try:
                if image_path.exists():
                    img = Image.open(image_path)
                    width, height = img.size
                    assert width > 0
                    assert height > 0
                    result = rec.check_text(ctx, img, expected_text)
                    cptrd = capsys.readouterr()
                    print(f"Файл {image_path} найден.")
                    if '![Успешно]' in cptrd.out:
                        successful_count += 1
                    else:
                        failed_count += 1
                        assert cptrd == f"{expected_text} не найден на изображении"
            except pyg.TestException:
                    print(f"Файл {image_path} не найден.")
                    failed_count += 1
            if image_count >= 100:
                with open('tests/find/result.txt', 'a') as file:
                    file.write(f"Папка: {folders}\n")
                    file.write(f"Успешно распознанных слов: {successful_count} в {folders}\n")
                    file.write(f"Не распознанных слов: {failed_count} в {folders}\n")
                    file.write(f"---------------------------------\n")
                successful_count = 0
                failed_count = 0
                assert successful_count == 0
                assert failed_count == 0
                break