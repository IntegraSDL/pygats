"""Module with library tests"""
import os
import pytest
from pygats.pygats import Context, screenshot, setup_test_env, teardown_test_env
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
    assert cptrd.out == '![Screenshot](step-1-0-passed.png)\n\n'

def test_setup(formatter):
    """test issue #29 setup doesn't return until process is done"""
    ctx = Context(formatter)
    assert ctx
    with open('output/stdout.txt', 'w', encoding='utf-8') as out:
        with open('output/stderr.txt', 'w', encoding='utf-8') as err:
            p = setup_test_env('python3', out, err)
            assert p
            teardown_test_env(ctx, p)
