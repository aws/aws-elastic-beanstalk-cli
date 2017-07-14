import os
from mock import patch, Mock
from unittest import TestCase

from ebcli.containers import compat
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
    @patch('ebcli.containers.compat.commands.version')
    def test_supported_docker_installed_not_installed(self, version):
        version.side_effect = OSError
        self.assertFalse(compat.supported_docker_installed())

    @patch('ebcli.containers.compat.commands.version')
    def test_supported_docker_installed_lower_version(self,
                                                      version):
        version.side_effect = CommandError
        self.assertFalse(compat.supported_docker_installed())

    @patch('ebcli.containers.compat.commands.version')
    def test_supported_docker_installed_same_version(self,
                                                     version):
        version.return_value = compat.SUPPORTED_DOCKER_V
        self.assertTrue(compat.supported_docker_installed())

    @patch('ebcli.containers.compat.commands.version')
    def test_supported_docker_installed_higher_version(self,
                                                       version):
        version.return_value = '1.9.0'
        self.assertTrue(compat.supported_docker_installed())

    @patch('ebcli.containers.compat.commands.version')
    def test_supported_docker_installed_v1_10(self,
                                                       version):
        version.return_value = '1.10.0'
        self.assertTrue(compat.supported_docker_installed())

    @patch('ebcli.containers.compat.commands.version')
    def test_supported_docker_installed_v10_0(self,
                                                       version):
        version.return_value = '10.0.0'
        self.assertTrue(compat.supported_docker_installed())

    @patch('ebcli.containers.compat.utils.exec_cmd_quiet')
    def test_container_ip_boot2docker_works(self, exec_cmd_quiet):
        exec_cmd_quiet.return_value = MOCK_MAC_CONTAINER_IP
        self.assertEquals(MOCK_MAC_CONTAINER_IP, compat.container_ip())

    @patch('ebcli.containers.compat.utils.exec_cmd_quiet')
    def test_container_ip_boot2docker_oserror(self, exec_cmd_quiet):
        exec_cmd_quiet.side_effect = OSError
        self.assertEquals(compat.LOCALHOST, compat.container_ip())

    @patch('ebcli.containers.compat.utils')
    @patch('ebcli.containers.compat.heuristics.is_boot2docker_installed')
    def test_boot2docker_setup_not_installed(self, is_boot2docker_installed,
                                             utils):
        is_boot2docker_installed.return_value = False
        compat.boot2docker_setup({})
        self.assertFalse(utils.exec_cmd_quiet.called)

    @patch('ebcli.containers.compat.fileoperations')
    @patch('ebcli.containers.compat._boot2docker_ip')
    @patch('ebcli.containers.compat.utils')
    @patch('ebcli.containers.compat.heuristics.is_boot2docker_installed')
    def test_boot2docker_setup_envvars_not_set(self, is_boot2docker_installed,
                                               utils, _boot2docker_ip,
                                               fileoperations):
        env = {}
        expected_env = {'DOCKER_HOST': 'tcp://192.168.59.103:2376',
                        'DOCKER_CERT_PATH': os.path.join('home','.boot2docker','certs', 'boot2docker-vm'),
                        'DOCKER_TLS_VERIFY': '1'}

        is_boot2docker_installed.return_value = True
        _boot2docker_ip.return_value = '192.168.59.103'
        fileoperations.get_home.return_value = os.path.join('home')

        compat.boot2docker_setup(env)

        self.assertDictEqual(expected_env, env)

    @patch('ebcli.containers.compat.utils')
    @patch('ebcli.containers.compat.heuristics.is_boot2docker_installed')
    def test_boot2docker_setup_envvars_is_set(self, is_boot2docker_installed,
                                              utils):
        env = {'DOCKER_HOST': 'tcp://192.168.59.103:9000',
               'DOCKER_CERT_PATH': '/new-path/certs',
               'DOCKER_TLS_VERIFY': '1'}
        expected_env = env.copy()
        is_boot2docker_installed.return_value = True

        compat.boot2docker_setup(env)

        self.assertDictEqual(expected_env, env)

    @patch('ebcli.containers.compat.utils')
    @patch('ebcli.containers.compat.heuristics.is_boot2docker_installed')
    def test_boot2docker_init_and_start(self, is_boot2docker_installed, utils):
        is_boot2docker_installed.return_value = True

        # init=None, status='poweroff', start=None, ip=192.168.59.103
        utils.exec_cmd_quiet.side_effect = [None, 'poweroff',
                                            None, '192.168.59.103']

        compat.boot2docker_setup({})

        utils.exec_cmd_quiet.assert_any_call(['boot2docker', 'init'])
        utils.exec_cmd_quiet.assert_any_call(['boot2docker', 'start'])

    @patch('ebcli.containers.compat.supported_docker_installed')
    def test_validate_docker_installed_not_installed(self, supported_docker_installed):
        supported_docker_installed.return_value = False
        self.assertRaises(CommandError, compat.validate_docker_installed)

    @patch('ebcli.containers.compat.supported_docker_installed')
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

    @patch('ebcli.containers.compat.boot2docker_setup')
    @patch('ebcli.containers.compat.validate_docker_installed')
    def test_setup(self, validate_docker_installed, boot2docker_setup):
        compat.setup(os.environ)
        validate_docker_installed.assert_called_once_with()
        boot2docker_setup.assert_called_once_with(os.environ)

    def test_remove_leading_zeros_from_version(self):
        versions_tests = []
        # tuples of (input, expected_result)
        versions_tests.append(('0001.000.000', '1.0.0'))
        versions_tests.append(('1.0001.0000-rc.1', '1.1.0-rc.1'))
        versions_tests.append(('1.3.0', '1.3.0'))
        versions_tests.append(('17.03.0-ce', '17.3.0-ce'))
        versions_tests.append(('107.3.30-ce', '107.3.30-ce'))
        versions_tests.append(('017.030.07-ce', '17.30.7-ce'))
        versions_tests.append(('17.03.08-ce', '17.3.8-ce'))
        for test in versions_tests:
            self.assertEqual(compat.remove_leading_zeros_from_version(test[0]), test[1])