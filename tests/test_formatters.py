"""Module with formatters tests"""
import pytest
from pygats.pygats import Context, begin_test, step, check, suite
from pygats.formatters import MarkdownFormatter as MD


@pytest.fixture(name='formatter')
def fixture_formatter():
    """formatter fixture for markdown"""
    return MD()


def test_formatter(formatter, capsys):  # pylint: disable=redefined-outer-name
    """Test formatter"""
    ctx = Context(formatter)
    assert ctx
    begin_test(ctx, 'First message')
    cptrd = capsys.readouterr()
    assert cptrd.out == '\n### First message\n\n'

    step(ctx, 'Hello world')
    cptrd = capsys.readouterr()
    assert cptrd.out == '\nStep 1: Hello world\n\n'


def test_check(formatter, capsys):  # pylint: disable=redefined-outer-name
    """Test check function"""
    ctx = Context(formatter)
    assert ctx
    result = check(ctx, 'Hello world', None)
    assert result is None
    cptrd = capsys.readouterr()
    assert cptrd.out == '\nHello world\n\n'


def test_suite(formatter, capsys):
    """Test suite function"""
    ctx = Context(formatter)
    assert ctx
    suite(ctx, 'suite name', 'Hello world')
    cptrd = capsys.readouterr()
    assert cptrd.out == '\n\n## Hello world\n\n'
