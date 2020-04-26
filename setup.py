#!/usr/bin/env python
from pathlib import Path

from setuptools import setup


def long_description():
    with (Path(__file__).parent / 'README.md').open(encoding='utf-8') as f:
        return f.read()


setup(name='systemd-socketserver',
      version='1.0',
      description='Socket server implementation that works with systemd socket activation',

      long_description=long_description(),
      long_description_content_type='text/markdown',

      author='Adam Zegelin',
      author_email='adam@zegelin.com',

      url='https://github.com/zegelin/python-systemd-socketserver',

      py_modules=['systemd_socketserver'],

      classifiers=[
          'Programming Language :: Python :: 3',
          'Intended Audience :: Developers',
      ],
      python_requires='>=3',  # TODO: determine exact Python version required
      install_requires=['systemd-python']
      )
