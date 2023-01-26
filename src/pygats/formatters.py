"""Formatters module
This module provides classes which supports formatters to help with test outputs
See MarkdownFormatter as example
"""

class MarkdownFormatter:
    """MD formatter for caption"""
    def print_header(self, level, msg):
        """Print markdown header message"""
        print()
        header_level = '#'*level
        print(f'{header_level} {msg}')
        print()

    def print_para(self, msg):
        """Print markdown paragraph"""
        print()
        print(f'{msg}')
        print()

    def print_footer(self, msg):
        """Print footer message"""
        print()
        print(f'{msg}')
        print()

    def print_code(self, code):
        """Print formatted code"""
        print('```')
        print(code)
        print('```')

    def print_img(self, img_path):
        """Print image path"""
        print(f'![Screenshot]({img_path})')
        print()
