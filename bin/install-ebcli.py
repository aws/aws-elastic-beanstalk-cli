#!/usr/bin/env python
# Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
import os
from subprocess import Popen, PIPE
import argparse

"""
Note: Will not work with homebrew versions of python.
"""


def run_cmd(cmd):
    sys.stdout.write("Running cmd: %s\n" % cmd)
    # p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    # stdout, stderr = p.communicate()
    # stdout = stdout.decode()
    # stderr = stderr.decode()
    rc = os.system(cmd)
    if rc != 0:
        raise Exception("Command returned non-zero status: "
                        "status={0}".format(rc))


def check_preconditions():
    # Must have python 2.7 or later
    if sys.version_info[:1] <= 2 and sys.version_info[:2][1] < 7:
        sys.stderr.write("Must run with python 2.7 or greater, not: {0}"
                         .format(sys.version))
        sys.exit(1)


def get_arguments():
    parser = argparse.ArgumentParser(description='Installs the AWS EB CLI in a virtualenv.')
    parser.add_argument('--version', action='store', help='explicit version to install')
    return parser.parse_args()


def install_pip():
    # Make sure pip/setuptools/virtualenv are up-to-date
    run_cmd('curl -o - -k https://s3.amazonaws.com/elasticbeanstalk-cli-resources/get-pip.py | python - --user')
    run_cmd('{python} -m pip install -U virtualenv --user'.format(python=sys.executable))
    run_cmd('{python} -m virtualenv ~/.ebvenv'.format(python=sys.executable))


def do_install(version=None):
    try:
        if version:
            version = '==' + str(version)
        else:
            version = ''
        # run_cmd('bash -c source ~/.ebvenv/bin/activate')
        run_cmd('~/.ebvenv/bin/pip install -U awsebcli{0}'.format(version))
        # run_cmd('deactivate')

        # Check install
        run_cmd('~/.ebvenv/bin/eb --version')
        sys.stdout.write('EB CLI Successfully installed\n')
    except Exception as e:
        sys.stderr.write('Error: Something went wrong during installation.\n')
        raise


def setup_path():
    # Set up link to shell script
    sys.stdout.write('==> setting up link..\n')
    try:
        if (not os.path.isdir('/usr/local')) or \
                    (not os.access('/usr/local', os.W_OK)):
            sys.stdout.write('Need temporary sudo permissions. If you dont have sudo permissions type Ctrl-C.')
            run_cmd("sudo mkdir -p /usr/local")
            run_cmd("sudo chmod a+w /usr/local")  # Fix permissions
        if not os.path.isdir('/usr/local/bin'):
            run_cmd('mkdir -p /usr/local/bin')
        run_cmd('ln -s ~/.ebvenv/bin/eb /usr/local/bin/eb')
    except Exception as e:
        sys.stdout.write('Error setting up link to /usr/local/bin. Add "alias eb=~/.ebvenv/bin/eb" to your profile.\n'
                         'Error: {e}\n'.format(e=e))


def install_ebcli(version):
    if not os.path.isdir('~/.ebvenv'):
        install_pip()
        do_install(version=version)
        setup_path()
    else:
        do_install(version=version)


def main():
    try:
        check_preconditions()
        get_arguments()
        args = get_arguments()
        install_ebcli(args.version)
    except Exception as e:
        sys.stderr.write('{e}\n'.format(e=e))


if __name__ == '__main__':
    main()