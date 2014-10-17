#!/usr/bin/env python
import sys

from setuptools import setup, find_packages
import ebcli

requires = ['cement==2.4',
            'six',
            'pyyaml',
            ## For botocore we need the following
            'python-dateutil',
            'jmespath'
            ]

try:
    with open('/etc/bash_completion.d/eb_completion.extra', 'w') as eo:
        eo.write('')
        data_files = [
            ('/etc/bash_completion.d/', ['bin/eb_completion.bash'])
        ]
except:
    print('User does not have write access to /etc. Completion will not work')
    data_files = []

setup_options = dict(
    name='aws-eb-cli',
    version=ebcli.__version__,
    description='Command Line Interface for AWS EB.',
    long_description=open('README.md').read(),
    scripts=['bin/eb_completion.bash'],
    data_files=data_files,
    author='Nick Humrich',
    author_email='humrichn@amazon.com',
    url='eb.example.com',
    packages=find_packages('.', exclude=['tests*', 'docs*', 'sampleApps*']),
    package_dir={'ebcli': 'ebcli',
                 'botocore_eb': 'botocore_eb'},
    package_data={
        'botocore_eb': ['data/*.json', 'data/aws/*.json', 'data/aws/*/*.json'],
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
        'Programming Language :: Python :: 2.6',
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

setup(**setup_options)

