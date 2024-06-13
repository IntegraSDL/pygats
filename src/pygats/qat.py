"""
Module for qt applications interacting
"""

from typing import Optional
import qat
import pathlib
from pygats.pygats import step, passed, failed


def register_application(name: str, path: str, args: Optional[str] = ''):
    """
    Register the application and add it to the configuration file

    Args:
        name (str): application name
        path (str): application path
        args (Optional[str]): application launch arguments
    """
    qat.register_application(name=name, path=path, args=args)


def start_application(ctx, name: str, args: Optional[str] = ''):
    """
    Launch the application

    Args:
        ctx (Context): context of test execution
        name (str): application name
        args (Optional[str]): application launch arguments

    Returns:
        app_ctx (qat.Globals.current_app_context): uniquely identifies the started
            application instance
    """
    step(ctx, f'Запуск приложения "{name}"')
    try:
        app_ctx = qat.start_application(app_name=name, args=args)
        qat.unlock_application()
    except Exception as e:
        failed(msg=f'Ошибка запуска приложения\n{e}')
    passed(ctx)
    return app_ctx


def set_current_application_context(ctx, app_ctx):
    """
    Change the current application context.

    Args:
        ctx (Context): context of test execution
        app_ctx (qat.Globals.current_app_context): uniquely identifies the started
            application instance
    """
    step(ctx, 'Смена текущего рабочего окна приложения')
    try:
        qat.set_current_application_context(app_ctx)
    except Exception as e:
        failed(msg=f'Ошибка смены рабочего окна приложения\n{e}')
    passed(ctx)


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
        failed(msg=f'Ошибка закрытия приложения\n{e}')
    passed(ctx)


def typewrite(ctx, definition: dict, message: str, count: Optional[int] = 1):
    """
    Function types keys on keyboard

    Args:
        ctx (Context): context of test execution
        definition (dict): uniquely identifies the QtObject
        message (str): text to typewrite
        count (Optional[int]): number of writes
    """
    if message.startswith('<') and message.endswith('>'):
        step(ctx, f'Набрать на клавиатуре "{message[1:-1]}" ...')
    else:
        step(ctx, f'Набрать на клавиатуре "{message}" ...')
    try:
        for _ in range(count):
            qat.type_in(definition, message)
    except Exception as e:
        failed(msg=f'Ошибка набора текста\n{e}')
    passed(ctx)


def click_left_button(ctx, definition: str, x: Optional[int] = None, y: Optional[int] = None,
                      clicks: Optional[int] = 1, object_name='None'):
    """
    Function clicks left button of mouse

    Args:
        ctx (Context): context of test execution
        definition (str): uniquely identifies the QtObject
        x (Optional[int]): coordinates to move mouse pointer
        y (Optional[int]): coordinates to move mouse pointer
        clicks (Optional[int]): number of clicks
    """
    message = str(definition)
    if message.startswith('<') and message.endswith('>'):
        message = message[1:-1]
    step(ctx, f'Нажать левую кнопку мыши по объекту "{object_name}"')
    try:
        for _ in range(clicks):
            qat.mouse_click(definition, x, y)
    except Exception as e:
        failed(msg=f'Ошибка {e}')
    passed(ctx)


def find_object(ctx, definition: dict, object_name='QtObject'):
    """
    Function finds QtObject in application

    Args:
        ctx (Context): context of test execution
        definition (dict): object definition

    Returns:
        QtObject (qat.internal.qt_object.QtObject): uniquely identifies the QtObject
    """
    step(ctx, f'Поиск объекта "{object_name}" ...')
    try:
        QtObject = qat.wait_for_object_exists(definition)
    except Exception as e:
        failed(msg=f'Ошибка поиска объекта\n{e}')
    passed(ctx)
    return QtObject


def find_all_objects(ctx, definition: dict):
    """
    Function finds all QtObjects in application

    Args:
        ctx (Context): context of test execution
        definition (dict): object definition

    Returns:
        QtObjects (qat.internal.qt_object.QtObject): uniquely identifies the QtObject
    """
    step(ctx, f'Поиск всех объектов, соответствующих данному определению "{definition}" ...')
    QtObjects = qat.find_all_objects(definition)
    passed(ctx)
    return QtObjects


