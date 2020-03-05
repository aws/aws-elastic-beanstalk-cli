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
import datetime
import sys

import unittest
from unittest import TestCase

from botocore.compat import six
from mock import call, patch

from ebcli.lib import utils
from ebcli.objects.exceptions import CommandError, InvalidOptionsError
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

        self.assertEqual(utils.exec_cmd(HAPPY_ARGS), expected_output)
        LOG.debug.assert_called_once_with(' '.join(HAPPY_ARGS))
        self.assertEqual(out.getvalue(), expected_output)

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
        self.assertEqual([], utils.flatten([]))

    def test_flatten_nested_single_list(self):
        self.assertEqual([0], utils.flatten([[0]]))

    def test_flatten_nested_long_list(self):
        self.assertEqual([0, 1, 2], utils.flatten([[0], [1], [2]]))

    def test_flatten__string_list(self):
        self.assertEqual(
            [
                '2018-09-15 19:41:43',
                'CREATE_IN_PROGRESS       ',
                'my-cfn-stack (AWS::CloudFormation::Stack)\nUser Initiated         '
            ],
            utils.flatten(
                [
                    ['2018-09-15 19:41:43'],
                    ['CREATE_IN_PROGRESS       '],
                    ['my-cfn-stack (AWS::CloudFormation::Stack)\nUser Initiated         ']
                ]
            )
        )

    @patch('os.path.getmtime')
    def test_last_modified_file(self, getmtime):
        getmtime.side_effect = [9.01, 200.0, 300.0, 5000.0]
        expected_last_mod_file = MOCK_FILES[-1]
        self.assertEqual(expected_last_mod_file,
                          utils.last_modified_file(MOCK_FILES))

    def test_anykey(self):
        key0, key1 = 'a', 'b'
        self.assertEqual(utils.anykey({key0: None}), key0)
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

    def test_parse_source__source_is_blank(self):
        self.assertEqual(
            (None, None, None),
            utils.parse_source('')
        )

    def test_parse_source__source_is_not_codecommit(self):
        with self.assertRaises(InvalidOptionsError) as context_manager:
            utils.parse_source('github')
        self.assertEqual(
            'Source location "github" is not supported by the EBCLI',
            str(context_manager.exception)
        )

    def test_parse_source__source_location_is_specified__repository_and_branch_are_not(self):
        self.assertEqual(
            ('codecommit', None, None),
            utils.parse_source('codecommit')
        )

    def test_parse_source__source_location_repository_and_branch_are_specified(self):
        self.assertEqual(
            ('codecommit', 'repository', 'branch'),
            utils.parse_source('codecommit/repository/branch')
        )

    def test_parse_source__branch_name_has_forward_slash(self):
        self.assertEqual(
            ('codecommit', 'repository', 'my/branch/name'),
            utils.parse_source('codecommit/repository/my/branch/name')
        )

    def test_pad_list(self):
        self.assertEqual(['text'], utils.padded_list(['text'], [1]))
        self.assertEqual(['text', '', '', ''], utils.padded_list(['text'], [1, 2, 3, 4]))
        self.assertEqual(
            ['text', 'hello, world', '', ''],
            utils.padded_list(['text', 'hello, world'], [1, 2, 3, 4])
        )
        self.assertEqual(
            ['text', 'hello, world'],
            utils.padded_list(['text', 'hello, world'], [1])
        )
        with self.assertRaises(AttributeError) as context_manager:
            utils.padded_list(['text'], [])

        self.assertEqual(
            'The reference_list argument must be non-empty.',
            str(context_manager.exception)
        )

    def test_pad_line(self):
        self.assertEqual('hello, world!\n', utils.padded_line('hello, world!'))
        self.assertEqual('  hello, world!\n', utils.padded_line('hello, world!', padding=2))
        self.assertEqual('hello, world!\n', utils.padded_line('hello, world!', padding=-1))
        self.assertEqual('hello, world!\n', utils.padded_line('hello, world!', padding='a'))

    def test_left_padded_string(self):
        self.assertEqual('  hello, world', utils.left_padded_string('hello, world', padding=2))

    def test_right_padded_string(self):
        self.assertEqual('hello, world  ', utils.right_padded_string('hello, world', padding=2))

    def test_longest_string(self):
        self.assertEqual(
            'abcde',
            utils.longest_string(['a', 'abc', 'abcde'])
        )

    def test_row_wrapper(self):
        string_width_mappings = [
            {
                'string': '2018-08-12 18:36:42',
                'width': 19
            },
            {
                'string': 'CREATE_COMPLETE',
                'width': 35
            },
            {
                'string': 'ServerlessRestApiDeployment47fc2d5f9d (AWS::ApiGateway::Deployment)\n'
                          'The API gateway, ServerlessRestApiDeployment47fc2d5f9d, was successfully built',
                'width': 67
            },
        ]
        self.assertEqual(
            [
                '2018-08-12 18:36:42   CREATE_COMPLETE                       ServerlessRestApiDeployment47fc2d5f9d (AWS::ApiGateway::Deployment)',
                '                                                            The API gateway, ServerlessRestApiDeployment47fc2d5f9d, was        ',
                '                                                            successfully built                                                 '
            ],
            utils.row_wrapper(string_width_mappings)
        )

    def test_row_wrapper__lengthy_resource_status(self):
        string_width_mappings = [
            {
                'string': '2018-08-12 18:36:42',
                'width': 19
            },
            {
                'string': 'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS',
                'width': 35
            },
            {
                'string': 'ServerlessRestApiDeployment47fc2d5f9d (AWS::ApiGateway::Deployment)\n'
                          'The API gateway, ServerlessRestApiDeployment47fc2d5f9d, was successfully built',
                'width': 67
            },
        ]
        self.assertEqual(
            [
                '2018-08-12 18:36:42   UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN   ServerlessRestApiDeployment47fc2d5f9d (AWS::ApiGateway::Deployment)',
                '                      _PROGRESS                             The API gateway, ServerlessRestApiDeployment47fc2d5f9d, was        ',
                '                                                            successfully built                                                 '
            ],
            utils.row_wrapper(string_width_mappings)
        )

    def test_random_string(self):
        utils.random_string()
        utils.random_string(length=10)

    def test_sleep(self):
        utils.sleep(sleep_time=0)

    def test_datetime_utcnow(self):
        now = datetime.datetime.utcnow()
        a_little_later = utils.datetime_utcnow()
        very_small_difference = datetime.timedelta(seconds=0.001)
        self.assertTrue(
            a_little_later - now < very_small_difference
        )

    def test_camel_to_snake__basic(self):
        input_str = 'fooBar'
        expected = 'foo_bar'

        result = utils.camel_to_snake(input_str)

        self.assertEqual(expected, result)

    def test_camel_to_snake__pascal(self):
        input_str = 'FooBar'
        expected = 'foo_bar'

        result = utils.camel_to_snake(input_str)

        self.assertEqual(expected, result)

    def test_camel_to_snake__complex(self):
        input_str = 'foo1Bar2__abcDef'
        expected = 'foo1_bar2__abc_def'

        result = utils.camel_to_snake(input_str)

        self.assertEqual(expected, result)

    def test_convert_dict_from_camel_to_snake__basic(self):
        input_dict = {
            'fooBar': 'fooBar',
            'FooBaz': 'FooBaz',
        }
        expected = {
            'foo_bar': 'fooBar',
            'foo_baz': 'FooBaz',
        }

        result = utils.convert_dict_from_camel_to_snake(input_dict)

        self.assertEqual(expected, result)

    def test_convert_dict_from_camel_to_snake__recursive(self):
        input_dict = {
            'fooBar': 'fooBar',
            'FooBaz': 'FooBaz',
            'nestedDict': {
                'abCd': 'abCd',
                'efGh': 'efGh',
            }
        }
        expected = {
            'foo_bar': 'fooBar',
            'foo_baz': 'FooBaz',
            'nested_dict': {
                'ab_cd': 'abCd',
                'ef_gh': 'efGh',
            }
        }

        result = utils.convert_dict_from_camel_to_snake(
            input_dict,
            recursive=True)

        self.assertEqual(expected, result)
