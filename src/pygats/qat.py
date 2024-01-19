"""
Module for interacting with qt applications
"""

from typing import Optional
import qat
from pygats.pygats import step, passed, failed


def register_application(name: str, path: str, args: Optional[str] = ''):
    """
    Register the application and add it to the configuration file

    Args:
        name (str): application name
        path (str): application parh
        args (Optional[str]): arguments that used when launching the application
    """
    qat.register_application(name=name, path=path, args=args)


def start_application(ctx, name: str, args: Optional[str] = ''):
    """
    Launch the application

    Args:
        ctx (Context): context of test execution
        name (str): application name
        args (Optional[str]): arguments that used when launching the application

    Returns:
        app_ctx (qat.Globals.current_app_context): uniquely identifies the started
            application instance
    """
    step(ctx, f'Запуск приложения {name}')
    try:
        app_ctx = qat.start_application(app_name=name, args=args)
        qat.unlock_application()
    except Exception as e:
        failed(ctx, msg=f'Ошибка запуска приложения\n{e}')
    passed()
    return app_ctx


def close_application(ctx, app_ctx):
    """
    Close the application

    Args:
        ctx (Context): context of test execution
        app_ctx (qat.Globals.current_app_context): uniquely identifies the started
            application instance
    """
    step(ctx, 'Закрытие приложения ...')
    try:
        qat.close_application(app_ctx)
    except Exception as e:
        failed(ctx, msg=f'Ошибка закрытия приложения\n{e}')
    passed()


def typewrite(ctx, definition: dict, message: str, count: Optional[int] = 1):
    """
    Function types keys on keyboard

    Args:
        ctx (Context): context of test execution
        definition (dict): uniquely identifies the QtObject
        message (str): text to typewrite
        count (Optional[int]): number of writes
    """
    step(ctx, f'Набрать на клавиатуре {message} ...')
    try:
        for _ in range(count):
            qat.type_in(definition, message)
    except Exception as e:
        failed(ctx, msg=f'Ошибка набора текста\n{e}')
    passed()


def click_left_button(ctx, definition: dict, x: Optional[int] = None, y: Optional[int] = None,
                      clicks: Optional[int] = 1):
    """
    Function clicks left button of mouse

    Args:
        ctx (Context): context of test execution
        definition (dict): uniquely identifies the QtObject
        x (Optional[int]): coordinates to move mouse pointer
        y (Optional[int]): coordinates to move mouse pointer
        clicks (Optional[int]): number of clicks
    """
    step(ctx, f'Нажать левую кнопку мыши {definition}')
    try:
        for _ in range(clicks):
            qat.mouse_click(definition, x, y)
    except Exception as e:
        failed(msg=f'Ошибка {e}')
    passed()


def find_object(ctx, definition: dict):
    """
    Function finds QtObject in application

    Args:
        ctx (Context): context of test execution
        definition (dict): object definition

    Returns:
        QtObject (list): uniquely identifies the QtObject
    """
    step(ctx, f'Поиск объекта {definition} ...')
    try:
        QtObject = qat.wait_for_object_exists(definition)
    except Exception as e:
        failed(msg=f'Ошибка поиска объекта\n{e}')
    passed()
    return QtObject


def find_all_objects(ctx, definition: dict):
    """
    Function finds all QtObjects in application

    Args:
        ctx (Context): context of test execution
        definition (dict): object definition

    Returns:
        QtObjects (list): uniquely identifies the QtObject
    """
    step(ctx, f'Поиск всех объектов, соответствующих данному определению {definition} ...')
    QtObjects = qat.find_all_objects(definition)
    passed()
    return QtObjects
