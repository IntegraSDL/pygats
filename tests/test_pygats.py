"""Module with library tests"""
import os
import pytest
from pygats.pygats import Context, screenshot
from pygats.formatters import MarkdownFormatter as MD
#from PIL import Image

def setup_module():
    """Setup module to prepare testing environment"""
    try:
        os.mkdir('output')
    except FileExistsError:
        pass


@pytest.fixture(name='formatter')
def fixture_formatter():
    """formatter fixture for markdown"""
    return MD()


def test_screenshot(formatter, capsys):
    """test screenshot"""
    ctx = Context(formatter)
    assert ctx
    screenshot(ctx)
    cptrd = capsys.readouterr()
    print(cptrd.out)
    assert cptrd.out == '![Screenshot](step-2-0-passed.png)\n\n'
