#coding=utf-8

from setuptools import setup, find_packages

setup(
    name='prepy',
    version='0.1',
    packages=find_packages(exclude=['tests*']),
    license='SPDX-License-Identifier: Apache-2.0 OR CC0-1.0',
    description='Helper functions to work with CSV and SQLite',
    long_description=open('README.md').read(),
    install_requires=[],
    url='https://github.com/infobaleen/prepy',
    author='Robert Åkerblom Andersson',
    author_email='robert@infobaleen.com'
)

