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

import unittest
import mock

from ebcli.core import fileoperations
from ebcli.objects.environment import Environment
from ebcli.operations import terminateops

from .. import mock_responses


class TestTerminateOps(unittest.TestCase):
    def setUp(self):
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')

        os.chdir('testDir')
        open('.gitignore', 'w').close()

        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            '64bit Amazon Linux 2014.03 v1.0.6 running PHP 5.5'
        )

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

    def test_cleanup_ignore_file__sc_specified(self):
        fileoperations.write_config_setting('global', 'sc', 'git')

        terminateops.cleanup_ignore_file()

        self.assertIsNone(fileoperations.get_config_setting('global', 'sc'))

    def test_cleanup_ignore_file__sc_not_specified(self):
        fileoperations.write_config_setting('global', 'sc', None)

        terminateops.cleanup_ignore_file()

        self.assertIsNone(fileoperations.get_config_setting('global', 'sc'))

    @mock.patch('ebcli.operations.terminateops.elasticbeanstalk.describe_application')
    @mock.patch('ebcli.operations.terminateops.elasticbeanstalk.get_environment_names')
    @mock.patch('ebcli.operations.terminateops.io.echo')
    @mock.patch('ebcli.operations.terminateops.io.validate_action')
    def test_ask_for_customer_confirmation_to_delete_all_application_resources(
            self,
            validate_action_mock,
            echo_mock,
            get_environment_names_mock,
            describe_application_mock
    ):
        describe_application_mock.return_value = mock_responses.DESCRIBE_APPLICATIONS_RESPONSE['Applications'][0]
        get_environment_names_mock.return_value = Environment.json_to_environment_objects_array(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments']
        )

        terminateops.ask_for_customer_confirmation_to_delete_all_application_resources(
            'my-application'
        )

        echo_mock.assert_called_once_with(
            """The application "my-application" and all its resources will be deleted.
This application currently has the following:
Running environments: 4
Configuration templates: 0
Application versions: 1
"""
        )

        validate_action_mock.assert_called_once_with(
            'To confirm, type the application name',
            'my-application'
        )

    @mock.patch('ebcli.operations.terminateops.elasticbeanstalk.get_application_versions')
    @mock.patch('ebcli.operations.terminateops.s3.delete_objects')
    def test_cleanup_application_versions(
            self,
            delete_objects_mock,
            get_application_versions_mock
    ):
        get_application_versions_mock.return_value = mock_responses.DESCRIBE_APPLICATION_VERSIONS_RESPONSE

        terminateops.cleanup_application_versions('my-applicaiton')

        delete_objects_mock_calls = [
            mock.call(
                'elasticbeanstalk-us-west-2-123123123123',
                [
                    'my-app/9112-stage-150723_224258.war',
                    'my-app/9111-stage-150723_222618.war'
                ]
            )
        ]
        delete_objects_mock.assert_has_calls(delete_objects_mock_calls)

    @mock.patch('ebcli.operations.terminateops.elasticbeanstalk.get_application_versions')
    @mock.patch('ebcli.operations.terminateops.s3.delete_objects')
    def test_cleanup_application_versions__no_app_versions(
            self,
            delete_objects_mock,
            get_application_versions_mock
    ):
        get_application_versions_mock.return_value = {'ApplicationVersions': []}

        terminateops.cleanup_application_versions('my-applicaiton')

        delete_objects_mock.assert_not_called()

    @mock.patch('ebcli.operations.terminateops.ask_for_customer_confirmation_to_delete_all_application_resources')
    @mock.patch('ebcli.operations.terminateops.cleanup_application_versions')
    @mock.patch('ebcli.operations.terminateops.elasticbeanstalk.delete_application_and_envs')
    @mock.patch('ebcli.operations.terminateops.commonops.wait_for_success_events')
    def test_delete_app__non_force_mode(
            self,
            wait_for_success_events_mock,
            delete_application_and_envs_mock,
            cleanup_application_versions_mock,
            ask_for_customer_confirmation_to_delete_all_application_resources_mock
    ):
        delete_application_and_envs_mock.return_value = 'some-request-id'

        terminateops.delete_app(
            'my-application',
            force=False,
            nohang=False,
            cleanup=True
        )

        ask_for_customer_confirmation_to_delete_all_application_resources_mock.assert_called_once_with('my-application')
        cleanup_application_versions_mock.assert_called_once_with('my-application')
        wait_for_success_events_mock.assert_called_once_with(
            'some-request-id',
            sleep_time=5,
            timeout_in_minutes=15
        )
        self.assertFalse(os.path.exists('.elasticbeanstalk'))

    @mock.patch('ebcli.operations.terminateops.ask_for_customer_confirmation_to_delete_all_application_resources')
    @mock.patch('ebcli.operations.terminateops.cleanup_application_versions')
    @mock.patch('ebcli.operations.terminateops.elasticbeanstalk.delete_application_and_envs')
    @mock.patch('ebcli.operations.terminateops.commonops.wait_for_success_events')
    def test_delete_app__force_mode(
            self,
            wait_for_success_events_mock,
            delete_application_and_envs_mock,
            cleanup_application_versions_mock,
            ask_for_customer_confirmation_to_delete_all_application_resources_mock
    ):
        delete_application_and_envs_mock.return_value = 'some-request-id'

        terminateops.delete_app(
            'my-application',
            force=True,
            nohang=False,
            cleanup=True
        )

        ask_for_customer_confirmation_to_delete_all_application_resources_mock.assert_not_called()
        cleanup_application_versions_mock.assert_called_once_with('my-application')
        wait_for_success_events_mock.assert_called_once_with(
            'some-request-id',
            sleep_time=5,
            timeout_in_minutes=15
        )
        self.assertFalse(os.path.exists('.elasticbeanstalk'))

    @mock.patch('ebcli.operations.terminateops.cleanup_application_versions')
    @mock.patch('ebcli.operations.terminateops.elasticbeanstalk.delete_application_and_envs')
    @mock.patch('ebcli.operations.terminateops.commonops.wait_for_success_events')
    def test_delete_app__local_directory_cleanup_not_requested(
            self,
            wait_for_success_events_mock,
            delete_application_and_envs_mock,
            cleanup_application_versions_mock
    ):
        delete_application_and_envs_mock.return_value = 'some-request-id'

        terminateops.delete_app(
            'my-application',
            force=True,
            nohang=False,
            cleanup=False
        )

        cleanup_application_versions_mock.assert_called_once_with('my-application')
        wait_for_success_events_mock.assert_called_once_with(
            'some-request-id',
            sleep_time=5,
            timeout_in_minutes=15
        )
        self.assertTrue(os.path.exists('.elasticbeanstalk'))

    @mock.patch('ebcli.operations.terminateops.cleanup_application_versions')
    @mock.patch('ebcli.operations.terminateops.elasticbeanstalk.delete_application_and_envs')
    @mock.patch('ebcli.operations.terminateops.commonops.wait_for_success_events')
    def test_delete_app__terminate_events_not_requested_to_be_followed(
            self,
            wait_for_success_events_mock,
            delete_application_and_envs_mock,
            cleanup_application_versions_mock
    ):
        delete_application_and_envs_mock.return_value = 'some-request-id'

        terminateops.delete_app(
            'my-application',
            force=True,
            nohang=True,
            cleanup=False
        )

        cleanup_application_versions_mock.assert_called_once_with('my-application')
        wait_for_success_events_mock.assert_not_called()

    def test_dissociate_environment_from_branch(self):
        fileoperations.write_config_setting(
            'branch-defaults',
            'default',
            {
                'environment': 'my-environment'
            }
        )

        terminateops.dissociate_environment_from_branch('my-environment')

        self.assertIsNotNone(fileoperations.get_config_setting('branch-defaults', 'default'))

    def test_dissociate_environment_from_branch__environment_is_not_default_env(self):
        fileoperations.write_config_setting(
            'branch-defaults',
            'default',
            {
                'environment': 'my-environment-2'
            }
        )

        terminateops.dissociate_environment_from_branch('my-environment')

        self.assertEqual(
            {
                'environment': 'my-environment-2'
            },
            fileoperations.get_config_setting('branch-defaults', 'default')
        )

    @mock.patch('ebcli.operations.terminateops.elasticbeanstalk.terminate_environment')
    @mock.patch('ebcli.operations.terminateops.commonops.wait_for_success_events')
    def test_terminate(
            self,
            wait_for_success_events_mock,
            terminate_environment_mock,
    ):
        terminate_environment_mock.return_value = 'some-request-id'

        terminateops.terminate('my-environment')

        wait_for_success_events_mock.assert_called_once_with(
            'some-request-id',
            timeout_in_minutes=15
        )

    @mock.patch('ebcli.operations.terminateops.elasticbeanstalk.terminate_environment')
    @mock.patch('ebcli.operations.terminateops.commonops.wait_for_success_events')
    def test_terminate__nohang(
            self,
            wait_for_success_events_mock,
            terminate_environment_mock,
    ):
        terminate_environment_mock.side_effect = None

        terminateops.terminate('my-environment', nohang=True)

        wait_for_success_events_mock.assert_not_called()

    @mock.patch('ebcli.operations.terminateops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.operations.terminateops.elasticbeanstalk.get_specific_configuration')
    def test_is_shared_load_balancer__shared_application_load_balancer(
        self,
        get_specific_configuration_mock,
        describe_configuration_settings_mock,
    ):
        namespace = 'aws:elasticbeanstalk:environment'
        load_balancer_is_shared = 'LoadBalancerIsShared'
        load_balancer_type = 'LoadBalancerType'
        app_name = 'my-application'
        env_name = 'my-environment'
        env_config = [
                {
                    'Namespace': 'aws:elasticbeanstalk:environment',
                    'OptionName': 'LoadBalancerType',
                    'Value': 'application',
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:environment',
                    'OptionName': 'LoadBalancerIsShared',
                    'Value': 'true'
                },
            ]
        expected_result = True

        describe_configuration_settings_mock.return_value = env_config
        get_specific_configuration_mock.side_effect = ['application', 'true']

        result = terminateops.is_shared_load_balancer(app_name, env_name)

        describe_configuration_settings_mock.assert_called_once_with(app_name, env_name)
        get_specific_configuration_mock.assert_has_calls(
            [
                mock.call(
                    env_config, namespace, load_balancer_type
                ),
                mock.call(
                    env_config, namespace, load_balancer_is_shared
                ),

            ],
            any_order=True
        )

        self.assertEqual(
            result,
            expected_result
        )

    @mock.patch('ebcli.operations.terminateops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.operations.terminateops.elasticbeanstalk.get_specific_configuration')
    def test_is_shared_load_balancer__application_load_balancer(
        self,
        get_specific_configuration_mock,
        describe_configuration_settings_mock,
    ):
        namespace = 'aws:elasticbeanstalk:environment'
        load_balancer_is_shared = 'LoadBalancerIsShared'
        load_balancer_type = 'LoadBalancerType'
        app_name = 'my-application'
        env_name = 'my-environment-2'
        env_config = [
                {
                    'Namespace': 'aws:elasticbeanstalk:environment',
                    'OptionName': 'LoadBalancerType',
                    'Value': 'application',
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:environment',
                    'OptionName': 'LoadBalancerIsShared',
                    'Value': 'false'
                },
            ]
        expected_result = False

        describe_configuration_settings_mock.return_value = env_config
        get_specific_configuration_mock.side_effect = ['application', 'false']

        result = terminateops.is_shared_load_balancer(app_name, env_name)

        describe_configuration_settings_mock.assert_called_once_with(app_name, env_name)
        get_specific_configuration_mock.assert_has_calls(
            [
                mock.call(
                    env_config, namespace, load_balancer_type
                ),
                mock.call(
                    env_config, namespace, load_balancer_is_shared
                ),

            ],
            any_order=True
        )

        self.assertEqual(
            result,
            expected_result
        )

    @mock.patch('ebcli.operations.terminateops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.operations.terminateops.elasticbeanstalk.get_specific_configuration')
    def test_is_shared_load_balancer__classic_load_balancer(
        self,
        get_specific_configuration_mock,
        describe_configuration_settings_mock,
    ):
        namespace = 'aws:elasticbeanstalk:environment'
        load_balancer_is_shared = 'LoadBalancerIsShared'
        load_balancer_type = 'LoadBalancerType'
        app_name = 'my-application'
        env_name = 'my-environment-3'
        env_config = [
                {
                    'Namespace': 'aws:elasticbeanstalk:environment',
                    'OptionName': 'LoadBalancerType',
                    'Value': 'classic',
                }
            ]
        expected_result = False
        describe_configuration_settings_mock.return_value = env_config
        get_specific_configuration_mock.return_value = 'classic'

        result = terminateops.is_shared_load_balancer(app_name, env_name)

        describe_configuration_settings_mock.assert_called_once_with(app_name, env_name)
        get_specific_configuration_mock.assert_called_once_with(env_config, namespace, load_balancer_type)

        self.assertEqual(
            result,
            expected_result
        )
