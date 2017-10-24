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
import unittest
import mock

from ebcli.lib import aws, cloudformation


class TestCloudFormation(unittest.TestCase):

	def test_wait_until_stack_exists__stack_does_not_exist(self):
		describe_stacks_response = {
			'Stacks': [
				{
					'StackId': 'stack_id',
					'StackName': 'stack_name',
					'Description': "my cloud formation stack",
					'Parameters': []
				}
			]
		}
		aws.make_api_call = mock.MagicMock(return_value=describe_stacks_response)

		with self.assertRaises(cloudformation.CFNTemplateNotFound) as exception:
			cloudformation.wait_until_stack_exists('non_existent_stack', timeout=0)

		self.assertEqual(
			exception.exception.message,
			"Could not find CFN stack, 'non_existent_stack'."
		)

	def test_wait_until_stack_exists__stack_exists(self):
		describe_stacks_response = {
			'Stacks': [
				{
					'StackId': 'stack_id',
					'StackName': 'stack_name',
					'Description': "my cloud formation stack",
					'Parameters': []
				}
			]
		}
		aws.make_api_call = mock.MagicMock(return_value=describe_stacks_response)

		cloudformation.wait_until_stack_exists('stack_name')
