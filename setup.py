from setuptools import setup

with open("README.md", "rb") as file:
    readme = file.read().decode("utf-8")

setup(name='pymagic_autogui',
      version='0.0.1',
      description='Automate end-to-end and exploratory testing',
      long_description=readme,
      long_description_content_type="text/md",
      url='https://github.com/IntegraSDL/pymagic-autogui',
      author='vsysoev',
      license='MIT',
      packages=['pymagic_autogui'],
      python_requires=">=3.7",
      install_requires=[
          'pyautogui',
          'Pillow',
          'pytesseract',
          'Levenshtein',
          'opencv-python',
          'numpy'
      ],
      extras_require={
        'dev': [
            # Testing
            'pytest',
            'tox'
        ]
      }
    )