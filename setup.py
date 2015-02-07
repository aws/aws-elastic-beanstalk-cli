#!/usr/bin/env python
import sys

from setuptools import setup, find_packages

import ebcli

requires = ['pyyaml>=3.11',
            'cement==2.4',
            ## For botocore we need the following
            'python-dateutil>=2.1,<3.0.0',
            'jmespath>=0.5.0'
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
    package_dir={'ebcli': 'ebcli'},
    package_data={
        'ebcli': ['bundled/botocore/data/aws/*.json',
                  'bundled/botocore/data/aws/*/*.json'],
        'ebcli.bundled.botocore.vendored.requests': ['*.pem']},
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
    data_files = setup_options['package_data']
    # This will actually give us a py2exe command.
    import py2exe
    import cement.ext
    import pkgutil
    import encodings
    # We need to manually include all cement.ext modules since py2exe doesnt
    # pull them in.
    includes = []
    for importer, modname, ispkg in pkgutil.iter_modules(cement.ext.__path__):
        includes.append('cement.ext.' + modname)
    # And we have some py2exe specific options.
    setup_options['options'] = {
        'py2exe': {
            'includes': ['encodings'] + includes,
            'optimize': 0,
            'skip_archive': True,
            'packages': ['ebcli'],
            }
    }
    setup_options['console'] = ['bin/eb']

setup(**setup_options)

if 'py2exe' in sys.argv:
    # After py2exe is done we need to import all the data files botocore
    # relies on
    import shutil
    import os
    from subprocess import Popen, PIPE

    def run(cmd):
        sys.stdout.write("Running cmd: %s\n" % cmd)
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, env=os.environ)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise Exception("Bad rc (%d): %s" % (p.returncode, stdout + stderr))
        return stdout + stderr

    def copy_data_directories():
        # We need to move the .json files in awscli and botocore
        # into the dist/ dir.
        python = sys.executable
        boto_data = run("""%s -c "from ebcli.bundled import botocore; import os; print(os.path.join(os.path.dirname(botocore.__file__), 'data'))" """ % python).strip()
        print(boto_data)
        shutil.copytree(boto_data, os.path.join('dist', 'ebcli', 'bundled', 'botocore', 'data'))

    def copy_ca_cert():
        # We need the cacert.pem from the requests library so we have
        # to copy that in dist.
        python = sys.executable
        ca_cert = run("""%s -c "from ebcli.bundled.botocore.vendored import requests; import os; print(os.path.join(os.path.dirname(requests.__file__), 'cacert.pem'))" """ % python).strip()
        shutil.copy(ca_cert, os.path.join('dist', 'ebcli', 'bundled', 'botocore', 'vendored', 'requests', 'cacert.pem'))

    copy_data_directories()
    copy_ca_cert()