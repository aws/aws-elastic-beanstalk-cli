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
import unittest

from ebcli.operations import consoleops


class TestConsoleOps(unittest.TestCase):
    @mock.patch('ebcli.operations.consoleops.utils.is_ssh')
    def test_open_console__ssh_shell(
            self,
            is_ssh_mock
    ):
        is_ssh_mock.return_value = True

        with self.assertRaises(consoleops.NotSupportedError) as context_manager:
            consoleops.open_console('my-application', 'environment-1')

        self.assertEqual(
            'The console command is not supported in an ssh type session',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.consoleops.utils.is_ssh')
    @mock.patch('ebcli.operations.consoleops.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.operations.consoleops.aws.get_region_name')
    @mock.patch('ebcli.operations.consoleops.commonops.open_webpage_in_browser')
    def test_open_console__non_ssh_shell(
            self,
            open_webpage_in_browser_mock,
            get_region_name_mock,
            get_environment_mock,
            is_ssh_mock
    ):
        is_ssh_mock.return_value = False
        environment_mock = mock.MagicMock()
        environment_mock.id = 'env-id'
        get_environment_mock.return_value = environment_mock
        get_region_name_mock.return_value = 'us-west-2'

        consoleops.open_console('my-application', 'environment-1')

        open_webpage_in_browser_mock.assert_called_once_with(
            'console.aws.amazon.com/elasticbeanstalk/home?region=us-west-2#/environment/dashboard?applicationName=my-application&environmentId=env-id',
            ssl=True
        )
