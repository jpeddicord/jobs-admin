#!/usr/bin/python

from distutils.core import setup

setup_info = dict(
    name='jobs-admin',
    version='0.1',
    description='jobs-admin',
    author='Jacob Peddicord',
    author_email='jpeddicord@ubuntu.com',
    url='https://launchpad.net/jobs-admin',
    packages=['JobsAdmin'],
    scripts=['jobs-admin'],
)

setup(**setup_info)