def find_object_by_id(ctx, window, id=''):
    """
    Function returns object by the specified id

    Args:
        window (qat.internal.qt_object.QtObject): uniquely identifies the QtObject (target window)
        id (str): id for QtObject. Defaults to ''.

    Returns:
        obj (qat.internal.qt_object.QtObject): uniquely identifies the QtObject
    """
    step(ctx, f'Поиск объекта по индексу "{id}" ...')
    obj = window.children[int(id[0])]
    id = id[1:]
    while id:
        obj = obj.children[int(id[0])]
        id = id[1:]
    passed(ctx)
    return obj


def generate_object_tree(ctx, window, dir_name='temp'):
    """
    Function generates tree of directories and files that repeats the structure of the object tree

    Args:
        ctx (Context): context of test execution
        window (qat.internal.qt_object.QtObject): uniquely identifies the QtObject (target window)
        dir_name (str): name of directory. Defaults to './temp'.
    """
    step(ctx, f'Создание директории {dir_name}, повторяющей структуру дерева объектов')
    path = pathlib.Path(f'./{dir_name}')
    path.mkdir(exist_ok=True)
    path = path / 'tree.yaml'
    path.touch(exist_ok=True)
    tree_file = open(path, 'w')

    def tree(window, indent='', index=0, parent_path=pathlib.Path(f'./{dir_name}'), id=''):
        for item in window.children:
            current_path = parent_path / f'{index}_{item.type}'
            id += str(index)
            if item.children != []:
                tree_file.write(f'{indent}[{index}]{item.type}\n')
                current_path.mkdir(exist_ok=True)
                tree(item, indent + '  ', index=0, parent_path=current_path, id=id)
                id = id[:len(id) - 1]
                index += 1
            else:
                tree_file.write(f'{indent}[{index}]{item.type}\n')
                current_path = current_path.with_suffix('.yaml')
                current_path.touch(exist_ok=True)
                with open(current_path, 'w') as file:
                    file.write(f'{item.type}: \"{id}\"\n\n')
                    for property in item.list_properties():
                        file.write(f'{property[0]}: {property[1]}\n')
                id = id[:len(id) - 1]
                index += 1

    tree(window)
    tree_file.close()
    passed(ctx)


def compare_object_tree(ctx, window, dir_name):
    """
    Function for comparison of changes in the properties of window object

    Args:
        window (qat.internal.qt_object.QtObject): uniquely identifies the QtObject (target window)
        dir_name (str): name of directory. Defaults to './temp'.
    """
    step(ctx, f'Сравнение изменений в свойствах объекта {dir_name}')
    path = pathlib.Path(f'./{dir_name}/differences.yaml')
    path.touch(exist_ok=True)
    diff_file = open(path, 'w')

    def tree(window, indent='', index=0, parent_path=pathlib.Path(f'./{dir_name}'), id=''):
        for item in window.children:
            current_path = parent_path / f'{index}_{item.type}'
            id += str(index)
            if item.children != []:
                tree(item, indent + '  ', 0, current_path, id)
                id = id[:len(id) - 1]
                index += 1
            else:
                duplicate = current_path.with_suffix('._d.yaml')
                temp_file = current_path.with_suffix('._temp.yaml')
                current_path = current_path.with_suffix('.yaml')
                if not current_path.exists():
                    return
                temp_file.touch(exist_ok=True)
                duplicate.touch(exist_ok=True)
                with open(duplicate, 'w') as file:
                    file.write(f'{item.type}: \"{id}\"\n\n')
                    for property in item.list_properties():
                        file.write(f'{property[0]}: {property[1]}\n')
                with open(current_path, 'r') as old_file, open(duplicate, 'r') as new_file, \
                     open(temp_file, 'w') as temp:
                    key = False
                    for old_line, new_line in zip(old_file, new_file):
                        if old_line != new_line:
                            key = True
                            temp.write(f'| old: {old_line}')
                            temp.write(f'| new: {new_line}')
                        else:
                            temp.write(old_line)
                    if key:
                        diff_file.write(f'Несоответствие: {current_path}\n')
                temp_file.replace(current_path)
                duplicate.unlink()
                id = id[:len(id) - 1]
                index += 1

    tree(window)
    diff_file.close()
    passed(ctx)
