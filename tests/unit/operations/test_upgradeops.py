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

import mock
import unittest

from ebcli.operations import upgradeops
from ebcli.objects.platform import PlatformVersion
from ebcli.objects.environment import Environment


class TestUpgradeOps(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')
        os.chdir('testDir')

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

    def test__get_warning_message__confirm(self):
        self.assertIsNone(
            upgradeops._get_warning_message(
                confirm=True,
                single=False,
                rolling_enabled=False,
                webserver=False,
                noroll=False
            )
        )

    def test__get_warning_message__single_instance(self):
        self.assertEqual(
            'This operation causes application downtime while Elastic Beanstalk '
            'replaces the instance.',
            upgradeops._get_warning_message(
                confirm=False,
                single=True,
                rolling_enabled=False,
                webserver=False,
                noroll=False
            )
        )

    def test__get_warning_message__not_rolling_enabled__noroll_set(self):
        self.assertEqual(
            'This operation causes application downtime while Elastic Beanstalk '
            'replaces your instances.',
            upgradeops._get_warning_message(
                confirm=False,
                single=False,
                rolling_enabled=False,
                webserver=False,
                noroll=True
            )
        )

    def test__get_warning_message__rolling_enabled(self):
        self.assertEqual(
            'This operation replaces your instances with minimal or zero downtime. '
            'You may cancel the upgrade after it has started by typing "eb abort".',
            upgradeops._get_warning_message(
                confirm=False,
                single=False,
                rolling_enabled=True,
                webserver=False,
                noroll=False
            )
        )

    def test__get_warning_message__not_rolling_enabled__noroll_not_specified__webserver_environment(self):
        self.assertEqual(
            'Elastic Beanstalk will enable Health-based rolling updates to avoid '
            'application downtime while it replaces your instances. You may cancel '
            'the upgrade after it has started by typing "eb abort". To upgrade '
            'without rolling updates, type "eb upgrade --noroll".',
            upgradeops._get_warning_message(
                confirm=False,
                single=False,
                rolling_enabled=False,
                webserver=True,
                noroll=False
            )
        )

    def test__get_warning_message__not_rolling_enabled__noroll_not_specified__non_webserver_environment(self):
        self.assertEqual(
            'Elastic Beanstalk will enable Time-based rolling updates to avoid '
            'application downtime while it replaces your instances. You may cancel '
            'the upgrade after it has started by typing "eb abort". To upgrade '
            'without rolling updates, type "eb upgrade --noroll".',
            upgradeops._get_warning_message(
                confirm=False,
                single=False,
                rolling_enabled=False,
                webserver=False,
                noroll=False
            )
        )

    def test__should_add_rolling__noroll_set(self):
        self.assertFalse(upgradeops._should_add_rolling(single=False, rolling_enabled=False, noroll=True))

    def test__should_add_rolling__single_environment(self):
        self.assertFalse(upgradeops._should_add_rolling(single=True, rolling_enabled=False, noroll=False))

    def test__should_add_rolling__rolling_enabled(self):
        self.assertFalse(upgradeops._should_add_rolling(single=False, rolling_enabled=True, noroll=False))

    def test__should_add_rolling(self):
        self.assertTrue(upgradeops._should_add_rolling(single=False, rolling_enabled=False, noroll=False))

    @mock.patch('ebcli.operations.upgradeops.elasticbeanstalk.get_environment_settings')
    @mock.patch('ebcli.operations.upgradeops.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.upgradeops.io.echo')
    @mock.patch('ebcli.operations.upgradeops.io.validate_action')
    @mock.patch('ebcli.operations.upgradeops.io.log_warning')
    @mock.patch('ebcli.operations.upgradeops._get_warning_message')
    @mock.patch('ebcli.operations.upgradeops._should_add_rolling')
    @mock.patch('ebcli.operations.upgradeops.do_upgrade')
    def test_upgrade_env__load_balanced_webserver_environment__rolling_update_not_enabled(
            self,
            do_upgrade_mock,
            _should_add_rolling_mock,
            _get_warning_message_mock,
            log_warning_mock,
            validate_action_mock,
            echo_mock,
            find_solution_stack_from_string_mock,
            get_environment_settings_mock
    ):
        find_solution_stack_from_string_mock.return_value = PlatformVersion(
            'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js '
            'running on 64bit Amazon Linux/4.5.2'
        )

        describe_configuration_settings_response = {
            'ConfigurationSettings': [
                {
                    'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.1',
                    'SolutionStackName': '64bit Amazon Linux 2017.09 v4.5.1 running Node.js',
                    'EnvironmentName': 'my-environment',
                    'Tier': {
                        'Type': 'Standard',
                        'Name': 'WebServer',
                        'Version': '1.0'
                    },
                    'OptionSettings': [
                        {
                            'ResourceName': 'AWSEBAutoScalingGroup',
                            'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
                            'OptionName': 'RollingUpdateEnabled',
                            'Value': 'false'
                        }
                    ]
                }
            ]
        }
        get_environment_settings_mock.return_value = Environment.json_to_environment_object(
            describe_configuration_settings_response['ConfigurationSettings'][0]
        )
        _get_warning_message_mock.return_value = 'some warning message'
        _should_add_rolling_mock.return_value = True

        upgradeops.upgrade_env('my-application', 'my-environment', 10, False, False)

        get_environment_settings_mock.assert_called_once_with('my-application', 'my-environment')
        echo_mock.assert_has_calls(
            [
                mock.call(),
                mock.call('The environment "my-environment" will be updated to use the most recent platform version.'),
                mock.call(
                    'Current platform:',
                    PlatformVersion(
                        'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.1'
                    )
                ),
                mock.call(
                    'Latest platform: ',
                    'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.2'
                ),
                mock.call(),
                mock.call('You can also change your platform version by typing "eb clone" and then "eb swap".'),
                mock.call()
            ]
        )
        _get_warning_message_mock.assert_called_once_with(False, False, False, True, False)
        log_warning_mock.assert_called_once_with('some warning message')
        validate_action_mock.assert_called_once_with('To continue, type the environment name', 'my-environment')
        _should_add_rolling_mock.assert_called_once_with(False, False, False)
        do_upgrade_mock.assert_called_once_with(
            'my-environment',
            True,
            10,
            'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.2',
            health_based=True,
            platform_arn='arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.2'
        )

    @mock.patch('ebcli.operations.upgradeops.elasticbeanstalk.get_environment_settings')
    @mock.patch('ebcli.operations.upgradeops.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.upgradeops.io.echo')
    @mock.patch('ebcli.operations.upgradeops.io.validate_action')
    @mock.patch('ebcli.operations.upgradeops.io.log_warning')
    @mock.patch('ebcli.operations.upgradeops._get_warning_message')
    @mock.patch('ebcli.operations.upgradeops._should_add_rolling')
    @mock.patch('ebcli.operations.upgradeops.do_upgrade')
    def test_upgrade_env__single_instance_webserver_environment__rolling_update_not_enabled(
            self,
            do_upgrade_mock,
            _should_add_rolling_mock,
            _get_warning_message_mock,
            log_warning_mock,
            validate_action_mock,
            echo_mock,
            find_solution_stack_from_string_mock,
            get_environment_settings_mock
    ):
        find_solution_stack_from_string_mock.return_value = PlatformVersion(
            'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js '
            'running on 64bit Amazon Linux/4.5.2'
        )

        describe_configuration_settings_response = {
            'ConfigurationSettings': [
                {
                    'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.1',
                    'SolutionStackName': '64bit Amazon Linux 2017.09 v4.5.1 running Node.js',
                    'EnvironmentName': 'my-environment',
                    'Tier': {
                        'Type': 'Standard',
                        'Name': 'WebServer',
                        'Version': '1.0'
                    },
                    'OptionSettings': [
                        {
                            'ResourceName': 'AWSEBAutoScalingGroup',
                            'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
                            'OptionName': 'RollingUpdateEnabled',
                            'Value': 'false'
                        },
                        {
                            'Namespace': 'aws:elasticbeanstalk:environment',
                            'OptionName': 'EnvironmentType',
                            'Value': 'SingleInstance'
                        }
                    ]
                }
            ]
        }
        get_environment_settings_mock.return_value = Environment.json_to_environment_object(
            describe_configuration_settings_response['ConfigurationSettings'][0]
        )
        _get_warning_message_mock.return_value = 'some warning message'
        _should_add_rolling_mock.return_value = False

        upgradeops.upgrade_env('my-application', 'my-environment', 10, False, False)

        get_environment_settings_mock.assert_called_once_with('my-application', 'my-environment')
        echo_mock.assert_has_calls(
            [
                mock.call(),
                mock.call('The environment "my-environment" will be updated to use the most recent platform version.'),
                mock.call(
                    'Current platform:',
                    PlatformVersion(
                        'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.1'
                    )
                ),
                mock.call(
                    'Latest platform: ',
                    'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.2'
                ),
                mock.call(),
                mock.call('You can also change your platform version by typing "eb clone" and then "eb swap".'),
                mock.call()
            ]
        )
        _get_warning_message_mock.assert_called_once_with(False, True, False, True, False)
        log_warning_mock.assert_called_once_with('some warning message')
        validate_action_mock.assert_called_once_with('To continue, type the environment name', 'my-environment')
        _should_add_rolling_mock.assert_called_once_with(True, False, False)
        do_upgrade_mock.assert_called_once_with(
            'my-environment',
            False,
            10,
            'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.2',
            health_based=True,
            platform_arn='arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.2'
        )

    @mock.patch('ebcli.operations.upgradeops.elasticbeanstalk.get_environment_settings')
    @mock.patch('ebcli.operations.upgradeops.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.upgradeops.io.echo')
    @mock.patch('ebcli.operations.upgradeops.io.validate_action')
    @mock.patch('ebcli.operations.upgradeops.io.log_warning')
    @mock.patch('ebcli.operations.upgradeops._should_add_rolling')
    @mock.patch('ebcli.operations.upgradeops.do_upgrade')
    def test_upgrade_env__force_confirm(
            self,
            do_upgrade_mock,
            _should_add_rolling_mock,
            log_warning_mock,
            validate_action_mock,
            echo_mock,
            find_solution_stack_from_string_mock,
            get_environment_settings_mock
    ):
        find_solution_stack_from_string_mock.return_value = PlatformVersion(
            'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js '
            'running on 64bit Amazon Linux/4.5.2'
        )

        describe_configuration_settings_response = {
            'ConfigurationSettings': [
                {
                    'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.1',
                    'SolutionStackName': '64bit Amazon Linux 2017.09 v4.5.1 running Node.js',
                    'EnvironmentName': 'my-environment',
                    'Tier': {
                        'Type': 'Standard',
                        'Name': 'WebServer',
                        'Version': '1.0'
                    },
                    'OptionSettings': [
                        {
                            'ResourceName': 'AWSEBAutoScalingGroup',
                            'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
                            'OptionName': 'RollingUpdateEnabled',
                            'Value': 'false'
                        }
                    ]
                }
            ]
        }
        get_environment_settings_mock.return_value = Environment.json_to_environment_object(
            describe_configuration_settings_response['ConfigurationSettings'][0]
        )
        _should_add_rolling_mock.return_value = True

        upgradeops.upgrade_env('my-application', 'my-environment', 10, True, False)

        get_environment_settings_mock.assert_called_once_with('my-application', 'my-environment')
        echo_mock.assert_has_calls(
            [
                mock.call(),
                mock.call('The environment "my-environment" will be updated to use the most recent platform version.'),
                mock.call(
                    'Current platform:',
                    PlatformVersion(
                        'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.1'
                    )
                ),
                mock.call(
                    'Latest platform: ',
                    'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.2'
                ),
                mock.call()
            ]
        )
        validate_action_mock.assert_not_called()
        _should_add_rolling_mock.assert_called_once_with(False, False, False)
        do_upgrade_mock.assert_called_once_with(
            'my-environment',
            True,
            10,
            'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.2',
            health_based=True,
            platform_arn='arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.2'
        )

    @mock.patch('ebcli.operations.upgradeops.elasticbeanstalk.get_environment_settings')
    @mock.patch('ebcli.operations.upgradeops.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.upgradeops.io.echo')
    @mock.patch('ebcli.operations.upgradeops.do_upgrade')
    def test_upgrade_env__using_latest_paltform(
            self,
            do_upgrade_mock,
            echo_mock,
            find_solution_stack_from_string_mock,
            get_environment_settings_mock
    ):
        find_solution_stack_from_string_mock.return_value = PlatformVersion(
            'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js '
            'running on 64bit Amazon Linux/4.5.2'
        )

        describe_configuration_settings_response = {
            'ConfigurationSettings': [
                {
                    'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.2',
                    'SolutionStackName': '64bit Amazon Linux 2017.09 v4.5.2 running Node.js',
                    'EnvironmentName': 'my-environment',
                    'Tier': {
                        'Type': 'Standard',
                        'Name': 'WebServer',
                        'Version': '1.0'
                    }
                }
            ]
        }
        get_environment_settings_mock.return_value = Environment.json_to_environment_object(
            describe_configuration_settings_response['ConfigurationSettings'][0]
        )

        upgradeops.upgrade_env('my-application', 'my-environment', 10, True, False)

        get_environment_settings_mock.assert_called_once_with('my-application', 'my-environment')
        echo_mock.assert_called_once_with('Environment already on most recent platform version.')
        do_upgrade_mock.assert_not_called()

    @mock.patch('ebcli.operations.upgradeops.commonops.update_environment')
    @mock.patch('ebcli.operations.upgradeops.io.log_warning')
    def test_do_upgrade__add_rolling(
            self,
            log_warning_mock,
            update_environment_mock
    ):
        upgradeops.do_upgrade(
            'my-environment',
            True,
            10,
            'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.2',
            health_based=True,
            platform_arn='arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.2'
        )

        update_environment_mock.assert_called_once_with(
            'my-environment',
            [
                {
                    'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
                    'OptionName': 'RollingUpdateEnabled',
                    'Value': 'true'
                },
                {
                    'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
                    'OptionName': 'RollingUpdateType',
                    'Value': 'Health'
                }
            ],
            None,
            platform_arn='arn:aws:elasticbeanstalk:us-west-2::platform/Node.js '
                         'running on 64bit Amazon Linux/4.5.2',
            timeout=10
        )
        log_warning_mock.assert_called_once_with(
            'Enabling Health-based rolling updates to environment.'
        )

    @mock.patch('ebcli.operations.upgradeops.commonops.update_environment')
    @mock.patch('ebcli.operations.upgradeops.io.log_warning')
    def test_do_upgrade__update_environment_with_solution_stack(
            self,
            log_warning_mock,
            update_environment_mock
    ):
        upgradeops.do_upgrade(
            'my-environment',
            True,
            10,
            '64bit Amazon Linux 2017.09 v4.5.2 running Node.js',
            health_based=True,
            platform_arn=''
        )

        update_environment_mock.assert_called_once_with(
            'my-environment',
            [
                {
                    'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
                    'OptionName': 'RollingUpdateEnabled',
                    'Value': 'true'
                },
                {
                    'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
                    'OptionName': 'RollingUpdateType',
                    'Value': 'Health'
                }
            ],
            None,
            solution_stack_name='64bit Amazon Linux 2017.09 v4.5.2 running Node.js',
            timeout=10
        )
        log_warning_mock.assert_called_once_with(
            'Enabling Health-based rolling updates to environment.'
        )

    @mock.patch('ebcli.operations.upgradeops.commonops.update_environment')
    @mock.patch('ebcli.operations.upgradeops.io.log_warning')
    def test_do_upgrade__time_based_update(
            self,
            log_warning_mock,
            update_environment_mock
    ):
        upgradeops.do_upgrade(
            'my-environment',
            True,
            10,
            'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.2',
            health_based=False,
            platform_arn='arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.2'
        )

        update_environment_mock.assert_called_once_with(
            'my-environment',
            [
                {
                    'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
                    'OptionName': 'RollingUpdateEnabled',
                    'Value': 'true'
                },
                {
                    'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
                    'OptionName': 'RollingUpdateType',
                    'Value': 'Time'
                }
            ],
            None,
            platform_arn='arn:aws:elasticbeanstalk:us-west-2::platform/Node.js '
                         'running on 64bit Amazon Linux/4.5.2',
            timeout=10
        )
        log_warning_mock.assert_called_once_with(
            'Enabling Time-based rolling updates to environment.'
        )


    @mock.patch('ebcli.operations.upgradeops.commonops.update_environment')
    def test_do_upgrade__no_rolling_updates(
            self,
            update_environment_mock
    ):
        upgradeops.do_upgrade(
            'my-environment',
            False,
            10,
            'arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.2',
            health_based=True,
            platform_arn='arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.2'
        )

        update_environment_mock.assert_called_once_with(
            'my-environment',
            None,
            None,
            platform_arn='arn:aws:elasticbeanstalk:us-west-2::platform/Node.js running on 64bit Amazon Linux/4.5.2',
            timeout=10
        )
