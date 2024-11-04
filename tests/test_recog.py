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


def test_check_text_1(capsys):
    text = rec.SearchedText("File", "eng", None)
    gen.bg_changer(True)
    rec.check_text(ctx, "tests/find/1.jpg", text)
    cptrd = capsys.readouterr()
    assert '![Успешно](step-1-passed.png)\n\n**Успешно**\n\n' in cptrd.out
