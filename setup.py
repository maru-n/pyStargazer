#!/usr/bin/env python
# coding: utf-8


from setuptools import setup, find_packages
from pystargazer import __author__, __version__

setup(
        name             = 'pyStargazer',
        version          = __version__,
        description      = 'python tools for StarGazer',
        author           = __author__,
        url              = 'https://github.com/maru-n/pyStargazer.git',
        packages         = find_packages(),
        install_requires = [],
        )
