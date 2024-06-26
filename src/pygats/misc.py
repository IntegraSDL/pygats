"""
This module consists of miscellaneous functions of pyGATs.
These functions might be removed from library in the future.
"""


import time
import subprocess
import os
from pygats.pygats import alt_with_key, passed


def setup_test_env(ctx, cmd, out_log, err_log):
    """
    Setup test environment (run cmd) before execute test cases

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        cmd (string): command line to start test process
        out_log (string): path to log file where stdout of the test process
                          will be stored
        err_log (string): path to log file where stderr of the test process
                          will be stored

    Returns:
        testProc (subprocess.Popen): returns Popen object which
                                     stores executed test process
    """
    ctx.formatter.print_header(2, 'Подготовка стенда к работе')
    ctx.formatter.print_para(f'{cmd} ...')
    env = os.environ.copy()
    dir_name = os.path.dirname(cmd)
    if dir_name == '':
        dir_name = os.path.expanduser('~')
    with subprocess.Popen(
            [cmd], stderr=err_log,
            stdout=out_log, env=env,
            cwd=dir_name) as test_proc:
        time.sleep(1)
        if test_proc is not None:
            passed(ctx)
        return test_proc


def teardown_test_env(ctx, test_proc):
    """
    Tear down test suite after all test cases done

    Args:
        ctx (Context): An object that contains information about the current
                    context.
        test_proc (subprocess.Popen class): object manage testing process
    """
    ctx.formatter.print_header(2, 'Завершение работы стенда')
    alt_with_key(ctx, 'f4')
    test_proc.kill()
    passed(ctx)
