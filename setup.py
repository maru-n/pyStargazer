#!/usr/bin/env python
# coding: utf-8


from setuptools import setup

setup(
        name             = 'pystargazer',
        version          = "0.0.2",
        description      = 'python class to use StarGazer by Hagisonic.',
        author           = "marun",
        url              = 'https://github.com/maru-n/pyStargazer.git',
        packages         = ['pystargazer'],
        install_requires = ['pyserial', 'numpy'],
        requires         = [],
        test_suite       = 'tests'
        )
