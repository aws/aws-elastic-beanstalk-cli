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

import sys

import unittest
from unittest import TestCase

from botocore.compat import six
from mock import patch

from ebcli.lib import utils
from ebcli.objects.exceptions import CommandError
StringIO = six.moves.StringIO


HELLO_WORLD_MSG = 'Hello, world!'
HAPPY_ARGS = ['echo', HELLO_WORLD_MSG]
OS_ERROR_ARGS = ['this_is_not_a_command']
COMMAND_ERROR_ARGS = ['date', 'illegal_argument']
MOCK_FILES = ['/a', '/b', '/c', '/d']


class TestUtils(TestCase):
    @unittest.skipIf(sys.platform.startswith('win'), 'Test is not equipped to run on Windows')
    @patch('ebcli.lib.utils.LOG')
    @patch('ebcli.lib.utils.sys.stdout', new_callable=StringIO)
    def test_exec_cmd_live_output_happy_case(self, out, LOG):
        expected_output = HELLO_WORLD_MSG + "\n"

        self.assertEquals(utils.exec_cmd(HAPPY_ARGS), expected_output)
        LOG.debug.assert_called_once_with(' '.join(HAPPY_ARGS))
        # Intercept stdout and ensure msg is printed
        self.assertEquals(out.getvalue(), expected_output)

    @patch('ebcli.lib.utils.LOG')
    def test_exec_cmd_live_output_oserror_case(self, LOG):
        self.assertRaises(OSError, utils.exec_cmd, OS_ERROR_ARGS)
        LOG.debug.assert_called_once_with(' '.join(OS_ERROR_ARGS))

    @unittest.skipIf(sys.platform.startswith('win'), 'Test is not equipped to run on Windows')
    @patch('ebcli.lib.utils.LOG')
    def test_exec_cmd_live_output_commanderror_case(self, LOG):
        self.assertRaises(CommandError, utils.exec_cmd, COMMAND_ERROR_ARGS)
        LOG.debug.assert_called_once_with(' '.join(COMMAND_ERROR_ARGS))

    def test_flatten_empty_list(self):
        self.assertEquals([], utils.flatten([]))

    def test_flatten_nested_single_list(self):
        self.assertEquals([0], utils.flatten([[0]]))

    def test_flatten_nested_long_list(self):
        self.assertEquals([0, 1, 2], utils.flatten([[0], [1], [2]]))

    @patch('os.path.getmtime')
    def test_last_modified_file(self, getmtime):
        getmtime.side_effect = [9.01, 200.0, 300.0, 5000.0]
        expected_last_mod_file = MOCK_FILES[-1]
        self.assertEquals(expected_last_mod_file,
                          utils.last_modified_file(MOCK_FILES))

    def test_anykey(self):
        key0, key1 = 'a', 'b'
        self.assertEquals(utils.anykey({key0: None}), key0)
        self.assertIn(utils.anykey({key0: None, key1: None}), {key0, key1})

    def test_merge_dicts_both_empty(self):
        self.assertDictEqual({}, utils.merge_dicts({}, {}))

    def test_merge_dicts_one_empty(self):
        mock_dict = {'abc': 123, 'bcd': 555}
        self.assertDictEqual(mock_dict, utils.merge_dicts(mock_dict, {}))
        self.assertDictEqual(mock_dict, utils.merge_dicts({}, mock_dict))

    def test_merge_dicts_not_overlapping(self):
        low_priority = {1: 1, 2: 2, 3: 3}
        high_priority = {'a': 'high_a', 'b': 'high_b', 'e': 'high_e'}
        expected = {1: 1, 2: 2, 3: 3, 'a': 'high_a', 'b': 'high_b', 'e': 'high_e'}

        self.assertDictEqual(expected, utils.merge_dicts(low_priority, high_priority))

    def test_merge_dicts_overlapping(self):
        low_priority = {'a': 'low_a', 'b': 'low_b', 'd': 'low_d'}
        high_priority = {'a': 'high_a', 'b': 'high_b', 'e': 'high_e'}
        expected = {'a': 'high_a', 'b': 'high_b', 'd': 'low_d', 'e': 'high_e'}

        self.assertDictEqual(expected, utils.merge_dicts(low_priority, high_priority))
