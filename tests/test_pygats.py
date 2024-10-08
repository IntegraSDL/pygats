"""Module with library tests"""
import os
import pathlib
import pytest
from pygats.pygats import screenshot, Context
from pygats.formatters import MarkdownFormatter as MD
from pygats.pygats import step
from pygats.pygats import passed, OUTPUT_PATH, SCREENSHOTS_ON
from pygats.pygats import failed, TestException

#from PIL import Image


@pytest.fixture(name='formatter')
def fixture_formatter():
    """formatter fixture for markdown"""
    return MD()


@pytest.fixture(name="create_ctx")
def fixture_create_ctx(formatter: MD):
    """ctx fixture for check for ctx creation"""
    global ctx 
    ctx = Context(formatter)
    assert ctx


def setup_module():
    """Setup module to prepare testing environment"""
    try:
        os.mkdir('output')
    except FileExistsError:
        pass


@pytest.mark.usefixtures("create_ctx")
class Test_pygats:
    def test_screenshot(formatter, capsys):
        """test screenshot"""
        SCREENSHOT_INDEX = 0
        screenshot(ctx)
        from pygats.pygats import SCREENSHOT_INDEX
        cptrd = capsys.readouterr()
        assert SCREENSHOT_INDEX == 1
        print(cptrd.out)
        assert cptrd.out == '![Screenshot](step-0-0-passed.png)\n\n'


    def test_step(self, formatter: MD):  
        STEP_INDEX = 0
        step(ctx,"test_message")
        from pygats.pygats import STEP_INDEX
        print(STEP_INDEX)
        assert STEP_INDEX == 1
        step(ctx,"test_message")
        from pygats.pygats import STEP_INDEX
        print(STEP_INDEX)
        assert STEP_INDEX == 2


    def test_passed(self, formatter: MD, capsys: pytest.CaptureFixture[str]):
        assert OUTPUT_PATH == pathlib.Path('output')
        if SCREENSHOTS_ON:
            passed(ctx)
            cptrd = capsys.readouterr()
            assert cptrd.out == '![Успешно](step-0-passed.png)\n\n**Успешно**\n\n'


    @pytest.mark.parametrize(
            "exception, msg",
            [
                (TestException, "Тест 1 не пройден"),
                (TestException, "Тест 2 не пройден"),
                (TestException, "Тест 3 не пройден"),
            ]
    )
    def test_failed(self, formatter, exception, msg):
        with pytest.raises(exception):
            failed(msg)
        with pytest.raises(TestException):
            failed()