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
from copy import deepcopy

import mock
import unittest

from ebcli.operations import scaleops

from .. import mock_responses


class TestScaleOps(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')
        os.chdir('testDir')

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

    @mock.patch('ebcli.operations.scaleops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.operations.scaleops.elasticbeanstalk.update_environment')
    @mock.patch('ebcli.operations.scaleops.commonops.wait_for_success_events')
    def test_scale(
            self,
            wait_for_success_events_mock,
            update_environment_mock,
            describe_configuration_settings_mock
    ):
        configuration_settings = deepcopy(
            mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE__2['ConfigurationSettings'][0]
        )
        namespace = 'aws:elasticbeanstalk:environment'
        setting = next((n for n in configuration_settings['OptionSettings'] if n["Namespace"] == namespace), None)
        setting['Value'] = 'LoadBalanced'
        describe_configuration_settings_mock.return_value = configuration_settings
        update_environment_mock.return_value = 'request-id'

        scaleops.scale('my-application', 'environment-1', 3, 'y', timeout=10)

        update_environment_mock.assert_called_once_with(
            'environment-1',
            [
                {
                    'Namespace': 'aws:autoscaling:asg',
                    'OptionName': 'MaxSize',
                    'Value': '3'
                },
                {
                    'Namespace': 'aws:autoscaling:asg',
                    'OptionName': 'MinSize',
                    'Value': '3'
                }
            ]
        )
        wait_for_success_events_mock.assert_called_once_with(
            'request-id',
            can_abort=True,
            timeout_in_minutes=10
        )

    @mock.patch('ebcli.operations.scaleops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.operations.scaleops.elasticbeanstalk.update_environment')
    @mock.patch('ebcli.operations.scaleops.commonops.wait_for_success_events')
    @mock.patch('ebcli.operations.scaleops.io.get_boolean_response')
    def test_scale__single_instance(
            self,
            get_boolean_response_mock,
            wait_for_success_events_mock,
            update_environment_mock,
            describe_configuration_settings_mock
    ):
        get_boolean_response_mock.return_value = True
        describe_configuration_settings_mock.return_value = mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE__2['ConfigurationSettings'][0]

        update_environment_mock.return_value = 'request-id'

        scaleops.scale('my-application', 'environment-1', 3, 'y', timeout=10)

        update_environment_mock.assert_called_once_with(
            'environment-1',
            [
                {
                    'Namespace': 'aws:elasticbeanstalk:environment',
                    'OptionName': 'EnvironmentType',
                    'Value': 'LoadBalanced'
                },
                {
                    'Namespace': 'aws:autoscaling:asg',
                    'OptionName': 'MaxSize',
                    'Value': '3'
                },
                {
                    'Namespace': 'aws:autoscaling:asg',
                    'OptionName': 'MinSize',
                    'Value': '3'
                }
            ]
        )
        wait_for_success_events_mock.assert_called_once_with(
            'request-id',
            can_abort=True,
            timeout_in_minutes=10
        )
