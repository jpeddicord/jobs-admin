#!/usr/bin/python

from distutils.core import setup
from subprocess import Popen, PIPE


setup_info = dict(
    name='jobs-admin',
    version='0.1~bzr',
    description='jobs-admin',
    author='Jacob Peddicord',
    author_email='jpeddicord@ubuntu.com',
    url='https://launchpad.net/jobsadmin',
    packages=['JobsAdmin', 'JobsAdmin.extras'],
    scripts=['jobs-admin'],
    data_files=[
        ('share/applications', ['jobs-admin.desktop']),
        ('share/jobs-admin', ['jobs-admin.ui']),
    ]
)

# get the bzr revision if applicable
if 'bzr' in setup_info['version']:
    try:
        setup_info['version'] += Popen(['bzr', 'revno'],stdout=PIPE).communicate()[0].strip()
    except: pass

setup(**setup_info)

