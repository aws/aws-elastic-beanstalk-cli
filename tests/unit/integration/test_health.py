# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
import asyncio
import pytest

import mock
import unittest

from ebcli.core.ebcore import EB
from ebcli.core import fileoperations
from ebcli.operations import commonops

from .. import mock_responses


class TestHealth(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.getcwd()
        if os.path.exists('testDir'):
            shutil.rmtree('testDir')
        os.mkdir('testDir')
        os.chdir('testDir')

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

    @classmethod
    def tearDownClass(cls):
        import time
        time.sleep(0.5)

    @mock.patch('ebcli.controllers.health.healthops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.display.data_poller.elasticbeanstalk.get_environment_health')
    @mock.patch('ebcli.display.data_poller.elasticbeanstalk.get_instance_health')
    def test_health(
            self,
            get_instance_health_mock,
            get_environment_health_mock,
            describe_configuration_settings_mock
    ):
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            'php-7.2'
        )
        commonops.set_environment_for_current_branch('environment-1')
        describe_configuration_settings_mock.return_value = mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE__2['ConfigurationSettings'][0]
        get_environment_health_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENT_HEALTH_RESPONSE
        get_instance_health_mock.return_value = mock_responses.DESCRIBE_INSTANCES_HEALTH_RESPONSE

        app = EB(argv=['health'])
        app.setup()
        app.run()

    @mock.patch('ebcli.controllers.health.healthops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.display.data_poller.elasticbeanstalk.get_environment_health')
    @mock.patch('ebcli.display.data_poller.elasticbeanstalk.get_instance_health')
    def test_health__mono(
            self,
            get_instance_health_mock,
            get_environment_health_mock,
            describe_configuration_settings_mock
    ):
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            'php-7.2'
        )
        commonops.set_environment_for_current_branch('environment-1')
        describe_configuration_settings_mock.return_value = mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE__2['ConfigurationSettings'][0]
        get_environment_health_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENT_HEALTH_RESPONSE
        get_instance_health_mock.return_value = mock_responses.DESCRIBE_INSTANCES_HEALTH_RESPONSE

        app = EB(argv=['health', '--mono'])
        app.setup()
        app.run()

    @pytest.mark.asyncio
    @mock.patch('ebcli.controllers.health.healthops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.display.data_poller.elasticbeanstalk.get_environment_health')
    @mock.patch('ebcli.display.data_poller.elasticbeanstalk.get_instance_health')
    async def test_health__refresh(
            self,
            get_instance_health_mock,
            get_environment_health_mock,
            describe_configuration_settings_mock
    ):
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            'php-7.2'
        )
        commonops.set_environment_for_current_branch('environment-1')
        describe_configuration_settings_mock.return_value = mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE__2['ConfigurationSettings'][0]
        get_environment_health_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENT_HEALTH_RESPONSE
        get_instance_health_mock.return_value = mock_responses.DESCRIBE_INSTANCES_HEALTH_RESPONSE

        async def run_eb_health_refresh():
            app = EB(argv=['health', '--refresh'])
            app.setup()
            app.run()

        await asyncio.wait_for(run_eb_health_refresh(), timeout=2)

    @mock.patch('ebcli.controllers.health.healthops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.display.data_poller.elasticbeanstalk.get_environment_health')
    @mock.patch('ebcli.display.data_poller.elasticbeanstalk.get_instance_health')
    def test_health__mono__view_status(
            self,
            get_instance_health_mock,
            get_environment_health_mock,
            describe_configuration_settings_mock
    ):
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            'php-7.2'
        )
        commonops.set_environment_for_current_branch('environment-1')
        describe_configuration_settings_mock.return_value = mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE__2['ConfigurationSettings'][0]
        get_environment_health_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENT_HEALTH_RESPONSE
        get_instance_health_mock.return_value = mock_responses.DESCRIBE_INSTANCES_HEALTH_RESPONSE

        app = EB(argv=['health', '--view', 'status'])
        app.setup()
        app.run()

    @mock.patch('ebcli.controllers.health.healthops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.display.data_poller.elasticbeanstalk.get_environment_health')
    @mock.patch('ebcli.display.data_poller.elasticbeanstalk.get_instance_health')
    def test_health__mono__view_request(
            self,
            get_instance_health_mock,
            get_environment_health_mock,
            describe_configuration_settings_mock
    ):
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            'php-7.2'
        )
        commonops.set_environment_for_current_branch('environment-1')
        describe_configuration_settings_mock.return_value = mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE__2['ConfigurationSettings'][0]
        get_environment_health_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENT_HEALTH_RESPONSE
        get_instance_health_mock.return_value = mock_responses.DESCRIBE_INSTANCES_HEALTH_RESPONSE

        app = EB(argv=['health', '--view', 'request'])
        app.setup()
        app.run()

    @mock.patch('ebcli.controllers.health.healthops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.display.data_poller.elasticbeanstalk.get_environment_health')
    @mock.patch('ebcli.display.data_poller.elasticbeanstalk.get_instance_health')
    def test_health__mono__view_cpu(
            self,
            get_instance_health_mock,
            get_environment_health_mock,
            describe_configuration_settings_mock
    ):
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            'php-7.2'
        )
        commonops.set_environment_for_current_branch('environment-1')
        describe_configuration_settings_mock.return_value = mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE__2['ConfigurationSettings'][0]
        get_environment_health_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENT_HEALTH_RESPONSE
        get_instance_health_mock.return_value = mock_responses.DESCRIBE_INSTANCES_HEALTH_RESPONSE

        app = EB(argv=['health', '--view', 'cpu'])
        app.setup()
        app.run()