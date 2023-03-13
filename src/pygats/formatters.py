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
