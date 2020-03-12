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

from ebcli.controllers.platform import use
from ebcli.objects.platform import PlatformBranch, PlatformVersion


class TestPlatformSelectController(unittest.TestCase):

    def setUp(self):
        self.platform_select_controller = use.PlatformSelectController()

    @mock.patch('ebcli.controllers.platform.use.alert_platform_status')
    @mock.patch('ebcli.controllers.platform.use.alert_platform_branch_status')
    @mock.patch('ebcli.controllers.platform.use.prompt_for_platform')
    @mock.patch('ebcli.controllers.platform.use.fileoperations.write_config_setting')
    def test_do_command__platform_version(
        self,
        write_config_setting_mock,
        prompt_for_platform_mock,
        alert_platform_branch_status_mock,
        alert_platform_status_mock,
    ):
        platform = PlatformVersion(
            'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.3 running on 64bit Amazon Linux/0.0.0',
            platform_name='PHP 7.3 running on 64bit Amazon Linux (platform name)',
            platform_branch_name='PHP 7.3 running on 64bit Amazon Linux')
        prompt_for_platform_mock.return_value = platform

        self.platform_select_controller.do_command()

        prompt_for_platform_mock.assert_called_once_with()
        alert_platform_status_mock.assert_called_once_with(platform)
        alert_platform_branch_status_mock.assert_not_called()
        write_config_setting_mock.assert_called_once_with(
            'global',
            'default_platform',
            'PHP 7.3 running on 64bit Amazon Linux')

    @mock.patch('ebcli.controllers.platform.use.alert_platform_status')
    @mock.patch('ebcli.controllers.platform.use.alert_platform_branch_status')
    @mock.patch('ebcli.controllers.platform.use.prompt_for_platform')
    @mock.patch('ebcli.controllers.platform.use.fileoperations.write_config_setting')
    def test_do_command__platform_version_sans_branch_name(
        self,
        write_config_setting_mock,
        prompt_for_platform_mock,
        alert_platform_branch_status_mock,
        alert_platform_status_mock,
    ):
        _self = mock.Mock()
        platform = PlatformVersion(
            'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 7.3 running on 64bit Amazon Linux/0.0.0',
            platform_name='PHP 7.3 running on 64bit Amazon Linux')
        prompt_for_platform_mock.return_value = platform

        self.platform_select_controller.do_command()

        prompt_for_platform_mock.assert_called_once_with()
        alert_platform_status_mock.assert_called_once_with(platform)
        alert_platform_branch_status_mock.assert_not_called()
        write_config_setting_mock.assert_called_once_with(
            'global',
            'default_platform',
            'PHP 7.3 running on 64bit Amazon Linux')

    @mock.patch('ebcli.controllers.platform.use.alert_platform_status')
    @mock.patch('ebcli.controllers.platform.use.alert_platform_branch_status')
    @mock.patch('ebcli.controllers.platform.use.prompt_for_platform')
    @mock.patch('ebcli.controllers.platform.use.fileoperations.write_config_setting')
    def test_do_command__platform_branch(
        self,
        write_config_setting_mock,
        prompt_for_platform_mock,
        alert_platform_branch_status_mock,
        alert_platform_status_mock,
    ):
        platform = PlatformBranch('PHP 7.3 running on 64bit Amazon Linux')
        prompt_for_platform_mock.return_value = platform

        self.platform_select_controller.do_command()

        prompt_for_platform_mock.assert_called_once_with()
        alert_platform_status_mock.assert_not_called()
        alert_platform_branch_status_mock.assert_called_once_with(platform)
        write_config_setting_mock.assert_called_once_with(
            'global',
            'default_platform',
            'PHP 7.3 running on 64bit Amazon Linux')
