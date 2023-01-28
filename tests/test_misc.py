"""Miscellaneous module tests"""
import os
import pytest
from pygats.misc import setup_test_env, teardown_test_env
from pygats.pygats import Context
from pygats.formatters import MarkdownFormatter as MD

# pylint: disable=R0801
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


def test_setup(formatter):
    """test issue #29 setup doesn't return until process is done"""
    ctx = Context(formatter)
    assert ctx
    with open('output/stdout.txt', 'w', encoding='utf-8') as out:
        with open('output/stderr.txt', 'w', encoding='utf-8') as err:
            p = setup_test_env('python3', out, err)
            assert p
            teardown_test_env(ctx, p)
