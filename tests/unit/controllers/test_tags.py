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
from mock import MagicMock, patch

from ebcli.objects.exceptions import NoEnvironmentForBranchError, InvalidOptionsError
from ebcli.controllers.tags import TagsController


class TestTags(unittest.TestCase):

    @patch('ebcli.core.io.log_error')
    @patch('ebcli.operations.commonops.get_current_branch_environment')
    def test_tags_command_fails_when_branch_has_no_default_environment(
            self,
            get_current_branch_environment,
            log_error
    ):
        get_current_branch_environment.return_value = None
        log_error.return_value = None

        controller = TagsController()
        controller.app = MagicMock()
        controller.app.pargs = self.__create_pargs(
            {
                'environment_name': None,
                'add': None,
                'delete': None,
                'update': None
            }
        )

        with self.assertRaises(NoEnvironmentForBranchError):
            controller.env_name()

    def test_tags__env_name__supplied_through_command_line(self):
        controller = TagsController()
        controller.app = MagicMock()

        controller.app.pargs = self.__create_pargs(
            {
                'environment_name': 'my_env',
                'add': None,
                'delete': None,
                'update': 'key1=value1'
            }
        )

        self.assertEqual('my_env', controller.env_name())

    @patch('ebcli.core.io.log_error')
    def test_tags_command_fails_when_list_appears_with_add_delete_or_update(self, log_error):
        log_error.return_value = None
        controller = TagsController()
        controller.app = MagicMock()

        controller.app.pargs = self.__create_pargs(
            {
                'environment_name': 'my_env',
                'add': 'key1=value1',
                'delete': None,
                'update': None
            }
        )
        self.__invoke_do_command_with_invalid_options_exception(controller)

        controller.app.pargs = self.__create_pargs(
            {
                'environment_name': 'my_env',
                'add': None,
                'delete': 'key1',
                'update': None
            }
        )
        self.__invoke_do_command_with_invalid_options_exception(controller)

        controller.app.pargs = self.__create_pargs(
            {
                'environment_name': 'my_env',
                'add': None,
                'delete': None,
                'update': 'key1=value1'
            }
        )
        self.__invoke_do_command_with_invalid_options_exception(controller)

    def __invoke_do_command_with_invalid_options_exception(self, controller):
        with self.assertRaises(InvalidOptionsError):
            controller.do_command()

    def __create_pargs(self, args):
        pargs = MagicMock()

        pargs.environment_name = args['environment_name']
        pargs.list = MagicMock(return_value='')
        pargs.add = MagicMock(return_value=args['add'])
        pargs.delete = MagicMock(return_value=args['delete'])
        pargs.update = MagicMock(return_value=args['update'])

        return pargs
