#!/usr/bin/env python
# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import sys

from setuptools import setup, find_packages

import ebcli


requires = [
    'botocore>=1.12.29,<1.13',
    'cement==2.8.2',
    'colorama>=0.3.9,<0.4.0',  # use the same range that 'docker-compose' uses
    'future>=0.16.0,<0.17.0',
    'pathspec==0.5.9',
    'python-dateutil>=2.1,<3.0.0',  # use the same range that 'botocore' uses
    'PyYAML>=3.10,<=3.13',  # use the same range that 'aws-cli' uses. This is also compatible with 'docker-compose'
    'requests>=2.20.1,<2.21',
    'setuptools >= 20.0',
    'semantic_version == 2.5.0',
    'six>=1.11.0,<1.12.0',
    'termcolor == 1.1.0',
    'urllib3>=1.24.1,<1.25',
    'wcwidth>=0.1.7,<0.2.0',
]

testing_requires = [
    'mock>=2.0.0',
    'pytest>=3.03',
    'pytest_socket',
]

extras_require = {
    # use the same ranges as 'docker-py':
    # https://github.com/docker/docker-py/blob/e0495a91e49d19dc357513536c2882b7eaf28a05/setup.py#L29-L30
    ':sys_platform == "win32" and python_version < "3.6"': 'pypiwin32==219',
    ':sys_platform == "win32" and python_version >= "3.6"': 'pypiwin32==223',

}
if not sys.platform.startswith('win'):
    requires.append('docker-compose >= 1.23.2, < 1.24.0')
    requires.append('blessed>=1.9.5')


setup_options = dict(
    name='awsebcli',
    version=ebcli.__version__,
    description='Command Line Interface for AWS EB.',
    long_description=open('README.rst').read() + open('CHANGES.rst').read(),
    scripts=['bin/eb'],
    data_files=[],
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
    extras_require=extras_require,
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
