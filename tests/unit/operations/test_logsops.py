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
import sys

import pytest
import unittest
import mock

from ebcli.operations import logsops
from ebcli.objects.exceptions import (
    InvalidOptionsError,
    NotFoundError,
    ServiceError
)
from ebcli.resources.statics import logs_operations_constants

from tests.unit import mock_logs


class TestLogsOperations(unittest.TestCase):
    app_name = 'MyFooApp'
    env_name = 'MyFooEnv'
    instance_id = 'i-123456789'
    instance_id_alt = 'i-666666666'
    specified_log_group = '/aws/elasticbeanstalk/{0}/specific/error.log'.format(env_name)

    def setUp(self):
        self.root_dir = os.getcwd()
        if os.path.isdir('testDir'):
            shutil.rmtree('testDir')

        os.mkdir('testDir')
        os.chdir('testDir')

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

    def test_beanstalk_prefix_for_environment(self):
        self.assertEqual(
            '/aws/elasticbeanstalk/my_env',
            logsops.cloudwatch_log_group_prefix_for_environment('my_env')
        )

    def test_beanstalk_log_group_for_environment_health_streaming(self):
        self.assertEqual(
            '/aws/elasticbeanstalk/my_env/environment-health.log',
            logsops.cloudwatch_log_group_for_environment_health_streaming('my_env')
        )

    @mock.patch('ebcli.operations.logsops.cloudwatch.get_all_stream_names')
    def test_cloudwatch_log_stream_names(self, get_all_stream_names_mock):
        get_all_stream_names_mock.return_value = ['log_stream_1', 'log_stream_2']

        self.assertEqual(
            ['log_stream_1', 'log_stream_2'],
            logsops.cloudwatch_log_stream_names('some_log_group', 'some_instance_id')
        )

    @mock.patch('ebcli.operations.logsops.io.get_event_streamer')
    @mock.patch('ebcli.operations.logsops.cloudwatch_log_stream_names')
    @mock.patch('ebcli.operations.logsops._create_log_stream_for_log_group')
    @mock.patch('ebcli.operations.logsops._delay_subsequent_stream_creation')
    @mock.patch('ebcli.operations.logsops._wait_to_poll_cloudwatch')
    def test_stream_cloudwatch_logs(
            self,
            _wait_to_poll_cloudwatch_mock,
            _delay_subsequent_stream_creation_mock,
            _create_log_stream_for_log_group_mock,
            cloudwatch_log_stream_names_mock,
            get_event_streamer_mock,
    ):
        streamer = mock.MagicMock()
        get_event_streamer_mock.return_value = streamer
        _wait_to_poll_cloudwatch_mock.side_effect = KeyboardInterrupt
        _delay_subsequent_stream_creation_mock.return_value = None
        cloudwatch_log_stream_names_mock.return_value = ['log_group_1', 'log_group_2']

        calls = [
            mock.call('/aws/elasticbeanstalk/my_environment', 'log_group_1', streamer, 0, None),
            mock.call('/aws/elasticbeanstalk/my_environment', 'log_group_2', streamer, 0, None),
        ]

        try:
            logsops.stream_instance_logs_from_cloudwatch(
                sleep_time=0,
                log_group='/aws/elasticbeanstalk/my_environment',
                specific_log_stream='i-213123qsdasdad'
            )
        except KeyboardInterrupt:
            pass

        _create_log_stream_for_log_group_mock.assert_has_calls(calls, any_order=True)

    @mock.patch('ebcli.operations.logsops.io.get_event_streamer')
    @mock.patch('ebcli.operations.logsops.cloudwatch_log_stream_names')
    @mock.patch('ebcli.operations.logsops._create_log_stream_for_log_group')
    @mock.patch('ebcli.operations.logsops._delay_subsequent_stream_creation')
    @mock.patch('ebcli.operations.logsops._wait_to_poll_cloudwatch')
    @mock.patch('ebcli.operations.logsops._updated_start_time')
    def test_stream_cloudwatch_logs__multiple_times(
            self,
            _updated_start_time_mock,
            _wait_to_poll_cloudwatch_mock,
            _delay_subsequent_stream_creation_mock,
            _create_log_stream_for_log_group_mock,
            cloudwatch_log_stream_names_mock,
            get_event_streamer_mock,
    ):
        streamer = mock.MagicMock()
        _updated_start_time_mock.return_value = '1231231231234'
        get_event_streamer_mock.return_value = streamer
        _wait_to_poll_cloudwatch_mock.side_effect = [None, KeyboardInterrupt]
        _delay_subsequent_stream_creation_mock.return_value = None
        cloudwatch_log_stream_names_mock.return_value = ['log_group_1']

        calls = [
            mock.call('/aws/elasticbeanstalk/my_environment', 'log_group_1', streamer, 0, None),
            mock.call('/aws/elasticbeanstalk/my_environment', 'log_group_1', streamer, 0, '1231231231234'),
        ]

        try:
            logsops.stream_instance_logs_from_cloudwatch(
                sleep_time=0,
                log_group='/aws/elasticbeanstalk/my_environment',
                specific_log_stream='i-213123qsdasdad'
            )
        except KeyboardInterrupt:
            pass

        _create_log_stream_for_log_group_mock.assert_has_calls(calls, any_order=True)

    def test_create_log_stream_for_log_group(self):
        streamer = mock.MagicMock()

        with mock.patch('ebcli.operations.logsops.stream_single_stream'):
            for i in range(1, 3):
                logsops._create_log_stream_for_log_group(
                    '/aws/elasticbeanstalk/my_environment',
                    'log_group_2',
                    streamer,
                    0
                )

    @mock.patch('ebcli.operations.logsops.commonops.update_environment')
    @mock.patch('ebcli.operations.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.environment_health_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    def test_disable_cloudwatch_logs__all(
            self,
            describe_configuration_settings_mock,
            environment_health_streaming_enabled_mock,
            instance_log_streaming_enabled_mock,
            update_environment_mock
    ):
        instance_log_streaming_enabled_mock.return_value = True
        environment_health_streaming_enabled_mock.return_value = True
        describe_configuration_settings_mock.side_effect = None

        logsops.disable_cloudwatch_logs(self.app_name, self.env_name, cloudwatch_log_source='all')

        update_environment_mock.assert_called_once_with(
            'MyFooEnv', changes=[
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs',
                    'OptionName': 'StreamLogs',
                    'Value': 'false'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs:health',
                    'OptionName': 'HealthStreamingEnabled',
                    'Value': 'false'
                }
            ],
            nohang=False,
            timeout=15
        )

    @mock.patch('ebcli.operations.logsops.commonops.update_environment')
    @mock.patch('ebcli.operations.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.environment_health_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    def test_disable_cloudwatch_logs__all__both_already_disabled(
            self,
            describe_configuration_settings_mock,
            environment_health_streaming_enabled_mock,
            instance_log_streaming_enabled_mock,
            update_environment_mock
    ):
        environment_health_streaming_enabled_mock.return_value = False
        instance_log_streaming_enabled_mock.return_value = False
        describe_configuration_settings_mock.side_effect = None

        logsops.disable_cloudwatch_logs(self.app_name, self.env_name, cloudwatch_log_source='all')

        update_environment_mock.assert_not_called()

    @mock.patch('ebcli.operations.logsops.commonops.update_environment')
    @mock.patch('ebcli.operations.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.environment_health_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    def test_disable_cloudwatch_logs__all__instance_log_streaming_already_disabled(
            self,
            describe_configuration_settings_mock,
            environment_health_streaming_enabled_mock,
            instance_log_streaming_enabled_mock,
            update_environment_mock
    ):
        instance_log_streaming_enabled_mock.return_value = False
        environment_health_streaming_enabled_mock.return_value = True

        logsops.disable_cloudwatch_logs(self.app_name, self.env_name, cloudwatch_log_source='all')

        update_environment_mock.assert_called_once_with(
            'MyFooEnv',
            changes=[
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs:health',
                    'OptionName': 'HealthStreamingEnabled',
                    'Value': 'false'
                }
            ],
            nohang=False,
            timeout=5
        )

    @mock.patch('ebcli.operations.logsops.commonops.update_environment')
    @mock.patch('ebcli.operations.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    def test_disable_cloudwatch_logs__instance(
            self,
            describe_configuration_settings_mock,
            instance_log_streaming_enabled,
            update_environment_mock
    ):
        instance_log_streaming_enabled.return_value = True
        describe_configuration_settings_mock.side_effect = None
        logsops.disable_cloudwatch_logs(self.app_name, self.env_name, cloudwatch_log_source='instance')

        update_environment_mock.assert_called_once_with(
            'MyFooEnv',
            changes=[
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs',
                    'OptionName': 'StreamLogs',
                    'Value': 'false'
                }
            ],
            nohang=False,
            timeout=15
        )

    @mock.patch('ebcli.operations.logsops.commonops.update_environment')
    @mock.patch('ebcli.operations.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    def test_disable_cloudwatch_logs__instance__already_disabled(
            self,
            describe_configuration_settings_mock,
            instance_log_streaming_disable,
            update_environment_mock
    ):
        instance_log_streaming_disable.return_value = False
        describe_configuration_settings_mock.side_effect = None
        logsops.disable_cloudwatch_logs(self.app_name, self.env_name, cloudwatch_log_source='instance')

        update_environment_mock.assert_not_called()

    @mock.patch('ebcli.operations.logsops.commonops.update_environment')
    @mock.patch('ebcli.operations.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    def test_disable_cloudwatch_logs__cloudwatch_log_source_not_specified_by_customer__defaults_to_instance__already_disabled(
            self,
            describe_configuration_settings_mock,
            instance_log_streaming_enabled,
            update_environment_mock
    ):
        instance_log_streaming_enabled.return_value = True

        logsops.disable_cloudwatch_logs(self.app_name, self.env_name, cloudwatch_log_source=None)

        update_environment_mock.assert_called_once_with(
            'MyFooEnv',
            changes=[
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs',
                    'OptionName': 'StreamLogs',
                    'Value': 'false'
                }
            ],
            nohang=False,
            timeout=15
        )

    @mock.patch('ebcli.operations.logsops.commonops.update_environment')
    @mock.patch('ebcli.operations.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    def test_disable_cloudwatch_logs__cloudwatch_log_source_not_specified_by_customer__defaults_to_instance__instance_already_disabled(
            self,
            describe_configuration_settings_mock,
            instance_log_streaming_disabled,
            update_environment_mock
    ):
        instance_log_streaming_disabled.return_value = False
        describe_configuration_settings_mock.side_effect = None
        logsops.disable_cloudwatch_logs(self.app_name, self.env_name, cloudwatch_log_source=None)

        update_environment_mock.assert_not_called()

    @mock.patch('ebcli.operations.logsops.commonops.update_environment')
    @mock.patch('ebcli.operations.logsops.environment_health_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    def test_disable_cloudwatch_logs__environment_health(
            self,
            describe_configuration_settings_mock,
            environment_health_streaming_enabled_mock,
            update_environment_mock
    ):
        environment_health_streaming_enabled_mock.return_value = True

        logsops.disable_cloudwatch_logs(self.app_name, self.env_name, cloudwatch_log_source='environment-health')

        update_environment_mock.assert_called_once_with(
            'MyFooEnv',
            changes=[
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs:health',
                    'OptionName': 'HealthStreamingEnabled',
                    'Value': 'false'
                }
            ],
            nohang=False,
            timeout=5
        )

    @mock.patch('ebcli.operations.logsops.commonops.update_environment')
    @mock.patch('ebcli.operations.logsops.environment_health_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    def test_disable_cloudwatch_logs__environment_health__already_disabled(
            self,
            describe_configuration_settings_mock,
            environment_health_streaming_enabled_mock,
            update_environment_mock
    ):
        environment_health_streaming_enabled_mock.return_value = False
        describe_configuration_settings_mock.side_effect = None
        logsops.disable_cloudwatch_logs(self.app_name, self.env_name, cloudwatch_log_source='environment-health')

        update_environment_mock.assert_not_called()

    @mock.patch('ebcli.operations.logsops._echo_link_to_cloudwatch_console')
    @mock.patch('ebcli.operations.logsops.commonops.update_environment')
    @mock.patch('ebcli.operations.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.environment_health_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.operations.logsops._raise_if_environment_is_not_using_enhanced_health')
    def test_enable_cloudwatch_logs__all(
            self,
            raise_if_environment_is_not_using_enhanced_health_mock,
            describe_configuration_settings_mock,
            environment_health_streaming_enabled_mock,
            instance_log_streaming_enabled_mock,
            update_environment_mock,
            _echo_link_to_cloudwatch_console_mock
    ):
        environment_health_streaming_enabled_mock.return_value = False
        instance_log_streaming_enabled_mock.return_value = False
        describe_configuration_settings_mock.side_effect = None
        raise_if_environment_is_not_using_enhanced_health_mock.side_effect = None
        _echo_link_to_cloudwatch_console_mock.side_effect = None
        logsops.enable_cloudwatch_logs(self.app_name, self.env_name, cloudwatch_log_source='all')

        update_environment_mock.assert_called_once_with(
            'MyFooEnv', changes=[
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs',
                    'OptionName': 'StreamLogs',
                    'Value': 'true'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs:health',
                    'OptionName': 'HealthStreamingEnabled',
                    'Value': 'true'
                }
            ],
            nohang=False,
            timeout=15
        )

    @mock.patch('ebcli.operations.logsops.commonops.update_environment')
    @mock.patch('ebcli.operations.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.environment_health_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.operations.logsops._raise_if_environment_is_not_using_enhanced_health')
    def test_enable_cloudwatch_logs__all__already_enabled(
            self,
            raise_if_environment_is_not_using_enhanced_health_mock,
            describe_configuration_settings_mock,
            environment_health_streaming_enabled_mock,
            instance_log_streaming_enabled_mock,
            update_environment_mock
    ):
        environment_health_streaming_enabled_mock.return_value = True
        instance_log_streaming_enabled_mock.return_value = True
        describe_configuration_settings_mock.side_effect = None
        raise_if_environment_is_not_using_enhanced_health_mock.side_effect = None

        logsops.enable_cloudwatch_logs(self.app_name, self.env_name, cloudwatch_log_source='all')

        update_environment_mock.assert_not_called()

    @mock.patch('ebcli.operations.logsops._echo_link_to_cloudwatch_console')
    @mock.patch('ebcli.operations.logsops.commonops.update_environment')
    @mock.patch('ebcli.operations.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.environment_health_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.operations.logsops._raise_if_environment_is_not_using_enhanced_health')
    def test_enable_cloudwatch_logs__all__environment_health_streaming_enabled(
            self,
            raise_if_environment_is_not_using_enhanced_health_mock,
            describe_configuration_settings_mock,
            environment_health_streaming_enabled_mock,
            instance_log_streaming_enabled_mock,
            update_environment_mock,
            _echo_link_to_cloudwatch_console_mock
    ):
        environment_health_streaming_enabled_mock.return_value = True
        instance_log_streaming_enabled_mock.return_value = False
        describe_configuration_settings_mock.side_effect = None
        raise_if_environment_is_not_using_enhanced_health_mock.side_effect = None
        _echo_link_to_cloudwatch_console_mock.side_effect = None

        logsops.enable_cloudwatch_logs(self.app_name, self.env_name, cloudwatch_log_source='all')

        update_environment_mock.assert_called_once_with(
            'MyFooEnv',
            changes=[
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs',
                    'OptionName': 'StreamLogs',
                    'Value': 'true'
                }
            ],
            nohang=False,
            timeout=15
        )

    @mock.patch('ebcli.operations.logsops.commonops.update_environment')
    @mock.patch('ebcli.operations.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.operations.logsops._echo_link_to_cloudwatch_console')
    def test_enable_cloudwatch_logs__instance(
            self,
            _echo_link_to_cloudwatch_console_mock,
            describe_configuration_settings_mock,
            instance_log_streaming_enabled_mock,
            update_environment_mock
    ):
        instance_log_streaming_enabled_mock.return_value = False
        describe_configuration_settings_mock.side_effect = None
        _echo_link_to_cloudwatch_console_mock.side_effect = None

        logsops.enable_cloudwatch_logs(self.app_name, self.env_name, cloudwatch_log_source='instance')

        update_environment_mock.assert_called_once_with(
            'MyFooEnv',
            changes=[
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs',
                    'OptionName': 'StreamLogs',
                    'Value': 'true'
                }
            ],
            nohang=False,
            timeout=15
        )

    @mock.patch('ebcli.operations.logsops.commonops.update_environment')
    @mock.patch('ebcli.operations.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    def test_enable_cloudwatch_logs__instance__already_enabled(
            self,
            describe_configuration_settings_mock,
            instance_log_streaming_enabled_mock,
            update_environment_mock
    ):
        instance_log_streaming_enabled_mock.return_value = True
        describe_configuration_settings_mock.side_effect = None
        logsops.enable_cloudwatch_logs(self.app_name, self.env_name, cloudwatch_log_source='instance')

        update_environment_mock.assert_not_called()

    @mock.patch('ebcli.operations.logsops._echo_link_to_cloudwatch_console')
    @mock.patch('ebcli.operations.logsops.commonops.update_environment')
    @mock.patch('ebcli.operations.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    def test_enable_cloudwatch_logs__cloudwatch_log_source_not_specified_by_customer__defaults_to_instance(
            self,
            describe_configuration_settings_mock,
            instance_log_streaming_enabled_mock,
            update_environment_mock,
            _echo_link_to_cloudwatch_console_mock
    ):
        instance_log_streaming_enabled_mock.return_value = False
        describe_configuration_settings_mock.side_effect = None
        _echo_link_to_cloudwatch_console_mock.side_effect = None

        logsops.enable_cloudwatch_logs(self.app_name, self.env_name, cloudwatch_log_source=None)

        update_environment_mock.assert_called_once_with(
            'MyFooEnv',
            changes=[
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs',
                    'OptionName': 'StreamLogs',
                    'Value': 'true'
                }
            ],
            nohang=False,
            timeout=15
        )

    @mock.patch('ebcli.operations.logsops.commonops.update_environment')
    @mock.patch('ebcli.operations.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    def test_enable_cloudwatch_logs__cloudwatch_log_source_not_specified_by_customer__defaults_to_instance__already_enabled(
            self,
            describe_configuration_settings_mock,
            instance_log_streaming_enabled_mock,
            update_environment_mock
    ):
        instance_log_streaming_enabled_mock.return_value = True
        describe_configuration_settings_mock.side_effect = None

        logsops.enable_cloudwatch_logs(self.app_name, self.env_name, cloudwatch_log_source=None)

        update_environment_mock.assert_not_called()

    @mock.patch('ebcli.operations.logsops._echo_link_to_cloudwatch_console')
    @mock.patch('ebcli.operations.logsops.commonops.update_environment')
    @mock.patch('ebcli.operations.logsops.environment_health_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.operations.logsops._raise_if_environment_is_not_using_enhanced_health')
    def test_enable_cloudwatch_logs__environment_health(
            self,
            raise_if_environment_is_not_using_enhanced_health_mock,
            describe_configuration_settings_mock,
            environment_health_streaming_enabled_mock,
            update_environment_mock,
            _echo_link_to_cloudwatch_console_mock
    ):
        environment_health_streaming_enabled_mock.return_value = False
        describe_configuration_settings_mock.side_effect = None
        raise_if_environment_is_not_using_enhanced_health_mock.side_effect = None
        _echo_link_to_cloudwatch_console_mock.side_effect = None

        logsops.enable_cloudwatch_logs(self.app_name, self.env_name, cloudwatch_log_source='environment-health')

        update_environment_mock.assert_called_once_with(
            'MyFooEnv',
            changes=[
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs:health',
                    'OptionName': 'HealthStreamingEnabled',
                    'Value': 'true'
                }
            ],
            nohang=False,
            timeout=5
        )

    @mock.patch('ebcli.operations.logsops.commonops.update_environment')
    @mock.patch('ebcli.operations.logsops.environment_health_streaming_enabled')
    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.operations.logsops._raise_if_environment_is_not_using_enhanced_health')
    def test_enable_cloudwatch_logs__environment_health__already_enabled(
            self,
            raise_if_environment_is_not_using_enhanced_health_mock,
            describe_configuration_settings_mock,
            environment_health_streaming_enabled_mock,
            update_environment_mock
    ):
        environment_health_streaming_enabled_mock.return_value = True
        describe_configuration_settings_mock.side_effect = None
        raise_if_environment_is_not_using_enhanced_health_mock.side_effect = None

        logsops.enable_cloudwatch_logs(self.app_name, self.env_name, cloudwatch_log_source='environment-health')

        update_environment_mock.assert_not_called()

    @mock.patch('ebcli.operations.logsops.cloudwatch.get_log_events')
    def test_get_cloudwatch_stream_logs_for_instance(self, get_log_events_mock):
        get_log_events_mock.return_value = {
            'events': [
                {
                    'timestamp': 1521501601426,
                    'message': '[2018-03-19T23:19:55.811Z] INFO  [2810]  - [Initialization] : Starting activity...',
                    'ingestionTime': 1521501607457
                },
                {
                    'timestamp': 1521501601426,
                    'message': '[2018-03-19T23:19:55.811Z] INFO  [2810]  - [Initialization/AddonsBefore] : Starting activity...',
                    'ingestionTime': 1521501607457
                }
            ]
        }

        self.assertEqual(
            '[my_log_stream] [2018-03-19T23:19:55.811Z] INFO  [2810]  - [Initialization] : Starting activity...{linesep}'
            '[my_log_stream] [2018-03-19T23:19:55.811Z] INFO  [2810]  - [Initialization/AddonsBefore] : Starting activity...'.format(
                linesep=os.linesep
            ),
            logsops.get_cloudwatch_log_stream_events(
                'log_group_name',
                'my_log_stream'
            )
        )

    @mock.patch('ebcli.operations.logsops.cloudwatch.get_log_events')
    def test_get_cloudwatch_stream_logs_for_instance__service_error_encountered(self, get_log_events_mock):
        get_log_events_mock.side_effect = ServiceError

        self.assertEqual(
            '',
            logsops.get_cloudwatch_log_stream_events(
                'log_group_name',
                'my_log_stream'
            )
        )

    @mock.patch('ebcli.operations.logsops.cloudwatch.get_log_events')
    def test_get_cloudwatch_stream_logs_for_instance__general_exception_encountered(self, get_log_events_mock):
        get_log_events_mock.side_effect = Exception

        self.assertEqual(
            '',
            logsops.get_cloudwatch_log_stream_events(
                'log_group_name',
                'my_log_stream'
            )
        )

    @mock.patch('ebcli.operations.logsops.cloudwatch.get_log_events')
    def test_get_logs_cloudwatch_throws_service_error(self, get_log_events_mock):
        get_log_events_mock.side_effect = ServiceError("Service is throwing an error!")

        logsops.get_cloudwatch_log_stream_events(self.specified_log_group, self.instance_id_alt)

        get_log_events_mock.assert_called_with(self.specified_log_group, self.instance_id_alt, limit=None)

    @mock.patch('ebcli.operations.logsops.cloudwatch.get_log_events')
    def test_get_logs_cloudwatch_throws_unknown_exception(self, get_log_events_mock):
        get_log_events_mock.side_effect = Exception("An unknown error appeared!")

        logsops.get_cloudwatch_log_stream_events(self.specified_log_group, self.instance_id, num_log_events=50)

        get_log_events_mock.assert_called_with(self.specified_log_group, self.instance_id, limit=50)

    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    def test_log_streaming_enabled__config_settings_not_passed_in(
            self,
            describe_configuration_settings_mock
    ):
        describe_configuration_settings_mock.return_value = {
            'OptionSettings': [
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs',
                    'OptionName': 'StreamLogs',
                    'Value': 'true'
                }
            ]
        }

        self.assertTrue(
            logsops.instance_log_streaming_enabled(self.app_name, self.env_name, None)
        )

        describe_configuration_settings_mock.return_value = {
            'OptionSettings': [
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs',
                    'OptionName': 'StreamLogs',
                    'Value': 'false'
                }
            ]
        }

        self.assertFalse(
            logsops.instance_log_streaming_enabled(self.app_name, self.env_name, None)
        )

    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    def test_log_streaming_enabled__config_settings_passed_in(
            self,
            describe_configuration_settings_mock
    ):
        describe_configuration_settings = {
            'OptionSettings': [
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs',
                    'OptionName': 'StreamLogs',
                    'Value': 'true'
                }
            ]
        }
        self.assertTrue(
            logsops.instance_log_streaming_enabled(self.app_name, self.env_name, describe_configuration_settings)
        )
        describe_configuration_settings_mock.assert_not_called()

        describe_configuration_settings = {
            'OptionSettings': [
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs',
                    'OptionName': 'StreamLogs',
                    'Value': 'false'
                }
            ]
        }
        self.assertFalse(
            logsops.instance_log_streaming_enabled(self.app_name, self.env_name, describe_configuration_settings)
        )
        describe_configuration_settings_mock.assert_not_called()

    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    def test_environment_health_streaming_enabled__config_settings_not_passed_in(
            self,
            describe_configuration_settings_mock
    ):
        describe_configuration_settings_mock.return_value = {
            'OptionSettings': [
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs:health',
                    'OptionName': 'HealthStreamingEnabled',
                    'Value': 'true'
                }
            ]
        }

        self.assertTrue(
            logsops.environment_health_streaming_enabled(self.app_name, self.env_name, None)
        )

        describe_configuration_settings_mock.return_value = {
            'OptionSettings': [
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs:health',
                    'OptionName': 'HealthStreamingEnabled',
                    'Value': 'false'
                }
            ]
        }

        self.assertFalse(
            logsops.environment_health_streaming_enabled(self.app_name, self.env_name, None)
        )

    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.describe_configuration_settings')
    def test_environment_health_streaming_enabled__config_settings_passed_in(
            self,
            describe_configuration_settings_mock
    ):
        describe_configuration_settings = {
            'OptionSettings': [
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs:health',
                    'OptionName': 'HealthStreamingEnabled',
                    'Value': 'true'
                }
            ]
        }
        self.assertTrue(
            logsops.environment_health_streaming_enabled(self.app_name, self.env_name, describe_configuration_settings)
        )
        describe_configuration_settings_mock.assert_not_called()

        describe_configuration_settings = {
            'OptionSettings': [
                {
                    'Namespace': 'aws:elasticbeanstalk:cloudwatch:logs:health',
                    'OptionName': 'HealthStreamingEnabled',
                    'Value': 'false'
                }
            ]
        }
        self.assertFalse(
            logsops.environment_health_streaming_enabled(self.app_name, self.env_name, describe_configuration_settings)
        )
        describe_configuration_settings_mock.assert_not_called()

    @mock.patch('ebcli.operations.logsops.elasticbeanstalk')
    def test_log_streaming_enabled_is_false(self, mock_beanstalk):
        meaningless_config = "doesn't matter"
        mock_beanstalk.describe_configuration_settings.return_value = meaningless_config
        mock_beanstalk.get_specific_configuration.return_value = None

        self.assertFalse(
            logsops.instance_log_streaming_enabled(self.app_name, self.env_name),
            "Expected log streaming to be disabled"
        )

    @mock.patch('ebcli.operations.logsops.beanstalk_log_group_builder')
    def test_log_group_builder_default(
            self,
            beanstalk_log_group_builder_mock
    ):
        beanstalk_log_group_builder_mock.return_value = '/aws/elasticbeanstalk/MyFooEnv/var/log/eb-activity.log'

        actual_log_group = logsops.beanstalk_log_group_builder(self.env_name)

        self.assertEqual(
            '/aws/elasticbeanstalk/MyFooEnv/var/log/eb-activity.log',
            actual_log_group,
            "Expected log group to be: {0} but got: {1}".format(
                '/aws/elasticbeanstalk/MyFooEnv/var/log/eb-activity.log',
                actual_log_group
            )
        )

    def test_log_group_builder_with_full_filepath(self):
        actual_log_group = logsops.beanstalk_log_group_builder(self.env_name, self.specified_log_group)
        self.assertEqual(
            self.specified_log_group,
            actual_log_group,
            "Expected log group to be: {0} but got: {1}".format(
                self.specified_log_group,
                actual_log_group
            )
        )

    def test_log_group_builder_with_partial_filepath(self):
        filepath = 'foo/specific/error.log'
        actual_log_group = logsops.beanstalk_log_group_builder(self.env_name, filepath)
        expected_log_group = '/aws/elasticbeanstalk/{0}/{1}'.format(self.env_name, filepath)
        self.assertEqual(
            expected_log_group,
            actual_log_group,
            "Expected log group to be: {0} but got: {1}".format(expected_log_group, actual_log_group)
        )

    @mock.patch('ebcli.operations.logsops.beanstalk_log_group_builder')
    def test_normalize_log_group_name__log_group_and_cloudwatch_log_source_not_passed_in_by_customer(
            self,
            beanstalk_log_group_builder_mock
    ):
        beanstalk_log_group_builder_mock.return_value = '/aws/elasticbeanstalk/MyFooEnv/var/log/eb-activity.log'

        self.assertEqual(
            '/aws/elasticbeanstalk/MyFooEnv/var/log/eb-activity.log',
            logsops.normalize_log_group_name('my_env')
        )

    def test_normalize_log_group_name__log_group_name_passed_in_but_not_cloudwatch_log_source(self):
        self.assertEqual(
            '/aws/elasticbeanstalk/my_env/some_log_group',
            logsops.normalize_log_group_name('my_env', log_group='some_log_group')
        )

    def test_normalize_log_group_name__log_group_name_and_instance_cloudwatch_log_source_arguments_passed_in(self):
        self.assertEqual(
            '/aws/elasticbeanstalk/my_env/some_log_group',
            logsops.normalize_log_group_name(
                'my_env',
                log_group='some_log_group',
                cloudwatch_log_source='instance'
            )
        )

    def test_normalize_log_group_name__log_group_name_and_environment_health_cloudwatch_log_source_arguments_passed_in__log_group_discarded(
            self
    ):
        with self.assertRaises(InvalidOptionsError) as context_manager:
            logsops.normalize_log_group_name(
                'my_env',
                log_group='some_log_group',
                cloudwatch_log_source='environment-health'
            )

        self.assertEqual(
            """You can't use the "--log-group" option when retrieving environment-health logs. These logs are in a specific, implied log group.""",
            str(context_manager.exception)
        )

    def test_normalize_log_group_name__invalid_cloudwatch_log_source(self):
        with self.assertRaises(InvalidOptionsError) as context_manager:
            logsops.normalize_log_group_name('my_env', log_group='some_log_group', cloudwatch_log_source='all')

        self.assertEqual(
            """Invalid CloudWatch Logs source type for retrieving logs: "all". Valid types: instance | environment-health""",
            str(context_manager.exception))

    def test_resolve_log_result_type(self):
        self.assertEqual('bundle', logsops.resolve_log_result_type(True, True))
        self.assertEqual('bundle', logsops.resolve_log_result_type(None, True))
        self.assertEqual('bundle', logsops.resolve_log_result_type(True, None))
        self.assertEqual('tail', logsops.resolve_log_result_type(None, None))

    @mock.patch('ebcli.operations.logsops.get_cloudwatch_log_stream_events')
    @mock.patch('ebcli.operations.logsops.io.echo_with_pager')
    def test_stream_logs_in_terminal(
            self,
            echo_with_pager_mock,
            get_cloudwatch_stream_logs_for_instance_mock
    ):
        log_stream_1_events = """[my_log_stream_1] [2018-03-19T23:19:55.811Z] INFO  [2810]  - [Initialization] : Starting activity...
[my_log_stream] [2018-03-19T23:19:55.811Z] INFO  [2810]  - [Initialization/AddonsBefore] : Starting activity..."""

        log_stream_2_events = """[my_log_stream_2] [2018-03-19T23:19:55.811Z] INFO  [2810]  - [Initialization] : Starting activity...
[my_log_stream] [2018-03-19T23:19:55.811Z] INFO  [2810]  - [Initialization/AddonsBefore] : Starting activity..."""

        get_cloudwatch_stream_logs_for_instance_mock.side_effect = [
            log_stream_1_events,
            log_stream_2_events
        ]

        logsops.stream_logs_in_terminal('log_group', ['log_stream_1', 'log_stream_2'])

        echo_with_pager_mock.assert_called_with(
            '{linesep}{linesep}============= log_stream_1 - log_group =============={linesep}{linesep}'
            '[my_log_stream_1] [2018-03-19T23:19:55.811Z] INFO  [2810]  - [Initialization] : Starting activity...\n'
            '[my_log_stream] [2018-03-19T23:19:55.811Z] INFO  [2810]  - [Initialization/AddonsBefore] : Starting activity...'
            '{linesep}'
            '{linesep}============= log_stream_2 - log_group =============={linesep}'
            '{linesep}'
            '[my_log_stream_2] [2018-03-19T23:19:55.811Z] INFO  [2810]  - [Initialization] : Starting activity...\n'
            '[my_log_stream] [2018-03-19T23:19:55.811Z] INFO  [2810]  - [Initialization/AddonsBefore] : Starting activity...'.format(
                linesep=os.linesep
            )
        )

    @mock.patch('ebcli.operations.logsops.cloudwatch.get_all_stream_names')
    @mock.patch('ebcli.operations.logsops.stream_logs_in_terminal')
    def test_retrieve_cloudwatch_logs__tail_instance_logs(
            self,
            stream_logs_in_terminal_mock,
            get_all_stream_names_mock
    ):
        get_all_stream_names_mock.return_value = ['log_stream_1', 'log_stream_2']

        logsops.retrieve_cloudwatch_logs('some_log_group', 'tail')

        stream_logs_in_terminal_mock.assert_called_once_with('some_log_group', ['log_stream_1', 'log_stream_2'])

    @mock.patch('ebcli.operations.logsops.cloudwatch.get_all_stream_names')
    @mock.patch('ebcli.operations.logsops.stream_logs_in_terminal')
    def test_retrieve_cloudwatch_logs__tail_environment_health_logs(
            self,
            stream_logs_in_terminal_mock,
            get_all_stream_names_mock
    ):
        get_all_stream_names_mock.return_value = ['log_stream_1', 'log_stream_2']

        logsops.retrieve_cloudwatch_logs(
            'some_log_group',
            'tail',
            cloudwatch_log_source=logs_operations_constants.LOG_SOURCES.ENVIRONMENT_HEALTH_LOG_SOURCE
        )

        stream_logs_in_terminal_mock.assert_called_once_with('some_log_group', ['log_stream_1', 'log_stream_2'])

    @pytest.mark.skipif(
        getattr(os, 'symlink', None) is None,
        reason="`os` module does not define `symlink` function for Python 2.7 on Windows"
    )
    @mock.patch('ebcli.operations.logsops.cloudwatch.get_all_stream_names')
    @mock.patch('ebcli.operations.logsops.get_cloudwatch_log_stream_events')
    def test_retrieve_cloudwatch_logs__info_type_bundle(
            self,
            get_cloudwatch_log_stream_events_mock,
            get_all_stream_names_mock
    ):
        os.mkdir('.elasticbeanstalk')

        get_all_stream_names_mock.return_value = ['log_stream_1']
        get_cloudwatch_log_stream_events_mock.return_value = 'These are the full logs\\xe2\\x96'

        logsops.retrieve_cloudwatch_logs('some_log_group', 'bundle')

        self.assertEqual(
            'These are the full logs\\xe2\\x96',
            open(os.path.join('.elasticbeanstalk', 'logs', 'latest', 'log_stream_1.log')).read()
        )

    @pytest.mark.skipif(
        getattr(os, 'symlink', None) is None,
        reason="`os` module does not define `symlink` function for Python 2.7 on Windows"
    )
    @mock.patch('ebcli.operations.logsops._timestamped_directory_name')
    @mock.patch('ebcli.operations.logsops.cloudwatch.get_all_stream_names')
    @mock.patch('ebcli.operations.logsops.get_cloudwatch_log_stream_events')
    def test_retrieve_cloudwatch_logs__info_type_bundle__multiple_retrieves(
            self,
            get_cloudwatch_log_stream_events_mock,
            get_all_stream_names_mock,
            _timestamped_directory_name_mock
    ):
        os.mkdir('.elasticbeanstalk')

        _timestamped_directory_name_mock.side_effect = [
            '180417_175442',
            '180417_175450'
        ]
        get_all_stream_names_mock.return_value = ['log_stream_1']
        get_cloudwatch_log_stream_events_mock.return_value = 'These are the full logs\\xe2\\x96'
        logsops.retrieve_cloudwatch_logs('some_log_group', 'bundle')
        self.assertEqual(
            'These are the full logs\\xe2\\x96',
            open(os.path.join('.elasticbeanstalk', 'logs', 'latest', 'log_stream_1.log')).read()
        )

        get_all_stream_names_mock.return_value = ['log_stream_2']
        get_cloudwatch_log_stream_events_mock.return_value = 'These are also the full logs\\xe2\\x96'
        logsops.retrieve_cloudwatch_logs('some_log_group', 'bundle')
        self.assertEqual(
            'These are also the full logs\\xe2\\x96',
            open(os.path.join('.elasticbeanstalk', 'logs', 'latest', 'log_stream_2.log')).read()
        )

    @mock.patch('ebcli.operations.logsops.cloudwatch.get_all_stream_names')
    @mock.patch('ebcli.operations.logsops.get_cloudwatch_log_stream_events')
    def test_retrieve_cloudwatch_logs__info_type_bundle__create_zip(
            self,
            get_cloudwatch_log_stream_events_mock,
            get_all_stream_names_mock
    ):
        os.mkdir('.elasticbeanstalk')

        get_all_stream_names_mock.return_value = ['log_stream_1']
        get_cloudwatch_log_stream_events_mock.return_value = 'These are the full logs\\xe2\\x96'

        logsops.retrieve_cloudwatch_logs('some_log_group', 'bundle', do_zip=True)

        logs_dir_contents = os.listdir(os.path.join('.elasticbeanstalk', 'logs'))
        self.assertEqual('.zip', logs_dir_contents[0][-4:])

    @pytest.mark.skipif(
        getattr(os, 'symlink', None) is None,
        reason="`os` module does not define `symlink` function for Python 2.7 on Windows"
    )
    @mock.patch('ebcli.operations.logsops.cloudwatch.get_all_stream_names')
    @mock.patch('ebcli.operations.logsops.get_cloudwatch_log_stream_events')
    def test_retrieve_cloudwatch_logs__info_type_bundle__environment_health_source(
            self,
            get_cloudwatch_log_stream_events_mock,
            get_all_stream_names_mock
    ):
        os.mkdir('.elasticbeanstalk')

        get_all_stream_names_mock.return_value = ['log_stream_1']
        get_cloudwatch_log_stream_events_mock.return_value = 'These are the full logs\\xe2\\x96'

        logsops.retrieve_cloudwatch_logs(
            'some_log_group',
            'bundle',
            cloudwatch_log_source=logs_operations_constants.LOG_SOURCES.ENVIRONMENT_HEALTH_LOG_SOURCE
        )

        self.assertEqual(
            'These are the full logs\\xe2\\x96',
            open(os.path.join('.elasticbeanstalk', 'logs', 'environment-health', 'latest', 'log_stream_1.log')).read()
        )

    @mock.patch('ebcli.operations.logsops.cloudwatch.get_all_stream_names')
    @mock.patch('ebcli.operations.logsops.get_cloudwatch_log_stream_events')
    def test_retrieve_cloudwatch_logs__info_type_bundle__environment_health_log_source__create_zip(
            self,
            get_cloudwatch_log_stream_events_mock,
            get_all_stream_names_mock
    ):
        os.mkdir('.elasticbeanstalk')

        get_all_stream_names_mock.return_value = ['log_stream_1']
        get_cloudwatch_log_stream_events_mock.return_value = 'These are the full logs\\xe2\\x96'

        logsops.retrieve_cloudwatch_logs(
            'some_log_group',
            'bundle',
            do_zip=True,
            cloudwatch_log_source=logs_operations_constants.LOG_SOURCES.ENVIRONMENT_HEALTH_LOG_SOURCE
        )

        logs_dir_contents = os.listdir(os.path.join('.elasticbeanstalk', 'logs', 'environment-health'))
        self.assertEqual('.zip', logs_dir_contents[0][-4:])

    @mock.patch('ebcli.operations.logsops.instance_log_streaming_enabled')
    def test_raise_if_instance_log_streaming_is_not_enabled__not_enabled__raises_exception(
            self,
            instance_log_streaming_enabled_mock
    ):
        instance_log_streaming_enabled_mock.return_value = False

        with self.assertRaises(InvalidOptionsError) as context_manager:
            logsops.raise_if_instance_log_streaming_is_not_enabled('some-app', 'some-env')

        self.assertEqual(
            """Can't retrieve instance logs for environment some-env. Instance log streaming is disabled.""",
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.logsops.instance_log_streaming_enabled')
    def test_raise_if_instance_log_streaming_is_not_enabled__enabled(
            self,
            instance_log_streaming_enabled_mock
    ):
        instance_log_streaming_enabled_mock.return_value = True

        logsops.raise_if_instance_log_streaming_is_not_enabled('some-app', 'some-env')

    @mock.patch('ebcli.operations.logsops.environment_health_streaming_enabled')
    def test_raise_if_environment_health_log_streaming_is_not_enabled__not_enabled__raises_exception(
            self,
            environment_health_streaming_enabled_mock
    ):
        environment_health_streaming_enabled_mock.return_value = False

        with self.assertRaises(InvalidOptionsError) as context_manager:
            logsops.raise_if_environment_health_log_streaming_is_not_enabled('some-app', 'some-env')

        self.assertEqual(
            """Can't retrieve environment-health logs for environment some-env. Environment-health log streaming is disabled.""",
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.logsops.environment_health_streaming_enabled')
    def test_raise_if_environment_health_log_streaming_is_not_enabled__raises_exception(
            self,
            environment_health_streaming_enabled_mock
    ):
        environment_health_streaming_enabled_mock.return_value = True

        logsops.raise_if_environment_health_log_streaming_is_not_enabled('some-app', 'some-env')

    @mock.patch('ebcli.operations.logsops._get_cloudwatch_messages')
    @mock.patch('ebcli.operations.logsops._wait_to_poll_cloudwatch')
    def test_get_cloudwatch_logs__simulate_ctrl_c_after_polling_cloudwatch_three_times(
            self,
            _wait_to_poll_cloudwatch_mock,
            _get_cloudwatch_messages_mock
    ):
        _wait_to_poll_cloudwatch_mock.return_value = None
        message_1 = '[my-log-stream-name] b\'I, [2018-03-08T02:35:00.179536+0000#21452]  INFO -- Packer: 1520476500,,ui,message,    HVM AMI builder: + for TAR_BALL in \\\'"$@"\\\'\''
        message_2 = "[my-log-stream-name] b'I, [2018-03-08T02:35:04.381352+0000#21452]  INFO -- Packer: 1520476504,,ui,message,    HVM AMI builder: \\x1b[K    100% |\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88'"
        message_3 = '\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88\\xe2\\x96\\x88| 460kB 1.4MB/s'

        _get_cloudwatch_messages_mock.side_effect = [
            (
                [message_1],
                'f/33907759104553211733662036833768876100389685601243824177',
                None
            ),
            (
                [message_2],
                'f/12312311231231211733662036833768876100389685601243824177',
                1520476504381
            ),
            (
                [message_3],
                'f/34536456456456456433662036833768876100389685601243824177',
                1520476508712
            ),
            KeyboardInterrupt
        ]
        streamer = mock.MagicMock()
        streamer.stream_event = mock.MagicMock()
        stream_event_calls = [
            mock.call(message_1),
            mock.call(message_2),
            mock.call(message_3)
        ]

        def messages_handler(messages):
            [streamer.stream_event(message) for message in messages]

        logsops.get_cloudwatch_messages(
            log_group_name='some-log-group-name',
            stream_name='some-log-group-stream-name',
            formatter=streamer,
            next_token=None,
            start_time=None,
            messages_handler=messages_handler
        )

        streamer.stream_event.assert_has_calls(stream_event_calls)
        self.assertEqual(3, _wait_to_poll_cloudwatch_mock.call_count)

    @mock.patch('ebcli.operations.logsops._get_cloudwatch_messages')
    @mock.patch('ebcli.operations.logsops._wait_to_poll_cloudwatch')
    def test_get_cloudwatch_logs__exit_with_service_error(
            self,
            _wait_to_poll_cloudwatch_mock,
            _get_cloudwatch_messages_mock
    ):
        _wait_to_poll_cloudwatch_mock.return_value = None

        _get_cloudwatch_messages_mock.side_effect = [
            ServiceError('Dummy service error message', code=4)
        ]
        streamer = mock.MagicMock()

        def messages_handler(messages):
            [streamer.stream_event(message) for message in messages]

        logsops.get_cloudwatch_messages(
            log_group_name='some-log-group-name',
            stream_name='some-log-group-stream-name',
            formatter=streamer,
            next_token=None,
            start_time=None,
            messages_handler=messages_handler
        )

        self.assertEqual(0, _wait_to_poll_cloudwatch_mock.call_count)

    @mock.patch('ebcli.operations.logsops._get_cloudwatch_messages')
    @mock.patch('ebcli.operations.logsops._wait_to_poll_cloudwatch')
    @mock.patch('ebcli.operations.logsops.LOG.debug')
    @mock.patch('traceback.format_exc')
    def test_get_cloudwatch_logs__retries_after_encountering_general_exception(
            self,
            traceback_format_exc_mock,
            LOG_debug_mock,
            _wait_to_poll_cloudwatch_mock,
            _get_cloudwatch_messages_mock
    ):
        _wait_to_poll_cloudwatch_mock.return_value = None
        traceback_format_exc_mock.return_value = 'This is a dummy stack trace'

        _get_cloudwatch_messages_mock.side_effect = [
            Exception('This is a general exception'),
            KeyboardInterrupt
        ]
        streamer = mock.MagicMock()

        def messages_handler(messages):
            [streamer.stream_event(message) for message in messages]

        logsops.get_cloudwatch_messages(
            log_group_name='some-log-group-name',
            stream_name='some-log-group-stream-name',
            formatter=streamer,
            next_token=None,
            start_time=None,
            messages_handler=messages_handler
        )

        LOG_debug_mock.assert_has_calls(
            [
                mock.call('Exception raised: This is a general exception'),
                mock.call('This is a dummy stack trace'),
            ]
        )
        self.assertEqual(1, _wait_to_poll_cloudwatch_mock.call_count)

    @mock.patch('ebcli.operations.logsops.cloudwatch.get_log_events')
    def test__get_cloudwatch_messages(self, get_log_events_mock):
        get_log_events_mock.return_value = {
            'events': [
                {
                    'timestamp': 1520476500179,
                    'message': 'I, [2018-03-08T02:35:00.179536+0000#21452]  INFO -- Packer: 1520476500,,ui,message,    HVM AMI builder: + for TAR_BALL in \'"$@"\'',
                    'ingestionTime': 1520476506246
                },
                {
                    'timestamp': 1520476504381,
                    'message': 'I, [2018-03-08T02:35:04.381352+0000#21452]  INFO -- Packer: 1520476504,,ui,message,    HVM AMI builder: \\x1b[K    100% |\\xe2\\x96| 460kB 1.4MB/s',
                    'ingestionTime': 1520476506246
                }
            ],
            'nextForwardToken': 'f/33907759104553211733662036833768876100389685601243824177',
            'nextBackwardToken': 'b/33907759010845480409436358393035787918721270553114116096',
            'ResponseMetadata': {
                'RequestId': '51637641-2279-11e8-89e2-977b487bfa41',
                'HTTPStatusCode': 200,
                'date': 'Thu, 08 Mar 2018 02:35:08 GMT',
                'RetryAttempts': 0
            }
        }

        if sys.version_info < (3, 0):
            expected_events = [
                '[my-log-stream-name] I, [2018-03-08T02:35:00.179536+0000#21452]  INFO -- Packer: 1520476500,,ui,message,    HVM AMI builder: + for TAR_BALL in \'"$@"\'',
                '[my-log-stream-name] I, [2018-03-08T02:35:04.381352+0000#21452]  INFO -- Packer: 1520476504,,ui,message,    HVM AMI builder: \\x1b[K    100% |\\xe2\\x96| 460kB 1.4MB/s'
            ]
        else:
            expected_events = [
                '[my-log-stream-name] b\'I, [2018-03-08T02:35:00.179536+0000#21452]  INFO -- Packer: 1520476500,,ui,message,    HVM AMI builder: + for TAR_BALL in \\\'"$@"\\\'\'',
                "[my-log-stream-name] b'I, [2018-03-08T02:35:04.381352+0000#21452]  INFO -- Packer: 1520476504,,ui,message,    HVM AMI builder: \\\\x1b[K    100% |\\\\xe2\\\\x96| 460kB 1.4MB/s'"
            ]

        actual_events = logsops._get_cloudwatch_messages(
            'my-log-group',
            'my-log-stream-name'
        )

        print(actual_events)
        self.assertEqual(
            (
                expected_events,
                'f/33907759104553211733662036833768876100389685601243824177',
                None
            ),
            actual_events
        )

    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.get_environment')
    def test_deployment_logs_log_group_name__non_windows_platform(self, get_environment_mock):
        environment_mock = mock.MagicMock()
        platform_mock = mock.MagicMock()
        platform_mock.name = 'arn:aws:elasticbeanstalk:ap-southeast-2::platform/PHP 5.4 running on 64bit Amazon Linux 2014.03/1.1.0'
        environment_mock.platform = platform_mock

        get_environment_mock.return_value = environment_mock

        self.assertEqual(
            '/aws/elasticbeanstalk/my-env/var/log/eb-activity.log',
            logsops.deployment_logs_log_group_name('my-env')
        )

    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.get_environment')
    def test_deployment_logs_log_group_name__al2_platforms(self, get_environment_mock):
        environment_mock = mock.MagicMock()
        platform_mock = mock.MagicMock()
        platform_mock.name = 'arn:aws:elasticbeanstalk:us-east-1::platform/Python 3.8 running on 64bit Amazon Linux 2/3.2.0'
        environment_mock.platform = platform_mock

        get_environment_mock.return_value = environment_mock

        self.assertEqual(
            '/aws/elasticbeanstalk/my-env/var/log/eb-engine.log',
            logsops.deployment_logs_log_group_name('my-env')
        )

    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.get_environment')
    def test_deployment_logs_log_group_name__windows_platform(self, get_environment_mock):
        environment_mock = mock.MagicMock()
        platform_mock = mock.MagicMock()
        platform_mock.name = 'arn:aws:elasticbeanstalk:ap-southeast-2::platform/IIS 10.0 running on 64bit Windows Server Core 2016/1.2.0'
        environment_mock.platform = platform_mock

        get_environment_mock.return_value = environment_mock

        self.assertEqual(
            '/aws/elasticbeanstalk/my-env/EBDeploy-Log',
            logsops.deployment_logs_log_group_name('my-env')
        )

    def test_get_platform_builder_group_name(self):
        self.assertEqual(
            '/aws/elasticbeanstalk/platform/platform_name',
            logsops._get_platform_builder_group_name('platform_name')
        )

    def test_raise_if_environment_is_not_using_enhanced_health(self):
        describe_configuration_settings = {
            'OptionSettings': [
                {
                    'Namespace': 'aws:elasticbeanstalk:healthreporting:system',
                    'OptionName': 'SystemType',
                    'Value': 'basic'
                }
            ]
        }

        with self.assertRaises(InvalidOptionsError) as context_manager:
            logsops._raise_if_environment_is_not_using_enhanced_health(describe_configuration_settings)

        self.assertEqual(
            'Enhanced health disabled. Could not setup health-transitions log streaming.',
            str(context_manager.exception)
        )

    def test_raise_if_environment_is_using_enhanced_health(self):
        describe_configuration_settings = {
            'OptionSettings': [
                {
                    'Namespace': 'aws:elasticbeanstalk:healthreporting:system',
                    'OptionName': 'SystemType',
                    'Value': 'enhanced'
                }
            ]
        }

        logsops._raise_if_environment_is_not_using_enhanced_health(describe_configuration_settings)


    @mock.patch('ebcli.operations.logsops.io.echo_with_pager')
    @mock.patch('ebcli.operations.logsops.utils.get_data_from_url')
    def test_handle_tail_logs(
            self,
            get_data_from_url_mock,
            echo_with_pager_mock
    ):
        get_data_from_url_mock.return_value = mock_logs.INSTANCE_TAIL_LOGS_RESPONSE
        logsops._handle_tail_logs(
            {
                'i-090689581e5afcfc6': 'https://elasticbeanstalk-us-east-1-1231231231234.s3.amazonaws.com/resources/environments/logs/tail/e-spfgk5xbd',
                'i-053efe7c102d0a540': 'https://elasticbeanstalk-us-east-1-1231231231234.s3.amazonaws.com/resources/environments/logs/tail/e-spfgk5xbd'
            }
        )

        # six.iteritems does not guarantee order in which key, value pairs of a dict are parsed
        try:
            echo_with_pager_mock.assert_called_with(
                os.linesep.join(
                    [
                        '============= i-090689581e5afcfc6 =============={linesep}-------------------------------------\n/var/log/awslogs.log\n-------------------------------------\n{\'skipped_events_count\': 0, \'first_event\': {\'timestamp\': 1522962583519, \'start_position\': 559799L, \'end_position\': 560017L}, \'fallback_events_count\': 0, \'last_event\': {\'timestamp\': 1522962583519, \'start_position\': 559799L, \'end_position\': 560017L}, \'source_id\': \'77b026040b93055eb448bdc0b59e446f\', \'num_of_events\': 1, \'batch_size_in_bytes\': 243}\n\n\n\n-------------------------------------\n/var/log/httpd/error_log\n-------------------------------------\n[Thu Apr 05 19:54:23.624780 2018] [mpm_prefork:warn] [pid 3470] AH00167: long lost child came home! (pid 3088)\n\n\n\n-------------------------------------\n/var/log/httpd/access_log\n-------------------------------------\n172.31.69.153 (94.208.192.103) - - [05/Apr/2018:20:57:55 +0000] "HEAD /pma/ HTTP/1.1" 404 - "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"\n\n\n\n-------------------------------------\n/var/log/eb-activity.log\n-------------------------------------\n  + chown -R webapp:webapp /var/app/ondeck\n[2018-04-05T19:54:21.630Z] INFO  [3555]  - [Application update app-180406_044630@3/AppDeployStage0/AppDeployPreHook/02_setup_envvars.sh] : Starting activity...\n\n\n-------------------------------------\n/tmp/sample-app.log\n-------------------------------------\n2018-04-05 20:52:51 Received message: \\xe2\\x96\\x88\\xe2\n\n\n\n-------------------------------------\n/var/log/eb-commandprocessor.log\n-------------------------------------\n[2018-04-05T19:45:05.526Z] INFO  [2853]  : Running 2 of 2 actions: AppDeployPostHook...',
                        '============= i-053efe7c102d0a540 =============={linesep}-------------------------------------\n/var/log/awslogs.log\n-------------------------------------\n{\'skipped_events_count\': 0, \'first_event\': {\'timestamp\': 1522962583519, \'start_position\': 559799L, \'end_position\': 560017L}, \'fallback_events_count\': 0, \'last_event\': {\'timestamp\': 1522962583519, \'start_position\': 559799L, \'end_position\': 560017L}, \'source_id\': \'77b026040b93055eb448bdc0b59e446f\', \'num_of_events\': 1, \'batch_size_in_bytes\': 243}\n\n\n\n-------------------------------------\n/var/log/httpd/error_log\n-------------------------------------\n[Thu Apr 05 19:54:23.624780 2018] [mpm_prefork:warn] [pid 3470] AH00167: long lost child came home! (pid 3088)\n\n\n\n-------------------------------------\n/var/log/httpd/access_log\n-------------------------------------\n172.31.69.153 (94.208.192.103) - - [05/Apr/2018:20:57:55 +0000] "HEAD /pma/ HTTP/1.1" 404 - "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"\n\n\n\n-------------------------------------\n/var/log/eb-activity.log\n-------------------------------------\n  + chown -R webapp:webapp /var/app/ondeck\n[2018-04-05T19:54:21.630Z] INFO  [3555]  - [Application update app-180406_044630@3/AppDeployStage0/AppDeployPreHook/02_setup_envvars.sh] : Starting activity...\n\n\n-------------------------------------\n/tmp/sample-app.log\n-------------------------------------\n2018-04-05 20:52:51 Received message: \\xe2\\x96\\x88\\xe2\n\n\n\n-------------------------------------\n/var/log/eb-commandprocessor.log\n-------------------------------------\n[2018-04-05T19:45:05.526Z] INFO  [2853]  : Running 2 of 2 actions: AppDeployPostHook...',
                    ]
                ).replace('{linesep}', os.linesep)
            )
        except AssertionError:
            echo_with_pager_mock.assert_called_with(
                os.linesep.join(
                    [
                        '============= i-053efe7c102d0a540 =============={linesep}-------------------------------------\n/var/log/awslogs.log\n-------------------------------------\n{\'skipped_events_count\': 0, \'first_event\': {\'timestamp\': 1522962583519, \'start_position\': 559799L, \'end_position\': 560017L}, \'fallback_events_count\': 0, \'last_event\': {\'timestamp\': 1522962583519, \'start_position\': 559799L, \'end_position\': 560017L}, \'source_id\': \'77b026040b93055eb448bdc0b59e446f\', \'num_of_events\': 1, \'batch_size_in_bytes\': 243}\n\n\n\n-------------------------------------\n/var/log/httpd/error_log\n-------------------------------------\n[Thu Apr 05 19:54:23.624780 2018] [mpm_prefork:warn] [pid 3470] AH00167: long lost child came home! (pid 3088)\n\n\n\n-------------------------------------\n/var/log/httpd/access_log\n-------------------------------------\n172.31.69.153 (94.208.192.103) - - [05/Apr/2018:20:57:55 +0000] "HEAD /pma/ HTTP/1.1" 404 - "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"\n\n\n\n-------------------------------------\n/var/log/eb-activity.log\n-------------------------------------\n  + chown -R webapp:webapp /var/app/ondeck\n[2018-04-05T19:54:21.630Z] INFO  [3555]  - [Application update app-180406_044630@3/AppDeployStage0/AppDeployPreHook/02_setup_envvars.sh] : Starting activity...\n\n\n-------------------------------------\n/tmp/sample-app.log\n-------------------------------------\n2018-04-05 20:52:51 Received message: \\xe2\\x96\\x88\\xe2\n\n\n\n-------------------------------------\n/var/log/eb-commandprocessor.log\n-------------------------------------\n[2018-04-05T19:45:05.526Z] INFO  [2853]  : Running 2 of 2 actions: AppDeployPostHook...',
                        '============= i-090689581e5afcfc6 =============={linesep}-------------------------------------\n/var/log/awslogs.log\n-------------------------------------\n{\'skipped_events_count\': 0, \'first_event\': {\'timestamp\': 1522962583519, \'start_position\': 559799L, \'end_position\': 560017L}, \'fallback_events_count\': 0, \'last_event\': {\'timestamp\': 1522962583519, \'start_position\': 559799L, \'end_position\': 560017L}, \'source_id\': \'77b026040b93055eb448bdc0b59e446f\', \'num_of_events\': 1, \'batch_size_in_bytes\': 243}\n\n\n\n-------------------------------------\n/var/log/httpd/error_log\n-------------------------------------\n[Thu Apr 05 19:54:23.624780 2018] [mpm_prefork:warn] [pid 3470] AH00167: long lost child came home! (pid 3088)\n\n\n\n-------------------------------------\n/var/log/httpd/access_log\n-------------------------------------\n172.31.69.153 (94.208.192.103) - - [05/Apr/2018:20:57:55 +0000] "HEAD /pma/ HTTP/1.1" 404 - "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"\n\n\n\n-------------------------------------\n/var/log/eb-activity.log\n-------------------------------------\n  + chown -R webapp:webapp /var/app/ondeck\n[2018-04-05T19:54:21.630Z] INFO  [3555]  - [Application update app-180406_044630@3/AppDeployStage0/AppDeployPreHook/02_setup_envvars.sh] : Starting activity...\n\n\n-------------------------------------\n/tmp/sample-app.log\n-------------------------------------\n2018-04-05 20:52:51 Received message: \\xe2\\x96\\x88\\xe2\n\n\n\n-------------------------------------\n/var/log/eb-commandprocessor.log\n-------------------------------------\n[2018-04-05T19:45:05.526Z] INFO  [2853]  : Running 2 of 2 actions: AppDeployPostHook...',
                    ]
                ).replace('{linesep}', os.linesep)
            )


class TestSetupLogs(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.getcwd()
        if os.path.isdir('testDir'):
            shutil.rmtree('testDir')

        os.mkdir('testDir')
        os.chdir('testDir')

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

    @mock.patch('ebcli.operations.logsops.utils.save_file_from_url')
    @mock.patch('ebcli.operations.logsops.fileoperations.delete_file')
    @mock.patch('ebcli.operations.logsops.fileoperations.unzip_folder')
    def test_download_logs_for_all_instances(
            self,
            unzip_folder_mock,
            delete_file_mock,
            save_file_from_url_mock
    ):
        save_file_from_url_mock.return_value = os.path.join('testDir', '.elasticbeanstalk', 'logs', '180404_044924', 'logs.zip')

        logsops._download_logs_for_all_instances(
            instance_id_list={
                'i-090689581e5afcfc6': 'https://elasticbeanstalk-us-east-1-1231231231234.s3.amazonaws.com/resources/environments/logs/tail/e-spfgk5xbd',
                'i-053efe7c102d0a540': 'https://elasticbeanstalk-us-east-1-1231231231234.s3.amazonaws.com/resources/environments/logs/tail/e-spfgk5xbd'
            },
            logs_location=os.path.join('testDir', '.elasticbeanstalk', 'logs', '180404_044924')
        )

        unzip_folder_mock.assert_has_calls(
            [
                mock.call(
                    os.path.join('testDir', '.elasticbeanstalk', 'logs', '180404_044924', 'logs.zip'),
                    os.path.join('testDir', '.elasticbeanstalk', 'logs', '180404_044924', 'i-090689581e5afcfc6')
                ),
                mock.call(
                    os.path.join('testDir', '.elasticbeanstalk', 'logs', '180404_044924', 'logs.zip'),
                    os.path.join('testDir', '.elasticbeanstalk', 'logs', '180404_044924', 'i-053efe7c102d0a540')
                )
            ],
            any_order=True
        )

        delete_file_mock.assert_has_calls(
            [
                mock.call(
                    os.path.join('testDir', '.elasticbeanstalk', 'logs', '180404_044924', 'logs.zip')
                ),
                mock.call(
                    os.path.join('testDir', '.elasticbeanstalk', 'logs', '180404_044924', 'logs.zip')
                )
            ]
        )

    @mock.patch('ebcli.operations.logsops.fileoperations.delete_directory')
    @mock.patch('ebcli.operations.logsops.fileoperations.zip_up_folder')
    @mock.patch('ebcli.operations.logsops.fileoperations.set_user_only_permissions')
    def test_handle_log_zipping(
            self,
            set_user_only_permissions_mock,
            zip_up_folder_mock,
            delete_directory_mock
    ):
        logsops._handle_log_zipping(
            logs_location=os.path.join('testDir', '.elasticbeanstalk', 'logs', '180404_044924')
        )

        zip_up_folder_mock.assert_called_once_with(
            os.path.join('testDir', '.elasticbeanstalk', 'logs', '180404_044924'),
            os.path.join('testDir', '.elasticbeanstalk', 'logs', '180404_044924.zip')
        )
        delete_directory_mock.assert_called_once_with(os.path.join('testDir', '.elasticbeanstalk', 'logs', '180404_044924'))
        set_user_only_permissions_mock.assert_called_once_with(os.path.join('testDir', '.elasticbeanstalk', 'logs', '180404_044924.zip'))

    @mock.patch('ebcli.operations.logsops.fileoperations.set_user_only_permissions')
    @mock.patch('ebcli.operations.logsops.fileoperations.get_logs_location')
    @mock.patch('ebcli.operations.logsops._timestamped_directory_name')
    @mock.patch('ebcli.operations.logsops._download_logs_for_all_instances')
    @mock.patch('ebcli.operations.logsops._handle_log_zipping')
    @mock.patch('ebcli.operations.logsops._attempt_update_symlink_to_latest_logs_retrieved')
    def test_handle_bundle_logs__without_zipping(
            self,
            attempt_update_of_symlink_to_latest_logs_mock,
            handle_log_zipping_mock,
            download_logs_for_all_instances_mock,
            _timestamped_directory_name_mock,
            get_logs_location_mock,
            set_user_only_permissions_mock
    ):
        os.mkdir('.elasticbeanstalk')
        os.mkdir(os.path.join('.elasticbeanstalk', 'logs'))

        instance_id_list = {
            'i-090689581e5afcfc6': 'https://elasticbeanstalk-us-east-1-1231231231234.s3.amazonaws.com/resources/environments/logs/tail/e-spfgk5xbd',
            'i-053efe7c102d0a540': 'https://elasticbeanstalk-us-east-1-1231231231234.s3.amazonaws.com/resources/environments/logs/tail/e-spfgk5xbd'
        }
        logs_location = os.path.join('.elasticbeanstalk', 'logs', '180404_044924')
        _timestamped_directory_name_mock.return_value = '180404_044924'
        get_logs_location_mock.return_value = logs_location

        logsops._handle_bundle_logs(instance_id_list, do_zip=False)

        get_logs_location_mock.assert_called_with('180404_044924')
        download_logs_for_all_instances_mock.assert_called_with(
            instance_id_list,
            logs_location
        )
        set_user_only_permissions_mock.assert_called_once_with(logs_location)

        attempt_update_of_symlink_to_latest_logs_mock.assert_called_once_with(logs_location)
        handle_log_zipping_mock.assert_not_called()

    @mock.patch('ebcli.operations.logsops.fileoperations.set_user_only_permissions')
    @mock.patch('ebcli.operations.logsops.fileoperations.get_logs_location')
    @mock.patch('ebcli.operations.logsops._timestamped_directory_name')
    @mock.patch('ebcli.operations.logsops._download_logs_for_all_instances')
    @mock.patch('ebcli.operations.logsops._handle_log_zipping')
    @mock.patch('ebcli.operations.logsops._attempt_update_symlink_to_latest_logs_retrieved')
    def test_handle_bundle_logs__with_zipping(
            self,
            attempt_update_of_symlink_to_latest_logs_mock,
            handle_log_zipping_mock,
            download_logs_for_all_instances_mock,
            _timestamped_directory_name_mock,
            get_logs_location_mock,
            set_user_only_permissions_mock
    ):
        os.mkdir('.elasticbeanstalk')
        os.mkdir(os.path.join('.elasticbeanstalk', 'logs'))

        instance_id_list = {
            'i-090689581e5afcfc6': 'https://elasticbeanstalk-us-east-1-1231231231234.s3.amazonaws.com/resources/environments/logs/tail/e-spfgk5xbd',
            'i-053efe7c102d0a540': 'https://elasticbeanstalk-us-east-1-1231231231234.s3.amazonaws.com/resources/environments/logs/tail/e-spfgk5xbd'
        }
        logs_location = os.path.join('.elasticbeanstalk', 'logs', '180404_044924')
        _timestamped_directory_name_mock.return_value = '180404_044924'
        get_logs_location_mock.return_value = logs_location

        logsops._handle_bundle_logs(instance_id_list, do_zip=True)

        get_logs_location_mock.assert_called_with('180404_044924')
        download_logs_for_all_instances_mock.assert_called_with(
            instance_id_list,
            logs_location
        )
        set_user_only_permissions_mock.assert_called_once_with(logs_location)

        attempt_update_of_symlink_to_latest_logs_mock.assert_not_called()
        handle_log_zipping_mock.assert_called_once_with(logs_location)

    @mock.patch('ebcli.operations.logsops.elasticbeanstalk.retrieve_environment_info')
    def test_def_get_instance_id_list(
            self,
            get_instance_id_list_mock
    ):
        get_instance_id_list_mock.return_value = mock_logs.REQUEST_ENVIRONMENT_INFO_RESPONSE

        print(logsops.get_instance_log_url_mappings('some-env', 'tail'))
        self.assertEqual(
            {
                'i-024a31a441247971d': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com',
                'i-0dce0f6c5e2d5fa48': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com',
                'i-090689581e5afcfc6': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com',
                'i-053efe7c102d0a540': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com'
            },
            logsops.get_instance_log_url_mappings('some-env', 'tail')
        )

    @mock.patch('ebcli.operations.logsops.get_instance_log_url_mappings')
    @mock.patch('ebcli.operations.logsops._handle_bundle_logs')
    @mock.patch('ebcli.operations.logsops._handle_tail_logs')
    def test_get_logs__tailed_logs(
            self,
            handle_tail_logs_mock,
            handle_bundle_logs_mock,
            get_instance_id_list_mock
    ):
        get_instance_id_list_mock.return_value = {
            'i-024a31a441247971d': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com',
            'i-0dce0f6c5e2d5fa48': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com',
            'i-090689581e5afcfc6': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com',
            'i-053efe7c102d0a540': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com'
        }

        logsops.get_logs('my-env', 'tail')

        handle_tail_logs_mock.assert_called_once_with(get_instance_id_list_mock.return_value)
        handle_bundle_logs_mock.assert_not_called()

    @mock.patch('ebcli.operations.logsops.get_instance_log_url_mappings')
    @mock.patch('ebcli.operations.logsops._handle_bundle_logs')
    @mock.patch('ebcli.operations.logsops._handle_tail_logs')
    def test_get_logs__bundled_logs(
            self,
            handle_tail_logs_mock,
            handle_bundle_logs_mock,
            get_instance_id_list_mock
    ):
        get_instance_id_list_mock.return_value = {
            'i-024a31a441247971d': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com',
            'i-0dce0f6c5e2d5fa48': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com',
            'i-090689581e5afcfc6': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com',
            'i-053efe7c102d0a540': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com'
        }

        logsops.get_logs('my-env', 'bundle')

        handle_tail_logs_mock.assert_not_called()
        handle_bundle_logs_mock.assert_called_once_with(get_instance_id_list_mock.return_value, False)

    @mock.patch('ebcli.operations.logsops.get_instance_log_url_mappings')
    @mock.patch('ebcli.operations.logsops._handle_bundle_logs')
    @mock.patch('ebcli.operations.logsops._handle_tail_logs')
    def test_get_logs__tailed_logs__specific_instance(
            self,
            handle_tail_logs_mock,
            handle_bundle_logs_mock,
            get_instance_id_list_mock
    ):
        get_instance_id_list_mock.return_value = {
            'i-024a31a441247971d': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com',
            'i-0dce0f6c5e2d5fa48': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com',
            'i-090689581e5afcfc6': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com',
            'i-053efe7c102d0a540': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com'
        }

        logsops.get_logs('my-env', 'tail', False, 'i-090689581e5afcfc6')

        handle_tail_logs_mock.assert_called_once_with(
            {
                'i-090689581e5afcfc6': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com'
            }
        )
        handle_bundle_logs_mock.assert_not_called()

    @mock.patch('ebcli.operations.logsops.get_instance_log_url_mappings')
    @mock.patch('ebcli.operations.logsops._handle_bundle_logs')
    @mock.patch('ebcli.operations.logsops._handle_tail_logs')
    def test_get_logs__bundled_logs__specific_instance(
            self,
            handle_tail_logs_mock,
            handle_bundle_logs_mock,
            get_instance_id_list_mock
    ):
        get_instance_id_list_mock.return_value = {
            'i-024a31a441247971d': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com',
            'i-0dce0f6c5e2d5fa48': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com',
            'i-090689581e5afcfc6': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com',
            'i-053efe7c102d0a540': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com'
        }

        logsops.get_logs('my-env', 'bundle', True, 'i-090689581e5afcfc6')

        handle_tail_logs_mock.assert_not_called()
        handle_bundle_logs_mock.assert_called_once_with(
            {
                'i-090689581e5afcfc6': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com'
            },
            True
        )

    def test_updated_instance_id_list(self):
        with self.assertRaises(NotFoundError) as context_manager:
            logsops._updated_instance_id_list(
                {
                    'i-024a31a441247971d': 'https://elasticbeanstalk-us-east-1-123123123123.s3.amazonaws.com',
                },
                'i-123123a455ef666'
            )

        self.assertEqual(
            """Can't find instance "i-123123a455ef666" in the environment's instance logs on CloudWatch Logs.""",
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.logsops.cloudwatch.log_group_exists')
    @mock.patch('ebcli.operations.logsops._wait_to_poll_cloudwatch')
    def test_wait_for_log_group_to_come_into_existence(
            self,
            _wait_to_poll_cloudwatch_mock,
            log_group_exists_mock
    ):
        log_group_exists_mock.side_effect = [
            False,
            False,
            True
        ]

        logsops.wait_for_log_group_to_come_into_existence('my-log-group')

        _wait_to_poll_cloudwatch_mock.assert_has_calls(
            [
                mock.call(10),
                mock.call(10)
            ]
        )

    @mock.patch('ebcli.operations.logsops.wait_for_log_group_to_come_into_existence')
    @mock.patch('ebcli.operations.logsops.stream_single_stream')
    def test_stream_platform_logs(
            self,
            stream_single_stream_mock,
            wait_for_log_group_to_come_into_existence
    ):
        logsops.stream_platform_logs('my-platform', '1.0.0')

        stream_single_stream_mock.assert_called_once_with(
            '/aws/elasticbeanstalk/platform/my-platform',
            '1.0.0',
            4,
            None,
            None
        )
        wait_for_log_group_to_come_into_existence.assert_called_once_with(
            '/aws/elasticbeanstalk/platform/my-platform',
            4
        )
