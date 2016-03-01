# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='smt',
    version='0.0.1',
    description='Example package for Python',
    long_description=readme,
    author='Andrea Danzi',
    author_email='andrea@danzi.tn.it',
    url='https://github.com/andreadanzi/[NOME MODULO]',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

