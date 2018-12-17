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
import datetime
from dateutil import tz

import mock
import unittest

from ebcli.display import traditional
from ebcli.objects import environment


class TestTraditionalHealthDataPoller(unittest.TestCase):
    def test_get_instance_states__no_load_balancer(self):
        self.assertEqual(
            [],
            traditional.TraditionalHealthDataPoller('fake app name', 'fake env name').get_instance_states(None)
        )

    def test_get_instance_states(self):
        poller = traditional.TraditionalHealthDataPoller('fake app name', 'fake env name')
        poller.get_load_balancer_instance_states = mock.MagicMock(
            return_value=[
                {
                    'Description': '',
                    'InstanceId': 'i-0cad09d6183cb22fb',
                    'Reason': '',
                    'State': 'healthy'
                },
                {
                    'Description': '',
                    'InstanceId': 'i-0f5678192487123ab',
                    'Reason': '',
                    'State': 'healthy'
                }
            ]
        )

        load_balancers = [{'Name': 'awseb-e-a-AWSEBLoa-1WOG31HKVP6LS'}]

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
                    'InstanceId': 'i-0f5678192487123ab',
                    'Reason': '',
                    'State': 'healthy'
                }
            ],
            poller.get_instance_states(load_balancers)
        )

    @mock.patch('ebcli.lib.elb.get_health_of_instances')
    def test_get_load_balancer_instance_states__using_elb_name(
        self,
        get_health_of_instances_mock
    ):
        get_health_of_instances_mock.return_value = [
            {
                'InstanceId': 'i-077ad825504695eb9',
                'State': 'InService',
                'ReasonCode': 'N/A',
                'Description': 'N/A'
            },
            {
                'InstanceId': 'i-0965954076351e6e0',
                'State': 'InService',
                'ReasonCode': 'N/A',
                'Description': 'N/A'
            },
            {
                'InstanceId': 'i-0aa042833bfdec77d',
                'State': 'InService',
                'ReasonCode': 'N/A',
                'Description': 'N/A'
            }
        ]

        poller = traditional.TraditionalHealthDataPoller('fake app name', 'fake env name')
        self.assertEqual(
            get_health_of_instances_mock.return_value,
            poller.get_load_balancer_instance_states('awseb-e-a-AWSEBLoa-1WOG31HKVP6LS')
        )

    @mock.patch('ebcli.lib.elbv2.get_target_groups_for_load_balancer')
    @mock.patch('ebcli.lib.elbv2.get_instance_healths_from_target_groups')
    def test_get_load_balancer_instance_states__using_elbv2_arn(
            self,
            get_instance_healths_from_target_groups_mock,
            get_target_groups_for_load_balancer_mock
    ):
        get_target_groups_for_load_balancer_mock.return_value = [
            {
                'TargetGroupArn': 'arn:aws:elasticloadbalancing:us-west-2:123123123123:targetgroup/awseb-AWSEB-Z40E0JSOX7VX/132a50d3c6332139',
                'TargetGroupName': 'awseb-AWSEB-Z40E0JSOX7VX',
                'Protocol': 'HTTP',
                'Port': 80,
                'VpcId': 'vpc-0b94a86c',
                'HealthCheckProtocol': 'HTTP',
                'HealthCheckPort': 'traffic-port',
                'HealthCheckIntervalSeconds': 15,
                'HealthCheckTimeoutSeconds': 5,
                'HealthyThresholdCount': 3,
                'UnhealthyThresholdCount': 5,
                'HealthCheckPath': '/',
                'Matcher': {
                    'HttpCode': '200'
                },
                'LoadBalancerArns': [
                    'arn:aws:elasticloadbalancing:us-west-2:123123123123:loadbalancer/app/awseb-AWSEB-13USMLK35OCE0/e8b5c23789b536c6'
                ]
            }
        ]
        get_instance_healths_from_target_groups_mock.return_value = [
            {
                'Description': '',
                'InstanceId': 'i-0cad09d6183cb22fb',
                'Reason': '',
                'State': 'healthy'
            }
        ]

        poller = traditional.TraditionalHealthDataPoller('fake app name', 'fake env name')
        self.assertEqual(
            get_instance_healths_from_target_groups_mock.return_value,
            poller.get_load_balancer_instance_states(
                'arn:aws:elasticloadbalancing:us-west-2:123123123123:loadbalancer/app/awseb-AWSEB-13USMLK35OCE0/e8b5c23789b536c6'
            )
        )

    @mock.patch('ebcli.lib.ec2.describe_instance')
    def test_get_instance_health(
            self,
            curtailed_describe_instance_response_mock
    ):
        curtailed_describe_instance_response_mock.side_effect = [
            {'InstanceId': 'i-0cad09d6183cb22fb', 'State': {'Code': 16, 'Name': 'running'}},
            {'InstanceId': 'i-0f5678192487123ab', 'State': {'Code': 16, 'Name': 'running'}},
        ]

        instance_states = [
            {
                'Description': '',
                'InstanceId': 'i-0cad09d6183cb22fb',
                'Reason': '',
                'State': 'healthy'
            },
            {
                'Description': '',
                'InstanceId': 'i-0f5678192487123ab',
                'Reason': '',
                'State': 'healthy'
            }
        ]

        poller = traditional.TraditionalHealthDataPoller('fake app name', 'fake env name')
        self.assertEqual(
            [
                {
                    'description': '',
                    'health': 'running',
                    'id': 'i-0cad09d6183cb22fb',
                    'state': 'healthy'
                },
                {
                    'description': '',
                    'health': 'running',
                    'id': 'i-0f5678192487123ab',
                    'state': 'healthy'
                }
            ],
            poller.get_instance_health(instance_states)
        )

    @mock.patch('ebcli.lib.ec2.describe_instance')
    def test_get_health_information_of_instance_not_associated_with_elb__only_adds_those_instances_that_are_not_already_associated_with_the_environments_load_balancer(
            self,
            curtailed_describe_instance_response_mock
    ):
        curtailed_describe_instance_response_mock.side_effect = [
            {'InstanceId': 'i-0f5678192487123ab', 'State': {'Code': 16, 'Name': 'terminated'}},
            {'InstanceId': 'i-0bfd123124124124d', 'State': {'Code': 16, 'Name': 'terminated'}}
        ]

        ids_of_all_instances = ['i-0cad09d6183cb22fb', 'i-0f5678192487123ab', 'i-0bfd123124124124d']

        instances_registered_with_elb = [
            {
                'Description': '',
                'InstanceId': 'i-0cad09d6183cb22fb',
                'Reason': '',
                'State': 'running'
            },
        ]

        poller = traditional.TraditionalHealthDataPoller('fake app name', 'fake env name')
        expected_instances = [
            {
                'description': 'N/A (Not registered with Load Balancer)',
                'health': 'terminated',
                'id': 'i-0f5678192487123ab',
                'state': 'n/a'
            },
            {
                'description': 'N/A (Not registered with Load Balancer)',
                'health': 'terminated',
                'id': 'i-0bfd123124124124d',
                'state': 'n/a'
            }
        ]
        actual_instances = poller.get_health_information_of_instance_not_associated_with_elb(
            ids_of_all_instances,
            instances_registered_with_elb
        )

        for expected_instance in expected_instances:
            self.assertTrue(expected_instance in actual_instances)

        curtailed_describe_instance_response_mock.assert_has_calls(
            [
                mock.call('i-0f5678192487123ab'),
                mock.call('i-0bfd123124124124d')
            ],
            any_order=True
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.display.traditional._datetime_utcnow_wrapper')
    def test_env_data(self, datetime_utcnow_mock, get_environment_mock):
        datetime_utcnow_mock.return_value = datetime.datetime(2018, 3, 14, 22, 0, 30, 195079)
        get_environment_mock.return_value = environment.Environment(
            name='fake env name',
            status='Ready',
            health='Green'
        )

        instance_states = [
            {
                'Description': '',
                'InstanceId': 'i-0cad09d6183cb22fb',
                'Reason': '',
                'State': 'InService'
            },
            {
                'Description': '',
                'InstanceId': 'i-0f5678192487123ab',
                'Reason': '',
                'State': 'terminated'
            },
            {
                'Description': '',
                'InstanceId': 'i-0bfd123124124124d',
                'Reason': '',
                'State': 'terminated'
            },
        ]

        poller = traditional.TraditionalHealthDataPoller('fake app name', 'fake env name')
        instance_ids = ['i-0cad09d6183cb22fb', 'i-0f5678192487123ab', 'i-0bfd123124124124d']
        self.assertEqual(
            {
                'Color': 'Green',
                'EnvironmentName': 'fake env name',
                'InService': 1,
                'Other': 2,
                'RefreshedAt': datetime.datetime(2018, 3, 14, 22, 0, 30, 195079),
                'Status': 'Ready',
                'Total': 3
            },
            poller.assemble_environment_data(instance_ids, instance_states)
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.get_environment_resources')
    @mock.patch('ebcli.display.traditional._datetime_utcnow_wrapper')
    def test_get_health_data(
            self,
            datetime_utcnow_mock,
            curtailed_get_environment_resources_mock
    ):
        self.maxDiff = None
        datetime_utcnow_mock.return_value = datetime.datetime(2018, 3, 14, 22, 0, 30, 195079)
        curtailed_get_environment_resources_mock.return_value = {
            'EnvironmentResources': {
                'EnvironmentName': 'fake env name',
                'Instances': [
                    {
                        'Id': 'i-0aa042833bfdec77d'
                    },
                    {
                        'Id': 'i-0965954076351e6e0'
                    },
                    {
                        'Id': 'i-077ad825504695eb9'
                    }
                ],
                'LoadBalancers': [
                    {
                        'Name': 'awseb-e-a-AWSEBLoa-1WOG31HKVP6LS'
                    }
                ],
            }
        }

        poller = traditional.TraditionalHealthDataPoller('fake app name', 'fake env name')
        poller.get_instance_states = mock.MagicMock(
            return_value=[
                {
                    'Description': '',
                    'InstanceId': 'i-0aa042833bfdec77d',
                    'Reason': '',
                    'State': 'healthy'
                },
                {
                    'Description': '',
                    'InstanceId': 'i-0965954076351e6e0',
                    'Reason': '',
                    'State': 'healthy'
                },
            ]
        )
        poller.get_instance_health = mock.MagicMock(
            return_value=[
                {
                    'description': '',
                    'health': 'running',
                    'id': 'i-0aa042833bfdec77d',
                    'state': 'healthy'
                },
                {
                    'description': '',
                    'health': 'running',
                    'id': 'i-0965954076351e6e0',
                    'state': 'healthy'
                },
            ]
        )
        poller.get_health_information_of_instance_not_associated_with_elb = mock.MagicMock(
            return_value=[
                {
                    'description': 'N/A (Not registered with Load Balancer)',
                    'health': 'terminated',
                    'id': 'i-077ad825504695eb9',
                    'state': 'n/a'
                }
            ]
        )
        poller.assemble_environment_data = mock.MagicMock(
            return_value={
                'Color': 'Green',
                'EnvironmentName': 'fake env name',
                'InService': 1,
                'Other': 2,
                'RefreshedAt': datetime.datetime(2018, 3, 14, 22, 0, 30, 195079),
                'Status': 'Ready',
                'Total': 3
            }
        )

        self.assertEqual(
            {
                'environment': {
                    'Color': 'Green',
                    'EnvironmentName': 'fake env name',
                    'InService': 1,
                    'Other': 2,
                    'RefreshedAt': datetime.datetime(2018, 3, 14, 22, 0, 30, 195079),
                    'Status': 'Ready',
                    'Total': 3
                },
                'instances': [
                    {
                        'description': '',
                        'health': 'running',
                        'id': 'i-0aa042833bfdec77d',
                        'state': 'healthy'
                    },
                    {
                        'description': '',
                        'health': 'running',
                        'id': 'i-0965954076351e6e0',
                        'state': 'healthy'
                    },
                    {
                        'description': 'N/A (Not registered with Load Balancer)',
                        'health': 'terminated',
                        'id': 'i-077ad825504695eb9',
                        'state': 'n/a'
                    }
                ]
            },
            poller._get_health_data()
        )
