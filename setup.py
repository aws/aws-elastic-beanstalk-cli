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

from pkg_resources import parse_requirements
from setuptools import setup, find_packages

import ebcli


with open("requirements.txt") as req:
    install_reqs = parse_requirements(req)
    requires = [str(ir) for ir in install_reqs]

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
    requires.append('docker-compose >= 1.25.2, <= 1.29.2')
    requires.append('blessed>=1.9.5')


setup_options = dict(
    name='awsebcli',
    version=ebcli.__version__,
    description='Command Line Interface for AWS EB.',
    long_description=open('README.rst').read() + open('CHANGES.rst').read(),
    scripts=['bin/eb'],
    data_files=[('', ['requirements.txt'])],
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
