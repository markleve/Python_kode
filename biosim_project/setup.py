# -*-coding: utf-8 -*-

"""
Setup file for biosim package.
"""

from distutils.core import setup
from Cython.Build import cythonize
import codecs
import os

__authors__ = 'Elisabeth Flatner and Marie Klever'
__emails__ = 'elisabeth.flatner@nmbu.no, marie.klever@nmbu.no'


def read_readme():
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
    return long_description

setup(
    # Basic information
    name='Biosim',
    version='0.1',

    # Packages to include
    packages=['biosim', 'biosim.tests'],

    # Required packages not included in Python standard library
    requires=['numpy (>=1.9.0)', 'matplotlib (>= 1.4.0)', 'nose (>=1.3.4)',
              'cython (>=0.21)'],

    # Metadata
    description='Model of the Ecosystem on Rossumisland',
    long_description=read_readme(),
    author='Elisabeth Flatner and Marie Klever',
    author_email='elisabeth.flatner@nmbu.no, marie.klever@nmbu.no',
    license='MIT Licence',

    ext_modules=cythonize("biosim/fitness_workers.pyx")
)
