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

import mock
import pytest_socket
import unittest

from ebcli.core.ebcore import EB
from ebcli.core import fileoperations


class TestUpgrade(unittest.TestCase):
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

    @mock.patch('ebcli.controllers.upgrade.upgradeops.upgrade_env')
    @mock.patch('ebcli.controllers.upgrade.UpgradeController.get_env_name')
    def test_upgrade(
            self,
            get_env_name_mock,
            upgrade_env_mock
    ):
        get_env_name_mock.return_value = 'my-environment'

        self.app = EB(argv=['upgrade'])
        self.app.setup()
        self.app.run()

        upgrade_env_mock.assert_called_once_with(
            'my-application',
            'my-environment',
            None,
            False,
            False
        )

    @mock.patch('ebcli.controllers.upgrade.upgradeops.upgrade_env')
    @mock.patch('ebcli.controllers.upgrade.UpgradeController.get_env_name')
    def test_upgrade__specify_timeout(
            self,
            get_env_name_mock,
            upgrade_env_mock
    ):
        get_env_name_mock.return_value = 'my-environment'

        self.app = EB(argv=['upgrade', '--timeout', '10'])
        self.app.setup()
        self.app.run()

        upgrade_env_mock.assert_called_once_with(
            'my-application',
            'my-environment',
            10,
            False,
            False
        )

    @mock.patch('ebcli.controllers.upgrade.upgradeops.upgrade_env')
    @mock.patch('ebcli.controllers.upgrade.UpgradeController.get_env_name')
    def test_upgrade__force_upgrade(
            self,
            get_env_name_mock,
            upgrade_env_mock
    ):
        get_env_name_mock.return_value = 'my-environment'

        self.app = EB(argv=['upgrade', '--force'])
        self.app.setup()
        self.app.run()

        upgrade_env_mock.assert_called_once_with(
            'my-application',
            'my-environment',
            None,
            True,
            False
        )

    @mock.patch('ebcli.controllers.upgrade.upgradeops.upgrade_env')
    @mock.patch('ebcli.controllers.upgrade.UpgradeController.get_env_name')
    def test_upgrade__disable_rolling_upgrade(
            self,
            get_env_name_mock,
            upgrade_env_mock
    ):
        get_env_name_mock.return_value = 'my-environment'

        self.app = EB(argv=['upgrade', '--noroll'])
        self.app.setup()
        self.app.run()

        upgrade_env_mock.assert_called_once_with(
            'my-application',
            'my-environment',
            None,
            False,
            True
        )
