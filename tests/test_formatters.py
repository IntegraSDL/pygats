"""Module with formatters tests"""
import pytest
import inspect
from pygats.pygats import Context, step, check, suite
from pygats.formatters import MarkdownFormatter as MD


@pytest.fixture(name='formatter')
def fixture_formatter():
    """formatter fixture for markdown"""
    return MD()


def test_formatter(formatter, capsys):  # pylint: disable=redefined-outer-name
    """Test formatter"""
    ctx = Context(formatter)
    assert ctx

    step(ctx, 'Hello world')
    cptrd = capsys.readouterr()
    assert cptrd.out == 'Step 1: Hello world\n\n'


def test_check(formatter, capsys):  # pylint: disable=redefined-outer-name
    """Test check function"""
    ctx = Context(formatter)
    assert ctx
    result = check(ctx, 'Hello world', None)
    assert result is None
    cptrd = capsys.readouterr()
    assert cptrd.out == 'Hello world\n\n'


def test_suite(formatter, capsys):
    """Test suite function"""
    ctx = Context(formatter)
    assert ctx
    suite(ctx, inspect.getmodule(test_suite))
    cptrd = capsys.readouterr()
    assert cptrd.out == '# Тестовый набор test_formatters\n\n'
