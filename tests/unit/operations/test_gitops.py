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
import datetime

from dateutil import tz
import mock
import unittest

from ebcli.operations import gitops
from ebcli.objects.event import Event


class TestEventOps(unittest.TestCase):
    @mock.patch('ebcli.operations.gitops.get_default_branch')
    @mock.patch('ebcli.operations.gitops.get_default_repository')
    @mock.patch('ebcli.operations.gitops.io.echo')
    def test_print_current_codecommit_settings__codecommit_not_setup(
            self,
            echo_mock,
            get_default_repository_mock,
            get_default_branch_mock
    ):
        get_default_branch_mock.return_value = False
        get_default_repository_mock.return_value = False
        self.assertFalse(gitops.print_current_codecommit_settings())
        echo_mock.assert_not_called()

    @mock.patch('ebcli.operations.gitops.get_default_branch')
    @mock.patch('ebcli.operations.gitops.get_default_repository')
    @mock.patch('ebcli.operations.gitops.io.echo')
    def test_print_current_codecommit_settings__codecommit_is_setup(
            self,
            echo_mock,
            get_default_repository_mock,
            get_default_branch_mock
    ):
        get_default_branch_mock.return_value = False
        get_default_repository_mock.return_value = True
        self.assertTrue(gitops.print_current_codecommit_settings())
        echo_mock.assert_has_calls(
            [
                mock.call('Current CodeCommit setup:'),
                mock.call('  Repository: True'),
                mock.call('  Branch: False')
            ]
        )
        echo_mock.reset_mock()

        get_default_branch_mock.return_value = True
        get_default_repository_mock.return_value = False
        self.assertTrue(gitops.print_current_codecommit_settings())
        echo_mock.assert_has_calls(
            [
                mock.call('Current CodeCommit setup:'),
                mock.call('  Repository: False'),
                mock.call('  Branch: True')
            ]
        )
        echo_mock.reset_mock()

        get_default_branch_mock.return_value = True
        get_default_repository_mock.return_value = True
        self.assertTrue(gitops.print_current_codecommit_settings())
        echo_mock.assert_has_calls(
            [
                mock.call('Current CodeCommit setup:'),
                mock.call('  Repository: True'),
                mock.call('  Branch: True')
            ]
        )

    @mock.patch('ebcli.operations.gitops.set_repo_default_for_current_environment')
    @mock.patch('ebcli.operations.gitops.set_branch_default_for_current_environment')
    @mock.patch('ebcli.operations.gitops.fileoperations.write_config_setting')
    def test_disable_codecommit(
            self,
            write_config_setting_mock,
            set_branch_default_for_current_environment_mock,
            set_repo_default_for_current_environment_mock
    ):
        gitops.disable_codecommit()

        set_repo_default_for_current_environment_mock.assert_called_once_with(None)
        set_branch_default_for_current_environment_mock.assert_called_once_with(None)
        write_config_setting_mock.assert_has_calls(
            [
                mock.call('global', 'repository', None),
                mock.call('global', 'branch', None)
            ]
        )

    @mock.patch('ebcli.operations.gitops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.gitops.codecommit.region_supported')
    @mock.patch('ebcli.operations.gitops.print_current_codecommit_settings')
    @mock.patch('ebcli.controllers.initialize.get_repository_interactive')
    @mock.patch('ebcli.controllers.initialize.get_branch_interactive')
    @mock.patch('ebcli.operations.gitops.set_repo_default_for_current_environment')
    @mock.patch('ebcli.operations.gitops.set_branch_default_for_current_environment')
    @mock.patch('ebcli.operations.gitops.aws.get_region_name')
    @mock.patch('ebcli.operations.gitops.io.get_boolean_response')
    def test_initialize_codecommit(
            self,
            get_boolean_response_mock,
            get_region_name_mock,
            set_branch_default_for_current_environment_mock,
            set_repo_default_for_current_environment_mock,
            get_branch_interactive_mock,
            get_repository_interactive_mock,
            print_current_codecommit_settings_mock,
            region_supported_mock,
            get_source_control_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.is_setup.return_value = True
        get_source_control_mock.return_value = source_control_mock
        region_supported_mock.return_value = True
        get_boolean_response_mock.return_value = True
        get_repository_interactive_mock.return_value = 'my-repository'
        get_branch_interactive_mock.return_value = 'my-branch'

        gitops.initialize_codecommit()

        region_supported_mock.assert_called_once_with()
        get_boolean_response_mock.assert_called_once_with(
            text='Do you wish to continue?',
            default=True)
        set_repo_default_for_current_environment_mock.assert_called_once_with('my-repository')
        set_branch_default_for_current_environment_mock.assert_called_once_with('my-branch')

    @mock.patch('ebcli.operations.gitops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.gitops.codecommit.region_supported')
    @mock.patch('ebcli.operations.gitops.print_current_codecommit_settings')
    @mock.patch('ebcli.controllers.initialize.get_repository_interactive')
    @mock.patch('ebcli.controllers.initialize.get_branch_interactive')
    @mock.patch('ebcli.operations.gitops.set_repo_default_for_current_environment')
    @mock.patch('ebcli.operations.gitops.set_branch_default_for_current_environment')
    @mock.patch('ebcli.operations.gitops.aws.get_region_name')
    @mock.patch('ebcli.operations.gitops.io.get_boolean_response')
    @mock.patch('ebcli.operations.gitops.io.log_error')
    def test_initialize_codecommit__region_does_not_support_codecommit(
            self,
            log_error_mock,
            get_boolean_response_mock,
            get_region_name_mock,
            set_branch_default_for_current_environment_mock,
            set_repo_default_for_current_environment_mock,
            get_branch_interactive_mock,
            get_repository_interactive_mock,
            print_current_codecommit_settings_mock,
            region_supported_mock,
            get_source_control_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.is_setup.return_value = True
        get_source_control_mock.return_value = source_control_mock
        region_supported_mock.return_value = False
        get_region_name_mock.return_value = 'some-region'

        gitops.initialize_codecommit()

        region_supported_mock.assert_called_once_with()
        get_boolean_response_mock.assert_not_called()
        set_repo_default_for_current_environment_mock.assert_not_called()
        set_branch_default_for_current_environment_mock.assert_not_called()
        get_repository_interactive_mock.assert_not_called()
        get_branch_interactive_mock.assert_not_called()
        print_current_codecommit_settings_mock.assert_not_called()
        log_error_mock.assert_called_once_with('The region some-region is not supported by CodeCommit')

    @mock.patch('ebcli.operations.gitops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.gitops.codecommit.region_supported')
    @mock.patch('ebcli.operations.gitops.print_current_codecommit_settings')
    @mock.patch('ebcli.controllers.initialize.get_repository_interactive')
    @mock.patch('ebcli.controllers.initialize.get_branch_interactive')
    @mock.patch('ebcli.operations.gitops.set_repo_default_for_current_environment')
    @mock.patch('ebcli.operations.gitops.set_branch_default_for_current_environment')
    @mock.patch('ebcli.operations.gitops.aws.get_region_name')
    @mock.patch('ebcli.operations.gitops.io.get_boolean_response')
    @mock.patch('ebcli.operations.gitops.io.log_error')
    def test_initialize_codecommit__source_control_is_not_setup(
            self,
            log_error_mock,
            get_boolean_response_mock,
            get_region_name_mack,
            set_branch_default_for_current_environment_mock,
            set_repo_default_for_current_environment_mock,
            get_branch_interactive_mock,
            get_repository_interactive_mock,
            print_current_codecommit_settings_mock,
            region_supported_mock,
            get_source_control_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.is_setup.return_value = False
        get_source_control_mock.return_value = source_control_mock

        gitops.initialize_codecommit()

        region_supported_mock.assert_not_called()
        get_boolean_response_mock.assert_not_called()
        set_repo_default_for_current_environment_mock.assert_not_called()
        set_branch_default_for_current_environment_mock.assert_not_called()
        get_repository_interactive_mock.assert_not_called()
        get_branch_interactive_mock.assert_not_called()
        print_current_codecommit_settings_mock.assert_not_called()
        log_error_mock.assert_called_once_with('Cannot setup CodeCommit because there is no Source Control setup')

    @mock.patch('ebcli.operations.gitops.get_repo_default_for_current_environment')
    def test_get_default_repository(
            self,
            get_repo_default_for_current_environment_mock
    ):
        get_repo_default_for_current_environment_mock.return_value = 'my-repository'

        self.assertEqual(
            'my-repository',
            gitops.get_default_repository()
        )

    @mock.patch('ebcli.operations.gitops.get_repo_default_for_current_environment')
    def test_get_default_repository__could_not_find_repository(
            self,
            get_repo_default_for_current_environment_mock
    ):
        get_repo_default_for_current_environment_mock.return_value = None

        self.assertIsNone(gitops.get_default_repository())

    @mock.patch('ebcli.operations.gitops.get_branch_default_for_current_environment')
    def test_get_default_branch(
            self,
            get_branch_default_for_current_environment_mock
    ):
        get_branch_default_for_current_environment_mock.return_value = 'my-branch'

        self.assertEqual(
            'my-branch',
            gitops.get_default_branch()
        )

    @mock.patch('ebcli.operations.gitops.get_branch_default_for_current_environment')
    def test_get_default_branch__could_not_find_repository(
            self,
            get_branch_default_for_current_environment
    ):
        get_branch_default_for_current_environment.return_value = None

        self.assertIsNone(gitops.get_default_branch())

    @mock.patch('ebcli.operations.gitops.get_config_setting_from_current_environment_or_default')
    def test_get_repo_default_for_current_environment(
            self,
            get_config_setting_from_current_environment_or_default_mock
    ):
        gitops.get_repo_default_for_current_environment()
        get_config_setting_from_current_environment_or_default_mock.assert_called_once_with('repository')

    @mock.patch('ebcli.operations.gitops.get_config_setting_from_current_environment_or_default')
    def test_get_branch_default_for_current_environment(
            self,
            get_config_setting_from_current_environment_or_default_mock
    ):
        gitops.get_branch_default_for_current_environment()
        get_config_setting_from_current_environment_or_default_mock.assert_called_once_with('branch')

    @mock.patch('ebcli.operations.gitops.write_setting_to_current_environment_or_default')
    def test_set_repo_default_for_current_environment(
            self,
            write_setting_to_current_environment_or_default_mock
    ):
        gitops.set_repo_default_for_current_environment('my-repository')
        write_setting_to_current_environment_or_default_mock.assert_called_once_with('repository', 'my-repository')

    @mock.patch('ebcli.operations.gitops.write_setting_to_current_environment_or_default')
    def test_set_branch_default_for_current_environment(
            self,
            write_setting_to_current_environment_or_default_mock
    ):
        gitops.set_branch_default_for_current_environment('my-branch')
        write_setting_to_current_environment_or_default_mock.assert_called_once_with('branch', 'my-branch')


    @mock.patch('ebcli.operations.gitops.fileoperations.write_config_setting')
    def test_set_repo_default_for_global(
            self,
            write_config_setting_mock
    ):
        gitops.set_repo_default_for_global('my-repository')
        write_config_setting_mock.assert_called_once_with('global', 'repository', 'my-repository')

    @mock.patch('ebcli.operations.gitops.fileoperations.write_config_setting')
    def test_set_branch_default_for_global(
            self,
            write_config_setting_mock
    ):
        gitops.set_branch_default_for_global('my-branch')
        write_config_setting_mock.assert_called_once_with('global', 'branch', 'my-branch')

    @mock.patch('ebcli.operations.gitops.commonops.get_current_branch_environment')
    @mock.patch('ebcli.operations.gitops.fileoperations.get_config_setting')
    def test_get_setting_from_current_environment(
            self,
            get_config_setting_mock,
            get_current_branch_environment_mock
    ):
        get_current_branch_environment_mock.return_value = 'my-environment'
        get_config_setting_mock.return_value = {'key': 'value'}

        self.assertEqual('value', gitops.get_setting_from_current_environment('key'))
        get_config_setting_mock.assert_called_once_with('environment-defaults', 'my-environment')

        self.assertIsNone(gitops.get_setting_from_current_environment('absent-key'))

    @mock.patch('ebcli.operations.gitops.commonops.get_current_branch_environment')
    @mock.patch('ebcli.operations.gitops.fileoperations.write_config_setting')
    def test_write_setting_to_current_environment_or_default(
            self,
            write_config_setting_mock,
            get_current_branch_environment_mock
    ):
        get_current_branch_environment_mock.return_value = 'my-environment'

        gitops.write_setting_to_current_environment_or_default('key', 'value')

        write_config_setting_mock.assert_called_once_with(
            'environment-defaults', 'my-environment', {'key': 'value'}
        )

    @mock.patch('ebcli.operations.gitops.commonops.get_current_branch_environment')
    @mock.patch('ebcli.operations.gitops.fileoperations.write_config_setting')
    def test_write_setting_to_current_environment_or_default__defaults(
            self,
            write_config_setting_mock,
            get_current_branch_environment_mock
    ):
        get_current_branch_environment_mock.return_value = None

        gitops.write_setting_to_current_environment_or_default('key', 'value')

        write_config_setting_mock.assert_called_once_with(
            'global', 'key', 'value'
        )

    @mock.patch('ebcli.operations.gitops.get_setting_from_current_environment')
    def test_get_config_setting_from_current_environment_or_default(
            self,
            get_setting_from_current_environment_mock
    ):
        get_setting_from_current_environment_mock.return_value = 'value'

        self.assertEqual(
            'value',
            gitops.get_config_setting_from_current_environment_or_default('key')
        )

    @mock.patch('ebcli.operations.gitops.get_setting_from_current_environment')
    @mock.patch('ebcli.operations.gitops.fileoperations.get_config_setting')
    def test_get_config_setting_from_current_environment_or_default__environment_config_is_none(
            self,
            get_config_setting_mock,
            get_setting_from_current_environment_mock
    ):
        get_setting_from_current_environment_mock.return_value = None
        get_config_setting_mock.return_value = 'value'

        self.assertEqual(
            'value',
            gitops.get_config_setting_from_current_environment_or_default('key')
        )

        get_config_setting_mock.assert_called_once_with('global', 'key')

    @mock.patch('ebcli.operations.gitops.get_default_branch')
    @mock.patch('ebcli.operations.gitops.get_default_repository')
    def test_git_management_enabled(
            self,
            get_default_repository_mock,
            get_default_branch_mock,
    ):
        get_default_repository_mock.return_value = False
        get_default_branch_mock.return_value = False
        self.assertFalse(gitops.git_management_enabled())

        get_default_repository_mock.return_value = True
        get_default_branch_mock.return_value = False
        self.assertFalse(gitops.git_management_enabled())

        get_default_repository_mock.return_value = False
        get_default_branch_mock.return_value = True
        self.assertFalse(gitops.git_management_enabled())

        get_default_repository_mock.return_value = True
        get_default_branch_mock.return_value = True
        self.assertTrue(gitops.git_management_enabled())
