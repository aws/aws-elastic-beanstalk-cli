import os
import subprocess
import sys

from cement.utils.misc import minimal_logger

from . import commands
from ..core import io, fileoperations
from ..lib import heuristics, utils
from ..resources.strings import strings
from ..objects.exceptions import CommandError


LOG = minimal_logger(__name__)
SUPPORTED_DOCKER_V = '1.6.0'
SUPPORTED_BOOT2DOCKER_V = '1.6.0'
LOCALHOST = '127.0.0.1'
EXPORT = 'export'
BOOT2DOCKER_RUNNING = 'running'


def supported_docker_installed():
    """
    Return whether proper Docker version is installed.
    :return: bool
    """

    try:
        return commands.version() >= SUPPORTED_DOCKER_V
    # OSError = Not installed
    # CommandError = docker versions less than 1.5 give exit code 1
    # with 'docker --version'.
    except (OSError, CommandError):
        return False


def validate_docker_installed():
    _validate_docker_installed(supported_docker_installed())

def _validate_docker_installed(supported_docker_installed):
    err = strings['local.dockernotpresent'].format(SUPPORTED_DOCKER_V,
                                                   SUPPORTED_BOOT2DOCKER_V)

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

    # The rest of this function is really hacky and I need to fix it soon,
    # but I'm not sure how to fix it yet. boot2docker hasn't a good api to use.
    boot2docker_certs_path = os.path.sep.join(['.boot2docker', 'certs',
                                              'boot2docker-vm'])

    env['DOCKER_HOST'] = 'tcp://{}:2376'.format(_boot2docker_ip())
    env['DOCKER_CERT_PATH'] = os.path.join(fileoperations.get_home(),
                                           boot2docker_certs_path)
    env['DOCKER_TLS_VERIFY'] = '1'

    # This is a Docker/boot2docker 1.6 thing for Windows. They need ssh.exe to
    # to be in $PATH so we include the bin folder of Git which has ssh.exe
    if is_windows():
        git_bin_path = "c:\Program Files (x86)\Git\bin"
        path = env.get('PATH', '')

        if git_bin_path not in path:
            env['PATH'] = env.get('PATH', '') + ';' + git_bin_path


    LOG.debug('DOCKER_HOST is set to ' + env['DOCKER_HOST'])
    LOG.debug('DOCKER_CERT_PATH is set to ' + env['DOCKER_CERT_PATH'])
    LOG.debug('DOCKER_TLS_VERIFY is set to ' + env['DOCKER_TLS_VERIFY'])
    LOG.debug('PATH is set to' + env['PATH'])


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
