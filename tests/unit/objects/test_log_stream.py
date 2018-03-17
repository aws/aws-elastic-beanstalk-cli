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

from ebcli.objects.log_stream import LogStream


class TestLogStream(unittest.TestCase):
	def test_log_streams__sorted(self):

		log_streams = [
			{
				'logStreamName': 'archive-health-2018-04-14-B5A100C12FEE498324A234B9ED377644',
				'creationTime': 1523674444444
			},
			{
				'logStreamName': 'archive-health-2018-04-16-B5A100C12FEE498324A234B9ED377644',
				'creationTime': 1523678888888
			},
			{
				'logStreamName': 'archive-health-2018-04-15-B5A100C12FEE498324A234B9ED377644',
				'creationTime': 1523676666666
			}
		]

		self.assertEqual(
			[
				'archive-health-2018-04-14-B5A100C12FEE498324A234B9ED377644',
				'archive-health-2018-04-15-B5A100C12FEE498324A234B9ED377644',
				'archive-health-2018-04-16-B5A100C12FEE498324A234B9ED377644'
			],
			[log_stream.name for log_stream in LogStream.log_stream_objects_from_json(log_streams)]
		)
