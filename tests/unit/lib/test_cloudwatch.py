# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import mock
from pytest_socket import disable_socket, enable_socket
import unittest

from ebcli.lib import cloudwatch

from .. import mock_responses


class TestCloudWatch(unittest.TestCase):
    def setUp(self):
        disable_socket()

    def tearDown(self):
        enable_socket()

    @mock.patch('ebcli.lib.cloudwatch.aws.make_api_call')
    def test_get_all_stream_names(self, make_api_call_mock):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_LOG_STREAMS_RESPONSE

        self.assertEqual(
            [
                'archive-health-2018-03-26',
                'archive-health-2018-03-27',
                'archive-health-2018-03-28',
            ],
            cloudwatch.get_all_stream_names('some-log-group')
        )

    @mock.patch('ebcli.lib.cloudwatch.aws.make_api_call')
    def test_get_log_events(self, make_api_call_mock):
        cloudwatch.get_log_events(
            'environment-health.log',
            'archive-health-2018-03-26',
            next_token='1234123412341234',
            start_time='4567456745674567',
            end_time='7890789078907890',
            limit=10
        )

        make_api_call_mock.assert_called_once_with(
            'logs',
            'get_log_events',
            endTime='7890789078907890',
            limit=10,
            logGroupName='environment-health.log',
            logStreamName='archive-health-2018-03-26',
            nextToken='1234123412341234',
            startFromHead=False,
            startTime='4567456745674567'
        )

    @mock.patch('ebcli.lib.cloudwatch.aws.make_api_call')
    def test_log_group_exists(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_LOG_GROUPS_RESPONSE

        self.assertTrue(cloudwatch.log_group_exists('my-log-group-name'))

    @mock.patch('ebcli.lib.cloudwatch.aws.make_api_call')
    def test_log_group_exists__log_group_does_not_exist(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = {
            'logGroups': []
        }

        self.assertFalse(cloudwatch.log_group_exists('my-log-group-name'))
