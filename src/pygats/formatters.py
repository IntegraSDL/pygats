"""Formatters module
This module provides classes which supports formatters to help with test
outputs. See MarkdownFormatter as example
"""


class MarkdownFormatter:
    """MD formatter for caption"""
    @staticmethod
    def print_header(level, text):
        """
        Print Markdown header with spaces lines

        Args:
            level (int): Level of header. Count of # in markdown header.
            text (string): Header text
        """
        print()
        header_level = '#' * level
        print(f'{header_level} {text}')
        print()

    @staticmethod
    def print_para(text):
        """
        Print Markdown paragraph

        Args:
            text (string): paragraph text
        """
        print()
        print(f'{text}')
        print()

    @staticmethod
    def print_footer(text):
        """
        Print footer

        Args:
            text (string): footer text
        """
        print()
        print(f'{text}')
        print()

    @staticmethod
    def print_code(code):
        """
        Print formatted code

        Args:
            code (string): code snippet to be printed
        """
        print('```')
        print(code)
        print('```')

    @staticmethod
    def print_img(img_path):
        """
        Print image path

        Args:
            img_path (string): path to image
        """
        print(f'![Screenshot]({img_path})')
        print()


def print_color_text(text: str, color: str):
    """
    Display text in a specific color

    Args:
        text (str): text to be printed
        color (str): text color
    """
    # pylint: disable=consider-using-f-string
    colors = {
        'red': "\033[31m{}\033[0m",
        'green': "\033[32m{}\033[0m",
        'yellow': "\033[33m{}\033[0m",
        'blue': "\033[34m{}\033[0m",
        'purple': "\033[35m{}\033[0m",
        'light blue': "\033[36m{}\033[0m",
        'white': "\033[37m{}\033[0m"
    }
    if colors.get(color):
        print(colors.get(color).format(text))
    else:
        print(text)
