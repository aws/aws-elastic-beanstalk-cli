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

from ebcli.core import fileoperations
from ebcli.core.ebcore import EB
from ebcli.objects.exceptions import InvalidOptionsError


class TestLogs(unittest.TestCase):
    APP_NAME = 'MyFooApp'
    ENV_NAME = 'MyFooEnv'
    SPECIFIED_LOG_GROUP = '/aws/elasticbeanstalk/foo/specific/error.log'

    def setUp(self):
        disable_socket()
        if os.path.exists('testDir'):
            shutil.rmtree('testDir')
        os.mkdir('testDir')
        self.root_dir = os.getcwd()
        os.chdir('testDir')
        self.patcher_base_get_app = mock.patch('ebcli.controllers.logs.AbstractBaseController.get_app_name')
        self.patcher_base_get_env = mock.patch('ebcli.controllers.logs.AbstractBaseController.get_env_name')
        self.mock_base_get_app = self.patcher_base_get_app.start()
        self.mock_base_get_env = self.patcher_base_get_env.start()
        self.mock_base_get_app.return_value = TestLogs.APP_NAME
        self.mock_base_get_env.return_value = TestLogs.ENV_NAME

        self.setup_application_workspace()

    def tearDown(self):
        enable_socket()
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')
        self.patcher_base_get_app.stop()
        self.patcher_base_get_env.stop()

    def setup_application_workspace(self):
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            'php-7.1',
            workspace_type='Application'
        )


