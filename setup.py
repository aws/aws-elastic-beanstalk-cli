#!/usr/bin/env python
import sys

from setuptools import setup, find_packages

import ebcli

requires = ['setuptools>=7.0',
            'pyyaml>=3.11',
            'six==1.8.0',
            'cement==2.4',
            ## For botocore we need the following
            'python-dateutil>=2.2',
            'jmespath>=0.4.1'
            ]

try:
    with open('/etc/bash_completion.d/eb_completion.extra', 'w') as eo:
        eo.write('')
        data_files = [
            ('/etc/bash_completion.d/', ['bin/eb_completion.bash'])
        ]
except:
    # print('User does not have write access to /etc. Completion will not work.')
    data_files = []

setup_options = dict(
    name='awsebcli',
    version=ebcli.__version__,
    description='Command Line Interface for AWS EB.',
    long_description=open('README.rst').read() + open('CHANGES.rst').read(),
    scripts=['bin/eb_completion.bash'],
    data_files=data_files,
    author='Nick Humrich',
    author_email='humrichn@amazon.com',
    url='http://aws.amazon.com/elasticbeanstalk/',
    packages=find_packages('.', exclude=['tests*', 'docs*', 'sampleApps*']),
    package_dir={'ebcli': 'ebcli',
                 'botocore_eb': 'botocore_eb'},
    package_data={
        'botocore_eb': ['data/aws/*.json', 'data/aws/*/*.json'],
        'botocore_eb.vendored.requests': ['*.pem']},
    install_requires=requires,
    license="Apache License 2.0",
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ),
    entry_points={
        'console_scripts': [
            'eb=ebcli.core.ebcore:main'
        ]
    }
)

if 'py2exe' in sys.argv:
    # This will actually give us a py2exe command.
    import py2exe
    # And we have some py2exe specific options.
    setup_options['options'] = {
        'py2exe': {
            'optimize': 0,
            'skip_archive': True,
            'packages': ['ebcli', 'botocore_eb'],
        }
    }
    setup_options['console'] = ['bin\eb']

setup(**setup_options)