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
import sys

import unittest

import botocore
import botocore.exceptions
import botocore.parsers

import mock
import pytest

from mock import patch, MagicMock
from ebcli import __version__ as current_ebcli_version
from ebcli.lib import aws


class TestAws(unittest.TestCase):

    def setUp(self):
        self.response_data = {
            'ResponseMetadata': {
                    'HTTPStatusCode': 500
            },
            'Error': {
                    'Message': '500 Internal Server Error'
            }
        }

        self.mock_credentials = {
            'AWS_ACCESS_KEY_ID': 'access_key',
            'AWS_SECRET_ACCESS_KEY': 'secret_key',
            'AWS_CONFIG_FILE': 'no-exist-foo',
        }

    def test_user_agent(self):
        aws.set_region('us-east-1')
        with mock.patch('os.environ', self.mock_credentials):
            client = aws._get_client('elasticbeanstalk')
        user_agent = client._client_config.user_agent

        self.assertTrue(
            user_agent.startswith(
                'eb-cli/{current_ebcli_version}'.format(
                    current_ebcli_version=current_ebcli_version
                )
            )
        )

    def test_handle_response_code__500x_code__max_attempts_reached(self):
        aggregated_response_message = [r"""Received 5XX error during attempt #11
   500 Internal Server Error
"""]

        with self.assertRaises(aws.MaxRetriesError) as context_manager:
            aws._handle_response_code(self.response_data, 11, aggregated_response_message)
 
        self.assertEqual(context_manager.exception.message,
               "Max retries exceeded for service error (5XX)\n" + ('\n').join(aggregated_response_message))


    @pytest.mark.skipif(sys.version_info < (3,4),
                        reason="requires python3.4 or higher")
    @patch('ebcli.lib.aws.LOG')
    def test_handle_response_code__500x_code__max_attempts_not_reached(self, LOG):
        aggregated_response_message = []

        aws._handle_response_code(self.response_data, 10, aggregated_response_message)

        calls = [
            mock.call('Response: {\'Error\': {\'Message\': \'500 Internal Server Error\'}, \'ResponseMetadata\': {\'HTTPStatusCode\': 500}}'),
            mock.call('API call finished, status = 500'),
            mock.call('Received 5XX error')
        ]

        LOG.debug.assert_has_calls(calls)

    @pytest.mark.skipif(sys.version_info > (2,7,11),
                        reason="requires python2.7.11 or lower")
    @patch('ebcli.lib.aws.LOG')
    def test_handle_response_code__500x_code__max_attempts_not_reached(self, LOG):
        aggregated_response_message = []

        aws._handle_response_code(self.response_data, 10, aggregated_response_message)

        calls = [
            mock.call("Response: {'Error': {'Message': '500 Internal Server Error'}, 'ResponseMetadata': {'HTTPStatusCode': 500}}"),
            mock.call('API call finished, status = 500'),
            mock.call('Received 5XX error')
        ]

        LOG.debug.assert_has_calls(calls)

    @mock.patch('ebcli.lib.aws._get_delay')
    @mock.patch('ebcli.lib.aws._set_operation')
    @mock.patch('ebcli.lib.aws._sleep')
    def test_make_api_call__failure__status_code_5xx(
            self,
            _sleep_mock,
            _set_operation_mock,
            _get_delay_mock
    ):
        self.maxDiff = None

        operation = MagicMock(
            side_effect=botocore.exceptions.ClientError(
                self.response_data,
                'some_operation'
            )
        )

        _set_operation_mock.return_value = operation
        _get_delay_mock.side_effect = None
        _sleep_mock.side_effect = None

        with self.assertRaises(aws.MaxRetriesError) as cm:
            aws.make_api_call('some_service', 'some_operation')

        exception_message = r"""Max retries exceeded for service error (5XX)
Received 5XX error during attempt #1
   500 Internal Server Error

Received 5XX error during attempt #2
   500 Internal Server Error

Received 5XX error during attempt #3
   500 Internal Server Error

Received 5XX error during attempt #4
   500 Internal Server Error

Received 5XX error during attempt #5
   500 Internal Server Error

Received 5XX error during attempt #6
   500 Internal Server Error

Received 5XX error during attempt #7
   500 Internal Server Error

Received 5XX error during attempt #8
   500 Internal Server Error

Received 5XX error during attempt #9
   500 Internal Server Error

Received 5XX error during attempt #10
   500 Internal Server Error

Received 5XX error during attempt #11
   500 Internal Server Error
"""

        self.assertEqual(
            exception_message,
            str(cm.exception)
        )

    def test_handle_response_code__TooManyConfigurationTemplatesException_received(self):
        self.response_data = {
            'ResponseMetadata': {
                'date': 'Tue, 20 Jun 2017 06:34:57 GMT',
                'RetryAttempts': 0,
                'HTTPStatusCode': 400,
                'RequestId':
                    '93836311-5582-11e7-8c17-c11b3f8f545e'
            },
            'Error': {
                'Code': 'TooManyConfigurationTemplatesException',
                'Type': 'Sender'
            }
        }

        exception_message = ' '.join([
            'Your request cannot be completed. You have reached the maximum',
            'number of saved configuration templates. Learn more about service',
            'limits: http://docs.aws.amazon.com/general/latest/gr/aws_service_limits.html'
        ])

        with self.assertRaises(aws.TooManyConfigurationTemplatesException) as context_manager:
            aws._handle_response_code(self.response_data, 0, [])

        self.assertEqual(context_manager.exception.message, exception_message)

    def test_handle_response_code__botocore_client_exception_AccessDenied(self):
        self.response_data = {
            'Error': {
                'Type': 'Sender',
                'Code': 'AccessDenied',
                'Message': 'User: arn:aws:iam::123123123123:user/permissionless_user is not authorized to perform: cloudformation:GetTemplate on resource: arn:aws:cloudformation:us-west-2:123123123123:stack/aws-yolo-stack/*'
            },
            'ResponseMetadata': {
                'RequestId': '123123123-ddfg-sdff-qwee-123123123dsfsdf',
                'HTTPStatusCode': 403,
                'HTTPHeaders': {
                    'x-amzn-requestid': '123123123-ddfg-sdff-qwee-123123123dsfsdf',
                    'content-type': 'text/xml',
                    'content-length': '439',
                    'date': 'Wed, 08 Nov 2017 04:16:52 GMT'
                },
                'RetryAttempts': 0
            }
        }

        exception_message = (
            'Operation Denied. User: arn:aws:iam::123123123123:user/permissionless_user '
            'is not authorized to perform: cloudformation:GetTemplate on resource: '
            'arn:aws:cloudformation:us-west-2:123123123123:stack/aws-yolo-stack/*'
        )

        with self.assertRaises(aws.NotAuthorizedError) as context_manager:
            aws._handle_response_code(self.response_data, 0, [])

        self.assertEqual(context_manager.exception.message, exception_message)

    @patch('ebcli.lib.aws._set_operation')
    @patch('ebcli.lib.aws._get_delay')
    def test_handle_botocore_response_parser_error(self, get_delay_mock, set_operation_mock):
        get_delay_mock.return_value = 0
        operation_mock = MagicMock(
            side_effect=[
                botocore.parsers.ResponseParserError(
                    os.linesep.join(
                        [
                            "Unable to parse response (no element found: line 1, column 0), invalid XML received:",
                            "b''"
                        ]
                    )
                ),
                botocore.parsers.ResponseParserError(
                    os.linesep.join(
                        [
                            "Unable to parse response (no element found: line 1, column 0), invalid XML received:",
                            "b''"
                        ]
                    )
                ),
                {
                    'Events': [],
                    'ResponseMetadata': {
                        'RequestId': 'd0ac21eb-c138-42cb-a679-eea1a6e56fe0',
                        'HTTPStatusCode': 200,
                        'date': 'Wed, 21 Feb 2018 09:09:16 GMT',
                        'RetryAttempts': 0
                    }
                }
            ]
        )
        set_operation_mock.return_value = operation_mock

        aws.make_api_call('some_aws_service', 'some_operation')

    @patch('ebcli.lib.aws._set_operation')
    @patch('ebcli.lib.aws._get_delay')
    def test_handle_botocore_response_parser_error__max_attempts_reached(self, get_delay_mock, set_operation_mock):
        self.maxDiff = None
        get_delay_mock.return_value = 0

        botocore_parse_errors = []
        for i in range(1, 12):
            botocore_parse_errors.append(
                botocore.parsers.ResponseParserError(
                    os.linesep.join(
                        [
                            "Unable to parse response (no element found: line 1, column 0), invalid XML received:",
                            "b''"
                        ]
                    )
                )
            )

        operation_mock = MagicMock(side_effect=botocore_parse_errors)
        set_operation_mock.return_value = operation_mock

        with self.assertRaises(aws.MaxRetriesError) as context_manager:
            aws.make_api_call('some_aws_service', 'some_operation')

        self.assertEqual(
            """Max retries exceeded for ResponseParserErrorsUnable to parse response (no element found: line 1, column 0), invalid XML received:
b''
Unable to parse response (no element found: line 1, column 0), invalid XML received:
b''
Unable to parse response (no element found: line 1, column 0), invalid XML received:
b''
Unable to parse response (no element found: line 1, column 0), invalid XML received:
b''
Unable to parse response (no element found: line 1, column 0), invalid XML received:
b''
Unable to parse response (no element found: line 1, column 0), invalid XML received:
b''
Unable to parse response (no element found: line 1, column 0), invalid XML received:
b''
Unable to parse response (no element found: line 1, column 0), invalid XML received:
b''
Unable to parse response (no element found: line 1, column 0), invalid XML received:
b''
Unable to parse response (no element found: line 1, column 0), invalid XML received:
b''""",
            str(context_manager.exception).replace('\r\n', '\n').replace(r'\s$', "")
        )
