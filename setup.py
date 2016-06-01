#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup


setup(
    name='grovepi-python3',
    description='More pythonized version of GrovePis python module rewritten for python3',
    version='0.1.0',
    url='https://github.com/elnappo/GrovePi-python3',
    license='MIT',
    author='elnappo',
    author_email='elnappo@nerdpol.io',
    keywords='grovepi i2c',
    platforms='any',
    py_modules=['grovepi'],
    scripts=['grovepi-cli.py'],
    install_requires=['RPi.GPIO'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],
)