class TestTrivialInvalidArgumentCombinations(TestLogs):
    def test_logs__invalid_options_combination__all_and_zip_cannot_be_used_together(self):
        self.app = EB(argv=['logs', '--all', '--zip'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            """You can't use the "--all" and "--zip" options together. They are two different ways to retrieve logs.""",
            str(context_manager.exception)
        )

    def test_logs__invalid_options_combination__all_and_instance_id_logs(self):
        # TODO: consider not making this an error
        self.app = EB(argv=['logs', '--all', '--instance', 'i-123456789'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            """You can't use "--instance" with "--all".""",
            str(context_manager.exception)
        )

    def test_logs__invalid_options_combination__cloudwatch_logs_and_instance(self):
        self.app = EB(argv=['logs', '--cloudwatch-logs', '--instance', 'i-someisntanceid'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            """You can't use the "--instance" option when setting log streaming. You can enable or disable instance log streaming for the entire environment and/or environment-health streaming.""",
            str(context_manager.exception)
        )

    def test_logs__invalid_options_combination__cloudwatch_logs_and_all(self):
        self.app = EB(argv=['logs', '--cloudwatch-logs', '--all'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            """You can't use the "--all" option when setting log streaming. This is an output option for log retrieval commands.""",
            str(context_manager.exception)
        )

    def test_logs__invalid_options_combination__cloudwatch_logs_and_zip(self):
        self.app = EB(argv=['logs', '--cloudwatch-logs', '--zip'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            """You can't use the "--zip" option when setting log streaming. This is an output option for log retrieval commands.""",
            str(context_manager.exception)
        )

    def test_logs__invalid_options_combination__cloudwatch_logs_and_log_group(self):
        self.app = EB(argv=['logs', '--cloudwatch-logs', '--log-group', 'some-log-group'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            """You can't use the "--log-group" option when setting log streaming. You can enable or disable all instance log group streaming and/or environment-health streaming.""",
            str(context_manager.exception)
        )

    def test_logs__invalid_options_combination__cloudwatch_logs_with_enable_option_and_log_group(self):
        self.app = EB(argv=['logs', '--cloudwatch-logs', 'enable', '--log-group', 'some-log-group'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            """You can't use the "--log-group" option when setting log streaming. You can enable or disable all instance log group streaming and/or environment-health streaming.""",
            str(context_manager.exception)
        )

    def test_logs__invalid_options_combination__cloudwatch_logs_with_disable_option_and_log_group(self):
        self.app = EB(argv=['logs', '--cloudwatch-logs', 'disable', '--log-group', 'some-log-group'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            """You can't use the "--log-group" option when setting log streaming. You can enable or disable all instance log group streaming and/or environment-health streaming.""",
            str(context_manager.exception)
        )

    def test_logs__invalid_options_combination__evironment_health_cloudwatch_log_source_with_log_group(self):
        self.app = EB(argv=['logs', '--cloudwatch-log-source', 'environment-health', '--log-group', 'some-log-source'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            """You can't use the "--log-group" option when retrieving environment-health logs. These logs are in a specific, implied log group.""",
            str(context_manager.exception)
        )

    def test_logs__invalid_options_combination__evironment_health_cloudwatch_log_source_with_instance(self):
        self.app = EB(argv=['logs', '--cloudwatch-log-source', 'environment-health', '--instance', 'i-1234567'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            """You can't use the "--instance" option when retrieving environment-health logs. The scope for these logs is the entire environment.""",
            str(context_manager.exception)
        )

    def test_logs__invalid_options_combination__all_cloudwatch_log_sources_with_stream(self):
        self.app = EB(argv=['logs', '--cloudwatch-log-source', 'all', '--stream'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            """Invalid CloudWatch Logs source type for setting log streaming: "{}". Valid types: instance | environment-health | all""",
            str(context_manager.exception)
        )

    def test_logs__all_cloudwatch_log_source_specified(self):
        self.app = EB(argv=['logs', '--cloudwatch-log-source', 'all'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            """Invalid CloudWatch Logs source type for retrieving logs: "{}". Valid types: instance | environment-health""",
            str(context_manager.exception)
        )

    def test_logs__invalid_cloudwatch_log_source_specified(self):
        self.app = EB(argv=['logs', '--cloudwatch-log-source', 'other-invalid-log-source'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            """Invalid CloudWatch Logs source type for setting log streaming: "{}". Valid types: instance | environment-health | all""",
            str(context_manager.exception)
        )


class TestGetLogsWithCloudWatchLogStreamingDisabled(TestLogs):
    @mock.patch('ebcli.controllers.logs.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.raise_if_instance_log_streaming_is_not_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.retrieve_cloudwatch_environment_health_logs')
    def test_logs__instance_cloudwatch_log_source_specified__cloudwatch_log_streaming_is_disabled(
            self,
            retrieve_cloudwatch_environment_health_logs_mock,
            raise_if_instance_log_streaming_is_not_enabled_mock,
            instance_log_streaming_enabled_mock
    ):
        instance_log_streaming_enabled_mock.return_value = False
        raise_if_instance_log_streaming_is_not_enabled_mock.side_effect = InvalidOptionsError

        self.app = EB(argv=['logs', '--cloudwatch-log-source', 'instance'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError):
            self.app.run()

        retrieve_cloudwatch_environment_health_logs_mock.assert_not_called()

    @mock.patch('ebcli.controllers.logs.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.raise_if_environment_health_log_streaming_is_not_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.retrieve_cloudwatch_environment_health_logs')
    def test_logs__environment_health_cloudwatch_log_source_specified__cloudwatch_log_streaming_is_disabled(
            self,
            retrieve_cloudwatch_environment_health_logs_mock,
            raise_if_environment_health_log_streaming_is_not_enabled_mock,
            instance_log_streaming_enabled_mock
    ):
        instance_log_streaming_enabled_mock.return_value = False
        raise_if_environment_health_log_streaming_is_not_enabled_mock.side_effect = InvalidOptionsError

        self.app = EB(argv=['logs', '--cloudwatch-log-source', 'environment-health'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError):
            self.app.run()

        retrieve_cloudwatch_environment_health_logs_mock.assert_not_called()

    @mock.patch('ebcli.controllers.logs.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.retrieve_beanstalk_logs')
    def test_logs__retrieve_tail_logs_by_default(
            self,
            retrieve_beanstalk_logs_mock,
            instance_log_streaming_enabled_mock
    ):
        instance_log_streaming_enabled_mock.return_value = False

        self.app = EB(argv=['logs'])
        self.app.setup()
        self.app.run()

        retrieve_beanstalk_logs_mock.assert_called_with(
            TestLogs.ENV_NAME,
            'tail',
            do_zip=False,
            instance_id=None
        )

    @mock.patch('ebcli.controllers.logs.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.retrieve_beanstalk_logs')
    def test_logs__all_logs(
            self,
            retrieve_beanstalk_logs_mock,
            instance_log_streaming_enabled_mock
    ):
        instance_log_streaming_enabled_mock.return_value = False

        self.app = EB(argv=['logs', '--all'])
        self.app.setup()
        self.app.run()

        retrieve_beanstalk_logs_mock.assert_called_with('MyFooEnv', 'bundle', do_zip=False, instance_id=None)

    @mock.patch('ebcli.controllers.logs.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.retrieve_beanstalk_logs')
    def test_logs__instance_logs_for_specific_instance(
            self,
            retrieve_beanstalk_logs_mock,
            instance_log_streaming_enabled_mock
    ):
        instance_log_streaming_enabled_mock.return_value = False

        self.app = EB(argv=['logs', '--instance', 'i-123456789'])
        self.app.setup()
        self.app.run()

        retrieve_beanstalk_logs_mock.assert_called_with(
            'MyFooEnv',
            'tail',
            do_zip=False,
            instance_id='i-123456789'
        )

    @mock.patch('ebcli.controllers.logs.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.retrieve_beanstalk_logs')
    def test_logs__zip_and_instance_id(
            self,
            retrieve_beanstalk_logs_mock,
            instance_log_streaming_enabled_mock
    ):
        instance_log_streaming_enabled_mock.return_value = False

        self.app = EB(argv=['logs', '--zip', '--instance', 'i-123123123'])
        self.app.setup()
        self.app.run()

        retrieve_beanstalk_logs_mock.assert_called_with(
            'MyFooEnv',
            'bundle',
            do_zip=True,
            instance_id='i-123123123'
        )


class TestGetLogsWithCloudWatchLogStreamingEnabled(TestLogs):
    @mock.patch('ebcli.controllers.logs.logsops.normalize_log_group_name')
    @mock.patch('ebcli.controllers.logs.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.raise_if_instance_log_streaming_is_not_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.retrieve_cloudwatch_instance_logs')
    def test_logs__no_args__cloudwatch_log_steaming_enabled__retrieves_tail_logs_by_default(
            self,
            retrieve_cloudwatch_instance_logs_mock,
            raise_if_instance_log_streaming_is_not_enabled_mock,
            instance_log_streaming_enabled_mock,
            normalize_log_group_name
    ):
        instance_log_streaming_enabled_mock.return_value = True
        raise_if_instance_log_streaming_is_not_enabled_mock.side_effect = None
        normalize_log_group_name.return_value = '/aws/elasticbeanstalk/MyFooEnv/var/log/eb-activity.log'

        self.app = EB(argv=['logs'])
        self.app.setup()
        self.app.run()

        retrieve_cloudwatch_instance_logs_mock.assert_called_with(
            '/aws/elasticbeanstalk/MyFooEnv/var/log/eb-activity.log',
            'tail',
            do_zip=False,
            specific_log_stream=None
        )

    @mock.patch('ebcli.controllers.logs.logsops.normalize_log_group_name')
    @mock.patch('ebcli.controllers.logs.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.raise_if_instance_log_streaming_is_not_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.retrieve_cloudwatch_instance_logs')
    def test_logs__no_args__cloudwatch_log_steaming_enabled__zips_logs(
            self,
            retrieve_cloudwatch_instance_logs_mock,
            raise_if_instance_log_streaming_is_not_enabled_mock,
            instance_log_streaming_enabled_mock,
            normalize_log_group_name
    ):
        instance_log_streaming_enabled_mock.return_value = True
        raise_if_instance_log_streaming_is_not_enabled_mock.side_effect = None
        normalize_log_group_name.return_value = '/aws/elasticbeanstalk/MyFooEnv/var/log/eb-activity.log'

        self.app = EB(argv=['logs', '--zip'])
        self.app.setup()
        self.app.run()

        retrieve_cloudwatch_instance_logs_mock.assert_called_with(
            '/aws/elasticbeanstalk/MyFooEnv/var/log/eb-activity.log',
            'bundle',
            do_zip=True,
            specific_log_stream=None
        )

    @mock.patch('ebcli.controllers.logs.logsops.normalize_log_group_name')
    @mock.patch('ebcli.controllers.logs.logsops.raise_if_instance_log_streaming_is_not_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.retrieve_cloudwatch_instance_logs')
    def test_logs__cloudwatch_log_source_is_instance__cloudwatch_log_steaming_enabled__retrieves_tail_logs_by_default(
            self,
            retrieve_cloudwatch_instance_logs_mock,
            raise_if_instance_log_streaming_is_not_enabled_mock,
            normalize_log_group_name
    ):
        raise_if_instance_log_streaming_is_not_enabled_mock.side_effect = None
        normalize_log_group_name.return_value = '/aws/elasticbeanstalk/MyFooEnv/var/log/eb-activity.log'

        self.app = EB(argv=['logs', '--cloudwatch-log-source', 'instance'])
        self.app.setup()
        self.app.run()

        retrieve_cloudwatch_instance_logs_mock.assert_called_with(
            '/aws/elasticbeanstalk/MyFooEnv/var/log/eb-activity.log',
            'tail',
            do_zip=False,
            specific_log_stream=None
        )

    @mock.patch('ebcli.controllers.logs.logsops.retrieve_cloudwatch_environment_health_logs')
    @mock.patch('ebcli.controllers.logs.logsops.raise_if_environment_health_log_streaming_is_not_enabled')
    def test_logs__cloudwatch_log_source_is_environment_health__cloudwatch_log_steaming_enabled__retrieves_tail_logs_by_default(
            self,
            raise_if_environment_health_log_streaming_is_not_enabled_mock,
            retrieve_cloudwatch_environment_health_logs
    ):
        retrieve_cloudwatch_environment_health_logs.return_value = None
        raise_if_environment_health_log_streaming_is_not_enabled_mock.side_effect = None

        self.app = EB(argv=['logs', '--cloudwatch-log-source', 'environment-health'])
        self.app.setup()
        self.app.run()

        retrieve_cloudwatch_environment_health_logs.assert_called_with(
            '/aws/elasticbeanstalk/MyFooEnv/environment-health.log',
            'tail',
            do_zip=False
        )

    @mock.patch('ebcli.controllers.logs.logsops.retrieve_cloudwatch_environment_health_logs')
    @mock.patch('ebcli.controllers.logs.logsops.raise_if_environment_health_log_streaming_is_not_enabled')
    def test_logs__cloudwatch_log_source_is_environment_health__cloudwatch_log_steaming_enabled__zips_logs(
            self,
            raise_if_environment_health_log_streaming_is_not_enabled_mock,
            retrieve_cloudwatch_environment_health_logs
    ):
        retrieve_cloudwatch_environment_health_logs.return_value = None
        raise_if_environment_health_log_streaming_is_not_enabled_mock.side_effect = None

        self.app = EB(argv=['logs', '--cloudwatch-log-source', 'environment-health', '--zip'])
        self.app.setup()
        self.app.run()

        retrieve_cloudwatch_environment_health_logs.assert_called_with(
            '/aws/elasticbeanstalk/MyFooEnv/environment-health.log',
            'bundle',
            do_zip=True
        )


class TestCloudWatchArgument(TestLogs):
    @mock.patch('ebcli.controllers.logs.logsops.enable_cloudwatch_logs')
    def test_logs__cloudwatch_logs__without_args__enables_instance(
            self,
            enable_cloudwatch_logs_mock
    ):
        self.app = EB(argv=['logs', '--cloudwatch-logs'])
        self.app.setup()
        self.app.run()

        enable_cloudwatch_logs_mock.assert_called_with('MyFooApp', 'MyFooEnv', 'instance')

    @mock.patch('ebcli.controllers.logs.logsops.enable_cloudwatch_logs')
    def test_logs__cloudwatch_logs__without_enable__enables_instance(
            self,
            enable_cloudwatch_logs_mock
    ):
        self.app = EB(argv=['logs', '--cloudwatch-logs', 'enable'])
        self.app.setup()
        self.app.run()

        enable_cloudwatch_logs_mock.assert_called_with('MyFooApp', 'MyFooEnv', 'instance')

    @mock.patch('ebcli.controllers.logs.logsops.enable_cloudwatch_logs')
    def test_logs__cloudwatch_logs__without_enable__explicitly_enable_instance_logs(
            self,
            enable_cloudwatch_logs_mock
    ):
        self.app = EB(argv=['logs', '--cloudwatch-logs', 'enable', '--cloudwatch-log-source', 'instance'])
        self.app.setup()
        self.app.run()

        enable_cloudwatch_logs_mock.assert_called_with('MyFooApp', 'MyFooEnv', 'instance')

    @mock.patch('ebcli.controllers.logs.logsops.enable_cloudwatch_logs')
    def test_logs__cloudwatch_logs__with_environment_health_cloudwatch_log_source_arg__enables_environment_health(
            self,
            enable_cloudwatch_logs_mock
    ):
        self.app = EB(argv=['logs', '--cloudwatch-logs', '--cloudwatch-log-source', 'environment-health'])
        self.app.setup()
        self.app.run()

        enable_cloudwatch_logs_mock.assert_called_with('MyFooApp', 'MyFooEnv', 'environment-health')

    @mock.patch('ebcli.controllers.logs.logsops.enable_cloudwatch_logs')
    def test_logs__cloudwatch_logs__with_environment_health_cloudwatch_log_source_arg__explicitly_enable_environment_health(
            self,
            enable_cloudwatch_logs_mock
    ):
        self.app = EB(argv=['logs', '--cloudwatch-logs', 'enable', '--cloudwatch-log-source', 'environment-health'])
        self.app.setup()
        self.app.run()

        enable_cloudwatch_logs_mock.assert_called_with('MyFooApp', 'MyFooEnv', 'environment-health')

    @mock.patch('ebcli.controllers.logs.logsops.enable_cloudwatch_logs')
    def test_logs__cloudwatch_logs__with_all_cloudwatch_log_source_arg__enables_all_logs_streaming(
            self,
            enable_cloudwatch_logs_mock
    ):
        self.app = EB(argv=['logs', '--cloudwatch-logs', '--cloudwatch-log-source', 'all'])
        self.app.setup()
        self.app.run()

        enable_cloudwatch_logs_mock.assert_called_with('MyFooApp', 'MyFooEnv', 'all')

    @mock.patch('ebcli.controllers.logs.logsops.enable_cloudwatch_logs')
    def test_logs__cloudwatch_logs__with_all_cloudwatch_log_source_arg__explicitly_all_logs_streaming(
            self,
            enable_cloudwatch_logs_mock
    ):
        self.app = EB(argv=['logs', '--cloudwatch-logs', 'enable', '--cloudwatch-log-source', 'all'])
        self.app.setup()
        self.app.run()

        enable_cloudwatch_logs_mock.assert_called_with('MyFooApp', 'MyFooEnv', 'all')

    @mock.patch('ebcli.controllers.logs.logsops.disable_cloudwatch_logs')
    def test_logs__cloudwatch_logs__disable__disable_instance_log_streaming(
            self,
            enable_cloudwatch_logs_mock
    ):
        self.app = EB(argv=['logs', '--cloudwatch-logs', 'disable'])
        self.app.setup()
        self.app.run()

        enable_cloudwatch_logs_mock.assert_called_with('MyFooApp', 'MyFooEnv', 'instance')

    @mock.patch('ebcli.controllers.logs.logsops.disable_cloudwatch_logs')
    def test_logs__cloudwatch_logs__disable__explicitly_disable_instance_log_streaming(
            self,
            enable_cloudwatch_logs_mock
    ):
        self.app = EB(argv=['logs', '--cloudwatch-logs', 'disable', '--cloudwatch-log-source', 'instance'])
        self.app.setup()
        self.app.run()

        enable_cloudwatch_logs_mock.assert_called_with('MyFooApp', 'MyFooEnv', 'instance')

    @mock.patch('ebcli.controllers.logs.logsops.disable_cloudwatch_logs')
    def test_logs__cloudwatch_logs__disable__explicitly_disable_environment_health_log_streaming(
            self,
            disable_cloudwatch_logs_mock
    ):
        self.app = EB(argv=['logs', '--cloudwatch-logs', 'disable', '--cloudwatch-log-source', 'environment-health'])
        self.app.setup()
        self.app.run()

        disable_cloudwatch_logs_mock.assert_called_with('MyFooApp', 'MyFooEnv', 'environment-health')

    @mock.patch('ebcli.controllers.logs.logsops.disable_cloudwatch_logs')
    def test_logs__cloudwatch_logs__disable__explicitly_disable_all_log_streaming(
            self,
            disable_cloudwatch_logs_mock
    ):
        self.app = EB(argv=['logs', '--cloudwatch-logs', 'disable', '--cloudwatch-log-source', 'all'])
        self.app.setup()
        self.app.run()

        disable_cloudwatch_logs_mock.assert_called_with('MyFooApp', 'MyFooEnv', 'all')


class TestStreamArgument(TestLogs):
    @mock.patch('ebcli.controllers.logs.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.stream_instance_logs_from_cloudwatch')
    def test_logs__stream_instance_logs__instance_log_streaming_is_disabled(
            self,
            stream_cloudwatch_logs_mock,
            instance_log_streaming_enabled_mock
    ):
        instance_log_streaming_enabled_mock.return_value = False

        self.app = EB(argv=['logs', '--stream'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            "Can't retrieve instance logs for environment MyFooEnv. Instance log streaming is disabled.",
            str(context_manager.exception)
        )
        stream_cloudwatch_logs_mock.assert_not_called()

    @mock.patch('ebcli.controllers.logs.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.stream_instance_logs_from_cloudwatch')
    def test_logs__stream_instance_logs_with_instance_cloudwatch_log_source__instance_log_streaming_is_disabled(
            self,
            stream_cloudwatch_logs_mock,
            instance_log_streaming_enabled_mock
    ):
        instance_log_streaming_enabled_mock.return_value = False

        self.app = EB(argv=['logs', '--stream', '--cloudwatch-log-source', 'instance'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            "Can't retrieve instance logs for environment MyFooEnv. Instance log streaming is disabled.",
            str(context_manager.exception)
        )
        stream_cloudwatch_logs_mock.assert_not_called()

    @mock.patch('ebcli.controllers.logs.logsops.environment_health_streaming_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.stream_environment_health_logs_from_cloudwatch')
    def test_logs__stream_environment_health_logs__environment_health_log_streaming_is_disabled(
            self,
            stream_cloudwatch_logs_mock,
            environment_health_streaming_enabled_mock
    ):
        environment_health_streaming_enabled_mock.return_value = False

        self.app = EB(argv=['logs', '--stream', '--cloudwatch-log-source', 'environment-health'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            """Can't retrieve environment-health logs for environment MyFooEnv. Environment-health log streaming is disabled.""",
            str(context_manager.exception)
        )
        stream_cloudwatch_logs_mock.assert_not_called()

    @mock.patch('ebcli.controllers.logs.logsops.normalize_log_group_name')
    @mock.patch('ebcli.controllers.logs.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.raise_if_instance_log_streaming_is_not_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.stream_instance_logs_from_cloudwatch')
    def test_logs__stream_instance_logs_by_default(
            self,
            stream_cloudwatch_logs_mock,
            raise_if_instance_log_streaming_is_not_enabled_mock,
            instance_log_streaming_enabled_mock,
            normalize_log_group_name
    ):
        instance_log_streaming_enabled_mock.return_value = True
        raise_if_instance_log_streaming_is_not_enabled_mock.side_effect = None
        normalize_log_group_name.return_value = '/aws/elasticbeanstalk/MyFooEnv/var/log/eb-activity.log'

        self.app = EB(argv=['logs', '--stream'])
        self.app.setup()
        self.app.run()

        stream_cloudwatch_logs_mock.assert_called_with(
            log_group='/aws/elasticbeanstalk/MyFooEnv/var/log/eb-activity.log',
            specific_log_stream=None
        )

    @mock.patch('ebcli.controllers.logs.logsops.normalize_log_group_name')
    @mock.patch('ebcli.controllers.logs.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.raise_if_instance_log_streaming_is_not_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.stream_instance_logs_from_cloudwatch')
    def test_logs__stream_instance_logs__cloudwatch_log_source_is_explicitly_specified(
            self,
            stream_cloudwatch_logs_mock,
            raise_if_instance_log_streaming_is_not_enabled_mock,
            instance_log_streaming_enabled_mock,
            normalize_log_group_name
    ):
        instance_log_streaming_enabled_mock.return_value = True
        raise_if_instance_log_streaming_is_not_enabled_mock.side_effect = None
        normalize_log_group_name.return_value = '/aws/elasticbeanstalk/MyFooEnv/var/log/eb-activity.log'

        self.app = EB(argv=['logs', '--stream', '--cloudwatch-log-source', 'instance'])
        self.app.setup()
        self.app.run()

        stream_cloudwatch_logs_mock.assert_called_with(
            log_group='/aws/elasticbeanstalk/MyFooEnv/var/log/eb-activity.log',
            specific_log_stream=None
        )

    @mock.patch('ebcli.controllers.logs.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.raise_if_instance_log_streaming_is_not_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.stream_instance_logs_from_cloudwatch')
    def test_logs__stream_logs_with_specified_stream_log_steaming_enabled(
            self,
            stream_cloudwatch_logs_mock,
            raise_if_instance_log_streaming_is_not_enabled_mock,
            instance_log_streaming_enabled_mock
    ):
        instance_log_streaming_enabled_mock.return_value = True
        raise_if_instance_log_streaming_is_not_enabled_mock.side_effect = None

        self.app = EB(argv=['logs', '--stream', '--log-group', TestLogs.SPECIFIED_LOG_GROUP])
        self.app.setup()
        self.app.run()

        stream_cloudwatch_logs_mock.assert_called_with(
            specific_log_stream=None,
            log_group='/aws/elasticbeanstalk/MyFooEnv/aws/elasticbeanstalk/foo/specific/error.log'
        )

    @mock.patch('ebcli.controllers.logs.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.raise_if_instance_log_streaming_is_not_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.stream_instance_logs_from_cloudwatch')
    def test_logs__stream_instance_logs__cloudwatch_log_source_is_explicitly_specified__log_group_specified(
            self,
            stream_cloudwatch_logs_mock,
            raise_if_instance_log_streaming_is_not_enabled_mock,
            instance_log_streaming_enabled_mock
    ):
        instance_log_streaming_enabled_mock.return_value = True
        raise_if_instance_log_streaming_is_not_enabled_mock.side_effect = None

        self.app = EB(argv=['logs', '--stream', '--cloudwatch-log-source', 'instance',  '--log-group', TestLogs.SPECIFIED_LOG_GROUP])
        self.app.setup()
        self.app.run()

        stream_cloudwatch_logs_mock.assert_called_with(
            specific_log_stream=None,
            log_group='/aws/elasticbeanstalk/MyFooEnv/aws/elasticbeanstalk/foo/specific/error.log'
        )

    @mock.patch('ebcli.controllers.logs.logsops.normalize_log_group_name')
    @mock.patch('ebcli.controllers.logs.logsops.instance_log_streaming_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.raise_if_instance_log_streaming_is_not_enabled')
    @mock.patch('ebcli.controllers.logs.logsops.retrieve_cloudwatch_instance_logs')
    def test_logs__get_logs__zip_logs__instance_log_streaming_to_cloudwatch_enabled(
            self,
            retrieve_cloudwatch_instance_logs_mock,
            raise_if_instance_log_streaming_is_not_enabled_mock,
            instance_log_streaming_enabled_mock,
            normalize_log_group_name
    ):
        instance_log_streaming_enabled_mock.return_value = True
        raise_if_instance_log_streaming_is_not_enabled_mock.side_effect = None
        retrieve_cloudwatch_instance_logs_mock.return_value = None
        normalize_log_group_name.return_value = '/aws/elasticbeanstalk/MyFooEnv/var/log/eb-activity.log'

        self.app = EB(argv=['logs', '--zip'])
        self.app.setup()
        self.app.run()

        retrieve_cloudwatch_instance_logs_mock.assert_called_with(
            '/aws/elasticbeanstalk/MyFooEnv/var/log/eb-activity.log',
            'bundle',
            do_zip=True,
            specific_log_stream=None
        )

    @mock.patch('ebcli.controllers.logs.logsops.enable_cloudwatch_logs')
    def test_logs__default_option_cloudwatch_logs(
            self,
            enable_cloudwatch_logs_mock
    ):
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['logs', '--cloudwatch-logs'])
        self.app.setup()
        self.app.run()
        self.app.close()

        enable_cloudwatch_logs_mock.enable_cloudwatch_logs(TestLogs.ENV_NAME)

    @mock.patch('ebcli.controllers.logs.logsops.enable_cloudwatch_logs')
    def test_logs__enable_cloudwatch_logs(
            self,
            enable_cloudwatch_logs_mock
    ):
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['logs', '--cloudwatch-logs', 'enable'])
        self.app.setup()
        self.app.run()
        self.app.close()

        enable_cloudwatch_logs_mock.enable_cloudwatch_logs(TestLogs.ENV_NAME)

    @mock.patch('ebcli.controllers.logs.logsops.disable_cloudwatch_logs')
    def test_logs__disable_cloudwatch_logs(
            self,
            disable_cloudwatch_logs_mock
    ):
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['logs', '--cloudwatch-logs', 'disable'])
        self.app.setup()
        self.app.run()
        self.app.close()

        disable_cloudwatch_logs_mock.disable_cloudwatch_logs(TestLogs.ENV_NAME)
