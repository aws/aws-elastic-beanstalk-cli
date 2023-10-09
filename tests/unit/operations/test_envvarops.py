# -*- coding: utf-8 -*-

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
from collections import Counter

import mock
from six import iteritems
import unittest

from ebcli.operations import envvarops

from .. import mock_responses

class TestEnvvarOps(unittest.TestCase):

    def assertListsOfDictsEquivalent(self, ls1, ls2):
        return self.assertEqual(
            Counter(frozenset(iteritems(d)) for d in ls1),
            Counter(frozenset(iteritems(d)) for d in ls2))

    def test_sanitize_environment_variables_from_customer_input(self):
        environment_variables_input = '  """  DB_USER"""   =     "\"  r=o\"o\'t\"\"  "   ,  DB_PAS\\ = SWORD="\"pass=\'\"word\""'

        self.assertEqual(
            [
                '  DB_USER="  r=o"o\'t""  ',
                'DB_PAS\\=SWORD=""pass=\'"word"'
            ],
            envvarops.sanitize_environment_variables_from_customer_input(environment_variables_input)
        )

    def test_sanitize_environment_variables_from_customer_input_blank_key(self):
        with self.assertRaises(envvarops.InvalidSyntaxError):
            envvarops.sanitize_environment_variables_from_customer_input('=')

        with self.assertRaises(envvarops.InvalidSyntaxError):
            envvarops.sanitize_environment_variables_from_customer_input('=bar')

    def test_create_environment_variables_list_empty(self):
        options, options_to_remove = envvarops.create_environment_variables_list([])
        self.assertEqual(options, list())
        self.assertEqual(options_to_remove, list())

        options, options_to_remove = envvarops.create_environment_variables_list(
            [],
            as_option_settings=False
        )
        self.assertEqual(options, dict())
        self.assertEqual(options_to_remove, set())

    def test_create_environment_variables_list_blank_key(self):
        with self.assertRaises(envvarops.InvalidSyntaxError):
            envvarops.create_environment_variables_list(['='])

        with self.assertRaises(envvarops.InvalidSyntaxError):
            envvarops.create_environment_variables_list(['=bar'])

    def test_create_environment_variables_list_simple(self):
        namespace = 'aws:elasticbeanstalk:application:environment'

        options, options_to_remove = envvarops.create_environment_variables_list(['foo=bar'])
        self.assertListsOfDictsEquivalent(
            options,
            [
                dict(
                    Namespace=namespace,
                    OptionName='foo',
                    Value='bar'
                )
            ]
        )
        self.assertListEqual(options_to_remove, list())

        options, options_to_remove = envvarops.create_environment_variables_list(['foo=bar', 'fish=good'])
        self.assertListsOfDictsEquivalent(
            options,
            [
                dict(
                    Namespace=namespace,
                    OptionName='foo',
                    Value='bar'
                ),
                dict(
                    Namespace=namespace,
                    OptionName='fish',
                    Value='good'
                )
            ]
        )
        self.assertEqual(options_to_remove, list())

        options, options_to_remove = envvarops.create_environment_variables_list(
            ['foo=bar', 'fish=good', 'trout=', 'baz='])
        self.assertListsOfDictsEquivalent(
            options,
            [
                dict(
                    Namespace=namespace,
                    OptionName='foo',
                    Value='bar'
                ),
                dict(
                    Namespace=namespace,
                    OptionName='fish',
                    Value='good'
                )
            ]
        )
        self.assertListsOfDictsEquivalent(
            options_to_remove, [
                dict(
                    Namespace=namespace,
                    OptionName='trout'
                ),
                dict(
                    Namespace=namespace,
                    OptionName='baz'
                )
            ]
        )

    def test_create_envvars_not_as_option_settings(self):
        options, options_to_remove = envvarops.create_environment_variables_list(
            ['foo=bar'],
            as_option_settings=False
        )
        self.assertEqual(options, dict(foo='bar'))
        self.assertEqual(options_to_remove, set())

        options, options_to_remove = envvarops.create_environment_variables_list(
            ['foo=bar', 'fish=good'],
            as_option_settings=False
        )
        self.assertDictEqual(options, dict(foo='bar', fish='good'))
        self.assertEqual(options_to_remove, set())

        options, options_to_remove = envvarops.create_environment_variables_list(
            ['foo=bar', 'fish=good', 'trout=', 'baz='],
            as_option_settings=False
        )
        self.assertDictEqual(options, dict(foo='bar', fish='good'))
        self.assertEqual(options_to_remove, {'trout', 'baz'})

    def test_create_envvars_crazy_characters(self):
        string1 = 'http://some.url.com/?quer=true&othersutff=1'
        string2 = 'some other !@=:;#$%^&*() weird, key'

        options, options_to_remove = envvarops.create_environment_variables_list(
            [
                'foo=' + string1,
                'weird er value='+ string2,
                'DB_USER="  r=o"o\'t""',
                'DB_PAS\\=SWORD=""pass=\'"word"'
            ],
            as_option_settings=False
        )
        self.assertEqual(
            options,
            {
                'foo': string1,
                'weird er value': string2,
                'DB_PAS\\': 'SWORD=""pass=\'"word"',
                'DB_USER': '"  r=o"o\'t""',
            }
        )
        self.assertEqual(options_to_remove, set())

    def test_create_envvars_error_because_of_double_quote_in_key(self):
        with self.assertRaises(envvarops.InvalidSyntaxError):
            envvarops.create_environment_variables_list(
                [
                    'DB_\"PAS\\=SWORD=""pass=\'"word"'
                ],
                as_option_settings=False
            )

    def test_create_envvars_not_bad_characters(self):
        strings = [
            '!hello',
            ',hello',
            '?hello',
            ';hello',
            '=hello',
            '$hello',
            '%hello',
            '😊'
        ]
        for s in strings:
            options, options_to_remove = envvarops.create_environment_variables_list(
                ['foo=' + s],
                as_option_settings=False
            )
            self.assertEqual(
                options,
                {
                    'foo': s
                }
            )

    @mock.patch('ebcli.operations.envvarops.elasticbeanstalk.describe_configuration_settings')
    @mock.patch('ebcli.operations.envvarops.print_environment_vars')
    def test_get_and_print_environment_vars(
            self,
            print_environment_vars_mock,
            describe_configuration_settings_mock
    ):
        describe_configuration_settings_mock.return_value = mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE__2['ConfigurationSettings'][0]

        envvarops.get_and_print_environment_vars('my-application', 'environment-1')

        print_environment_vars_mock.assert_called_once_with({'DB_USERNAME': 'root'})

    @mock.patch('ebcli.operations.envvarops.io.echo')
    def test_print_environment_vars__no_envvars(
            self,
            echo_mock
    ):
        envvarops.print_environment_vars({})

        echo_mock.assert_not_called()

    @mock.patch('ebcli.operations.envvarops.io.echo')
    def test_print_environment_vars(
            self,
            echo_mock
    ):
        envvarops.print_environment_vars(
            {
                'DB_USERNAME': 'root',
                'DB_PASSWORD': 'password'
            }
        )

        echo_mock.assert_has_calls(
            [
                mock.call(' Environment Variables:'),
                mock.call('    ', 'DB_USERNAME', '=', 'root'),
                mock.call('    ', 'DB_PASSWORD', '=', 'password')
            ],
            any_order=True
        )

    @mock.patch('ebcli.operations.envvarops.elasticbeanstalk.update_environment')
    @mock.patch('ebcli.operations.envvarops.commonops.wait_for_success_events')
    def test_setenv(
            self,
            wait_for_success_events_mock,
            update_environment_mock
    ):
        update_environment_mock.return_value = 'request-id'

        envvarops.setenv(
            'my-application',
            'environment-1',
            ['foo=bar', 'fish=good', 'trout=', 'baz='],
            timeout=1
        )

        self.assertEqual(
            'environment-1',
            update_environment_mock.call_args[0][0]
        )
        self.assertListsOfDictsEquivalent(
            update_environment_mock.call_args[0][1],
            [
                {
                    'Namespace': 'aws:elasticbeanstalk:application:environment',
                    'OptionName': 'foo',
                    'Value': 'bar'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:application:environment',
                    'OptionName': 'fish',
                    'Value': 'good'
                }
            ]
        )
        self.assertListsOfDictsEquivalent(
            update_environment_mock.call_args[1]['remove'],
            [
                {
                    'Namespace': 'aws:elasticbeanstalk:application:environment',
                    'OptionName': 'baz'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:application:environment',
                    'OptionName': 'trout'
                }
            ]
        )

        wait_for_success_events_mock.assert_called_once_with(
            'request-id', can_abort=True, timeout_in_minutes=1
        )
