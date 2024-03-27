# pyGATs

[![Pylint](https://github.com/IntegraSDL/pygats/actions/workflows/pylint.yml/badge.svg)](https://github.com/IntegraSDL/pygats/actions/workflows/pylint.yml)
[![Python package](https://github.com/IntegraSDL/pygats/actions/workflows/python-package.yml/badge.svg)](https://github.com/IntegraSDL/pygats/actions/workflows/python-package.yml)
[![Upload Python Package](https://github.com/IntegraSDL/pygats/actions/workflows/python-publish.yml/badge.svg)](https://github.com/IntegraSDL/pygats/actions/workflows/python-publish.yml)

**This library is in development process. API is not stabilized yet. It will
be completely changed soon.**


This is python3 library which combines power of pyautogui, opencv, tesseract, 
markdown and other staff to automate end-to-end and exploratory testing.

This library might be used to automate testing process with Xvbf and docker.

pyGATs depends on pyautogui, pytesseract, opencv and others. Please see section
dependencies in pyproject.toml file.


## How to test

```
python3 -m pytest
```

## Linter

```
pylint $(git ls-files '*.py')
```
## Build documentation

```
cd docs
make html
```

# Example Usage

```python
import pygats.pygats as pygats
import pygats.recog as recog

from pygats.formatters import MarkdownFormatter as MD


ctx = pygats.Context(MD())


def test_launch_app():
    pygats.begin_test(ctx, "Checking registration and launch of the application")
    ...

def test_login():
    pygats.begin_test(ctx, "Verification of the implementation of login identification and password authentication")
    ...

...

test_suites = [
    test_launch_app,
    test_login,
    ...
]


if __name__ == '__main__':
    pygats.suite(ctx, "report_directory", "Test case")
    pygats.run(test_suites)

```

As a result of executing the script, we get a report in Markdown format in the "output" directory
