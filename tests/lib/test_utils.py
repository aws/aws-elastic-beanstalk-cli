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

from unittest import TestCase
from mock import patch
from ebcli.lib import utils
from ebcli.objects.exceptions import CommandError
from botocore.compat import six
StringIO = six.moves.StringIO


HELLO_WORLD_MSG = 'Hello, world!'
HAPPY_ARGS = ['echo', HELLO_WORLD_MSG]
OS_ERROR_ARGS = ['this_is_not_a_command']
COMMAND_ERROR_ARGS = ['date', 'illegal_argument']
MOCK_FILES = ['/a', '/b', '/c', '/d']


class TestUtils(TestCase):
    @patch('ebcli.lib.utils.LOG')
    @patch('ebcli.lib.utils.sys.stdout', new_callable=StringIO)
    def test_exec_cmd_live_output_happy_case(self, out, LOG):
        expected_output = HELLO_WORLD_MSG + '\n'

        self.assertEquals(utils.exec_cmd(HAPPY_ARGS), expected_output)
        LOG.debug.assert_called_once_with(' '.join(HAPPY_ARGS))
        # Intercept stdout and ensure msg is printed
        self.assertEquals(out.getvalue(), expected_output)

    @patch('ebcli.lib.utils.LOG')
    def test_exec_cmd_live_output_oserror_case(self, LOG):
        self.assertRaises(OSError, utils.exec_cmd, OS_ERROR_ARGS)
        LOG.debug.assert_called_once_with(' '.join(OS_ERROR_ARGS))

    @patch('ebcli.lib.utils.LOG')
    def test_exec_cmd_live_output_commanderror_case(self, LOG):
        self.assertRaises(CommandError, utils.exec_cmd, COMMAND_ERROR_ARGS)
        LOG.debug.assert_called_once_with(' '.join(COMMAND_ERROR_ARGS))

    def test_flatten_empty_list(self):
        self.assertEquals(utils.flatten([]), [])

    def test_flatten_nested_single_list(self):
        self.assertEquals(utils.flatten([[0]]), [0])

    def test_flatten_nested_long_list(self):
        self.assertEquals(utils.flatten([[0],[1],[2]]), [0,1,2])

    @patch('os.path.getmtime')
    def test_last_modified_file(self, getmtime):
        getmtime.side_effect = [9.01, 200.0, 300.0, 5000.0]
        expected_last_mod_file = MOCK_FILES[-1]
        self.assertEquals(utils.last_modified_file(MOCK_FILES),
                          expected_last_mod_file)

    def test_anykey(self):
        key0, key1 = 'a', 'b'
        self.assertEquals(utils.anykey({key0: None}), key0)
        self.assertIn(utils.anykey({key0: None, key1: None}), {key0, key1})
