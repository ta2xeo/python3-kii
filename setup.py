#!/usr/bin/env python

import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


requires = [
    'requests',
]


setup(name='python3-kii',
      version='0.2.3',
      description='A Python Library for Kii Cloud REST API',
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
      ],
      author='Tatsuji Tsuchiya',
      author_email='ta2xeo@gmail.com',
      packages=find_packages(),
      url='',
      keywords='web kii baas api',
      license='MIT',
      install_requires=requires,
      tests_require=requires + ['pytest'],
      test_suite='tests',
      cmdclass={'test': PyTest})
