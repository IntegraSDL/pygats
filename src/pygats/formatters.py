"""Formatters module
This module provides classes which supports formatters to help with test
outputs. See MarkdownFormatter as example
"""


class MarkdownFormatter:
    """MD formatter for caption"""
    def print_header(self, level, text):
        """
        Print markdown header with spaces lines

        Args:
            level (int): Level of header. Count of # in markdown header.
            text (string): Header text
        """
        print()
        header_level = '#'*level
        print(f'{header_level} {text}')
        print()

    def print_para(self, text):
        """
        Print markdown paragraph

        Args:
            text (string): paragraph text
        """
        print()
        print(f'{text}')
        print()

    def print_footer(self, text):
        """
        Print footer

        Args:
            text (string): footer text
        """
        print()
        print(f'{text}')
        print()

    def print_code(self, code):
        """
        Print formatted code

        Args:
            code (string): code snippet to be printed
        """
        print('```')
        print(code)
        print('```')

    def print_img(self, img_path):
        """
        Print image path

        Args:
            img_path (string): path to image
        """
        print(f'![Screenshot]({img_path})')
        print()
