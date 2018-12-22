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

from ebcli.core import fileoperations
from ebcli.core.ebcore import EB
import ebcli.core.ebpcore
from ebcli.core.ebpcore import EBP
from ebcli.controllers.platform import logs
from ebcli.objects.exceptions import ApplicationWorkspaceNotSupportedError
from ebcli.objects.platform import PlatformVersion
from ebcli.objects.solutionstack import SolutionStack


class LogsTest(unittest.TestCase):
    platform = PlatformVersion(
        'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5'
    )
    solution_stack = SolutionStack(
        '64bit Amazon Linux 2017.09 v4.4.0 running Node.js'
    )

    def setUp(self):
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')

        os.chdir('testDir')

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

    def setup_platform_workspace(self):
        fileoperations.create_config_file(
            'my-platform',
            'us-west-2',
            self.platform.name,
            workspace_type='Platform'
        )

    def setup_application_workspace(self):
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            self.solution_stack.name,
            workspace_type='Application'
        )


class TestEBPlatformLogs(LogsTest):
    def test_logs__application_workspace__command_not_applicable(self):
        self.setup_application_workspace()

        with self.assertRaises(ApplicationWorkspaceNotSupportedError) as context_manager:
            app = EB(argv=['platform', 'logs'])
            app.setup()
            app.run()

        self.assertEqual(
            'This command is not supported outside Platform workspaces.',
            str(context_manager.exception)
        )

    def test_logs__neutral_workspace__command_not_applicable(self):
        self.setup_application_workspace()
        fileoperations.write_config_setting('global', 'workspace', None)

        with self.assertRaises(ApplicationWorkspaceNotSupportedError) as context_manager:
            app = EB(argv=['platform', 'logs'])
            app.setup()
            app.run()

        self.assertEqual(
            'This command is not supported outside Platform workspaces.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_version')
    @mock.patch('ebcli.controllers.platform.logs.logsops.stream_platform_logs')
    @mock.patch('ebcli.controllers.platform.logs.paginate_cloudwatch_logs')
    def test_logs__platform_workspace__version_not_specified__stream_argument_not_specified__print_paginated_logs(
            self,
            paginate_cloudwatch_logs_mock,
            stream_platform_logs_mock,
            get_platform_version_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        get_platform_name_mock.return_value = 'custom-platform-4'
        get_platform_version_mock.return_value = '1.0.3'

        app = EB(argv=['platform', 'logs'])
        app.setup()
        app.run()

        paginate_cloudwatch_logs_mock.assert_called_once_with('custom-platform-4', '1.0.3')
        stream_platform_logs_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_version')
    @mock.patch('ebcli.controllers.platform.logs.logsops.stream_platform_logs')
    @mock.patch('ebcli.controllers.platform.logs.paginate_cloudwatch_logs')
    def test_logs__platform_workspace__version_specified_and_is_valid_semantic_version(
            self,
            paginate_cloudwatch_logs_mock,
            stream_platform_logs_mock,
            get_platform_version_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        get_platform_name_mock.return_value = 'custom-platform-4'

        app = EB(argv=['platform', 'logs', '1.0.3'])
        app.setup()
        app.run()

        paginate_cloudwatch_logs_mock.assert_called_once_with('custom-platform-4', '1.0.3')
        stream_platform_logs_mock.assert_not_called()
        get_platform_version_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_version')
    @mock.patch('ebcli.controllers.platform.logs.logsops.stream_platform_logs')
    @mock.patch('ebcli.controllers.platform.logs.paginate_cloudwatch_logs')
    def test_logs__platform_workspace__version_specified_and_is_valid_platform_arn(
            self,
            paginate_cloudwatch_logs_mock,
            stream_platform_logs_mock,
            get_platform_version_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        get_platform_name_mock.return_value = 'custom-platform-4'

        app = EB(argv=['platform', 'logs', 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3'])
        app.setup()
        app.run()

        paginate_cloudwatch_logs_mock.assert_called_once_with('custom-platform-4', '1.0.3')
        stream_platform_logs_mock.assert_not_called()
        get_platform_version_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_version')
    @mock.patch('ebcli.controllers.platform.logs.logsops.stream_platform_logs')
    @mock.patch('ebcli.controllers.platform.logs.paginate_cloudwatch_logs')
    def test_logs__platform_workspace__version_specified_and_is_valid_short_format(
            self,
            paginate_cloudwatch_logs_mock,
            stream_platform_logs_mock,
            get_platform_version_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        get_platform_name_mock.return_value = 'custom-platform-4'

        app = EB(argv=['platform', 'logs', 'custom-platform-4/1.0.3'])
        app.setup()
        app.run()

        paginate_cloudwatch_logs_mock.assert_called_once_with('custom-platform-4', '1.0.3')
        stream_platform_logs_mock.assert_not_called()
        get_platform_version_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_version')
    @mock.patch('ebcli.controllers.platform.logs.logsops.stream_platform_logs')
    @mock.patch('ebcli.controllers.platform.logs.paginate_cloudwatch_logs')
    def test_logs__platform_workspace__version_specified_and_is_invalid(
            self,
            paginate_cloudwatch_logs_mock,
            stream_platform_logs_mock,
            get_platform_version_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        get_platform_name_mock.return_value = 'custom-platform-4'

        with self.assertRaises(logs.InvalidPlatformVersionError) as context_manager:
            app = EB(argv=['platform', 'logs', '1.0.3.5'])
            app.setup()
            app.run()

        self.assertEqual(
            'Invalid version format. Only ARNs, version numbers, or platform_name/version formats are accepted.',
            str(context_manager.exception)
        )
        paginate_cloudwatch_logs_mock.assert_not_called()
        stream_platform_logs_mock.assert_not_called()
        get_platform_version_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_version')
    @mock.patch('ebcli.controllers.platform.logs.logsops.stream_platform_logs')
    @mock.patch('ebcli.controllers.platform.logs.paginate_cloudwatch_logs')
    @mock.patch('ebcli.controllers.platform.logs.platformops.PackerStreamFormatter')
    def test_logs__platform_workspace__stream_logs(
            self,
            PackerStreamFormatter_mock,
            paginate_cloudwatch_logs_mock,
            stream_platform_logs_mock,
            get_platform_version_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        streamer_formatter_mock = mock.MagicMock()
        PackerStreamFormatter_mock.return_value = streamer_formatter_mock
        get_platform_name_mock.return_value = 'custom-platform-4'

        app = EB(argv=['platform', 'logs', '1.0.3', '--stream'])
        app.setup()
        app.run()

        paginate_cloudwatch_logs_mock.assert_not_called()
        stream_platform_logs_mock.assert_called_once_with(
            'custom-platform-4',
            '1.0.3',
            formatter=streamer_formatter_mock,
            log_name='custom-platform-4/1.0.3'
        )
        get_platform_version_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_version')
    @mock.patch('ebcli.controllers.platform.logs.logsops.stream_platform_logs')
    @mock.patch('ebcli.controllers.platform.logs.paginate_cloudwatch_logs')
    @mock.patch('ebcli.controllers.platform.logs.platformops.PackerStreamFormatter')
    def test_logs__platform_workspace__stream_logs__unable_to_find_cloudwatch_logs(
            self,
            PackerStreamFormatter_mock,
            paginate_cloudwatch_logs_mock,
            stream_platform_logs_mock,
            get_platform_version_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        streamer_formatter_mock = mock.MagicMock()
        PackerStreamFormatter_mock.return_value = streamer_formatter_mock
        get_platform_name_mock.return_value = 'custom-platform-4'
        stream_platform_logs_mock.side_effect = logs.NotFoundError

        with self.assertRaises(logs.NotFoundError) as context_manager:
            app = EB(argv=['platform', 'logs', '1.0.3', '--stream'])
            app.setup()
            app.run()

        self.assertEqual(
            'Unable to find logs in CloudWatch.',
            str(context_manager.exception)
        )
        paginate_cloudwatch_logs_mock.assert_not_called()
        stream_platform_logs_mock.assert_called_once_with(
            'custom-platform-4',
            '1.0.3',
            formatter=streamer_formatter_mock,
            log_name='custom-platform-4/1.0.3'
        )
        get_platform_version_mock.assert_not_called()


class TestEBPLogs(LogsTest):
    def test_logs__application_workspace__command_not_applicable(self):
        self.setup_application_workspace()

        with self.assertRaises(ApplicationWorkspaceNotSupportedError) as context_manager:
            app = EBP(argv=['logs'])
            app.setup()
            app.run()

        self.assertEqual(
            'This command is not supported outside Platform workspaces.',
            str(context_manager.exception)
        )

    def test_logs__neutral_workspace__command_not_applicable(self):
        self.setup_application_workspace()
        fileoperations.write_config_setting('global', 'workspace', None)

        with self.assertRaises(ApplicationWorkspaceNotSupportedError) as context_manager:
            app = EBP(argv=['logs'])
            app.setup()
            app.run()

        self.assertEqual(
            'This command is not supported outside Platform workspaces.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_version')
    @mock.patch('ebcli.controllers.platform.logs.logsops.stream_platform_logs')
    @mock.patch('ebcli.controllers.platform.logs.paginate_cloudwatch_logs')
    def test_logs__platform_workspace__version_not_specified__stream_argument_not_specified__print_paginated_logs(
            self,
            paginate_cloudwatch_logs_mock,
            stream_platform_logs_mock,
            get_platform_version_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        get_platform_name_mock.return_value = 'custom-platform-4'
        get_platform_version_mock.return_value = '1.0.3'

        app = EBP(argv=['logs'])
        app.setup()
        app.run()

        paginate_cloudwatch_logs_mock.assert_called_once_with('custom-platform-4', '1.0.3')
        stream_platform_logs_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_version')
    @mock.patch('ebcli.controllers.platform.logs.logsops.stream_platform_logs')
    @mock.patch('ebcli.controllers.platform.logs.paginate_cloudwatch_logs')
    def test_logs__platform_workspace__version_specified_and_is_valid_semantic_version(
            self,
            paginate_cloudwatch_logs_mock,
            stream_platform_logs_mock,
            get_platform_version_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        get_platform_name_mock.return_value = 'custom-platform-4'

        app = EBP(argv=['logs', '1.0.3'])
        app.setup()
        app.run()

        paginate_cloudwatch_logs_mock.assert_called_once_with('custom-platform-4', '1.0.3')
        stream_platform_logs_mock.assert_not_called()
        get_platform_version_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_version')
    @mock.patch('ebcli.controllers.platform.logs.logsops.stream_platform_logs')
    @mock.patch('ebcli.controllers.platform.logs.paginate_cloudwatch_logs')
    def test_logs__platform_workspace__version_specified_and_is_valid_platform_arn(
            self,
            paginate_cloudwatch_logs_mock,
            stream_platform_logs_mock,
            get_platform_version_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        get_platform_name_mock.return_value = 'custom-platform-4'

        app = EBP(argv=['logs', 'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-4/1.0.3'])
        app.setup()
        app.run()

        paginate_cloudwatch_logs_mock.assert_called_once_with('custom-platform-4', '1.0.3')
        stream_platform_logs_mock.assert_not_called()
        get_platform_version_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_version')
    @mock.patch('ebcli.controllers.platform.logs.logsops.stream_platform_logs')
    @mock.patch('ebcli.controllers.platform.logs.paginate_cloudwatch_logs')
    def test_logs__platform_workspace__version_specified_and_is_valid_short_format(
            self,
            paginate_cloudwatch_logs_mock,
            stream_platform_logs_mock,
            get_platform_version_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        get_platform_name_mock.return_value = 'custom-platform-4'

        app = EBP(argv=['logs', 'custom-platform-4/1.0.3'])
        app.setup()
        app.run()

        paginate_cloudwatch_logs_mock.assert_called_once_with('custom-platform-4', '1.0.3')
        stream_platform_logs_mock.assert_not_called()
        get_platform_version_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_version')
    @mock.patch('ebcli.controllers.platform.logs.logsops.stream_platform_logs')
    @mock.patch('ebcli.controllers.platform.logs.paginate_cloudwatch_logs')
    def test_logs__platform_workspace__version_specified_and_is_invalid(
            self,
            paginate_cloudwatch_logs_mock,
            stream_platform_logs_mock,
            get_platform_version_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        get_platform_name_mock.return_value = 'custom-platform-4'

        with self.assertRaises(logs.InvalidPlatformVersionError) as context_manager:
            app = EBP(argv=['logs', '1.0.3.5'])
            app.setup()
            app.run()

        self.assertEqual(
            'Invalid version format. Only ARNs, version numbers, or platform_name/version formats are accepted.',
            str(context_manager.exception)
        )
        paginate_cloudwatch_logs_mock.assert_not_called()
        stream_platform_logs_mock.assert_not_called()
        get_platform_version_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_version')
    @mock.patch('ebcli.controllers.platform.logs.logsops.stream_platform_logs')
    @mock.patch('ebcli.controllers.platform.logs.paginate_cloudwatch_logs')
    @mock.patch('ebcli.controllers.platform.logs.platformops.PackerStreamFormatter')
    def test_logs__platform_workspace__stream_logs(
            self,
            PackerStreamFormatter_mock,
            paginate_cloudwatch_logs_mock,
            stream_platform_logs_mock,
            get_platform_version_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        streamer_formatter_mock = mock.MagicMock()
        PackerStreamFormatter_mock.return_value = streamer_formatter_mock
        get_platform_name_mock.return_value = 'custom-platform-4'

        app = EBP(argv=['logs', '1.0.3', '--stream'])
        app.setup()
        app.run()

        paginate_cloudwatch_logs_mock.assert_not_called()
        stream_platform_logs_mock.assert_called_once_with(
            'custom-platform-4',
            '1.0.3',
            formatter=streamer_formatter_mock,
            log_name='custom-platform-4/1.0.3'
        )
        get_platform_version_mock.assert_not_called()

    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_name')
    @mock.patch('ebcli.controllers.platform.logs.fileoperations.get_platform_version')
    @mock.patch('ebcli.controllers.platform.logs.logsops.stream_platform_logs')
    @mock.patch('ebcli.controllers.platform.logs.paginate_cloudwatch_logs')
    @mock.patch('ebcli.controllers.platform.logs.platformops.PackerStreamFormatter')
    def test_logs__platform_workspace__stream_logs__unable_to_find_cloudwatch_logs(
            self,
            PackerStreamFormatter_mock,
            paginate_cloudwatch_logs_mock,
            stream_platform_logs_mock,
            get_platform_version_mock,
            get_platform_name_mock
    ):
        self.setup_platform_workspace()

        streamer_formatter_mock = mock.MagicMock()
        PackerStreamFormatter_mock.return_value = streamer_formatter_mock
        get_platform_name_mock.return_value = 'custom-platform-4'
        stream_platform_logs_mock.side_effect = logs.NotFoundError

        with self.assertRaises(logs.NotFoundError) as context_manager:
            app = EBP(argv=['logs', '1.0.3', '--stream'])
            app.setup()
            app.run()

        self.assertEqual(
            'Unable to find logs in CloudWatch.',
            str(context_manager.exception)
        )
        paginate_cloudwatch_logs_mock.assert_not_called()
        stream_platform_logs_mock.assert_called_once_with(
            'custom-platform-4',
            '1.0.3',
            formatter=streamer_formatter_mock,
            log_name='custom-platform-4/1.0.3'
        )
        get_platform_version_mock.assert_not_called()