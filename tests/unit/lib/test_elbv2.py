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
import mock
import unittest

from ebcli.lib import elbv2
from ebcli.objects.exceptions import NotFoundError, ServiceError


class TestElbv2(unittest.TestCase):
	def test_get_instance_healths_from_target_groups__zero_target_groups_passed_in(self):
		self.assertEqual(
			[],
			elbv2.get_instance_healths_from_target_groups(target_group_arns=[])
		)

	@mock.patch('ebcli.lib.elbv2._make_api_call')
	def test_get_instance_healths_from_target_groups__one_target_group_arn__one_instance(
			self,
			make_api_call_mock
	):
		make_api_call_mock.return_value = {
			"TargetHealthDescriptions": [
				{
					"Target": {
						"Id": "i-0cad09d6183cb22fb",
						"Port": 80
					},
					"HealthCheckPort": "80",
					"TargetHealth": {
						"State": "healthy"
					}
				},
			]
		}

		self.assertEqual(
			[
				{
					'Description': '',
					'InstanceId': 'i-0cad09d6183cb22fb',
					'Reason': '',
					'State': 'healthy'
				}
			],
			elbv2.get_instance_healths_from_target_groups(
				target_group_arns=[
					'arn:aws:elasticloadbalancing:us-west-2:1123123123:targetgroup/awseb-AWSEB-213123123123/c432cd690a5f6d62'
				]
			)
		)

	@mock.patch('ebcli.lib.elbv2._make_api_call')
	def test_get_instance_healths_from_target_groups__many_instances_for_one_target_arn(
			self,
			make_api_call_mock
	):
		make_api_call_mock.return_value = {
			"TargetHealthDescriptions": [
				{
					"Target": {
						"Id": "i-0cad09d6183cb22fb",
						"Port": 80
					},
					"HealthCheckPort": "80",
					"TargetHealth": {
						"State": "healthy"
					}
				},
				{
					"Target": {
						"Id": "i-1237d9d6183cffda6",
						"Port": 80
					},
					"HealthCheckPort": "80",
					"TargetHealth": {
						"State": "healthy"
					}
				},
			]
		}

		self.assertEqual(
			[
				{
					'Description': '',
					'InstanceId': 'i-0cad09d6183cb22fb',
					'Reason': '',
					'State': 'healthy'
				},
				{
					'Description': '',
					'InstanceId': 'i-1237d9d6183cffda6',
					'Reason': '',
					'State': 'healthy'
				}
			],
			elbv2.get_instance_healths_from_target_groups(
				target_group_arns=[
					'arn:aws:elasticloadbalancing:us-west-2:1123123123:targetgroup/awseb-AWSEB-213123123123/c432cd690a5f6d62'
				])
		)

	@mock.patch('ebcli.lib.elbv2._make_api_call')
	def test_get_instance_healths_from_target_groups__one_target_group_arn__target_group_is_non_existent(
			self,
			make_api_call_mock
	):
		make_api_call_mock.side_effect = ServiceError

		with self.assertRaises(NotFoundError):
			elbv2.get_instance_healths_from_target_groups(
				target_group_arns=[
					'arn:aws:elasticloadbalancing:us-west-2:1123123123:targetgroup/awseb-AWSEB-213123123123/c432cd690a5f6d62'
				]
			)
