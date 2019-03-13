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

import unittest
from mock import MagicMock, patch

from ebcli.controllers import tags
from ebcli.objects.exceptions import NoEnvironmentForBranchError, InvalidOptionsError
from ebcli.operations import commonops
from ebcli.core import fileoperations
from ebcli.core.ebcore import EB

class TestTags(unittest.TestCase):

    def setUp(self):
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')

        os.chdir('testDir')

        fileoperations.create_config_file(
            'test-app',
            'us-west-2',
            'php'
        )

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

    @patch('ebcli.controllers.tags.TagsController.get_env_name')
    def test_tags__command_fails_when_branch_has_no_default_environment(
            self,
            get_env_name_mock,
    ):
        get_env_name_mock.side_effect = NoEnvironmentForBranchError

        app = EB(argv=['tags', '--list'])
        app.setup()
        with self.assertRaises(NoEnvironmentForBranchError):
            app.run()

    @patch('ebcli.controllers.tags.elasticbeanstalk.get_environment_arn')
    @patch('ebcli.controllers.tags.TagOps')
    def test_tags__environment_passed_as_positional__default_env_exists_in_config_yml__the_environments_are_different(
            self,
            TagOps_mock,
            get_environment_arn_mock
    ):
        tagops_mock = MagicMock()
        TagOps_mock.return_value = tagops_mock
        commonops.set_environment_for_current_branch('some_env')

        app = EB(argv=['tags', '--update', 'key1=value1', 'env_name'])
        app.setup()
        app.run()

        get_environment_arn_mock.assert_called_once_with('env_name')
        tagops_mock.update_tags.assert_called_once_with(tags.Environment)

    @patch('ebcli.controllers.tags.elasticbeanstalk.get_environment_arn')
    @patch('ebcli.controllers.tags.TagOps')
    def test_tags__environment_passed_as_positional__default_env_absent_in_config_yml(
            self,
            TagOps_mock,
            get_environment_arn_mock
    ):
        tagops_mock = MagicMock()
        TagOps_mock.return_value = tagops_mock
        commonops.set_environment_for_current_branch(None)

        app = EB(argv=['tags', '--update', 'key1=value1', 'env_name'])
        app.setup()
        app.run()

        get_environment_arn_mock.assert_called_once_with('env_name')
        tagops_mock.update_tags.assert_called_once_with(tags.Environment)

    @patch('ebcli.controllers.tags.TagOps')
    def test_tags__environment_passed_as_resource_argument__default_env_present_in_config_yml(
            self,
            TagOps_mock,
    ):
        tagops_mock = MagicMock()
        TagOps_mock.return_value = tagops_mock
        commonops.set_environment_for_current_branch('default-env')

        app = EB(
            argv=[
                'tags',
                '--update', 'key1=value1',
                '--resource',
                    'arn:aws:elasticbeanstalk:us-west-2:123123123123:'
                    'environment/my-application/environment-1'
            ])
        app.setup()
        app.run()

        tagops_mock.update_tags.assert_called_once_with(tags.Environment)

    @patch('ebcli.controllers.tags.TagOps')
    def test_tags__environment_passed_as_resource_argument__default_env_absent_in_config_yml(
            self,
            TagOps_mock,
    ):
        tagops_mock = MagicMock()
        TagOps_mock.return_value = tagops_mock
        commonops.set_environment_for_current_branch(None)

        app = EB(
            argv=[
                'tags',
                '--update', 'key1=value1',
                '--resource',
                'arn:aws:elasticbeanstalk:us-west-2:123123123123:'
                'environment/my-application/environment-1'
            ])
        app.setup()
        app.run()

        tagops_mock.update_tags.assert_called_once_with(tags.Environment)

    @patch('ebcli.controllers.tags.TagOps')
    def test_tags__other_resource_passed_as_resource_argument__default_env_present_in_config_yml(
            self,
            TagOps_mock,
    ):
        tagops_mock = MagicMock()
        TagOps_mock.return_value = tagops_mock
        commonops.set_environment_for_current_branch('default-env')

        app = EB(
            argv=[
                'tags',
                '--update', 'key1=value1',
                '--resource',
                'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.0'
            ])
        app.setup()
        app.run()

        tagops_mock.update_tags.assert_called_once_with(None)

    @patch('ebcli.controllers.tags.TagOps')
    def test_tags__other_resource_passed_as_resource_argument__default_env_absent_in_config_yml(
            self,
            TagOps_mock,
    ):
        tagops_mock = MagicMock()
        TagOps_mock.return_value = tagops_mock
        commonops.set_environment_for_current_branch(None)

        app = EB(
            argv=[
                'tags',
                '--update', 'key1=value1',
                '--resource',
                    'arn:aws:elasticbeanstalk:us-west-2:123123123:platform/custom-platform-2/1.0.0'
            ])
        app.setup()
        app.run()

        tagops_mock.update_tags.assert_called_once_with(None)

    @patch('ebcli.controllers.tags.TagsController.get_env_name')
    @patch('ebcli.operations.tagops.tagops.TagOps.update_tags')
    @patch('ebcli.operations.tagops.tagops.TagOps.handle_update_string')
    @patch('ebcli.operations.tagops.tagops.TagOps.handle_deletion_string')
    @patch('ebcli.operations.tagops.tagops.TagOps.handle_addition_string')
    @patch('ebcli.lib.elasticbeanstalk.get_environment_arn')
    def test_tags__env_name__supplied_through_command_line__update(
            self,
            get_environment_arn_mock,
            handle_addition_mock,
            handle_delete_mock,
            handle_update_mock,
            update_tags_mock,
            get_env_name_mock,
    ):
        get_env_name_mock.return_value = 'my_env'
        get_environment_arn_mock.return_value = 'my_env_arn'
        app = EB(argv=['tags', 'my_env', '--update', 'key1=value1'])
        app.setup()
        app.run()

        handle_addition_mock.assert_not_called()
        handle_delete_mock.assert_not_called()
        handle_update_mock.assert_called_once_with('key1=value1')

        update_tags_mock.assert_called_once_with(tags.Environment)

    @patch('ebcli.controllers.tags.TagsController.get_env_name')
    @patch('ebcli.operations.tagops.tagops.TagOps.update_tags')
    @patch('ebcli.operations.tagops.tagops.TagOps.handle_update_string')
    @patch('ebcli.operations.tagops.tagops.TagOps.handle_deletion_string')
    @patch('ebcli.operations.tagops.tagops.TagOps.handle_addition_string')
    @patch('ebcli.lib.elasticbeanstalk.get_environment_arn')
    def test_tags__env_name__supplied_through_command_line__delete(
            self,
            get_environment_arn_mock,
            handle_addition_mock,
            handle_delete_mock,
            handle_update_mock,
            update_tags_mock,
            get_env_name_mock,
    ):
        get_env_name_mock.return_value = 'my_env'
        get_environment_arn_mock.return_value = 'my_env_arn'
        app = EB(argv=['tags', 'my_env', '--delete', 'key1'])
        app.setup()
        app.run()

        handle_addition_mock.assert_not_called()
        handle_delete_mock.assert_called_once_with('key1')
        handle_update_mock.assert_not_called()

        update_tags_mock.assert_called_once_with(tags.Environment)

    @patch('ebcli.controllers.tags.TagsController.get_env_name')
    @patch('ebcli.operations.tagops.tagops.TagOps.update_tags')
    @patch('ebcli.operations.tagops.tagops.TagOps.handle_update_string')
    @patch('ebcli.operations.tagops.tagops.TagOps.handle_deletion_string')
    @patch('ebcli.operations.tagops.tagops.TagOps.handle_addition_string')
    @patch('ebcli.lib.elasticbeanstalk.get_environment_arn')
    def test_tags__env_name__supplied_through_command_line__add(
            self,
            get_environment_arn_mock,
            handle_addition_mock,
            handle_delete_mock,
            handle_update_mock,
            update_tags_mock,
            get_env_name_mock,
    ):
        get_env_name_mock.return_value = 'my_env'
        get_environment_arn_mock.return_value = 'my_env_arn'
        app = EB(argv=['tags', 'my_env', '--add', 'key1=value1'])
        app.setup()
        app.run()

        handle_delete_mock.assert_not_called()
        handle_addition_mock.assert_called_once_with('key1=value1')
        handle_update_mock.assert_not_called()

        update_tags_mock.assert_called_once_with(tags.Environment)

    @patch('ebcli.controllers.tags.TagsController.get_env_name')
    def test_tags_command_fails_when_list_appears_with_add_delete_or_update(
            self,
            get_env_name_mock,
    ):
        get_env_name_mock.return_value = 'my_env'
        app = EB(argv=['tags', 'my_env', '--add', 'key1=value1', '--list'])
        app.setup()

        with self.assertRaises(InvalidOptionsError):
            app.run()

    @patch('ebcli.controllers.tags.TagsController.get_env_name')
    @patch('ebcli.operations.tagops.tagops.TagOps.update_tags')
    @patch('ebcli.operations.tagops.tagops.TagOps.handle_update_string')
    @patch('ebcli.operations.tagops.tagops.TagOps.handle_deletion_string')
    @patch('ebcli.operations.tagops.tagops.TagOps.handle_addition_string')
    @patch('ebcli.lib.elasticbeanstalk.get_environment_arn')
    def test_tags__resource__supplied_through_command_line__add(
            self,
            get_environment_arn_mock,
            handle_addition_mock,
            handle_delete_mock,
            handle_update_mock,
            update_tags_mock,
            get_env_name_mock,
    ):
        get_env_name_mock.return_value = ''
        get_environment_arn_mock.return_value = 'my_env_arn'
        app = EB(argv=['tags', '--resource', 'test_arn_name', '--add', 'key1=value1'])
        app.setup()
        app.run()

        handle_delete_mock.assert_not_called()
        handle_addition_mock.assert_called_once_with('key1=value1')
        handle_update_mock.assert_not_called()

        update_tags_mock.assert_called_once_with(None)

    @patch('ebcli.controllers.tags.TagsController.get_env_name')
    def test_tags__resource_and_environment_name_specified__failure(
            self,
            get_env_name_mock,
    ):
        get_env_name_mock.return_value = 'my_env'
        app = EB(argv=['tags', 'my_env', '--add', 'key1=value1', '--resource', 'my_arn'])
        app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            app.run()

        self.assertEqual(
            "You can't specify the '--resource' option with the "
            "'environment' positional argument",
            str(context_manager.exception))

    @patch('ebcli.controllers.tags.TagsController.get_env_name')
    def test_tags__failure_case__no_action(
            self,
            get_env_name_mock,
    ):
        get_env_name_mock.return_value = 'my_env'
        app = EB(argv=['tags', 'my_env'])
        app.setup()
        with self.assertRaises(InvalidOptionsError) as context_manager:
            app.run()

        self.assertEqual(
            'usage: eb tags [<environment_name>] option [options ...]',
            str(context_manager.exception)
        )
