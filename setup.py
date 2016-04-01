#!/usr/bin/env python
import sys

from setuptools import setup, find_packages

import ebcli

requires = ['pyyaml>=3.11',
            'botocore>=1.0.1',
            'cement==2.8.2',
            'colorama==0.3.7',
            'pathspec==0.3.4',
            'setuptools >= 20.0',
            ## For docker-compose
            'docopt >= 0.6.1, < 0.7',
            'requests >= 2.6.1, <= 2.9.1',
            'texttable >= 0.8.1, < 0.9',
            'websocket-client >= 0.11.0, < 1.0',
            'docker-py >= 1.1.0, <= 1.7.2',
            'dockerpty >= 0.3.2, <= 0.4.1',
            'semantic_version == 2.5.0'
           ]

if not sys.platform.startswith('win'):
    requires.append('blessed==1.9.5')

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
    author='AWS Elastic Beanstalk',
    author_email='aws-eb-cli@amazon.com',
    url='http://aws.amazon.com/elasticbeanstalk/',
    packages=find_packages('.', exclude=['tests*', 'docs*', 'sampleApps*']),
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
    ),
    entry_points={
        'console_scripts': [
            'eb=ebcli.core.ebcore:main'
        ]
    }
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


if 'py2exe' in sys.argv:
    data_files = setup_options['package_data']
    # This will actually give us a py2exe command.
    import py2exe
    import cement.ext
    import pkgutil
    import encodings
    # We need to manually include all cement.ext modules since py2exe doesnt
    # pull them in.
    _unpack_eggs(['jmespath', 'python-dateutil', 'pyyaml'])
    includes = []
    for importer, modname, ispkg in pkgutil.iter_modules(cement.ext.__path__):
        includes.append('cement.ext.' + modname)
    # And we have some py2exe specific options.
    setup_options['options'] = {
        'py2exe': {
            'includes': ['encodings'] + includes,
            'excludes': ['Tkinter', 'tcl'],
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
