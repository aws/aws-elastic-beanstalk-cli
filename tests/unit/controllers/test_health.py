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
from pytest_socket import disable_socket, enable_socket
import unittest

from ebcli.core.ebcore import EB


class TestHealth(unittest.TestCase):
    def setUp(self):
        disable_socket()
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')

        os.chdir('testDir')

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

        enable_socket()

    @mock.patch('ebcli.controllers.health.HealthController.get_app_name')
    @mock.patch('ebcli.controllers.health.HealthController.get_env_name')
    @mock.patch('ebcli.controllers.health.healthops.display_interactive_health')
    def test_health(
            self,
            display_interactive_health_mock,
            get_env_name_mock,
            get_app_name_mock
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(argv=['health'])
        app.setup()
        app.run()

        display_interactive_health_mock.assert_called_once_with(
            'my-application',
            'environment-1',
            False,
            False,
            'split'
        )

    @mock.patch('ebcli.controllers.health.HealthController.get_app_name')
    @mock.patch('ebcli.controllers.health.HealthController.get_env_name')
    @mock.patch('ebcli.controllers.health.healthops.display_interactive_health')
    def test_health__set_view_type(
            self,
            display_interactive_health_mock,
            get_env_name_mock,
            get_app_name_mock
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(argv=['health', '--view', 'request'])
        app.setup()
        app.run()

        display_interactive_health_mock.assert_called_once_with(
            'my-application',
            'environment-1',
            False,
            False,
            'request'
        )

    @mock.patch('ebcli.controllers.health.HealthController.get_app_name')
    @mock.patch('ebcli.controllers.health.HealthController.get_env_name')
    @mock.patch('ebcli.controllers.health.healthops.display_interactive_health')
    def test_health__should_refresh(
            self,
            display_interactive_health_mock,
            get_env_name_mock,
            get_app_name_mock
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(argv=['health', '--refresh'])
        app.setup()
        app.run()

        display_interactive_health_mock.assert_called_once_with(
            'my-application',
            'environment-1',
            True,
            False,
            'split'
        )

    @mock.patch('ebcli.controllers.health.HealthController.get_app_name')
    @mock.patch('ebcli.controllers.health.HealthController.get_env_name')
    @mock.patch('ebcli.controllers.health.healthops.display_interactive_health')
    def test_health__mono_format_and_refresh(
            self,
            display_interactive_health_mock,
            get_env_name_mock,
            get_app_name_mock
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(argv=['health', '--refresh', '--mono', '--view', 'request'])
        app.setup()
        app.run()

        display_interactive_health_mock.assert_called_once_with(
            'my-application',
            'environment-1',
            True,
            True,
            'request'
        )
