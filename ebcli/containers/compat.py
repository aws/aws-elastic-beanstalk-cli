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
import os
import re
import sys
from semantic_version import Version

from cement.utils.misc import minimal_logger

from ebcli.containers import commands
from ebcli.core import fileoperations
from ebcli.lib import heuristics, utils
from ebcli.resources.strings import strings
from ebcli.objects.exceptions import CommandError


LOG = minimal_logger(__name__)
SUPPORTED_DOCKER_V = '1.6.0'
SUPPORTED_BOOT2DOCKER_V = '1.6.0'
LOCALHOST = '127.0.0.1'
EXPORT = 'export'
BOOT2DOCKER_RUNNING = 'running'
DOCKER_HOST = 'DOCKER_HOST'
DOCKER_CERT_PATH = 'DOCKER_CERT_PATH'
DOCKER_TLS_VERIFY = 'DOCKER_TLS_VERIFY'


def supported_docker_installed():
    """
    Return whether proper Docker version is installed.
    :return: bool
    """

    try:
        clean_version = remove_leading_zeros_from_version(commands.version())
        return Version(clean_version) >= Version(SUPPORTED_DOCKER_V)
    except (OSError, CommandError):
        return False


def validate_docker_installed():
    _validate_docker_installed(supported_docker_installed())


def _validate_docker_installed(supported_docker_installed):
    versions = {'boot2docker-version': SUPPORTED_BOOT2DOCKER_V,
                'docker-version': SUPPORTED_DOCKER_V}
    err = strings['local.dockernotpresent'].format(**versions)

    if not supported_docker_installed:
        raise CommandError(err)


def container_ip():
    """
    Return the ip address that local containers are or will be running on.
    :return str
    """
    try:
        return _boot2docker_ip()
    except OSError:
        return LOCALHOST


def _boot2docker_ip():
    args = ['boot2docker', 'ip']
    return utils.exec_cmd_quiet(args).strip()


def setup(env=os.environ):
    validate_docker_installed()
    boot2docker_setup(env)


def boot2docker_setup(env=os.environ):
    if not heuristics.is_boot2docker_installed():
        return
    LOG.debug('Ensuring boot2docker VM has initialized, started and the client is set up...')

    _init_boot2docker()
    if not _is_boot2docker_running():
        _start_boot2docker()

    boot2docker_certs_path = os.path.sep.join(['.boot2docker', 'certs',
                                               'boot2docker-vm'])

    if DOCKER_HOST not in env:
        env[DOCKER_HOST] = 'tcp://{}:2376'.format(_boot2docker_ip())

    if DOCKER_CERT_PATH not in env:
        env[DOCKER_CERT_PATH] = os.path.join(fileoperations.get_home(),
                                             boot2docker_certs_path)
    if DOCKER_TLS_VERIFY not in env:
        env[DOCKER_TLS_VERIFY] = '1'

    LOG.debug('DOCKER_HOST is set to ' + env[DOCKER_HOST])
    LOG.debug('DOCKER_CERT_PATH is set to ' + env[DOCKER_CERT_PATH])
    LOG.debug('DOCKER_TLS_VERIFY is set to ' + env[DOCKER_TLS_VERIFY])
    LOG.debug('PATH is set to ' + env.get('PATH', ''))


def is_windows():
    return 'win32' in str(sys.platform).lower()


def _is_boot2docker_running():
    return _get_boot2docker_status() == BOOT2DOCKER_RUNNING


def _get_boot2docker_status():
    return utils.exec_cmd_quiet(['boot2docker', 'status']).strip()


def _start_boot2docker():
    utils.exec_cmd_quiet(['boot2docker', 'start'])


def _init_boot2docker():
    utils.exec_cmd_quiet(['boot2docker', 'init'])


def remove_leading_zeros_from_version(version_string):
    # regex explaination: remove zeroes if both:
    # 1. the start of string (major version) or following a '.'
    # 2. followed by some other digit
    return re.sub(r'((?<=\.)|^)[0]+(?=\d+)', r'', version_string)
