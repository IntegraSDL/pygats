pyGATs
========

**This library is in development process. API is not stabilized yet. It will
be completly changed soon.**


pyGATs tis python3 library which combines power of pyautogui, opencv, tesseract, 
markdown and other staff to automate end-to-end and exploratorytesting.

This library might be used to automate testing process with Xvbf and docker.

pyGATs depends on pyautogui, pytesseract, opencv and others. Please see section
dependencies in pyproject.toml file.,
by providing a basic explanation of how to do it easily.

Look how easy it is to use:

    import pygats
    # Get your stuff done
    pygats.do_stuff()

Features
--------

- provides interface (pyautogui) to control mouse, keyboard and screenshots
  during testing process
- provides screenshots processing (opencv) to check test steps results
- provides text recognition (pytesseract) to find and understand text on the
  screenshots

Installation
------------

Install pyGATs by running:

    install pygats

Contribute
----------

- Issue Tracker: https://github.com/IntegraSDL/pygats/issues
- Source Code: https://github.com/IntegraSDL/pygats

Support
-------

If you are having issues, please let us know through issue tracker

License
-------

The project is licensed under the MIT license.
