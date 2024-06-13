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
"""
Header: Description of test suites
"""
import pygats.pygats as pygats
import pygats.recog as recog

from pygats.formatters import MarkdownFormatter as MD


ctx = pygats.Context(formatter=MD(), timeout=0.5)


def test_function():
    """
    Definition: definition of the test function

    Actions:
        1: action 1
        2: action 2
        3: ...

    Expected: expected result
    """
    pygats.run_action(ctx)
    ...
    pygats.run_action(ctx, action_2_function)
    ...


...


test_suites = [
    test_function,
    ...
]


if __name__ == '__main__':
    pygats.run(ctx, test_suites)

```

As a result of executing the script, we get a report in Markdown format in the "output" directory

## Usage features

Docstring of the document and the test functions are required attributes to get the required test report.
> If you do not specify a docstring, the corresponding report entries will be replaced with standard entries.

Docstring must be in YAML format. Docstring may contain additional entries in this format, if necessary.

When writing a test function, it is necessary to have a docstring that has 3 key entries:
- Definition - definition of the test function, what it checks;
- Actions - a list of actions to perform the verification;
- Expected - expected result.

`run_action()` function is required to print the description of the action before executing it. It can be used in 2 ways:
- `pygats.run_action(ctx)`, after which the steps of executing the action are performed;
- `pygats.run_action(ctx, function, **kwargs)`. In this case, we pass a function containing the necessary steps. If it has additional arguments, we pass them separated by commas. The arguments must be named.
