# Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

import unittest
import mock

from ebcli.core.ebcore import EB
from ebcli.objects.exceptions import NotFoundError, InvalidOptionsError


class TestLogs(unittest.TestCase):
    app_name = 'MyFooApp'
    env_name = 'MyFooEnv'
    instance_id = 'i-123456789'
    default_log_group = '/aws/elasticbeanstalk/foo/test/activity.log'
    specified_log_group = '/aws/elasticbeanstalk/foo/specific/error.log'

    def setUp(self):
        self.patcher_restore_ops = mock.patch('ebcli.controllers.logs.logsops')
        self.patcher_base_get_app = mock.patch('ebcli.controllers.logs.AbstractBaseController.get_app_name')
        self.patcher_base_get_env = mock.patch('ebcli.controllers.logs.AbstractBaseController.get_env_name')
        self.mock_logs_ops = self.patcher_restore_ops.start()
        self.mock_base_get_app = self.patcher_base_get_app.start()
        self.mock_base_get_env = self.patcher_base_get_env.start()

    def tearDown(self):
        self.patcher_restore_ops.stop()
        self.patcher_base_get_app.stop()
        self.patcher_base_get_env.stop()

    ##### EB REQUEST/RETRIEVE FEATURE #####
    def test_no_args_tail_logs(self):
        # Mock out methods
        self.mock_base_get_app.return_value = self.app_name
        self.mock_base_get_env.return_value = self.env_name
        self.mock_logs_ops.log_streaming_enabled.return_value = False

        # Run the command
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['logs'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # Assert calls were made
        self.mock_logs_ops.log_streaming_enabled.assert_called_with(self.app_name, self.env_name)
        self.mock_logs_ops.retrieve_beanstalk_logs.assert_called_with(self.env_name, 'tail', do_zip=False, instance_id=None)

    def test_all_logs(self):
        # Mock out methods
        self.mock_base_get_app.return_value = self.app_name
        self.mock_base_get_env.return_value = self.env_name
        self.mock_logs_ops.log_streaming_enabled.return_value = False

        # Run the command
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['logs', '--all'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # Assert calls were made
        self.mock_logs_ops.log_streaming_enabled.assert_called_with(self.app_name, self.env_name)
        self.mock_logs_ops.retrieve_beanstalk_logs.assert_called_with(self.env_name, 'bundle', do_zip=False, instance_id=None)

    def test_stream_logs(self):
        # Mock out methods
        self.mock_base_get_app.return_value = self.app_name
        self.mock_base_get_env.return_value = self.env_name
        self.mock_logs_ops.log_streaming_enabled.return_value = False

        # Run the command
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['logs', '--stream'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # Assert calls were made
        self.mock_logs_ops.log_streaming_enabled.assert_called_with(self.app_name, self.env_name)
        self.mock_logs_ops.stream_cloudwatch_logs.assert_called_with(self.env_name, log_group=None, instance_id=None)

    def test_all_and_instance_id_logs(self):
        # Mock out methods
        self.mock_base_get_app.return_value = self.app_name
        self.mock_base_get_env.return_value = self.env_name
        self.mock_logs_ops.log_streaming_enabled.return_value = False

        # Run the command
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['logs', '--all', '--instance', self.instance_id])
        self.app.setup()
        self.assertRaises(InvalidOptionsError, self.app.run)
        self.app.close()

        # Assert calls were made
        self.mock_logs_ops.log_streaming_enabled.assert_not_called()
        self.mock_logs_ops.logs.assert_not_called()

    def test_stream_logs_bad_log_group(self):
        # Mock out methods
        self.mock_base_get_app.return_value = self.app_name
        self.mock_base_get_env.return_value = self.env_name
        self.mock_logs_ops.log_streaming_enabled.return_value = False
        self.mock_logs_ops.stream_cloudwatch_logs.side_effect = NotFoundError("Cannot find Log Group!")

        # Run the command
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['logs', '--stream', '--log-group', self.specified_log_group])
        self.app.setup()
        self.assertRaises(NotFoundError, self.app.run)
        self.app.close()

        # Assert calls were made
        self.mock_logs_ops.log_streaming_enabled.assert_called_with(self.app_name, self.env_name)
        self.mock_logs_ops.stream_cloudwatch_logs.assert_called_with(self.env_name, log_group=self.specified_log_group, instance_id=None)

    ##### LOG STREAMING FEATURE #####
    def test_no_args_tail_logs_log_steaming_enabled(self):
        # Mock out methods
        self.mock_base_get_app.return_value = self.app_name
        self.mock_base_get_env.return_value = self.env_name
        self.mock_logs_ops.log_streaming_enabled.return_value = True
        self.mock_logs_ops.beanstalk_log_group_builder.return_value = self.default_log_group

        # Run the command
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['logs'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # Assert calls were made
        self.mock_logs_ops.log_streaming_enabled.assert_called_with(self.app_name, self.env_name)
        self.mock_logs_ops.beanstalk_log_group_builder.assert_called_with(self.env_name, None)
        self.mock_logs_ops.retrieve_cloudwatch_logs.assert_called_with(self.default_log_group, 'tail', do_zip=False,
                                                              instance_id=None)

    def test_stream_logs_log_steaming_enabled(self):
        # Mock out methods
        self.mock_base_get_app.return_value = self.app_name
        self.mock_base_get_env.return_value = self.env_name
        self.mock_logs_ops.log_streaming_enabled.return_value = True
        self.mock_logs_ops.beanstalk_log_group_builder.return_value = self.default_log_group

        # Run the command
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['logs', '--stream'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # Assert calls were made
        self.mock_logs_ops.log_streaming_enabled.assert_called_with(self.app_name, self.env_name)
        self.mock_logs_ops.beanstalk_log_group_builder.assert_called_with(self.env_name, None)
        self.mock_logs_ops.stream_cloudwatch_logs.assert_called_with(self.env_name, log_group=self.default_log_group, instance_id=None)

    def test_stream_logs_with_specified_strem_log_steaming_enabled(self):
        # Mock out methods
        self.mock_base_get_app.return_value = self.app_name
        self.mock_base_get_env.return_value = self.env_name
        self.mock_logs_ops.log_streaming_enabled.return_value = True
        self.mock_logs_ops.beanstalk_log_group_builder.return_value = self.specified_log_group

        # Run the command
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['logs', '--stream', '--log-group', self.specified_log_group])
        self.app.setup()
        self.app.run()
        self.app.close()

        # Assert calls were made
        self.mock_logs_ops.log_streaming_enabled.assert_called_with(self.app_name, self.env_name)
        self.mock_logs_ops.beanstalk_log_group_builder.assert_called_with(self.env_name, self.specified_log_group)
        self.mock_logs_ops.stream_cloudwatch_logs.assert_called_with(self.env_name, log_group=self.specified_log_group, instance_id=None)

    def test_all_zipped_logs_log_steaming_enabled(self):
        # Mock out methods
        self.mock_base_get_app.return_value = self.app_name
        self.mock_base_get_env.return_value = self.env_name
        self.mock_logs_ops.log_streaming_enabled.return_value = True
        self.mock_logs_ops.beanstalk_log_group_builder.return_value = self.default_log_group

        # Run the command
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['logs', '--all', '--zip'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # Assert calls were made
        self.mock_logs_ops.log_streaming_enabled.assert_called_with(self.app_name, self.env_name)
        self.mock_logs_ops.beanstalk_log_group_builder.assert_called_with(self.env_name, None)
        self.mock_logs_ops.retrieve_cloudwatch_logs.assert_called_with(self.default_log_group, 'bundle', do_zip=True,
                                                              instance_id=None)

    def test_no_args_tail_logs_log_steaming_enabled_bad_log_group(self):
        # Mock out methods
        self.mock_base_get_app.return_value = self.app_name
        self.mock_base_get_env.return_value = self.env_name
        self.mock_logs_ops.log_streaming_enabled.return_value = True
        self.mock_logs_ops.beanstalk_log_group_builder.return_value = self.default_log_group
        self.mock_logs_ops.retrieve_cloudwatch_logs.side_effect = NotFoundError("Cannot find Log Group!")

        # Run the command
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['logs'])
        self.app.setup()
        self.assertRaises(NotFoundError, self.app.run)
        self.app.close()

        # Assert calls were made
        self.mock_logs_ops.log_streaming_enabled.assert_called_with(self.app_name, self.env_name)
        self.mock_logs_ops.beanstalk_log_group_builder.assert_called_with(self.env_name, None)
        self.mock_logs_ops.retrieve_cloudwatch_logs.assert_called_with(self.default_log_group, 'tail', do_zip=False,
                                                                       instance_id=None)

    def test_default_option_cloudwatch_logs(self):
        # Mock out methods
        self.mock_base_get_app.return_value = self.app_name
        self.mock_base_get_env.return_value = self.env_name

        # Run the command
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['logs', '--cloudwatch-logs'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # Assert calls were made
        self.mock_logs_ops.enable_cloudwatch_logs(self.env_name)

    def test_enable_cloudwatch_logs(self):
        # Mock out methods
        self.mock_base_get_app.return_value = self.app_name
        self.mock_base_get_env.return_value = self.env_name

        # Run the command
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['logs', '--cloudwatch-logs', 'enable'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # Assert calls were made
        self.mock_logs_ops.enable_cloudwatch_logs(self.env_name)

    def test_disable_cloudwatch_logs(self):
        # Mock out methods
        self.mock_base_get_app.return_value = self.app_name
        self.mock_base_get_env.return_value = self.env_name

        # Run the command
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['logs', '--cloudwatch-logs', 'disable'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # Assert calls were made
        self.mock_logs_ops.disable_cloudwatch_logs(self.env_name)