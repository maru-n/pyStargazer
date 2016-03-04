#!/usr/bin/env python
# coding: utf-8


from setuptools import setup
from pystargazer import __author__, __version__

setup(
        name             = 'pystargazer',
        version          = __version__,
        description      = 'python class to use StarGazer by Hagisonic.',
        author           = __author__,
        url              = 'https://github.com/maru-n/pyStargazer.git',
        packages         = ['pystargazer'],
        install_requires = [],
        requires         =  ['pyserial', 'numpy'],
        )
