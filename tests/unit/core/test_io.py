# -*- coding: UTF-8 -*-
#
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
import sys

import mock
import unittest

from ebcli.core import io


class TestIo(unittest.TestCase):
    @mock.patch('ebcli.core.io.prompt')
    def test_prompt_for_environment_name(self, mock_prompt):
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
            'bad\\char',
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

        result = io.prompt_for_environment_name()
        self.assertEqual(result, 'standard-name')
        self.assertEqual(mock_prompt.call_count, len(invalid_cases))

        mock_prompt.side_effect = valid_cases
        for case in valid_cases:
            value = io.prompt_for_environment_name()
            self.assertEqual(value, case)

    @mock.patch('ebcli.core.io.get_input')
    def test_get_boolean_response(self, get_input_mock):
        get_input_mock.return_value = 'y'
        result = io.get_boolean_response()
        get_input_mock.assert_called_once_with('(Y/n)', default='y')
        self.assertTrue(result)

    @mock.patch('ebcli.core.io.get_input')
    def test_get_boolean_response__text_sans_default(self, get_input_mock):
        get_input_mock.return_value = 'y'
        result = io.get_boolean_response(text='This is the prompt text.')
        get_input_mock.assert_called_once_with(
            'This is the prompt text. (Y/n)',
            default='y')
        self.assertTrue(result)

    @mock.patch('ebcli.core.io.get_input')
    def test_get_boolean_response__text_default_false(self, get_input_mock):
        get_input_mock.return_value = 'y'
        result = io.get_boolean_response(
            text='This is the prompt text.',
            default=False)
        get_input_mock.assert_called_once_with(
            'This is the prompt text. (y/N)',
            default='n')
        self.assertTrue(result)

    @mock.patch('ebcli.core.io.get_input')
    def test_get_boolean_response__bad_input(self, get_input_mock):
        response_list = ['a', '1', 'Ys', 'x', '', 'nah', '?', 'y']
        get_input_mock.side_effect = response_list
        result = io.get_boolean_response()

        self.assertTrue(result)
        self.assertEqual(get_input_mock.call_count, len(response_list))

    @mock.patch('ebcli.core.io.get_input')
    def test_get_boolean_response_true(self, get_input_mock):
        get_input_mock.side_effect = ['y', 'Y', 'YES', 'yes', 'Yes']

        result1 = io.get_boolean_response()
        result2 = io.get_boolean_response()
        result3 = io.get_boolean_response()
        result4 = io.get_boolean_response()
        result5 = io.get_boolean_response()
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertTrue(result3)
        self.assertTrue(result4)
        self.assertTrue(result5)

    @mock.patch('ebcli.core.io.get_input')
    def test_get_boolean_response_false(self, get_input_mock):
        get_input_mock.side_effect = ['n', 'N', 'NO', 'no', 'No']
        result1 = io.get_boolean_response()
        result2 = io.get_boolean_response()
        result3 = io.get_boolean_response()
        result4 = io.get_boolean_response()
        result5 = io.get_boolean_response()
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

    @mock.patch('sys.stdout.isatty')
    def test_term_is_colorable(self, isatty_mock):
        isatty_mock.return_value = True

        self.assertTrue(io.term_is_colorable())

    @mock.patch('sys.stdout.isatty')
    def test_term_is_colorable(self, isatty_mock):
        isatty_mock.return_value = False

        self.assertFalse(io.term_is_colorable())

    def test_convert_to_string(self):
        class DummyObj:
            def __str__(self):
                return 'dummy_object'

        self.assertEqual('asasdad', io._convert_to_string('asasdad'))

        self.assertEqual('ßßßßß', io._convert_to_string(u'ßßßßß'))
        self.assertEqual('ßßßßß', io._convert_to_string(u'ßßßßß'.encode('utf-8')))

        self.assertEqual('10', io._convert_to_string(int(10)))
        self.assertEqual('10.09876', io._convert_to_string(10.09876))
        if sys.version_info < (3, 0):
            self.assertEqual('10', io._convert_to_string(long(10)))

        self.assertEqual('dummy_object', io._convert_to_string(DummyObj()))

    @mock.patch('ebcli.core.io.colorama.init')
    @mock.patch('ebcli.core.io.term_is_colorable')
    def test_bold(
            self,
            term_is_colorable_mock,
            init_mock
    ):
        term_is_colorable_mock.return_value = True
        self.assertEqual('\x1b[1mßßßßß\x1b[22m', io.bold(u'ßßßßß'))
        init_mock.assert_called_once()

    @mock.patch('ebcli.core.io.colorama.init')
    @mock.patch('ebcli.core.io.term_is_colorable')
    def test_bold__term_is_not_colorable(
            self,
            term_is_colorable_mock,
            init_mock
    ):
        term_is_colorable_mock.return_value = False
        self.assertEqual('ßßßßß', io.bold(u'ßßßßß'))
        init_mock.assert_not_called()

    def test_remap_color(self):
        self.assertEqual('YELLOW', io._remap_color('ORANGE'))
        self.assertEqual('WHITE', io._remap_color('GRAY'))
        self.assertEqual('WHITE', io._remap_color('GREY'))
        self.assertEqual('SOmE OtHEr cOLoR', io._remap_color('SOmE OtHEr cOLoR'))

    @mock.patch('ebcli.core.io.colorama.init')
    @mock.patch('ebcli.core.io.term_is_colorable')
    def test_color(
            self,
            term_is_colorable_mock,
            init_mock
    ):
        term_is_colorable_mock.return_value = True
        self.assertEqual('\x1b[33mßßßßß\x1b[39m', io.color('ORANGE', u'ßßßßß'))

        init_mock.assert_called_once()

    @mock.patch('ebcli.core.io.colorama.init')
    @mock.patch('ebcli.core.io.term_is_colorable')
    def test_color__term_is_not_colorable(
            self,
            term_is_colorable_mock,
            init_mock
    ):
        term_is_colorable_mock.return_value = False
        self.assertEqual('ßßßßß', io.color('ORANGE', u'ßßßßß'))

        init_mock.assert_not_called()

    @mock.patch('ebcli.core.io.colorama.init')
    @mock.patch('ebcli.core.io.term_is_colorable')
    def test_on_color(
            self,
            term_is_colorable_mock,
            init_mock
    ):
        term_is_colorable_mock.return_value = True
        self.assertEqual('\x1b[43mßßßßß\x1b[49m', io.on_color('ORANGE', u'ßßßßß'))

        init_mock.assert_called_once()

    @mock.patch('ebcli.core.io.colorama.init')
    @mock.patch('ebcli.core.io.term_is_colorable')
    def test_on_color__term_is_not_colorable(
            self,
            term_is_colorable_mock,
            init_mock
    ):
        term_is_colorable_mock.return_value = False
        self.assertEqual('ßßßßß', io.on_color('ORANGE', u'ßßßßß'))

        init_mock.assert_not_called()

    @mock.patch('ebcli.core.io.print_')
    def test_echo_and_justify(self, print_mock):
        io.echo_and_justify(4, 'how ', 'now ', 'brown ', 'cow ')

        print_mock.assert_called_once_with('how now brown cow')

    @mock.patch('ebcli.core.io.print_')
    def test_echo(self, print_mock):
        io.echo(
            'how ', 'now ', 'brown ', 'cow ',
            sep=','
        )

        print_mock.assert_called_once_with('how ', 'now ', 'brown ', 'cow ', sep=',')

    @mock.patch('ebcli.core.io.echo')
    def test_log_alert(self, echo_mock):
        io.log_alert('hello, world!')

        echo_mock.assert_called_once_with('Alert:', 'hello, world!')

    @mock.patch('ebcli.core.io.ebglobals')
    @mock.patch('ebcli.core.io.echo')
    def test_log_info(
            self,
            echo_mock,
            ebglobals_mock
    ):
        io.log_info('hello, world!')
        echo_mock.assert_not_called()

    @mock.patch('ebcli.core.io.ebglobals', spec={})
    @mock.patch('ebcli.core.io.echo')
    def test_log_info__cement_application_not_defined_yet(
            self,
            echo_mock,
            ebglobals_mock
    ):
        io.log_info('hello, world!')
        echo_mock.assert_called_once_with('INFO: hello, world!')

    @mock.patch('ebcli.core.io.ebglobals')
    @mock.patch('ebcli.core.io.echo')
    def test_log_warning(
            self,
            echo_mock,
            ebglobals_mock
    ):
        io.log_warning('hello, world!')
        echo_mock.assert_not_called()

    @mock.patch('ebcli.core.io.ebglobals', spec={})
    @mock.patch('ebcli.core.io.echo')
    def test_log_warning__cement_application_not_defined_yet(
            self,
            echo_mock,
            ebglobals_mock
    ):
        io.log_warning('hello, world!')
        echo_mock.assert_called_once_with('WARN: hello, world!')

    @mock.patch('ebcli.core.io.ebglobals')
    def test_log_error__debug_mode(
            self,
            ebglobals_mock
    ):
        ebglobals_mock.app.pargs.debug = True
        io.log_error('hello, world!')
        ebglobals_mock.app.log.error.asswert_called_once_with()

    @mock.patch('ebcli.core.io.ebglobals')
    @mock.patch('ebcli.core.io.echo')
    def test_log_error(
            self,
            echo_mock,
            ebglobals_mock
    ):
        ebglobals_mock.app.pargs.debug = False

        io.log_error('hello, world!')

        ebglobals_mock.app.log.error.assert_not_called()
        echo_mock.assert_called_once_with('ERROR: hello, world!')

    @mock.patch('ebcli.core.io.ebglobals', spec={})
    @mock.patch('ebcli.core.io.echo')
    def test_log_error__cement_app_not_initialized_yet(
            self,
            echo_mock,
            ebglobals_mock
    ):
        io.log_error('hello, world!')

        echo_mock.assert_called_once_with('ERROR: hello, world!')

    @mock.patch('ebcli.core.io._get_input')
    def test_get_input(self, _get_input_mock):
        _get_input_mock.return_value = 'customer input'
        self.assertEqual(
            'customer input',
            io.get_input('some prompt')
        )

        _get_input_mock.assert_called_once_with('some prompt')

    @mock.patch('ebcli.core.io._get_input')
    def test_get_input__use_default(self, _get_input_mock):
        _get_input_mock.return_value = ''
        self.assertEqual(
            'default customer input',
            io.get_input('some prompt', default='default customer input')
        )

        _get_input_mock.assert_called_once_with('some prompt')

    @mock.patch('ebcli.core.io.pydoc.pager')
    def test_echo_with_pager(self, pager_mock):
        io.echo_with_pager('some text')
        pager_mock.assert_called_once_with('some text')

    @mock.patch('ebcli.core.io.get_input')
    def test_prompt(self, get_input_mock):
        get_input_mock.return_value = '10'

        io.prompt('some text', default='22')

        get_input_mock.assert_called_once_with('(some text)', '22')

    def test_prompt_for_unique_name__default_is_the_list(self):
        with self.assertRaises(AssertionError) as context_manager:
            io.prompt_for_unique_name('default', ['default', 'default_2'])
        self.assertEqual('Default name is not unique', str(context_manager.exception))

    @mock.patch('ebcli.core.io.prompt')
    @mock.patch('ebcli.core.io.echo')
    def test_prompt_for_unique_name__default_is_the_list(
            self,
            echo_mock,
            prompt_mock
    ):
        prompt_mock.side_effect = [
            'name_1',
            'name_2',
            'name_3',
        ]
        self.assertEqual(
            'name_3',
            io.prompt_for_unique_name('default', ['name_1', 'name_2'])
        )

        echo_mock.assert_has_calls(
            [
                mock.call('Sorry that name already exists, try another.'),
                mock.call('Sorry that name already exists, try another.')
            ]
        )

    @mock.patch('ebcli.core.io.getpass.getpass')
    def test_get_pass__gets_right_first_time(
            self,
            get_pass_mock
    ):
        get_pass_mock.side_effect = [
            'password',
            'password',
        ]

        self.assertEqual(
            'password',
            io.get_pass('')
        )

    @mock.patch('ebcli.core.io.getpass.getpass')
    def test_get_pass__gets_right_second_time(
            self,
            get_pass_mock
    ):
        get_pass_mock.side_effect = [
            'password',
            'passwor∂',
            'password',
            'password',
        ]

        self.assertEqual(
            'password',
            io.get_pass('')
        )

        self.assertEqual(4, get_pass_mock.call_count)

    @mock.patch('ebcli.core.io.get_input')
    def test_validate_action__mismatch(
            self,
            get_input_mock
    ):
        get_input_mock.return_value = 'unexpected_input'

        with self.assertRaises(io.ValidationError) as context_manager:
            io.validate_action('customer prompt', 'expected_input')

        self.assertEqual('Names do not match. Exiting.', str(context_manager.exception))

    @mock.patch('ebcli.core.io.get_input')
    def test_validate_action(
            self,
            get_input_mock
    ):
        get_input_mock.return_value = 'expected_input'

        io.validate_action('customer prompt', 'expected_input')

    @mock.patch('ebcli.core.io.sys.stdout.write')
    def test_update_upload_progress__progress_is_between_zero_and_one(
            self,
            write_mock
    ):
        io.update_upload_progress(0.50)

        write_mock.assert_called_once_with(
            '\rUploading: [#########################-------------------------] 50% '
        )

    @mock.patch('ebcli.core.io.sys.stdout.write')
    def test_update_upload_progress__progress_is_negative(
            self,
            write_mock
    ):
        io.update_upload_progress(-1)

        write_mock.assert_called_once_with(
            '\rUploading: [--------------------------------------------------] 0% Halt...\r\n'
        )

    @mock.patch('ebcli.core.io.sys.stdout.write')
    def test_update_upload_progress__progress_is_zero(
            self,
            write_mock
    ):
        io.update_upload_progress(0)

        write_mock.assert_called_once_with(
            '\rUploading: [--------------------------------------------------] 0% '
        )

    @mock.patch('ebcli.core.io.sys.stdout.write')
    def test_update_upload_progress__progress_is_non_numerical(
            self,
            write_mock
    ):
        io.update_upload_progress('a')

        write_mock.assert_called_once_with(
            '\rUploading: [--------------------------------------------------] 0% error: progress var must be float\r\n'
        )

    @mock.patch('ebcli.core.io.sys.stdout.write')
    def test_update_upload_progress__progress_is_complete(
            self,
            write_mock
    ):
        io.update_upload_progress(1)

        write_mock.assert_called_once_with(
            '\rUploading: [##################################################] 100% Done...\r\n'
        )
