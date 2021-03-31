# -*- coding: utf-8 -*-

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

import unittest

import mock
from ebcli.operations import configops
from ebcli.objects.exceptions import InvalidSyntaxError
from yaml.scanner import ScannerError

class TestConfigOperations(unittest.TestCase):
    app_name = 'ebcli-app'
    env_name = 'ebcli-env'
    platform_arn = 'arn:aws:elasticbeanstalk:us-east-1::platform/Platform1/1.0.0'
    new_platform_arn = 'arn:aws:elasticbeanstalk:us-east-1::platform/Platform2/1.0.0'

    file_location = '/wow/eb/white space/.intere-sting'
    editor = 'emacs'
    nohang = False
    changes = "foo-change"
    remove = "remove-me"

    api_model = {'PlatformArn': platform_arn}
    usr_model = {'PlatformArn': new_platform_arn}
    usr_modification = '{"OptionSettings":{"aws:autoscaling:asg":{"MaxSize":"6"}}}'
    usr_modification_file = 'file://' + file_location

    @mock.patch('ebcli.operations.configops.commonops')
    @mock.patch('ebcli.operations.configops.EnvironmentSettings')
    @mock.patch('ebcli.operations.configops.elasticbeanstalk')
    @mock.patch('ebcli.operations.configops.fileoperations')
    def test_update_environment_configuration_solution_stack_changed(self, mock_fileops, mock_elasticbeanstalk, mock_env_settings, mock_commonops):
        mock_elasticbeanstalk.describe_configuration_settings.return_value = self.api_model
        mock_fileops.get_environment_from_file.return_value = self.usr_model
        mock_env_settings.return_value = mock_env_settings
        mock_env_settings.convert_api_to_usr_model.return_value = self.usr_model
        mock_env_settings.collect_changes.return_value = self.changes, self.remove
        mock_fileops.save_env_file.return_value = self.file_location
        configops.update_environment_configuration(self.app_name, self.env_name, self.nohang)
        # verify that changes will be made
        mock_commonops.update_environment.assert_called_with(self.env_name, self.changes, self.nohang,
                                                             platform_arn=self.new_platform_arn,
                                                             remove=self.remove, timeout=None,
                                                             solution_stack_name=None)

    @mock.patch('ebcli.operations.configops.commonops')
    @mock.patch('ebcli.operations.configops.EnvironmentSettings')
    @mock.patch('ebcli.operations.configops.elasticbeanstalk')
    @mock.patch('ebcli.operations.configops.fileoperations')
    def test_update_environment_configuration_no_change(self, mock_fileops, mock_elasticbeanstalk, mock_env_settings, mock_commonops):
        mock_elasticbeanstalk.describe_configuration_settings.return_value = self.usr_model
        mock_fileops.get_environment_from_file.return_value = self.usr_model
        mock_env_settings.return_value = mock_env_settings
        mock_env_settings.convert_api_to_usr_model.return_value = self.usr_model
        mock_env_settings.collect_changes.return_value = None, None
        mock_fileops.save_env_file.return_value = self.file_location
        configops.update_environment_configuration(self.app_name, self.env_name, self.nohang)
        mock_commonops.update_environment.assert_not_called()

    @mock.patch('ebcli.operations.configops.commonops')
    @mock.patch('ebcli.operations.configops.EnvironmentSettings')
    @mock.patch('ebcli.operations.configops.elasticbeanstalk')
    @mock.patch('ebcli.operations.configops.fileoperations')
    def test_update_environment_configuration_bad_usr_modification(self, mock_fileops, mock_elasticbeanstalk, mock_env_settings,
                                                        mock_commonops):
        mock_elasticbeanstalk.describe_configuration_settings.return_value = self.usr_model
        mock_fileops.get_environment_from_file.side_effect = InvalidSyntaxError("Bad user changes")
        mock_env_settings.return_value = mock_env_settings
        mock_env_settings.convert_api_to_usr_model.return_value = self.usr_model
        mock_fileops.save_env_file.return_value = self.file_location
        configops.update_environment_configuration(self.app_name, self.env_name, self.nohang)
        mock_commonops.update_environment.assert_not_called()

    @mock.patch('ebcli.operations.configops.commonops')
    @mock.patch('ebcli.operations.configops.EnvironmentSettings')
    def test_modify_environment_configuration(self, mock_env_settings, mock_commonops):
        mock_env_settings.return_value = mock_env_settings
        mock_env_settings.convert_usr_model_to_api.return_value = self.changes
        configops.modify_environment_configuration(self.env_name, self.usr_modification, self.nohang)
        # verify that changes will be made
        mock_commonops.update_environment.assert_called_with(self.env_name, self.changes, self.nohang,
                                                             platform_arn=None,
                                                             remove=[], timeout=None,
                                                             solution_stack_name=None)

    @mock.patch('ebcli.operations.configops.commonops')
    @mock.patch('ebcli.operations.configops.fileoperations')
    @mock.patch('ebcli.operations.configops.safe_load')
    def test_modify_environment_configuration_bad_usr_modification(self, mock_safe_load, mock_fileops, mock_commonops):
        mock_safe_load.side_effect = ScannerError("Bad user changes")
        with self.assertRaises(InvalidSyntaxError) as context_manager:
            configops.modify_environment_configuration(self.env_name, self.usr_modification, self.nohang)
            self.assertEqual(
                'The environment configuration contains invalid syntax.',
                str(context_manager.exception)
            )
