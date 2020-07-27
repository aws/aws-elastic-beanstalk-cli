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
import mock
import unittest

from ebcli.lib import elbv2
from ebcli.objects.exceptions import NotFoundError, ServiceError

from .. import mock_responses


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

    @mock.patch('ebcli.lib.elbv2._make_api_call')
    def test_get_listeners_for_load_balancer__with_load_balancer_arn(
            self,
            _make_api_call_mock
    ):
        load_balancer_arn = 'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-2/5a957e362e1339a9'
        _make_api_call_mock.return_value = mock_responses.GET_LISTENERS_FOR_LOAD_BALANCER_RESPONSE

        expected_result = mock_responses.GET_LISTENERS_FOR_LOAD_BALANCER_RESPONSE

        result = elbv2.get_listeners_for_load_balancer(load_balancer_arn)

        _make_api_call_mock.assert_called_once_with('describe_listeners',LoadBalancerArn=load_balancer_arn)

        self.assertEqual(
            result,
            expected_result
        )

    @mock.patch('ebcli.lib.elbv2._make_api_call')
    def test_describe_load_balancer__pass_load_balancer_name(
            self,
            _make_api_call_mock
    ):
        load_balancer = ['alb-1']
        _make_api_call_mock.return_value = mock_responses.DESCRIBE_LOAD_BALANCERS_RESPONSE

        expected_result = mock_responses.DESCRIBE_LOAD_BALANCERS_RESPONSE
        result = elbv2.describe_load_balancers(load_balancer)

        _make_api_call_mock.assert_called_once_with('describe_load_balancers', Names=load_balancer)

        self.assertEqual(
            result,
            expected_result
        )
