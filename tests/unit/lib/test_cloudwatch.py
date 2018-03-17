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
import unittest
import mock

from ebcli.lib import cloudwatch


class TestCloudWatch(unittest.TestCase):
	@mock.patch('ebcli.lib.cloudwatch.describe_log_streams')
	def test_get_all_stream_names(self, describe_log_streams_mock):
		describe_log_streams_mock.return_value = {
			'logStreams': [
				{
					'lastIngestionTime': 1522104918499,
					'firstEventTimestamp': 1522104834000,
					'uploadSequenceToken': '49581045816077287818028642094834630247536380630456711345',
					'arn': 'arn:aws:logs:us-east-1:123123123123:log-group:/aws/elasticbeanstalk/env-name/environment-health.log:log-stream:archive-health-2018-03-26',
					'creationTime': 1522104860498,
					'storedBytes': 0,
					'logStreamName': 'archive-health-2018-03-26',
					'lastEventTimestamp': 1522104864000
				},
				{
					'lastIngestionTime': 1522185082040,
					'firstEventTimestamp': 1522114566000,
					'uploadSequenceToken': '495782746617210878802139966459935713174460150927741245',
					'arn': 'arn:aws:logs:us-east-1:123123123123:log-group:/aws/elasticbeanstalk/env-name/environment-health.log:log-stream:archive-health-2018-03-27',
					'creationTime': 1522114571763,
					'storedBytes': 0,
					'logStreamName': 'archive-health-2018-03-27',
					'lastEventTimestamp': 1522185066000
				},
				{
					'lastIngestionTime': 1522273517592,
					'firstEventTimestamp': 1522214971000,
					'uploadSequenceToken': '4957832466795318902173372629991138882266085318618712345',
					'arn': 'arn:aws:logs:us-east-1:123123123123:log-group:/aws/elasticbeanstalk/env-name/environment-health.log:log-stream:archive-health-2018-03-28',
					'creationTime': 1522215000673,
					'storedBytes': 0,
					'logStreamName': 'archive-health-2018-03-28',
					'lastEventTimestamp': 1522273511000
				},
			]
		}

		self.assertEqual(
			[
				'archive-health-2018-03-26',
				'archive-health-2018-03-27',
				'archive-health-2018-03-28',
			],
			cloudwatch.get_all_stream_names('some-log-group')
		)
