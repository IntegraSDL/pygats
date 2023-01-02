# pyGATs

[![Pylint](https://github.com/IntegraSDL/pygats/actions/workflows/pylint.yml/badge.svg)](https://github.com/IntegraSDL/pygats/actions/workflows/pylint.yml)
[![Python package](https://github.com/IntegraSDL/pygats/actions/workflows/python-package.yml/badge.svg)](https://github.com/IntegraSDL/pygats/actions/workflows/python-package.yml)
[![Upload Python Package](https://github.com/IntegraSDL/pygats/actions/workflows/python-publish.yml/badge.svg)](https://github.com/IntegraSDL/pygats/actions/workflows/python-publish.yml)

**This library is in development process. API is not stabilized yet. It will
be completly changed soon.**


This is python3 library which combines power of pyautogui, opencv, tesseract, 
markdown and other staff to automate end-to-end and exploratorytesting.

This library might be used to automate testing process with Xvbf and docker.

pyGATs depends on pyautogui, pytesseract, opencv and others. Please see section
dependencies in pyproject.toml file.


## How to test

```
python3 -m pytest
```

## Build documentation

```
cd docs
make html
```
