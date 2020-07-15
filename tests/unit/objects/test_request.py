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
import copy

import unittest
import mock

from ebcli.objects import requests, solutionstack, tier


class TestRequests(unittest.TestCase):
    maxDiff = None
    solution = solutionstack.SolutionStack('64bit Amazon Linux 2014.03 v1.0.6 running PHP 5.5')

    def test_create_environment_request_init(self):
        request_args = {
            'app_name': 'ebcli-intTest-app',
            'cname': None,
            'env_name': 'my-awesome-env',
            'instance_profile': None,
            'instance_type': None,
            'key_name': None,
            'platform': self.solution,
            'sample_application': False,
            'service_role': None,
            'single_instance': False,
            'template_name': None,
            'tier': None,
            'version_label': None,
            'group_name': None,
            'tags': [],
            'database': {
                'username': 'root',
                'password': 'password',
                'engine': 'mysql',
                'size': '10',
                'instance': 'db.t2.micro',
                'version': '5.6.35'
            },
            'vpc': {
                'id': 'my-vpc-id',
                'ec2subnets': 'subnet-1,subnet-2,subnet-3',
                'elbsubnets': 'subnet-1,subnet-2,subnet-3',
                'elbscheme': 'public',
                'publicip': 'true',
                'securitygroups': 'security-group-1,security-group-2',
                'dbsubnets': 'subnet-1,subnet-2,subnet-3'
            },
            'elb_type': None,
            'scale': None,
        }

        create_environment_request = requests.CreateEnvironmentRequest(**request_args)

        self.assertFalse(create_environment_request.compiled)
        self.assertEqual([], create_environment_request.option_settings)
        self.assertEqual('Environment created from the EB CLI using "eb create"', create_environment_request.description)
        self.assertIsNone(create_environment_request.scale)

    def test_create_environment__app_name_not_passed_in(self):
        with self.assertRaises(TypeError) as context_manager:
            requests.CreateEnvironmentRequest(env_name='my-env')

        self.assertEqual(
            'CreateEnvironmentRequest requires key-word argument app_name',
            str(context_manager.exception)
        )

    def test_create_environment__env_name_not_passed_in(self):
        with self.assertRaises(TypeError) as context_manager:
            requests.CreateEnvironmentRequest(app_name='my-app')

        self.assertEqual(
            'CreateEnvironmentRequest requires key-word argument env_name',
            str(context_manager.exception)
        )

    def test_create_environment__scale_is_not_an_int(self):
        with self.assertRaises(TypeError) as context_manager:
            requests.CreateEnvironmentRequest(app_name='my-app', env_name='my-env', scale='1')

        self.assertEqual(
            'key-word argument scale must be of type int',
            str(context_manager.exception)
        )

    def test_add_option_setting(self):
        request = requests.CreateEnvironmentRequest(app_name='my-app', env_name='my-env')
        request.add_option_setting('MyNameSpace', 'MyOptionName', 'MyValue')

        self.assertEqual(
            [
                {
                    'Namespace': 'MyNameSpace',
                    'OptionName': 'MyOptionName',
                    'Value': 'MyValue'
                }
            ],
            request.option_settings
        )

    def test_add_option_setting__with_resource(self):
        request = requests.CreateEnvironmentRequest(app_name='my-app', env_name='my-env')
        request.add_option_setting('MyNameSpace', 'MyOptionName', 'MyValue', resource='MyResource')

        self.assertEqual(
            [
                {
                    'Namespace': 'MyNameSpace',
                    'OptionName': 'MyOptionName',
                    'ResourceName': 'MyResource',
                    'Value': 'MyValue'
                }
            ],
            request.option_settings
        )

    def test_compile_vpc_options__no_vpc_args(self):
        request = requests.CreateEnvironmentRequest(app_name='my-app', env_name='my-env')
        request_copy = copy.copy(request)

        request_copy.compile_vpc_options()

        self.assertEqual(request, request_copy)

    def test_compile_vpc_options(self):
        request_args = {
            'app_name': 'ebcli-intTest-app',
            'env_name': 'my-awesome-env',
            'vpc': {
                'id': 'my-vpc-id',
                'ec2subnets': 'subnet-1,subnet-2,subnet-3',
                'elbsubnets': 'subnet-1,subnet-2,subnet-3',
                'elbscheme': 'public',
                'publicip': 'true',
                'securitygroups': 'security-group-1,security-group-2',
                'dbsubnets': 'subnet-1,subnet-2,subnet-3'
            }
        }
        request = requests.CreateEnvironmentRequest(**request_args)
        self.assertEqual([], request.option_settings)

        request.compile_vpc_options()
        self.assertEqual(
            [
                {
                    'Namespace': 'aws:ec2:vpc',
                    'OptionName': 'VPCId',
                    'Value': 'my-vpc-id'
                },
                {
                    'Namespace': 'aws:ec2:vpc',
                    'OptionName': 'AssociatePublicIpAddress',
                    'Value': 'true'
                },
                {
                    'Namespace': 'aws:ec2:vpc',
                    'OptionName': 'ELBScheme',
                    'Value': 'public'
                },
                {
                    'Namespace': 'aws:ec2:vpc',
                    'OptionName': 'ELBSubnets',
                    'Value': 'subnet-1,subnet-2,subnet-3'
                },
                {
                    'Namespace': 'aws:ec2:vpc',
                    'OptionName': 'Subnets',
                    'Value': 'subnet-1,subnet-2,subnet-3'
                },
                {
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'SecurityGroups',
                    'Value': 'security-group-1,security-group-2'
                },
                {
                    'Namespace': 'aws:ec2:vpc',
                    'OptionName': 'DBSubnets',
                    'Value': 'subnet-1,subnet-2,subnet-3'
                }
            ],
            request.option_settings
        )

    def test_compile_database_options__no_database_args(self):
        request = requests.CreateEnvironmentRequest(app_name='my-app', env_name='my-env')
        request_copy = copy.copy(request)

        request_copy.compile_database_options()

        self.assertEqual(request, request_copy)

    def test_compile_database_options(self):
        request_args = {
            'app_name': 'ebcli-intTest-app',
            'env_name': 'my-awesome-env',
            'database': {
                'username': 'root',
                'password': 'password',
                'engine': 'mysql',
                'size': '10',
                'instance': 'db.t2.micro',
                'version': '5.6.35'
            }
        }
        request = requests.CreateEnvironmentRequest(**request_args)
        self.assertEqual([], request.option_settings)

        request.compile_database_options()
        self.assertEqual(
            [
                {
                    'Namespace': 'aws:rds:dbinstance',
                    'OptionName': 'DBPassword',
                    'Value': 'password'
                },
                {
                    'Namespace': 'aws:rds:dbinstance',
                    'OptionName': 'DBUser',
                    'Value': 'root'
                },
                {
                    'Namespace': 'aws:rds:dbinstance',
                    'OptionName': 'DBInstanceClass',
                    'Value': 'db.t2.micro'
                },
                {
                    'Namespace': 'aws:rds:dbinstance',
                    'OptionName': 'DBAllocatedStorage',
                    'Value': '10'
                },
                {
                    'Namespace': 'aws:rds:dbinstance',
                    'OptionName': 'DBEngine',
                    'Value': 'mysql'
                },
                {
                    'Namespace': 'aws:rds:dbinstance',
                    'OptionName': 'DBEngineVersion',
                    'Value': '5.6.35'
                },
                {
                    'Namespace': 'aws:rds:dbinstance',
                    'OptionName': 'DBDeletionPolicy',
                    'Value': 'Snapshot'
                }
            ],
            request.option_settings
        )

    def test_compile_spot_options(self):
        request_args = {
            'app_name': 'ebcli-intTest-app',
            'env_name': 'my-awesome-env',
            'enable_spot': 'true',
            'instance_types': 't2.micro, t2.large',
            'spot_max_price': '.5',
        }
        request = requests.CreateEnvironmentRequest(**request_args)
        self.assertEqual([], request.option_settings)

        request.compile_spot_options()
        self.assertEqual(
            [
                {
                    'Namespace': 'aws:ec2:instances',
                    'OptionName': 'EnableSpot',
                    'Value': 'true'
                },
                {
                    'Namespace': 'aws:ec2:instances',
                    'OptionName': 'InstanceTypes',
                    'Value': 't2.micro, t2.large'
                },
                {
                    'Namespace': 'aws:ec2:instances',
                    'OptionName': 'SpotMaxPrice',
                    'Value': '.5'
                },
            ],
            request.option_settings
        )

    def test_common_options(self):
        request_args = {
            'app_name': 'ebcli-intTest-app',
            'cname': None,
            'env_name': 'my-awesome-env',
            'instance_profile': 'my-instance-profile',
            'instance_type': 't2.micro',
            'key_name': 'my-key-name',
            'platform': self.solution,
            'sample_application': False,
            'service_role': 'my-service-role',
            'single_instance': False,
            'template_name': None,
            'tier': 'webserver',
            'version_label': None,
            'group_name': None,
            'tags': [],
            'elb_type': 'application',
            'scale': 10,
        }

        request = requests.CreateEnvironmentRequest(**request_args)
        request.compile_common_options()
        self.assertEqual(
            [
                {
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'IamInstanceProfile',
                    'Value': 'my-instance-profile'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:environment',
                    'OptionName': 'ServiceRole',
                    'Value': 'my-service-role'
                },
                {
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'InstanceType',
                    'Value': 't2.micro'
                },
                {
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'EC2KeyName',
                    'Value': 'my-key-name'
                },
                {
                    'Namespace': 'aws:autoscaling:asg',
                    'OptionName': 'MaxSize',
                    'Value': '10'
                },
                {
                    'Namespace': 'aws:autoscaling:asg',
                    'OptionName': 'MinSize',
                    'Value': '10'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:environment',
                    'OptionName': 'LoadBalancerType',
                    'Value': 'application'
                }
            ],
            request.option_settings
        )

    def test_common_options__single_instance(self):
        request_args = {
            'app_name': 'ebcli-intTest-app',
            'env_name': 'my-awesome-env',
            'single_instance': True,
        }

        request = requests.CreateEnvironmentRequest(**request_args)
        request.compile_common_options()
        self.assertEqual(
            [
                {
                    'Namespace': 'aws:elasticbeanstalk:environment',
                    'OptionName': 'EnvironmentType',
                    'Value': 'SingleInstance'
                }
            ],
            request.option_settings
        )

    def test_add_client_defaults__uses_template_name_if_one_exists(self):
        request_args = {
            'app_name': 'ebcli-intTest-app',
            'env_name': 'my-awesome-env',
            'template_name': 'my-saved-configuration-template-name',
        }

        request = requests.CreateEnvironmentRequest(**request_args)
        request_copy = copy.copy(request)
        request.add_client_defaults()
        self.assertEqual(
            request_copy,
            request
        )

    @mock.patch('ebcli.lib.ec2.has_default_vpc')
    def test_add_client_defaults(self, has_default_vpc_mock):
        has_default_vpc_mock.return_value = True

        request_args = {
            'app_name': 'ebcli-intTest-app',
            'cname': None,
            'env_name': 'my-awesome-env',
            'instance_profile': 'my-instance-profile',
            'key_name': 'my-key-name',
            'platform': self.solution,
        }

        request = requests.CreateEnvironmentRequest(**request_args)
        request.add_client_defaults()
        self.assertEqual(
            [
                {
                    'Namespace': 'aws:elasticbeanstalk:command',
                    'OptionName': 'BatchSize',
                    'Value': '30'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:command',
                    'OptionName': 'BatchSizeType',
                    'Value': 'Percentage'
                },
                {
                    'Namespace': 'aws:elb:policies',
                    'OptionName': 'ConnectionDrainingEnabled',
                    'Value': 'true'
                },
                {
                    'Namespace': 'aws:elb:loadbalancer',
                    'OptionName': 'CrossZone',
                    'Value': 'true'
                },
                {
                    'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
                    'OptionName': 'RollingUpdateEnabled',
                    'Value': 'true'
                },
                {
                    'Namespace': 'aws:autoscaling:updatepolicy:rollingupdate',
                    'OptionName': 'RollingUpdateType',
                    'Value': 'Health'
                }
            ],
            request.option_settings
        )

    @mock.patch('ebcli.lib.ec2.has_default_vpc')
    def test_add_client_defaults__worker_tier(self, has_default_vpc_mock):
        has_default_vpc_mock.return_value = True

        request_args = {
            'app_name': 'ebcli-intTest-app',
            'cname': None,
            'tier': tier.Tier('Worker', 'SQS/HTTP', ''),
            'env_name': 'my-awesome-env',
            'instance_profile': 'my-instance-profile',
            'key_name': 'my-key-name',
            'platform': self.solution,
        }

        request = requests.CreateEnvironmentRequest(**request_args)
        request.add_client_defaults()
        self.assertEqual(
            [
                {
                    'Namespace': 'aws:elasticbeanstalk:command',
                    'OptionName': 'BatchSize',
                    'Value': '30'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:command',
                    'OptionName': 'BatchSizeType',
                    'Value': 'Percentage'
                }
            ],
            request.option_settings
        )

    def test_compile_shared_lb_options(self):
        request_args = {
            'elb_type': 'application',
            'app_name': 'ebcli-intTest-app',
            'env_name': 'my-awesome-env',
            'shared_lb': 'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-1/72074d479748b405',
            'shared_lb_port': '100'
        }
        request = requests.CreateEnvironmentRequest(**request_args)
        self.assertEqual([], request.option_settings)

        request.compile_shared_lb_options()
        self.assertEqual(
            [
                {
                    'Namespace': 'aws:elasticbeanstalk:environment',
                    'OptionName': 'LoadBalancerIsShared',
                    'Value': 'true'
                },
                {
                    'Namespace': 'aws:elbv2:loadbalancer',
                    'OptionName': 'SharedLoadBalancer',
                    'Value': 'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-1/72074d479748b405'
                },
                {
                    'Namespace': 'aws:elbv2:listener:100',
                    'OptionName': 'Rules',
                    'Value': 'default'
                }
            ],
            request.option_settings
        )

    def test_get_standard_kwargs(self):
        pass
