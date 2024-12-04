"""Module with library tests"""
import os
import pathlib
import pytest
import pygats.pygats as pyg
from pygats.formatters import MarkdownFormatter as MD
from contextlib import nullcontext as does_not_raise

def setup_module():
    """Setup module to prepare testing environment"""
    try:
        os.mkdir('output')
    except FileExistsError:
        pass


@pytest.fixture(name='formatter', scope="session", autouse=True)
def fixture_formatter():
    """formatter fixture for markdown"""
    return MD()


@pytest.fixture(name="ctx_formatter", scope="session", autouse=True)
def create_ctx(formatter: MD):
    """ctx fixture for check for ctx creation"""
    ctx = pyg.Context(formatter)
    return ctx


@pytest.fixture(name="variables", scope="function")
def variables():
    """a fixture for initializing variables and clearing them after tests"""
    global SCREENSHOT_INDEX, STEP_INDEX
    yield
    SCREENSHOT_INDEX = 0
    STEP_INDEX = 0


def test_screenshot(capsys, ctx_formatter, variables):
    """test screenshot"""
    ctx = ctx_formatter
    pyg.screenshot(ctx)
    cptrd = capsys.readouterr()
    assert pyg.SCREENSHOT_INDEX == 1
    print(cptrd.out)
    assert cptrd.out == '![Screenshot](step-0-0-passed.png)\n\n'

    
def test_passed(capsys, variables, ctx_formatter):
    """test passed"""
    ctx = ctx_formatter
    assert pyg.OUTPUT_PATH == pathlib.Path('output')
    pyg.passed(ctx)
    cptrd = capsys.readouterr()
    assert pyg.STEP_INDEX == 0
    assert cptrd.out == '![Успешно](step-0-passed.png)\n\n**Успешно**\n\n'


def test_step(variables, ctx_formatter):
    """test step"""
    ctx = ctx_formatter
    pyg.step(ctx, "test_message")
    assert pyg.STEP_INDEX == 1


def test_failed():
    """test failed"""
    with pytest.raises(pyg.TestException):
        pyg.failed("тест пройден")


@pytest.mark.parametrize(
        "string_length, character_set, expectation",
        [
            (0, "grgrtgrtgBSBJCBE", pytest.raises(ValueError)),
            (1, "78439439846N", does_not_raise()),
            (-2, "Тест 2 не пройден", pytest.raises(ValueError)),
            (3, " ", does_not_raise()),
            (4, None, does_not_raise()),
            (5, "", does_not_raise())
        ]
)
def test_random_string(string_length, character_set, expectation):
    """test random_string"""
    with expectation:
        symbol = pyg.random_string(string_length, character_set)
        print(symbol)
        assert string_length == len(symbol)


@pytest.mark.parametrize(
        "img_path, expectation",
        [
            ("pygats/output/example.png", does_not_raise()),
            ("pygats/output.png", pytest.raises(pyg.TestException)),
        ]
)
def test_locate_on_screen(img_path, expectation, ctx_formatter):
    """test locate_on_screen"""
    ctx = ctx_formatter
    with expectation:
        pyg.locate_on_screen(ctx, img_path)


def test_check(ctx_formatter): 
    """test check"""
    ctx = ctx_formatter
    none_result = pyg.check(ctx, "test with func=None")
    assert none_result == None
    func_result = pyg.check(ctx, "test with func=step()", pyg.step(ctx, "test"))
    assert func_result == pyg.step(ctx, "test")