"""Module with library tests"""
import pytest
import pygats.recog as rec
import pygats.pygats as pyg
from pygats.formatters import MarkdownFormatter as MD
from PIL import Image

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


def test_rectangle_center_coords():
    """test rectangle_center_coords"""
    coord = rec.ROI(1,3,1,3)
    abscissa_and_ordinate = rec.ROI.rectangle_center_coords(coord)
    print(rec.ROI.rectangle_center_coords(coord))
    assert abscissa_and_ordinate == (1.5, 4.5)


def test_check_text(capsys, generator_photo):
    """test check_text"""
    text = rec.SearchedText("File", "eng", None)
    img = generator_photo
    width, height = img.size
    assert width > 0
    assert height > 0
    rec.check_text(ctx, img, text)
    cptrd = capsys.readouterr()
    print(cptrd)
    assert '![Успешно](step-1-passed.png)\n\n**Успешно**\n\n' in cptrd.out


def test_check_text_failed(generator_photo):
    """test check_text with word which tesseract cant find"""
    text = rec.SearchedText("Fie", "eng", None)
    img = generator_photo
    with pytest.raises(pyg.TestException):
        rec.check_text(ctx, img, text)
        assert pyg.failed() == f"{text} не найден на изображении"
