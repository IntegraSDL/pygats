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
        print(text)
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
    def print_img(img_path, text):
        """
        Print image path

        Args:
            img_path (string): path to image
        """
        print(f'![{text}]({img_path})')
        print()

    @staticmethod
    def print_bold(text):
        """
        Print Markdown bold text

        Args:
            text (string): bold text
        """
        print(f'**{text}**')
        print()

    @staticmethod
    def print_list(text):
        """
        Print Markdown unordered list text

        Args:
            text (string): unordered list text
        """
        print(f'* {text}')
