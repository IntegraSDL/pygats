"""Module with library tests"""
import pytest
import os
from pygats.pygats import Context, screenshot 
from pygats.formatters import MarkdownFormatter as MD
#from PIL import Image

def setup_module(module):
    try:
        os.mkdir('output')
    except FileExistsError:
        pass
@pytest.fixture
def formatter_fixture():
    """formatter fixture for markdown"""
    return MD()


def test_screenshot(formatter_fixture, capsys):
    """test screenshot"""
    ctx = Context(formatter_fixture)
    assert ctx
    screenshot(ctx)
    cptrd = capsys.readouterr()
    print(cptrd.out)
    assert cptrd.out == '![Screenshot](step-1-0-passed.png)\n\n'


