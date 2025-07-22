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
import re
from setuptools import setup, find_packages

import ebcli


def parse_requirements(filename):
    """
    Parse a requirements file, returning a list of requirements.
    This replaces the deprecated pkg_resources.parse_requirements function.
    """
    requirements = []
    with open(filename) as f:
        for line in f:
            line = line.strip()
            # Skip empty lines, comments, and editable installs
            if not line or line.startswith('#'):
                continue
            # Handle requirement specs with markers
            if ';' in line:
                req, marker = line.split(';', 1)
                requirements.append(f"{req.strip()};{marker.strip()}")
            else:
                requirements.append(line)
    return requirements


# Parse requirements.txt
requires = parse_requirements("requirements.txt")

testing_requires = [
    'mock>=2.0.0',
    'pytest>=8.3.5',
    'pytest_socket>=0.5.1',
]

extras_require = {
    # use the same ranges as 'docker-py':
    # https://github.com/docker/docker-py/blob/e0495a91e49d19dc357513536c2882b7eaf28a05/setup.py#L29-L30
    ':sys_platform == "win32" and python_version < "3.6"': 'pypiwin32==219',
    ':sys_platform == "win32" and python_version >= "3.6"': 'pypiwin32==223',

}

setup_options = dict(
    name='awsebcli',
    version=ebcli.__version__,
    description='Command Line Interface for AWS EB.',
    long_description=open('README.rst').read() + open('CHANGES.rst').read(),
    data_files=[('', ['requirements.txt'])],
    author='AWS Elastic Beanstalk',
    author_email='aws-eb-cli@amazon.com',
    url='http://aws.amazon.com/elasticbeanstalk/',
    packages=find_packages('.', exclude=['tests*', 'docs*', 'sampleApps*', 'scripts*']),
    package_dir={'ebcli': 'ebcli'},
    package_data={
        'ebcli.lib': ['botocoredata/*/*/*.json'],
        'ebcli.containers': ['containerfiles/*'],
        'ebcli.labs': ['cloudwatchfiles/*.config'],
        'ebcli.controllers': ['migrate_scripts/*.ps1']},
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ),
    entry_points={
        'console_scripts': [
            'eb=ebcli.core.ebcore:main',
            'ebp=ebcli.core.ebpcore:main'
        ]
    },
)

setup(**setup_options)
