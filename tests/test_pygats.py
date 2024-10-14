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


@pytest.fixture(scope="session", autouse=True)
def fixture_create_ctx(formatter: MD):
    """ctx fixture for check for ctx creation"""
    global ctx
    ctx = pyg.Context(formatter)
    yield
    return ctx


@pytest.fixture(scope="function", autouse=True)
def fixture_variables():
    """a fixture for initializing variables and clearing them after tests"""
    global SCREENSHOT_INDEX, STEP_INDEX
    yield
    SCREENSHOT_INDEX = 0
    STEP_INDEX = 0


def test_screenshot(capsys):
    """test screenshot"""
    pyg.__screenshot(ctx)
    cptrd = capsys.readouterr()
    assert pyg.SCREENSHOT_INDEX == 1
    print(cptrd.out)
    assert cptrd.out == '![Screenshot](step-0-0-passed.png)\n\n'

    
def test_passed(capsys):
    """test passed"""
    assert pyg.OUTPUT_PATH == pathlib.Path('output')
    pyg.__passed(ctx)
    cptrd = capsys.readouterr()
    assert pyg.STEP_INDEX == 0
    assert cptrd.out == '![Успешно](step-0-passed.png)\n\n**Успешно**\n\n'


def test_step():
    """test step"""
    pyg.__step(ctx,"test_message")
    print(pyg.STEP_INDEX)
    assert pyg.STEP_INDEX == 1
    pyg.__step(ctx,"test_message")
    print(pyg.STEP_INDEX)
    assert pyg.STEP_INDEX == 2


def test_failed():
    """test failed"""
    with pytest.raises(pyg.TestException):
        pyg.__failed("тест пройден")


@pytest.mark.parametrize(
        "string_length, character_set, expectation",
        [
            (0, "grgrtgrtgBSBJCBE", pytest.raises(ValueError)),
            (1, "78439439846N", does_not_raise()),
            (-2, "Тест 2 не пройден", pytest.raises(ValueError)),
            (3, " ", does_not_raise()),
            (4, None, does_not_raise()),
            (5, "",pytest.raises(IndexError))
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
            ("pygats/output/Screenshot from 2024-10-13 20-34-25.png", does_not_raise()),
            ("/pygats/output.png", pytest.raises(OSError)) #test screenshot does not exist
        ]
)
def test_locate_on_screen(img_path,expectation):
    """test locate_on_screen"""
    with expectation:
        pyg.locate_on_screen(ctx, img_path)


def test_check(): # wanna do __check()
    """test check"""
    none_result = pyg.check(ctx,"test with func=None")
    assert none_result == None
    func_result = pyg.check(ctx,"test with func=__step()", pyg.__step(ctx,"test"))
    assert func_result == pyg.__step(ctx,"test")
    

#approx()

