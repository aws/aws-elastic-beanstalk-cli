#!/usr/bin/env python
import sys

from setuptools import setup, find_packages

import ebcli


requires = [
    'botocore>=1.12.1,<1.13',
    'cement==2.8.2',
    'colorama>=0.3.9,<0.4.0',  # use the same range that 'docker-compose' uses
    'pathspec==0.5.5',
    'python-dateutil>=2.1,<3.0.0',  # use the same range that 'botocore' uses
    'PyYAML>=3.10,<=3.13',  # use the same range that 'aws-cli' uses. This is also compatible with 'docker-compose'
    'setuptools >= 20.0',
    'semantic_version == 2.5.0',
    'six == 1.11.0',
    'termcolor == 1.1.0',
    'urllib3>=1.21.1,<1.23'
]

testing_requires = [
    'mock>=2.0.0',
    'pytest>=3.03',
    'pytest_socket',
]

if not sys.platform.startswith('win'):
    requires.append('docker-compose >= 1.21.2, < 1.22.0')
    requires.append('blessed>=1.9.5')

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
    scripts=['bin/eb', 'bin/eb_completion.bash'],
    data_files=data_files,
    author='AWS Elastic Beanstalk',
    author_email='aws-eb-cli@amazon.com',
    url='http://aws.amazon.com/elasticbeanstalk/',
    packages=find_packages('.', exclude=['tests*', 'docs*', 'sampleApps*', 'scripts*']),
    package_dir={'ebcli': 'ebcli'},
    package_data={
        'ebcli.lib': ['botocoredata/*/*/*.json'],
        'ebcli.containers': ['containerfiles/*'],
        'ebcli.labs': ['cloudwatchfiles/*.config']},
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
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ),
    entry_points={
        'console_scripts': [
            'eb=ebcli.core.ebcore:main',
            'ebp=ebcli.core.ebpcore:main'
        ]
    },
)


def _unpack_eggs(egg_list):
    import os
    for pkg in egg_list:
        import pkg_resources
        eggs = pkg_resources.require(pkg)
        from setuptools.archive_util import unpack_archive
        for egg in eggs:
            if os.path.isdir(egg.location):
                sys.path.insert(0, egg.location)
                continue
            unpack_archive(egg.location, os.path.abspath(os.path.dirname(egg.location)))


setup(**setup_options)
