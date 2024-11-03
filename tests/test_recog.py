"""Module with library tests"""
from pathlib import Path
import pytest
import pygats.recog as rec
import pygats.pygats as pyg
from pygats.formatters import MarkdownFormatter as MD
from PIL import Image
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

def test_check_text(capsys, generator_photo):
    """test check_text checks if "File is exist on image"""
    text = rec.SearchedText("File", "eng", None)
    width, height = img.size
    assert width > 0
    assert height > 0
    fill_color = Path('find/fill_colors')
    for picture in fill_color.glob('*'):
        img = Image.open(f'tests/find/fill_colors/{fill_color[1:]}.jpg')
        print(f"Проверка картинки {picture}с цветом шрифта {fill_color[1:]}")
        rec.check_text(ctx, img, text)
        cptrd = capsys.readouterr()
        assert '![Успешно](step-1-passed.png)\n\n**Успешно**\n\n' in cptrd.out


def test_check_text_failed(capsys, generator_photo):
    """test check_text with word Fie which tesseract cant find"""
    text = rec.SearchedText("Fie", "eng", None)
    img = generator_photo
    with pytest.raises(pyg.TestException):
        rec.check_text(ctx, img, text)
        cptrd = capsys.readouterr()
        assert cptrd == f"{text} не найден на изображении"


def test_check_text_1(capsys):
    text = rec.SearchedText("File", "eng", None)
    gen.bg_changer()
    rec.check_text(ctx, "tests/find/1.jpg", text)
    cptrd = capsys.readouterr()
    assert '![Успешно](step-1-passed.png)\n\n**Успешно**\n\n' in cptrd.out
