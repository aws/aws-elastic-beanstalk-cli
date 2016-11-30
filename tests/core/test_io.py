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
            'this-name-is-now-fine-99',
            '1234567890123456789012345678901234567890',
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

    @mock.patch('ebcli.core.io.get_input')
    def test_get_boolean_response_bad(self, mock_io):
        # populate with all bad responses
        # Last response must be valid in order to terminate loop
        response_list = ['a', '1', 'Ys', 'x', '', 'nah', '?', 'y']
        mock_io.side_effect = response_list
        result = io.get_boolean_response()

        #test
        self.assertTrue(result)
        self.assertEqual(mock_io.call_count, len(response_list))

    @mock.patch('ebcli.core.io.get_input')
    def test_get_boolean_response_true(self, mock_io):
        mock_io.side_effect = ['y', 'Y', 'YES', 'yes', 'Yes']
        result1 = io.get_boolean_response()  # test with y
        result2 = io.get_boolean_response()  # test with Y
        result3 = io.get_boolean_response()  # test with YES
        result4 = io.get_boolean_response()  # test with yes
        result5 = io.get_boolean_response()  # test with Yes
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertTrue(result3)
        self.assertTrue(result4)
        self.assertTrue(result5)

    @mock.patch('ebcli.core.io.get_input')
    def test_get_boolean_response_false(self, mock_io):
        mock_io.side_effect = ['n', 'N', 'NO', 'no', 'No']
        result1 = io.get_boolean_response()  # test with n
        result2 = io.get_boolean_response()  # test with N
        result3 = io.get_boolean_response()  # test with NO
        result4 = io.get_boolean_response()  # test with no
        result5 = io.get_boolean_response()  # test with No
        self.assertFalse(result1)
        self.assertFalse(result2)
        self.assertFalse(result3)
        self.assertFalse(result4)
        self.assertFalse(result5)

    @mock.patch('ebcli.core.io.sys')
    def test_event_streamer(self, mock_sys):
        mock_sys.stdout.isatty.return_value = True
        with mock.patch('ebcli.core.io.echo') as echo_mocked:
            streamer = io.get_event_streamer()
            streamer.stream_event("msg1")
            streamer.stream_event("msg2")
            echo_mocked.assert_called_with(streamer.prompt, end='')
            streamer.end_stream()
        self.assertEqual(streamer.eventcount, 2, "Expected event count to be 2 but was: {0}".format(streamer.eventcount))

    @mock.patch('ebcli.core.io.sys')
    def test_event_streamer_with_unsafe_exit(self, mock_sys):
        mock_sys.stdout.isatty.return_value = True
        with mock.patch('ebcli.core.io.echo') as echo_mocked:
            streamer = io.get_event_streamer()
            streamer.stream_event("msg1", safe_to_quit=False)
            echo_mocked.assert_called_with(streamer.unsafe_prompt, end='')
            streamer.end_stream()
        self.assertEqual(streamer.eventcount, 1, "Expected event count to be 1 but was: {0}".format(streamer.eventcount))

    @mock.patch('ebcli.core.io.sys')
    def test_pipe_streamer(self, mock_sys):
        mock_sys.stdout.isatty.return_value = False
        message = "msg1"
        with mock.patch('ebcli.core.io.echo') as echo_mocked:
            streamer = io.get_event_streamer()
            streamer.stream_event(message)
            echo_mocked.assert_called_with(message)
            streamer.end_stream()
        self.assertEqual(streamer.eventcount, 0, "Expected event count to be 0 but was: {0}".format(streamer.eventcount))