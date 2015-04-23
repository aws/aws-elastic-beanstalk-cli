import os
from mock import patch, Mock
from unittest import TestCase

from ebcli.docker import compat
from ebcli.objects.exceptions import CommandError


DOCKER_HOST_KEY = 'DOCKER_HOST'
DOCKER_HOST_VAL = 'tcp://192.168.59.105:2376'
DOCKER_TLS_VERIFY_KEY = 'DOCKER_TLS_VERIFY'
DOCKER_TLS_VERIFY_VAL = '1'
DOCKER_CERT_PATH_KEY = 'DOCKER_CERT_PATH'
DOCKER_CERT_PATH_VAL = '/a/b/c'
MOCK_MAC_CONTAINER_IP = '123.456.789'
EXPECTED_SHELLINIT = os.linesep.join(['    export {}={}'.format(DOCKER_TLS_VERIFY_KEY, DOCKER_TLS_VERIFY_VAL),
                                      '    export {}={}'.format(DOCKER_HOST_KEY, DOCKER_HOST_VAL),
                                      '    export {}={}'.format(DOCKER_CERT_PATH_KEY, DOCKER_CERT_PATH_VAL)])

EXPECTED_ENVIRON_VARS_SET = {DOCKER_HOST_KEY: DOCKER_HOST_VAL,
                             DOCKER_TLS_VERIFY_KEY: DOCKER_TLS_VERIFY_VAL,
                             DOCKER_CERT_PATH_KEY: DOCKER_CERT_PATH_VAL}


class TestCompat(TestCase):

    @patch('ebcli.docker.compat.commands.version')
    def test_supported_docker_installed_not_installed(self, version):
        version.side_effect = OSError
        self.assertFalse(compat.supported_docker_installed())

    @patch('ebcli.docker.compat.commands.version')
    def test_supported_docker_installed_lower_version(self,
                                                      version):
        version.side_effect = CommandError
        self.assertFalse(compat.supported_docker_installed())

    @patch('ebcli.docker.compat.commands.version')
    def test_supported_docker_installed_same_version(self,
                                                     version):
        version.return_value = compat.SUPPORTED_DOCKER_V
        self.assertTrue(compat.supported_docker_installed())

    @patch('ebcli.docker.compat.commands.version')
    def test_supported_docker_installed_higher_version(self,
                                                       version):
        version.return_value = '1.9.0'
        self.assertTrue(compat.supported_docker_installed())

    @patch('ebcli.docker.compat.utils.exec_cmd_quiet')
    def test_container_ip_boot2docker_works(self, exec_cmd_quiet):
        exec_cmd_quiet.return_value = MOCK_MAC_CONTAINER_IP
        self.assertEquals(MOCK_MAC_CONTAINER_IP, compat.container_ip())

    @patch('ebcli.docker.compat.utils.exec_cmd_quiet')
    def test_container_ip_boot2docker_oserror(self, exec_cmd_quiet):
        exec_cmd_quiet.side_effect = OSError
        self.assertEquals(compat.LOCALHOST, compat.container_ip())

    @patch('ebcli.docker.compat.utils')
    @patch('ebcli.docker.compat.heuristics.is_boot2docker_installed')
    def test_boot2docker_setup_not_installed(self, is_boot2docker_installed,
                                             utils):
        is_boot2docker_installed.return_value = False
        compat.boot2docker_setup({})
        self.assertFalse(utils.exec_cmd_quiet.called)

    @patch('ebcli.docker.compat.supported_docker_installed')
    def test_validate_docker_installed_not_installed(self, supported_docker_installed):
        supported_docker_installed.return_value = False
        self.assertRaises(CommandError, compat.validate_docker_installed)

    @patch('ebcli.docker.compat.supported_docker_installed')
    def test_validate_docker_installed_is_installed(self, supported_docker_installed):
        supported_docker_installed.return_value = True
        try:
            compat.validate_docker_installed()
        except CommandError:
            self.fail('Docker is installed')

    def test_validate_docker_installed_helper_not_installed(self):
        self.assertRaises(CommandError, compat._validate_docker_installed, False)

    def test_validate_docker_installed_helper_is_installed(self):
        try:
            compat._validate_docker_installed(True)
        except CommandError:
            self.fail('Docker is installed')

    @patch('ebcli.docker.compat.boot2docker_setup')
    @patch('ebcli.docker.compat.validate_docker_installed')
    def test_setup(self, validate_docker_installed, boot2docker_setup):
        compat.setup(os.environ)
        validate_docker_installed.assert_called_once_with()
        boot2docker_setup.assert_called_once_with(os.environ)
