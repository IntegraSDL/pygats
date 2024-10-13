"""Module with library tests"""
import os
import pathlib
import pytest
from pygats.pygats import *
from pygats.formatters import MarkdownFormatter as MD
from pygats.pygats import __step, __screenshot, __passed, __failed
from contextlib import nullcontext as does_not_raise

from pygats.recog import recognize_text_with_data

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
    ctx = Context(formatter)
    assert ctx
    yield
    ctx = None


@pytest.fixture(scope="function", autouse=True)
def fixture_variables():
    global SCREENSHOT_INDEX, STEP_INDEX
    SCREENSHOT_INDEX = 0
    STEP_INDEX = 0
    yield
    SCREENSHOT_INDEX = 0
    STEP_INDEX = 0


def test_screenshot(capsys):
    """test screenshot"""
    __screenshot(ctx)
    from pygats.pygats import SCREENSHOT_INDEX
    cptrd = capsys.readouterr()
    assert SCREENSHOT_INDEX == 1
    print(cptrd.out)
    assert cptrd.out == '![Screenshot](step-0-0-passed.png)\n\n'

    
def test_passed(capsys):
    """test passed"""
    assert OUTPUT_PATH == pathlib.Path('output')
    if SCREENSHOTS_ON:
        __passed(ctx)
        cptrd = capsys.readouterr()
        assert STEP_INDEX == 0
        assert cptrd.out == '![Успешно](step-0-passed.png)\n\n**Успешно**\n\n'


def test_step():
    """ test step"""
    __step(ctx,"test_message")
    from pygats.pygats import STEP_INDEX
    print(STEP_INDEX)
    assert STEP_INDEX == 1
    __step(ctx,"test_message")
    from pygats.pygats import STEP_INDEX
    print(STEP_INDEX)
    assert STEP_INDEX == 2


@pytest.mark.parametrize(
        "exception, msg",
        [
            (TestException, "Тест 1 не пройден"),
            (TestException, "Тест 2 не пройден"),
            (TestException, "Тест 3 не пройден"),
        ]
)
def test_failed(exception, msg):
    """test failed"""
    with pytest.raises(exception):
        __failed(msg)
    with pytest.raises(TestException):
        __failed()


@pytest.mark.parametrize(
        "string_length, character_set, expectation",
        [
            (0, "grgrtgrtgBSBJCBE", pytest.raises(ValueError)),
            (1, "78439439846N" , does_not_raise()),
            (-2, "Тест 2 не пройден", pytest.raises(ValueError)),
            (3, " ", does_not_raise()),
            (4, None, does_not_raise()),
            (5, "",pytest.raises(IndexError))
        ]
)
def test_random_string(string_length, character_set, expectation):
    with expectation:
        symbol = random_string(string_length, character_set )
        print(symbol)
    if character_set != "" and string_length > 0:
        assert string_length == len(symbol)


@pytest.mark.parametrize(
        "img_path, expectation",
        [
            ("/home/muervos/pygats_folder/pygats/output/Screenshot from 2024-10-13 20-34-25.png", does_not_raise()),
            ("/home/muervos/pygats_folder/pygats/output.png", pytest.raises(OSError)) #test screenshot does not exist
        ]
)
def test_locate_on_screen(img_path,expectation):
    with expectation:
        locate_on_screen(ctx, img_path)


def test_check(): # wanna do __check()
    none_result = check(ctx,"test with func=None")
    assert none_result == None
    func_result = check(ctx ,"test with func=",__step(ctx,"test"))
    assert func_result == __step(ctx,"test")
    

#approx()

