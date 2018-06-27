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
import mock
from pytest_socket import enable_socket, disable_socket
import unittest

from ebcli.display.traditional import TraditionalHealthScreen
from ebcli.display.screen import Screen
from ebcli.operations import healthops
from ebcli.objects.platform import PlatformVersion


class TestHealthops(unittest.TestCase):
    def setUp(self):
        disable_socket()

    def tearDown(self):
        enable_socket()

    def test_create_traditional_health_table(self):
        screen = TraditionalHealthScreen()

        self.assertEqual(0, len(screen.tables))
        healthops.create_traditional_health_tables(screen)
        self.assertEqual(2, len(screen.tables))
        self.assertEqual(
            ['instance-id', 'EC2 Health', 'ELB State', 'ELB description'],
            [column.name for column in screen.tables[0].columns]
        )
        self.assertEqual(
            ['Key', 'Action'],
            [column.name for column in screen.tables[1].columns]
        )

    def test_create_health_tables__linux_platforms__no_healthd_2_support(self):
        platform = PlatformVersion(
            'arn:aws:elasticbeanstalk:us-west-1::platform/Tomcat 6 with Java 6 running on 32bit Amazon Linux/0.1.0'
        )
        screen = Screen()
        self.assertEqual(0, len(screen.tables))
        healthops.create_health_tables(screen, platform)
        self.assertEqual(4, len(screen.tables))

    def test_create_health_tables__linux(self):
        screen = Screen()
        platform = PlatformVersion(
            'arn:aws:elasticbeanstalk:us-west-2::platform/Go 1 running on 64bit Amazon Linux/2.7.0'
        )

        healthops.create_health_tables(screen, platform)
        self.assertEqual(5, len(screen.tables))
        self.assertEqual(
            ['instance-id', 'status', 'cause'],
            [column.name for column in screen.tables[0].columns]
        )
        self.assertEqual(
            [
                'instance-id',
                'r/sec',
                '%2xx',
                '%3xx',
                '%4xx',
                '%5xx',
                'p99 ',
                'p90 ',
                'p75',
                'p50',
                'p10'
            ],
            [column.name for column in screen.tables[1].columns]
        )

        self.assertEqual(
            [
                'instance-id',
                'type',
                'az',
                'running',
                'load 1',
                'load 5',
                'user %',
                'nice %',
                'system %',
                'idle %',
                'iowait %'
            ],
            [column.name for column in screen.tables[2].columns]
        )

        self.assertEqual(
            ['instance-id', 'status', 'id', 'version', 'ago'],
            [column.name for column in screen.tables[3].columns]
        )

    def test_create_health_tables__windows(self):
        screen = Screen()
        platform = PlatformVersion(
            'arn:aws:elasticbeanstalk:us-east-1::platform/IIS 10.0 running on 64bit Windows Server 2016/2.1.0'
        )

        healthops.create_health_tables(screen, platform)
        self.assertEqual(5, len(screen.tables))
        self.assertEqual(
            ['instance-id', 'status', 'cause'],
            [column.name for column in screen.tables[0].columns]
        )
        self.assertEqual(
            [
                'instance-id',
                'r/sec',
                '%2xx',
                '%3xx',
                '%4xx',
                '%5xx',
                'p99 ',
                'p90 ',
                'p75',
                'p50',
                'p10'
            ],
            [column.name for column in screen.tables[1].columns]
        )

        self.assertEqual(
            [
                'instance-id',
                'type',
                'az',
                'running',
                '% user time',
                '% privileged time',
                '% idle time'
            ],
            [column.name for column in screen.tables[2].columns]
        )

        self.assertEqual(
            ['instance-id', 'status', 'id', 'version', 'ago'],
            [column.name for column in screen.tables[3].columns]
        )

    @mock.patch('ebcli.operations.healthops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.operations.healthops.create_health_tables')
    @mock.patch('ebcli.operations.healthops.Screen')
    @mock.patch('ebcli.operations.healthops.term')
    @mock.patch('ebcli.operations.healthops.DataPoller')
    def test_display_interactive_health__enhanced_health(
            self,
            DataPoller_mock,
            term_mock,
            screen_mock,
            create_health_tables_mock,
            describe_configuration_settings_mock
    ):
        poller_mock = mock.MagicMock()
        DataPoller_mock.return_value = poller_mock
        screen_mock.return_value = healthops.Screen()
        describe_configuration_settings_mock.return_value = {
            'SolutionStackName': '64bit Amazon Linux 2018.03 v4.5.1 running Node.js',
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.1',
            'ApplicationName': 'vpc-tests',
            'Description': 'Environment created from the EB CLI using "eb create"',
            'EnvironmentName': 'vpc-tests-dev-single',
            'DeploymentStatus': 'deployed',
            'OptionSettings': [
                {
                    'Namespace': 'aws:elasticbeanstalk:healthreporting:system',
                    'OptionName': 'SystemType',
                    'Value': 'enhanced'
                },
            ]
        }

        healthops.display_interactive_health(
            'my-application',
            'environment-1',
            False,
            False,
            None
        )

        create_health_tables_mock.assert_called_once()
        screen_mock.return_value.start_screen.assert_called_once()

    @mock.patch('ebcli.operations.healthops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.operations.healthops.create_traditional_health_tables')
    @mock.patch('ebcli.operations.healthops.TraditionalHealthScreen')
    @mock.patch('ebcli.operations.healthops.term')
    @mock.patch('ebcli.operations.healthops.TraditionalHealthDataPoller')
    def test_display_interactive_health__basic_health(
            self,
            TraditionalHealthDataPoller_mock,
            term_mock,
            screen_mock,
            create_traditional_health_tables_mock,
            describe_configuration_settings_mock
    ):
        poller_mock = mock.MagicMock()
        TraditionalHealthDataPoller_mock.return_value = poller_mock
        screen_mock.return_value = healthops.TraditionalHealthScreen()
        describe_configuration_settings_mock.return_value = {
            'SolutionStackName': '64bit Amazon Linux 2018.03 v4.5.1 running Node.js',
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.1',
            'ApplicationName': 'vpc-tests',
            'Description': 'Environment created from the EB CLI using "eb create"',
            'EnvironmentName': 'vpc-tests-dev-single',
            'DeploymentStatus': 'deployed',
            'OptionSettings': [
                {
                    'Namespace': 'aws:elasticbeanstalk:healthreporting:system',
                    'OptionName': 'SystemType',
                    'Value': 'basic'
                },
            ],
            'Tier': {
                'Name': 'WebServer'
            }
        }

        healthops.display_interactive_health(
            'my-application',
            'environment-1',
            False,
            False,
            None
        )

        create_traditional_health_tables_mock.assert_called_once()
        screen_mock.return_value.start_screen.assert_called_once()
        poller_mock.start_background_polling.assert_called_once()

    @mock.patch('ebcli.operations.healthops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.operations.healthops.create_traditional_health_tables')
    @mock.patch('ebcli.operations.healthops.TraditionalHealthScreen')
    @mock.patch('ebcli.operations.healthops.term')
    @mock.patch('ebcli.operations.healthops.TraditionalHealthDataPoller')
    def test_display_interactive_health__basic_health__worker_tier(
            self,
            TraditionalHealthDataPoller_mock,
            term_mock,
            screen_mock,
            create_traditional_health_tables_mock,
            describe_configuration_settings_mock
    ):
        poller_mock = mock.MagicMock()
        TraditionalHealthDataPoller_mock.return_value = poller_mock
        screen_mock.return_value = healthops.TraditionalHealthScreen()
        describe_configuration_settings_mock.return_value = {
            'SolutionStackName': '64bit Amazon Linux 2018.03 v4.5.1 running Node.js',
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.1',
            'ApplicationName': 'vpc-tests',
            'Description': 'Environment created from the EB CLI using "eb create"',
            'EnvironmentName': 'vpc-tests-dev-single',
            'DeploymentStatus': 'deployed',
            'OptionSettings': [
                {
                    'Namespace': 'aws:elasticbeanstalk:healthreporting:system',
                    'OptionName': 'SystemType',
                    'Value': 'basic'
                },
            ],
            'Tier': {
                'Name': 'Worker'
            }
        }

        with self.assertRaises(healthops.NotSupportedError) as context_manager:
            healthops.display_interactive_health(
                'my-application',
                'environment-1',
                False,
                False,
                None
            )

        self.assertEqual(
            'The health dashboard is currently not supported for this environment.',
            str(context_manager.exception)
        )
        create_traditional_health_tables_mock.assert_not_called()
        screen_mock.return_value.start_screen.assert_not_called()
        poller_mock.start_background_polling.assert_not_called()
