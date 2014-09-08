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

from ebcli.core import io


class TestFileOperations(unittest.TestCase):
    def setUp(self):
        pass

    @mock.patch('ebcli.core.io.prompt')
    def test_prompt_for_environment_name(self, mock_prompt):
        # Make a list of bad environment Names
        invalid_cases = [
            'Inv@lid',
            'sml',
            'this-name-is-too-long-99',
            'this-name-is-definitely-too-long-like-seriously-who-does-this',
            'bad:char',
            'bad_char',
            'bad+char',
            'bad=char',
            'bad?char',
            'bad>char',
            'bad\char',
            'bad/char',
            'bad#char',
            'bad?char',
            '-startswithhyphen',
            'endswithhyphen-',
            '-bothsideshyphen-',
            'spaces are bad',
            # end in valid case for loop completion
            'standard-name',
        ]

        # Make a list of good names
        valid_cases = [
            'ALL-UPPER',
            'MiXeD-CaSe',
            'normal-env-name',
            '1starts-with-num',
            'ends-with-num1',
            'has0-nums1-23422',
            'this-name-is-just-right',
            'four']

        mock_prompt.side_effect = invalid_cases

        # Do invalid cases. Should loop through them all
        result = io.prompt_for_environment_name()
        self.assertEqual(result, 'standard-name')
        self.assertEqual(mock_prompt.call_count, len(invalid_cases))

        # Do valid cases
        mock_prompt.side_effect = valid_cases
        for case in valid_cases:
            value = io.prompt_for_environment_name()
            self.assertEqual(value, case)