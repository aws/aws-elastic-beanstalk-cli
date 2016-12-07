# -*- coding: utf-8 -*-

# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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


class TestConfigOperations(unittest.TestCase):
    app_name = 'ebcli-app'
    env_name = 'ebcli-env'
    solution_stack_name = 'Solution Stack Name'
    new_solution_stack_name = 'New Solution Stack Name'

    file_location = '/wow/eb/white space/.intere-sting'
    editor = 'emacs'
    nohang = False

    @mock.patch('ebcli.operations.configops.os')
    @mock.patch('ebcli.operations.configops.fileoperations')
    def test_open_file_for_editing_with_editor(self, mock_fileops, mock_os):
        # setup editor
        mock_fileops.get_editor.return_value = self.editor
        # do the actual call
        configops.open_file_for_editing(self.file_location)
        # assert the command has been properly escaped and opened with editor
        mock_os.system.assert_called_with('{0} "{1}"'.format(self.editor, self.file_location))

    @mock.patch('ebcli.operations.configops.commonops')
    @mock.patch('ebcli.operations.configops.configuration')
    @mock.patch('ebcli.operations.configops.elasticbeanstalk')
    @mock.patch('ebcli.operations.configops.fileoperations')
    def test_update_environment_configuration_solution_stack_changed(self, mock_fileops, mock_elasticbeanstalk, mock_configuration, mock_commonops):
        # Mock the configuration returned by api
        mock_elasticbeanstalk.describe_configuration_settings.return_value = {'SolutionStackName': self.solution_stack_name}
        # Mock the configuration after user edition
        mock_fileops.get_environment_from_file.return_value = {'SolutionStackName': self.new_solution_stack_name}
        # Assume no change or removals
        mock_configuration.collect_changes.return_value = None, None
        # Mock out the file operations
        mock_fileops.save_env_file.return_value = self.file_location
        mock_fileops.get_editor.return_value = None
        # Do the actual call
        configops.update_environment_configuration(self.app_name, self.env_name, self.nohang)
        # verify that changes will be made
        mock_commonops.update_environment.assert_called_with(self.env_name, None, self.nohang,
                                                             solution_stack_name=self.new_solution_stack_name, remove=None, timeout=None)

    @mock.patch('ebcli.operations.configops.commonops')
    @mock.patch('ebcli.operations.configops.configuration')
    @mock.patch('ebcli.operations.configops.elasticbeanstalk')
    @mock.patch('ebcli.operations.configops.fileoperations')
    def test_update_environment_configuration_no_change(self, mock_fileops, mock_elasticbeanstalk, mock_configuration, mock_commonops):
        # Mock the configuration returned by api
        mock_elasticbeanstalk.describe_configuration_settings.return_value = {'SolutionStackName': self.solution_stack_name}
        # Mock the configuration after user edition
        mock_fileops.get_environment_from_file.return_value = {'SolutionStackName': self.solution_stack_name}
        # Assume no change or removals
        mock_configuration.collect_changes.return_value = None, None
        # Mock out the file operations
        mock_fileops.save_env_file.return_value = self.file_location
        mock_fileops.get_editor.return_value = None
        # Do the actual call
        configops.update_environment_configuration(self.app_name, self.env_name, self.nohang)
        # verify that no changes will be made
        mock_commonops.update_environment.assert_not_called()
