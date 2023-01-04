"""Module with library tests"""
import pytest
from pygats.pygats import Context, begin_test, MarkdownFormatter, step
#from PIL import Image

@pytest.fixture
def formatter_fixture():
    """formatter fixture for markdown"""
    return MarkdownFormatter() 


def test_formatter(formatter_fixture, capsys): # pylint: disable=redefined-outer-name
    """Test formatter"""
    ctx = Context(formatter_fixture)
    assert ctx
    begin_test(ctx, 'First message')
    cptrd = capsys.readouterr()
    assert cptrd.out == '\n### First message\n\n'

    step(ctx, 'Hello world')
    cptrd = capsys.readouterr()
    assert cptrd.out == '\nStep 1: Hello world\n\n'
