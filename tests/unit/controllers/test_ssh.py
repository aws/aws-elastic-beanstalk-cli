# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

import shutil

import unittest
import pytest_socket
import mock

from ebcli.controllers import ssh
from ebcli.core import fileoperations
from ebcli.core.ebcore import EB


class TestInit(unittest.TestCase):
    def setUp(self):
        pytest_socket.disable_socket()
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')

        os.chdir('testDir')

        fileoperations.create_config_file('my-application', 'us-west-2', 'php')

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

        pytest_socket.enable_socket()

    @mock.patch('ebcli.controllers.ssh.SSHController.get_env_name')
    @mock.patch('ebcli.controllers.ssh.sshops.prepare_for_ssh')
    def test_ssh(
            self,
            prepare_for_ssh_mock,
            get_env_name_mock
    ):
        get_env_name_mock.return_value = 'my-environment'

        app = EB(argv=['ssh'])
        app.setup()
        app.run()

        prepare_for_ssh_mock.assert_called_with(
            command=None,
            custom_ssh=None,
            env_name='my-environment',
            force=False,
            instance=None,
            keep_open=False,
            number=None,
            setup=False,
            timeout=None
        )

    @mock.patch('ebcli.controllers.ssh.SSHController.get_env_name')
    @mock.patch('ebcli.controllers.ssh.sshops.prepare_for_ssh')
    def test_ssh__setup__with_timeout(
            self,
            prepare_for_ssh_mock,
            get_env_name_mock
    ):
        get_env_name_mock.return_value = 'my-environment'

        app = EB(argv=['ssh', '--setup', '--timeout', '10'])
        app.setup()
        app.run()

        prepare_for_ssh_mock.assert_called_with(
            command=None,
            custom_ssh=None,
            env_name='my-environment',
            force=False,
            instance=None,
            keep_open=False,
            number=None,
            setup=True,
            timeout=10
        )

    @mock.patch('ebcli.controllers.ssh.SSHController.get_env_name')
    @mock.patch('ebcli.controllers.ssh.sshops.prepare_for_ssh')
    def test_ssh__setup__without_timeout(
            self,
            prepare_for_ssh_mock,
            get_env_name_mock
    ):
        get_env_name_mock.return_value = 'my-environment'

        app = EB(argv=['ssh', '--setup'])
        app.setup()
        app.run()

        prepare_for_ssh_mock.assert_called_with(
            command=None,
            custom_ssh=None,
            env_name='my-environment',
            force=False,
            instance=None,
            keep_open=False,
            number=None,
            setup=True,
            timeout=None
        )

    @mock.patch('ebcli.controllers.ssh.SSHController.get_env_name')
    @mock.patch('ebcli.controllers.ssh.sshops.prepare_for_ssh')
    def test_ssh__timeout_without_setup(
            self,
            prepare_for_ssh_mock,
            get_env_name_mock
    ):
        get_env_name_mock.return_value = 'my-environment'

        app = EB(argv=['ssh', '--timeout', '10'])
        app.setup()

        with self.assertRaises(ssh.InvalidOptionsError) as context_manager:
            app.run()

        self.assertEqual(
            'You can only use the "--timeout" argument with the "--setup" argument',
            str(context_manager.exception)
        )
        prepare_for_ssh_mock.assert_not_called()
