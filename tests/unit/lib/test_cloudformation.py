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

from dateutil import tz
import mock
import unittest

from ebcli.lib import cloudformation

from .. import mock_responses


class TestCloudFormation(unittest.TestCase):
    @mock.patch('ebcli.lib.cloudformation.aws.make_api_call')
    def test_wait_until_stack_exists__stack_does_not_exist(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_STACKS_RESPONSE

        with self.assertRaises(cloudformation.CFNTemplateNotFound) as exception:
            cloudformation.wait_until_stack_exists('non_existent_stack', timeout=0)

        self.assertEqual(
            exception.exception.message,
            "Could not find CFN stack, 'non_existent_stack'."
        )

    @mock.patch('ebcli.lib.cloudformation.aws.make_api_call')
    def test_wait_until_stack_exists__stack_exists(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_STACKS_RESPONSE

        cloudformation.wait_until_stack_exists('stack_name')

    @mock.patch('ebcli.lib.cloudformation.aws.make_api_call')
    def test_get_template(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.GET_TEMPLATE_RESPONSE

        self.assertEqual(
            mock_responses.GET_TEMPLATE_RESPONSE,
            cloudformation.get_template('mystackname')
        )

    @mock.patch('ebcli.lib.cloudformation.aws.make_api_call')
    def test_stack_names(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_STACKS_RESPONSE

        self.assertEqual(
            ['stack_name'],
            cloudformation.stack_names()
        )

    @mock.patch('ebcli.lib.cloudformation.aws.make_api_call')
    @mock.patch('ebcli.lib.cloudformation.utils.prevent_throttling')
    def test_events__with_timestamp(
            self,
            prevent_throttling_mock,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_STACK_EVENTS_RESPONSE
        prevent_throttling_mock.side_effect = None
        events = cloudformation.events(
            'sam-cfn-stack',
            start_time=datetime.datetime(2018, 8, 12, 18, 36, 58, 294000, tzinfo=tz.tzutc())
        )
        self.assertEqual(
            'b31b10d0-9e5e-11e8-8eb0-02c3ece5f9fa',
            events[0].event_id
        )
        self.assertEqual(
            'HelloWorldFunctionHelloWorldPermissionProd-CREATE_COMPLETE-2018-08-12T18:36:58.371Z',
            events[1].event_id
        )

    @mock.patch('ebcli.lib.cloudformation.aws.make_api_call')
    @mock.patch('ebcli.lib.cloudformation.utils.prevent_throttling')
    def test_events__events_span_multiple_pages(
            self,
            prevent_throttling_mock,
            make_api_call_mock
    ):
        prevent_throttling_mock.side_effect = None
        make_api_call_mock.side_effect = [
            {
                'StackEvents': [
                    {
                        'EventId': 'b31b10d0-9e5e-11e8-8eb0-02c3ece5f9fa',
                        'Timestamp': datetime.datetime(2018, 8, 12, 18, 37, 0, 365000, tzinfo=tz.tzutc()),
                    }
                ],
                'NextToken': 'next-token-1'
            },
            {
                'StackEvents': [
                    {
                        'EventId': 'HelloWorldFunctionHelloWorldPermissionProd',
                        'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 58, 371000, tzinfo=tz.tzutc())
                    }
                ],
                'NextToken': 'next-token-2'
            },
            {
                'StackEvents': [
                    {
                        'Timestamp': datetime.datetime(2018, 8, 12, 18, 36, 24, 294000, tzinfo=tz.tzutc())
                    }
                ]
            },
        ]

        events = cloudformation.events(
            'sam-cfn-stack',
            start_time=datetime.datetime(2018, 8, 12, 18, 36, 50, 0, tzinfo=tz.tzutc())
        )
        self.assertEqual('b31b10d0-9e5e-11e8-8eb0-02c3ece5f9fa', events[0].event_id)
        self.assertEqual('HelloWorldFunctionHelloWorldPermissionProd', events[1].event_id)
        self.assertEqual(2, len(events))

        make_api_call_mock.assert_has_calls(
            [
                mock.call(
                    'cloudformation',
                    'describe_stack_events',
                    StackName='sam-cfn-stack'
                ),
                mock.call(
                    'cloudformation',
                    'describe_stack_events',
                    StackName='sam-cfn-stack',
                    NextToken='next-token-1'
                ),
                mock.call(
                    'cloudformation',
                    'describe_stack_events',
                    StackName='sam-cfn-stack',
                    NextToken='next-token-2'
                )
            ]
        )
