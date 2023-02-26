"""
This module consists of miscellaneous functions of pyGATs.
These functions might be removed from library in future.
"""


import time
import subprocess
import os
from pygats.pygats import alt_with_key, passed


def setup_test_env(cmd, out_log, err_log):
    """
    Setup test environment (run cmd) before execute test cases

    Args:
        cmd (string): command line to start test process
        out_log (string): path to log file where stdout of the test process
                          will be stored
        err_log (string): path to log file where stderr of the test process
                          will be stored

    Returns:
        testProc (subprocess.Popen): returns Popen object which
                                     stores executed test process
    """
    print('## Подготовка стенда к работе')
    print(f'{cmd} ...')
    env = os.environ.copy()
    dirName = os.path.dirname(cmd)
    if dirName == '':
        dirName = os.path.expanduser('~')
    with subprocess.Popen(
            [cmd], stderr=err_log,
            stdout=out_log, env=env,
            cwd=dirName) as testProc:
        time.sleep(1)
        if testProc is not None:
            passed()
        return testProc


def teardown_test_env(ctx, test_proc):
    """
    Tear down test suite after all test cases done

    Args:
        ctx (Context pygats.Context): context
        test_proc (subprocess.Popen class): object manage testing process
    """
    print('## Завершение работы стенда')
    alt_with_key(ctx, 'f4')
    test_proc.kill()
    passed()
