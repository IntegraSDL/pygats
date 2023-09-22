import pygats.pygats as p
import pygats.recog as r
from pygats.formatters import MarkdownFormatter as MD
import time
import gen
import pytest
import os


def time_decorator(func):
    def wrapper():
        start = time.time()
        func()
        seconds = int(time.time() - start)
        seconds = seconds % (24 * 3600)
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        with open('tests/find/result.txt', 'a') as file:
            file.write('Время выполнения: %02d:%02d:%02d\n' % (hours, minutes, seconds))
    return wrapper


def find(img, txt):
    _, key = r.find_text(img, txt)
    if not key:
        global count_false
        count_false += 1
        print(f'WARNING! Текст "{txt.content}" не найден')
    else:
        global count_true
        count_true += 1


def print_percent(count_true, count_false):
    with open('tests/find/result.txt', 'a') as file:
        file.write('Результаты выполнения:\n')
        count_all = count_true+count_false
        file.write(f'\tУспешно: {count_true}/{count_all}, %.2f' % ((count_true/count_all)*100) + '%\n')
        file.write(f'\tНеуспешно: {count_false}/{count_all}, %.2f' % ((count_false/count_all)*100) + '%\n')


ctx = p.Context(MD())


@time_decorator
def study_font_white():
    with open('tests/find/result.txt', 'a') as file:
        file.write('\n<Исследование распознавания в зависимости от шрифта\n\
                   Белый фон 350х50, черный текст 18 размера\n')
    global count_true
    global count_false
    count_true = 0
    count_false = 0
    fonts_list = ['Arial', 'Arial_Bold',
                  'Arial_Italic', 'Arial_Bold_Italic',
                  'Calibri', 'Calibri_Bold',
                  'Calibri_Italic', 'Calibri_Bold_Italic',
                  'TimesNewRoman', 'TimesNewRoman_Bold',
                  'TimesNewRoman_Italic', 'TimesNewRoman_Bold_Italic']
    with open('tests/find/words.txt') as test_file:
        lines = test_file.readlines()
    for font in fonts_list:
        for line in lines:
            line = line[:len(line)-1]
            img = gen.gen('white', 10, 15, font, 18, line, True)
            find(img, r.SearchedText(line, 'rus', 'all'))
    print_percent(count_true, count_false)


@time_decorator
def study_font_gray():
    with open('tests/find/result.txt', 'a') as file:
        file.write('\n<Исследование распознавания в зависимости от шрифта\n\
                   Серый фон 350х50, черный текст 18 размера\n')
    global count_true
    global count_false
    count_true = 0
    count_false = 0
    fonts_list = ['Arial', 'Arial_Bold',
                  'Arial_Italic', 'Arial_Bold_Italic',
                  'Calibri', 'Calibri_Bold',
                  'Calibri_Italic', 'Calibri_Bold_Italic',
                  'TimesNewRoman', 'TimesNewRoman_Bold',
                  'TimesNewRoman_Italic', 'TimesNewRoman_Bold_Italic']
    with open('tests/find/words.txt') as test_file:
        lines = test_file.readlines()
    for font in fonts_list:
        for line in lines:
            line = line[:len(line)-1]
            img = gen.gen('gray', 10, 15, font, 18, line, True)
            find(img, r.SearchedText(line, 'rus', 'all'))
    print_percent(count_true, count_false)


@time_decorator
def study_font_blue():
    with open('tests/find/result.txt', 'a') as file:
        file.write('\n<Исследование распознавания в зависимости от шрифта\n\
                   Синий фон 350х50, черный текст 18 размера\n')
    global count_true
    global count_false
    count_true = 0
    count_false = 0
    fonts_list = ['Arial', 'Arial_Bold',
                  'Arial_Italic', 'Arial_Bold_Italic',
                  'Calibri', 'Calibri_Bold',
                  'Calibri_Italic', 'Calibri_Bold_Italic',
                  'TimesNewRoman', 'TimesNewRoman_Bold',
                  'TimesNewRoman_Italic', 'TimesNewRoman_Bold_Italic']
    with open('tests/find/words.txt') as test_file:
        lines = test_file.readlines()
    for font in fonts_list:
        for line in lines:
            line = line[:len(line)-1]
            img = gen.gen('blue', 10, 15, font, 18, line, True)
            find(img, r.SearchedText(line, 'rus', 'all'))
    print_percent(count_true, count_false)


@time_decorator
def study_font_yellow():
    with open('tests/find/result.txt', 'a') as file:
        file.write('\n<Исследование распознавания в зависимости от шрифта\n\
                   Желтый фон 350х50, черный текст 18 размера\n')
    global count_true
    global count_false
    count_true = 0
    count_false = 0
    fonts_list = ['Arial', 'Arial_Bold',
                  'Arial_Italic', 'Arial_Bold_Italic',
                  'Calibri', 'Calibri_Bold',
                  'Calibri_Italic', 'Calibri_Bold_Italic',
                  'TimesNewRoman', 'TimesNewRoman_Bold',
                  'TimesNewRoman_Italic', 'TimesNewRoman_Bold_Italic']
    with open('tests/find/words.txt') as test_file:
        lines = test_file.readlines()
    for font in fonts_list:
        for line in lines:
            line = line[:len(line)-1]
            img = gen.gen('yellow-grad', 10, 15, font, 18, line, True)
            find(img, r.SearchedText(line, 'rus', 'all'))
    print_percent(count_true, count_false)


@time_decorator
def study_size():
    with open('tests/find/result.txt', 'a') as file:
        file.write('\n<Исследование распознавания в зависимости от размера шрифта\n\
                   Белый фон 1920х1080, черный текст размера 8-112 с шагом 8\n')
    global count_true
    global count_false
    count_true = 0
    count_false = 0
    fonts_list = ['Arial', 'Arial_Bold',
                  'Arial_Italic', 'Arial_Bold_Italic',
                  'Calibri', 'Calibri_Bold',
                  'Calibri_Italic', 'Calibri_Bold_Italic',
                  'TimesNewRoman', 'TimesNewRoman_Bold',
                  'TimesNewRoman_Italic', 'TimesNewRoman_Bold_Italic']
    with open('tests/find/words.txt') as test_file:
        lines = test_file.readlines()
    for font in fonts_list:
        diff = 65
        for size in range(8, 113, 8):
            for line in lines:
                line = line[:len(line)-1]
                img = gen.gen('white', 1005-diff, 500, font, size, line)
                find(img, r.SearchedText(line, 'rus', 'all'))
            diff += 65
    print_percent(count_true, count_false)


@pytest.mark.skipif("FIND_RUN" not in os.environ, reason="Starting is done manually")
def test_all():
    study_font_white()
    study_font_gray()
    study_font_blue()
    study_font_yellow()
    study_size()
