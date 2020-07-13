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

from ebcli.lib import elasticbeanstalk
from ebcli.objects.requests import CreateEnvironmentRequest, CloneEnvironmentRequest
from ebcli.objects.platform import PlatformVersion
from ebcli.objects.buildconfiguration import BuildConfiguration

from .. import mock_responses


class TestElasticbeanstalk(unittest.TestCase):
    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_create_application_version(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.CREATE_APPLICATION_VERSION_RESPONSE

        self.assertEqual(
            mock_responses.CREATE_APPLICATION_VERSION_RESPONSE,
            elasticbeanstalk.create_application_version(
                'my-application',
                'v1',
                'MyAppv1',
                'my-bucket',
                'sample-war'
            )
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'create_application_version',
            ApplicationName='my-application',
            Description='MyAppv1',
            Process=False,
            SourceBundle={
                'S3Bucket': 'my-bucket',
                'S3Key': 'sample-war'
            },
            VersionLabel='v1'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_create_application_version_with_codecommit(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.CREATE_APPLICATION_VERSION_RESPONSE__WITH_CODECOMMIT

        self.assertEqual(
            mock_responses.CREATE_APPLICATION_VERSION_RESPONSE__WITH_CODECOMMIT,
            elasticbeanstalk.create_application_version(
                'my-application',
                'v1',
                'MyAppversion',
                None,
                None,
                repository='my-repository',
                commit_id='532452452eeaadcbf532452452eeaadcbf'
            )
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_create_application_version_with_codebuild(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.CREATE_APPLICATION_VERSION_RESPONSE__WITH_CODECOMMIT
        self.assertEqual(
            mock_responses.CREATE_APPLICATION_VERSION_RESPONSE__WITH_CODECOMMIT,
            elasticbeanstalk.create_application_version(
                'my-application',
                'v1',
                'MyAppversion',
                'my-bucket',
                'sample-war',
                build_configuration=BuildConfiguration(
                    service_role='CodeBuildServiceRole',
                    image='Java 8 Image',
                    compute_type='t2.micro',
                    timeout='5',
                )
            )
        )
        make_api_call_mock.assert_called_with(
            'elasticbeanstalk',
            'create_application_version',
            ApplicationName='my-application',
            BuildConfiguration={
                'CodeBuildServiceRole': 'CodeBuildServiceRole',
                'Image': 'Java 8 Image',
                'ComputeType': 't2.micro',
                'TimeoutInMinutes': '5'
            },
            Description='MyAppversion',
            Process=True,
            SourceBuildInformation={
                'SourceType': 'Zip',
                'SourceRepository': 'S3',
                'SourceLocation': 'my-bucket/sample-war'
            },
            VersionLabel='v1'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_environments__attempting_to_match_single_env__match_found(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE

        environments = elasticbeanstalk.get_environments(['environment-1'])
        self.assertEqual('Environment', environments[0].__class__.__name__)

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_environments__attempting_to_match_single_env__match_not_found(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = {
            'Environments': []
        }

        with self.assertRaises(elasticbeanstalk.NotFoundError) as context_manager:
            elasticbeanstalk.get_environments(['my-environment'])

        self.assertEqual(
            'Could not find any environments from the list: my-environment',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_environments__attempting_to_match_multiple_env__match_not_found(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = {
            'Environments': []
        }

        with self.assertRaises(elasticbeanstalk.NotFoundError) as context_manager:
            elasticbeanstalk.get_environments(
                [
                    'my-absent-environment-1',
                    'my-absent-environment-2'
                ]
            )

        self.assertEqual(
            'Could not find any environments from the list: my-absent-environment-1, my-absent-environment-2',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_environments__attempting_to_match_multiple_env__partial_match_found(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE

        environments = elasticbeanstalk.get_environments(
            [
                'environment-1',
                'my-absent-environment'
            ]
        )

        self.assertEqual(4, len(environments))
        self.assertEqual('Environment', environments[0].__class__.__name__)

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_app_version_labels(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_APPLICATION_VERSIONS_RESPONSE

        version_labels = elasticbeanstalk.get_app_version_labels('my-application')

        self.assertEqual(
            [
                'version-label-1',
                'version-label-2',
            ],
            version_labels
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_app_version_labels__no_version_labels(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = {
            'ApplicationVersions': []
        }

        version_labels = elasticbeanstalk.get_app_version_labels('my-application')

        self.assertEqual(
            [],
            version_labels
        )

    @mock.patch('ebcli.lib.elasticbeanstalk._make_api_call')
    def test_application_version_exists(
            self,
            _make_api_call_mock
    ):
        _make_api_call_mock.return_value = mock_responses.DESCRIBE_APPLICATION_VERSIONS_RESPONSE

        application_version = elasticbeanstalk.application_version_exists('my-application', 'version-label-1')

        self.assertEqual(
            {
                "ApplicationName": "my-application",
                "VersionLabel": "version-label-1",
                "Description": "update cover page",
                "DateCreated": "2015-07-23T01:32:26.079Z",
                "DateUpdated": "2015-07-23T01:32:26.079Z",
                "SourceBundle": {
                    "S3Bucket": "elasticbeanstalk-us-west-2-123123123123",
                    "S3Key": "my-app/9112-stage-150723_224258.war"
                }
            },
            application_version
        )

    @mock.patch('ebcli.lib.elasticbeanstalk._make_api_call')
    def test_application_version_exists__application_version_not_found(
            self,
            _make_api_call_mock
    ):
        _make_api_call_mock.return_value = {
            'ApplicationVersions': []
        }

        application_version = elasticbeanstalk.application_version_exists('my-application', 'version-label-1')

        self.assertIsNone(application_version)

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_delete_platform(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DELETE_PLATFORM_VERSION_RESPONSE
        self.assertEqual(
            mock_responses.DELETE_PLATFORM_VERSION_RESPONSE,
            elasticbeanstalk.delete_platform(
                'arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/zqozvhohaq-custom-platform/1.0.0'
            )
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_list_platform_versions(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.side_effect = [
            mock_responses.LIST_CUSTOM_PLATFOM_VERSIONS_RESPONSE__WITH_NEXT_TOKEN,
            mock_responses.LIST_CUSTOM_PLATFOM_VERSIONS_RESPONSE
        ]

        self.assertEqual(
            (
                mock_responses.LIST_CUSTOM_PLATFOM_VERSIONS_RESPONSE['PlatformSummaryList']
                +
                mock_responses.LIST_CUSTOM_PLATFOM_VERSIONS_RESPONSE__WITH_NEXT_TOKEN['PlatformSummaryList']
            ),
            elasticbeanstalk.list_platform_versions(
                filters=[
                    {
                        'Type': 'PlatformOwner',
                        'Operator': '=',
                        'Values': 'self'
                    }
                ]
            )
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_describe_platform_version(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_CUSTOM_PLATFORM_VERSION_RESPONSE
        self.assertEqual(
            mock_responses.DESCRIBE_CUSTOM_PLATFORM_VERSION_RESPONSE['PlatformDescription'],
            elasticbeanstalk.describe_platform_version(
                "arn:aws:elasticbeanstalk:us-west-2:123123123123:platform/xutrezqmqw-custom-platform/1.0.0"
            )
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_create_application(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.CREATE_APPLICATION_RESPONSE
        self.assertEqual(
            mock_responses.CREATE_APPLICATION_RESPONSE,
            elasticbeanstalk.create_application(
                'my-application',
                'my-application'
            )
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_create_application__invalid_parameter_value_error_encountered(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.side_effect = elasticbeanstalk.aws.InvalidParameterValueError(
            message='Application existing-application already exists.'
        )
        with self.assertRaises(elasticbeanstalk.AlreadyExistsError):
            elasticbeanstalk.create_application(
                'existing-application',
                'my-application'
            )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_create_application__general_exception(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.side_effect = Exception('could not create app')
        with self.assertRaises(Exception) as context_manager:
            elasticbeanstalk.create_application(
                'existing-application',
                'my-application'
            )

        self.assertEqual(
            'could not create app',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_create_platform_version(
            self,
            make_api_call_mock
    ):
        elasticbeanstalk.create_platform_version(
            'my-custom-platform',
            '1.2.3',
            'my-bucket',
            'my-key',
            'my-instance-profile',
            'my-ec2-key-name',
            't2.micro',
            tags=[
                {'Key': 'a', 'Value': 'value1'},
                {'Key': 'b', 'Value': 'value2'}
            ],
            vpc={
                'id': 'vpc-id',
                'subnets': 'subnet-id-1,subnet-id-2',
                'publicip': 'true',
            }
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'create_platform_version',
            OptionSettings=[
                {
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'IamInstanceProfile',
                    'Value': 'my-instance-profile'
                },
                {
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'EC2KeyName',
                    'Value': 'my-ec2-key-name'
                },
                {
                    'Namespace': 'aws:autoscaling:launchconfiguration',
                    'OptionName': 'InstanceType',
                    'Value': 't2.micro'
                },
                {
                    'Namespace': 'aws:ec2:vpc',
                    'OptionName': 'VPCId',
                    'Value': 'vpc-id'
                },
                {
                    'Namespace': 'aws:ec2:vpc',
                    'OptionName': 'Subnets',
                    'Value': 'subnet-id-1,subnet-id-2'
                },
                {
                    'Namespace': 'aws:ec2:vpc',
                    'OptionName': 'AssociatePublicIpAddress',
                    'Value': 'true'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:healthreporting:system',
                    'OptionName': 'SystemType',
                    'Value': 'enhanced'
                },
                {
                    'Namespace': 'aws:elasticbeanstalk:environment',
                    'OptionName': 'ServiceRole',
                    'Value': 'aws-elasticbeanstalk-service-role'
                }
            ],
            PlatformDefinitionBundle={
                'S3Bucket': 'my-bucket',
                'S3Key': 'my-key'
            },
            PlatformName='my-custom-platform',
            PlatformVersion='1.2.3',
            Tags=[
                {'Key': 'a', 'Value': 'value1'},
                {'Key': 'b', 'Value': 'value2'}
            ],
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    @mock.patch('ebcli.lib.elasticbeanstalk.aws.get_region_name')
    @mock.patch('ebcli.lib.ec2.has_default_vpc')
    def test_create_environment(
            self,
            has_default_vpc_mock,
            get_region_name_mock,
            make_api_call_mock
    ):
        self.maxDiff = None
        has_default_vpc_mock.return_value = True
        get_region_name_mock.return_value = 'us-east-1'
        make_api_call_mock.return_value = mock_responses.CREATE_ENVIRONMENT_RESPONSE
        environment_request = CreateEnvironmentRequest(
            app_name='my-application',
            env_name='environment-1',
            platform=PlatformVersion("arn:aws:elasticbeanstalk:us-west-2::platform/Docker running on 64bit Amazon Linux/2.1.0"),
            database={
                'username': 'root',
                'password': 'password',
                'engine': 'mysql',
                'size': '10',
                'instance': 'db.t2.micro',
                'version': '5.6.35'
            },
            vpc={
                'id': 'my-vpc-id',
                'ec2subnets': 'subnet-1,subnet-2,subnet-3',
                'elbsubnets': 'subnet-1,subnet-2,subnet-3',
                'elbscheme': 'public',
                'publicip': 'true',
                'securitygroups': 'security-group-1,security-group-2',
                'dbsubnets': 'subnet-1,subnet-2,subnet-3',
            }
        )

        elasticbeanstalk.create_environment(environment_request)

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'create_environment',
            ApplicationName='my-application',
            Description='Environment created from the EB CLI using "eb create"',
            EnvironmentName='environment-1',
            OptionSettings=[
                {
                    'Namespace': 'aws:elasticbeanstalk:healthreporting:system',
                    'OptionName': 'SystemType',
                    'Value': 'enhanced'
                },
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
                },
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
                },
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
            PlatformArn='arn:aws:elasticbeanstalk:us-west-2::platform/Docker running on 64bit Amazon Linux/2.1.0',
            TemplateSpecification={
                'TemplateSnippets': [
                    {
                        'SnippetName': 'RdsExtensionEB',
                        'Order': 10000,
                        'SourceUrl': 'https://s3.amazonaws.com/elasticbeanstalk-env-resources-us-east-1/eb_snippets/rds/rds.json'
                    }
                ]
            }
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    @mock.patch('ebcli.lib.elasticbeanstalk.aws.get_region_name')
    @mock.patch('ebcli.lib.ec2.has_default_vpc')
    def test_clone_environment(
            self,
            has_default_vpc_mock,
            get_region_name_mock,
            make_api_call_mock
    ):
        self.maxDiff = None
        has_default_vpc_mock.return_value = True
        get_region_name_mock.return_value = 'us-east-1'
        make_api_call_mock.return_value = mock_responses.CREATE_ENVIRONMENT_RESPONSE
        environment_request = CloneEnvironmentRequest(
            app_name='my-application',
            env_name='environment-1-clone',
            original_name='environment-1',
            platform=PlatformVersion("arn:aws:elasticbeanstalk:us-west-2::platform/Docker running on 64bit Amazon Linux/2.1.0"),
        )

        elasticbeanstalk.clone_environment(environment_request)

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'create_environment',
            ApplicationName='my-application',
            Description='Environment cloned from environment-1-clone from the EB CLI using "eb clone"',
            EnvironmentName='environment-1-clone',
            OptionSettings=[],
            PlatformArn='arn:aws:elasticbeanstalk:us-west-2::platform/Docker running on 64bit Amazon Linux/2.1.0',
            TemplateSpecification={
                'TemplateSource': {
                    'EnvironmentName': 'environment-1'
                }
            }
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_delete_application(
            self,
            mock_api_call_mock
    ):
        mock_api_call_mock.return_value = {
            'ResponseMetadata': {
                'RequestId': '123123123123'
            }
        }

        elasticbeanstalk.delete_application('my-application')

        mock_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'delete_application',
            ApplicationName='my-application'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_delete_application_version(
            self,
            mock_api_call_mock
    ):
        mock_api_call_mock.return_value = {
            'ResponseMetadata': {
                'RequestId': '123123123123'
            }
        }

        elasticbeanstalk.delete_application_version(
            'my-application',
            'v1'
        )

        mock_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'delete_application_version',
            ApplicationName='my-application',
            DeleteSourceBundle=True,
            VersionLabel='v1'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_delete_application_and_envs(
            self,
            mock_api_call_mock
    ):
        mock_api_call_mock.return_value = {
            'ResponseMetadata': {
                'RequestId': '123123123123'
            }
        }

        elasticbeanstalk.delete_application_and_envs(
            'my-application'
        )

        mock_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'delete_application',
            ApplicationName='my-application',
            TerminateEnvByForce=True
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_describe_application(
            self,
            mock_api_call_mock
    ):
        mock_api_call_mock.return_value = {
            'Applications': [
                {
                    'ApplicationName': 'my-application'
                }
            ],
            'ResponseMetadata': {
                'RequestId': 'd88449fe-feef-4d28-afdb-c8a34e99f757',
                'HTTPStatusCode': 200,
                'date': 'Wed, 16 May 2018 00:43:52 GMT',
                'RetryAttempts': 0
            }
        }

        self.assertEqual(
            {'ApplicationName': 'my-application'},
            elasticbeanstalk.describe_application(
                'my-application'
            )
        )

        mock_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'describe_applications',
            ApplicationNames=['my-application']
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_describe_application__not_found(
            self,
            mock_api_call_mock
    ):
        mock_api_call_mock.return_value = {
            'Applications': [],
            'ResponseMetadata': {
                'RequestId': 'd88449fe-feef-4d28-afdb-c8a34e99f757',
                'HTTPStatusCode': 200,
                'date': 'Wed, 16 May 2018 00:43:52 GMT',
                'RetryAttempts': 0
            }
        }

        with self.assertRaises(elasticbeanstalk.NotFoundError):
            elasticbeanstalk.describe_application(
                'absent-application'
            )

        mock_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'describe_applications',
            ApplicationNames=['absent-application']
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_is_cname_available(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.CHECK_DNS_AVAILABILITY_RESPONSE

        self.assertTrue(
            elasticbeanstalk.is_cname_available(
                "my-cname.elasticbeanstalk.com"
            )
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_swap_environment_cnames(
            self,
            mock_api_call_mock
    ):
        mock_api_call_mock.return_value = {
            'Applications': [],
            'ResponseMetadata': {
                'RequestId': 'd88449fe-feef-4d28-afdb-c8a34e99f757',
                'HTTPStatusCode': 200,
                'date': 'Wed, 16 May 2018 00:43:52 GMT',
                'RetryAttempts': 0
            }
        }

        elasticbeanstalk.swap_environment_cnames(
            'source-environment',
            'dest-environment'
        )

        mock_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'swap_environment_cnames',
            DestinationEnvironmentName='dest-environment',
            SourceEnvironmentName='source-environment'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_describe_applications(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_APPLICATIONS_RESPONSE

        self.assertEqual(
            mock_responses.DESCRIBE_APPLICATIONS_RESPONSE['Applications'],
            elasticbeanstalk.describe_applications()
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_application_exist(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_APPLICATION_RESPONSE

        self.assertTrue(elasticbeanstalk.application_exist('my-application'))

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_application_exist__false(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = {
            'Applications': []
        }

        self.assertFalse(elasticbeanstalk.application_exist('my-application'))

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_describe_configuration_settings(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE

        self.assertEqual(
            mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE['ConfigurationSettings'][0],
            elasticbeanstalk.describe_configuration_settings(
                'my-application',
                'environment-1'
            )
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_application_names(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_APPLICATIONS_RESPONSE

        self.assertEqual(
            ['my-application', 'my-application-2', 'my-application-3'],
            elasticbeanstalk.get_application_names()
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_option_setting_from_environment(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE

        self.assertEqual(
            '20',
            elasticbeanstalk.get_option_setting_from_environment(
                'my-application',
                'environment-1',
                'aws:elb:policies',
                'ConnectionDrainingTimeout'
            )
        )

    def test_get_option_setting(self):
        self.assertEqual(
            '20',
            elasticbeanstalk.get_option_setting(
                mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE['ConfigurationSettings'][0]['OptionSettings'],
                'aws:elb:policies',
                'ConnectionDrainingTimeout'
            )
        )

    def test_get_option_setting__option_not_found(self):
        self.assertIsNone(
            elasticbeanstalk.get_option_setting(
                mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE['ConfigurationSettings'][0]['OptionSettings'],
                'aws:elb:policies21313213',
                'ConnectionDrainingTimeout'
            )
        )

    def test_create_option_setting(self):
        self.assertEqual(
            {
                'Namespace': 'aws:elb:policies',
                'OptionName': 'ConnectionDrainingTimeout',
                'Value': '20'
            },
            elasticbeanstalk.create_option_setting(
                'aws:elb:policies',
                'ConnectionDrainingTimeout',
                '20'
            )
        )

    def test_get_specific_configuration(self):
        self.assertEqual(
            '20',
            elasticbeanstalk.get_specific_configuration(
                mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE['ConfigurationSettings'][0],
                'aws:elb:policies',
                'ConnectionDrainingTimeout'
            )
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_specific_configuration_for_env(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE
        self.assertEqual(
            '20',
            elasticbeanstalk.get_specific_configuration_for_env(
                'my-application',
                'environment-1',
                'aws:elb:policies',
                'ConnectionDrainingTimeout'
            )
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_available_solution_stacks__none_available(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = {
            'SolutionStacks': []
        }

        with self.assertRaises(elasticbeanstalk.NotFoundError) as context_manager:
            elasticbeanstalk.get_available_solution_stacks()

        self.assertEqual(
            'Elastic Beanstalk could not find any platforms. '
            'Ensure you have the necessary permissions to access Elastic Beanstalk.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_available_solution_stacks(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.LIST_AVAILABLE_SOLUTION_STACKS

        self.assertEqual(
            len(mock_responses.LIST_AVAILABLE_SOLUTION_STACKS['SolutionStacks']),
            len(elasticbeanstalk.get_available_solution_stacks())
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_application_versions(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_APPLICATION_VERSIONS_RESPONSE
        elasticbeanstalk.get_application_versions(
            'my-application',
            version_labels=['v1', 'v2'],
            max_records=10,
            next_token='asdfadfasdf'
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'describe_application_versions',
            ApplicationName='my-application',
            MaxRecords=10,
            NextToken='asdfadfasdf',
            VersionLabels=['v1', 'v2']
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_applications(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_APPLICATIONS_RESPONSE

        applications = elasticbeanstalk.get_all_applications()
        self.assertEqual(
            {'my-application-2', 'my-application', 'my-application-3'},
            set([application.name for application in applications]),
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'describe_applications'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_raw_app_environments(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE
        self.assertEqual(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments'],
            elasticbeanstalk.get_raw_app_environments(
                'my-application',
                include_deleted=True,
                deleted_back_to="2015-08-13T23:30:07Z"
            )
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'describe_environments',
            ApplicationName='my-application',
            IncludeDeleted=True,
            IncludedDeletedBackTo='2015-08-13T23:30:07Z'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_app_environments(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE
        self.assertEqual(
            len(mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments']),
            len(
                elasticbeanstalk.get_app_environments(
                    'my-application',
                    include_deleted=True,
                    deleted_back_to="2015-08-13T23:30:07Z"
                )
            )
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'describe_environments',
            ApplicationName='my-application',
            IncludeDeleted=True,
            IncludedDeletedBackTo='2015-08-13T23:30:07Z'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_all_environment_names(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE
        self.assertEqual(
            {'environment-1', 'environment-2', 'environment-3', 'environment-4'},
            set(elasticbeanstalk.get_all_environment_names())
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_all_environments(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE
        self.assertEqual(
            4,
            len(elasticbeanstalk.get_all_environment_names())
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_environment(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE__SINGLE_ENVIRONMENT

        environment = elasticbeanstalk.get_environment(
            app_name='my-application',
            env_name='environment-1',
            env_id='e-sfsdfsfasdads',
            include_deleted=True,
            deleted_back_to='2015-08-13T23:30:07Z',
        )
        self.assertEqual('environment-1', environment.name)
        self.assertEqual('e-sfsdfsfasdads', environment.id)

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'describe_environments',
            ApplicationName='my-application',
            EnvironmentIds=['e-sfsdfsfasdads'],
            EnvironmentNames=['environment-1'],
            IncludeDeleted=True,
            IncludedDeletedBackTo='2015-08-13T23:30:07Z'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_environment__environment_not_found(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = {
            'Environments': []
        }

        with self.assertRaises(elasticbeanstalk.NotFoundError) as context_manager:
            elasticbeanstalk.get_environment(
                app_name='my-application',
                env_name='environment-1',
                env_id='e-sfsdfsfasdads',
                include_deleted=True,
                deleted_back_to='2015-08-13T23:30:07Z',
            )

        self.assertEqual(
            'Environment "environment-1" not Found.',
            str(context_manager.exception)
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'describe_environments',
            ApplicationName='my-application',
            EnvironmentIds=['e-sfsdfsfasdads'],
            EnvironmentNames=['environment-1'],
            IncludeDeleted=True,
            IncludedDeletedBackTo='2015-08-13T23:30:07Z'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_environment_names(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE
        self.assertEqual(
            {'environment-2', 'environment-3', 'environment-1', 'environment-4'},
            set(elasticbeanstalk.get_environment_names('my-application'))
        )
        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'describe_environments',
            ApplicationName='my-application',
            IncludeDeleted=False
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_app_version_labels(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_APPLICATION_VERSIONS_RESPONSE
        self.assertEqual(
            {'version-label-2', 'version-label-1'},
            set(elasticbeanstalk.get_app_version_labels('my-application'))
        )
        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'describe_application_versions',
            ApplicationName='my-application'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_environment_settings(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE

        environment = elasticbeanstalk.get_environment_settings(
            'my-application',
            'environment-1'
        )

        self.assertEqual('environment-1', environment.name)
        self.assertEqual(
            mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE['ConfigurationSettings'][0]['OptionSettings'],
            environment.option_settings
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'describe_configuration_settings',
            ApplicationName='my-application',
            EnvironmentName='environment-1'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_environment_resources(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENT_RESOURCES_RESPONSE

        self.assertEqual(
            mock_responses.DESCRIBE_ENVIRONMENT_RESOURCES_RESPONSE,
            elasticbeanstalk.get_environment_resources('environment-1')
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'describe_environment_resources',
            EnvironmentName='environment-1'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_new_events__no_new_events(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = {
            'Events': []
        }

        self.assertEqual(
            [],
            elasticbeanstalk.get_new_events(
                'my-application',
                'environment-1',
                '1341234123412341234134',
                last_event_time=datetime.datetime(2018, 3, 27, 23, 47, 41, 830000, tzinfo=tz.tzutc()),
                version_label='v1',
                platform_arn='arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.0 running on 64bit Amazon Linux/2.7.0'
            )
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'describe_events',
            ApplicationName='my-application',
            EnvironmentName='environment-1',
            PlatformArn='arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.0 running on 64bit Amazon Linux/2.7.0',
            RequestId='1341234123412341234134',
            StartTime='2018-03-27 23:47:41.831000+00:00',
            VersionLabel='v1'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_new_events(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_EVENTS_RESPONSE

        self.assertEqual(
            set(elasticbeanstalk.Event.json_to_event_objects(mock_responses.DESCRIBE_EVENTS_RESPONSE['Events'])),
            set(elasticbeanstalk.get_new_events(
                'my-application',
                'environment-1',
                '1341234123412341234134',
                last_event_time=datetime.datetime(2018, 3, 27, 23, 47, 41, 830000, tzinfo=tz.tzutc()),
                version_label='v1',
                platform_arn='arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.0 running on 64bit Amazon Linux/2.7.0'
            ))
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'describe_events',
            ApplicationName='my-application',
            EnvironmentName='environment-1',
            PlatformArn='arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.0 running on 64bit Amazon Linux/2.7.0',
            RequestId='1341234123412341234134',
            StartTime='2018-03-27 23:47:41.831000+00:00',
            VersionLabel='v1'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_storage_location(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.CREATE_STORAGE_LOCATION_RESPONSE

        self.assertEqual(
            'elasticbeanstalk-us-west-2-0123456789012',
            elasticbeanstalk.get_storage_location()
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'create_storage_location'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_abort_environment_update(
            self,
            make_api_call_mock
    ):
        elasticbeanstalk.abort_environment_update('environment-1')

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'abort_environment_update',
            EnvironmentName='environment-1'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_create_configuration_template(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.CREATE_CONFIGURATION_TEMPLATE_RESPONSE
        self.assertEqual(
            mock_responses.CREATE_CONFIGURATION_TEMPLATE_RESPONSE,
            elasticbeanstalk.create_configuration_template(
                'my-application',
                'environment-1',
                'my-template',
                'my configuration template',
                'mytag=tag-value'
            )
        )
        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'create_configuration_template',
            ApplicationName='my-application',
            Description='my configuration template',
            TemplateName='my-template',
            TemplateSpecification={
                'TemplateSource': {
                    'EnvironmentName': 'environment-1'
                }
            },
            Tags='mytag=tag-value'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_delete_configuration_template(
            self,
            make_api_call_mock
    ):
        elasticbeanstalk.delete_configuration_template(
            'my-application',
            'environment-1'
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'delete_configuration_template',
            ApplicationName='my-application',
            TemplateName='environment-1'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_validate_template__template_is_valid(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.VALIDATE_CONFIGURATION_SETTINGS_RESPONSE__VALID
        self.assertEqual(
            mock_responses.VALIDATE_CONFIGURATION_SETTINGS_RESPONSE__VALID,
            elasticbeanstalk.validate_template(
                'my-application',
                'my-template',
                '64bit Debian jessie v2.10.0 running Python 3.4 (Preconfigured - Docker)'
            )
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'validate_configuration_settings',
            ApplicationName='my-application',
            TemplateName='my-template',
            TemplateSpecification={
                'TemplateSource': {
                    'SolutionStackName': '64bit Debian jessie v2.10.0 running Python 3.4 (Preconfigured - Docker)'
                }
            }
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_validate_template__template_is_invalid(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.VALIDATE_CONFIGURATION_SETTINGS_RESPONSE__INVALID
        self.assertEqual(
            mock_responses.VALIDATE_CONFIGURATION_SETTINGS_RESPONSE__INVALID,
            elasticbeanstalk.validate_template(
                'my-application',
                'my-template',
                '64bit Debian jessie v2.10.0 running Python 3.4 (Preconfigured - Docker)'
            )
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'validate_configuration_settings',
            ApplicationName='my-application',
            TemplateName='my-template',
            TemplateSpecification={
                'TemplateSource': {
                    'SolutionStackName': '64bit Debian jessie v2.10.0 running Python 3.4 (Preconfigured - Docker)'
                }
            }
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_validate_template__platform_arn_is_specified(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.VALIDATE_CONFIGURATION_SETTINGS_RESPONSE__VALID
        self.assertEqual(
            mock_responses.VALIDATE_CONFIGURATION_SETTINGS_RESPONSE__VALID,
            elasticbeanstalk.validate_template(
                'my-application',
                'my-template',
                'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5'
            )
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'validate_configuration_settings',
            ApplicationName='my-application',
            TemplateName='my-template',
            TemplateSpecification={
                'TemplateSource': {
                    'PlatformArn': 'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5'
                }
            }
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_describe_template(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE

        self.assertEqual(
            mock_responses.DESCRIBE_CONFIGURATION_SETTINGS_RESPONSE['ConfigurationSettings'][0],
            elasticbeanstalk.describe_template('my-application', 'my-template')
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'describe_configuration_settings',
            ApplicationName='my-application',
            TemplateName='my-template'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_environment_health(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENT_HEALTH_RESPONSE

        self.assertEqual(
            mock_responses.DESCRIBE_ENVIRONMENT_HEALTH_RESPONSE,
            elasticbeanstalk.get_environment_health('environment-1')
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'describe_environment_health',
            AttributeNames=[
                'HealthStatus',
                'Status',
                'Color',
                'Causes',
                'ApplicationMetrics',
                'InstancesHealth',
                'RefreshedAt'
            ],
            EnvironmentName='environment-1'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_environment_health__attributes_are_specified(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = {
            'HealthStatus': 'Ok'
        }

        self.assertEqual(
            {
                'HealthStatus': 'Ok'
            },
            elasticbeanstalk.get_environment_health('environment-1', attributes=['HealthStatus'])
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'describe_environment_health',
            AttributeNames=[
                'HealthStatus'
            ],
            EnvironmentName='environment-1'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_instance_health(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_INSTANCES_HEALTH_RESPONSE

        self.assertEqual(
            mock_responses.DESCRIBE_INSTANCES_HEALTH_RESPONSE,
            elasticbeanstalk.get_instance_health(
                'environment-1',
                next_token='1234123412341234'
            )
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'describe_instances_health',
            AttributeNames=[
                'HealthStatus',
                'Color',
                'Causes',
                'ApplicationMetrics',
                'RefreshedAt',
                'LaunchedAt',
                'System',
                'Deployment',
                'AvailabilityZone',
                'InstanceType'
            ],
            EnvironmentName='environment-1',
            NextToken='1234123412341234'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_compose_environments(
            self,
            make_api_call_mock
    ):
        elasticbeanstalk.compose_environments(
            'my-application',
            [
                'v1',
                'v2'
            ],
            group_name='dev'
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'compose_environments',
            ApplicationName='my-application',
            GroupName='dev',
            VersionLabels=['v1', 'v2']
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_rebuild_environments(
            self,
            make_api_call_mock
    ):
        elasticbeanstalk.rebuild_environment(
            env_id='e-1234123434',
            env_name='environment-1'
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'rebuild_environment',
            EnvironmentId='e-1234123434',
            EnvironmentName='environment-1'
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_get_environment_arn(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE__SINGLE_ENVIRONMENT
        self.assertEqual(
            'arn:aws:elasticbeanstalk:us-west-2:123123123123:environment/my-application/environment-1',
            elasticbeanstalk.get_environment_arn('environment-1')
        )

        make_api_call_mock.assert_called_once_with(
            'elasticbeanstalk',
            'describe_environments',
            EnvironmentNames=['environment-1'],
            IncludeDeleted=False
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_list_tags_for_resource(
            self,
            make_api_call_mock
    ):
        make_api_call_mock.side_effect = [
            mock_responses.LIST_TAGS_FOR_RESOURCE_RESPONSE,
        ]

        self.assertEqual(
            [
                {
                    'Key': 'Name',
                    'Value': 'environment-1'
                },
                {
                    'Key': 'elasticbeanstalk:environment-id',
                    'Value': 'e-cnpdgh26cm'
                },
                {
                    'Key': 'elasticbeanstalk:environment-name',
                    'Value': 'environment-1'
                }
            ],
            elasticbeanstalk.list_tags_for_resource('arn:aws:elasticbeanstalk:us-west-2:123123123123:environment/my-application/environment-1')
        )

        make_api_call_mock.assert_has_calls(
            [
                mock.call(
                    'elasticbeanstalk',
                    'list_tags_for_resource',
                    ResourceArn='arn:aws:elasticbeanstalk:us-west-2:123123123123:environment/my-application/environment-1'
                )
            ]
        )

    @mock.patch('ebcli.lib.elasticbeanstalk.aws.make_api_call')
    def test_update_tags_for_resource(
            self,
            make_api_call_mock
    ):
        elasticbeanstalk.update_tags_for_resource(
            'arn:aws:elasticbeanstalk:us-west-2:123123123123:environment/my-application/environment-1',
            tags_to_add='KEY1=VALUE1,KEY2=VALUE2',
            tags_to_remove='KEY3'
        )

        make_api_call_mock.assert_has_calls(
            [
                mock.call(
                    'elasticbeanstalk',
                    'update_tags_for_resource',
                    ResourceArn='arn:aws:elasticbeanstalk:us-west-2:123123123123:environment/my-application/environment-1',
                    TagsToAdd='KEY1=VALUE1,KEY2=VALUE2',
                    TagsToRemove='KEY3'
                )
            ]
        )

    @mock.patch('ebcli.lib.elasticbeanstalk._make_api_call')
    def test_list_platform_branches__no_filters(
        self,
        _make_api_call_mock
    ):
        api_response = {
            'PlatformBranchSummaryList': [
                {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux', 'LifecycleState': 'Supported'}
            ],
        }
        _make_api_call_mock.return_value = api_response
        expected_result = api_response['PlatformBranchSummaryList']

        result = elasticbeanstalk.list_platform_branches()

        _make_api_call_mock.assert_called_once_with('list_platform_branches')
        self.assertEqual(result, expected_result)

    @mock.patch('ebcli.lib.elasticbeanstalk._make_api_call')
    def test_list_platform_branches__with_filters(
        self,
        _make_api_call_mock
    ):
        api_response = {
            'PlatformBranchSummaryList': [
                {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux', 'LifecycleState': 'Supported'}
            ],
        }
        filters = [
            {'Attribute': 'PlatformName', 'Operator': '=', 'Values': ['Python']}
        ]
        _make_api_call_mock.return_value = api_response
        expected_result = api_response['PlatformBranchSummaryList']

        result = elasticbeanstalk.list_platform_branches(filters=filters)

        _make_api_call_mock.assert_called_once_with('list_platform_branches', Filters=filters)
        self.assertEqual(result, expected_result)

    @mock.patch('ebcli.lib.elasticbeanstalk._make_api_call')
    def test_list_platform_branches__pagination(
        self,
        _make_api_call_mock
    ):
        api_responses = [
            {
                'PlatformBranchSummaryList': [
                    {'PlatformName': 'Python', 'BranchName': 'Python 3.6 running on 64bit Amazon Linux', 'LifecycleState': 'Supported'},
                    {'PlatformName': 'Python', 'BranchName': 'Python 3.4 running on 64bit Amazon Linux', 'LifecycleState': 'Deprecated'}
                ],
                'NextToken': 's91T7CbPGkFOIOXjkrEMYzEjMSNxNDY5aTY='
            },
            {
                'PlatformBranchSummaryList': [
                    {'PlatformName': 'Python', 'BranchName': 'Python 2.7 running on 64bit Amazon Linux', 'LifecycleState': 'Deprecated'},
                    {'PlatformName': 'Python', 'BranchName': 'Python 2.7 running on 32bit Amazon Linux', 'LifecycleState': 'Retired'}
                ],
                'NextToken': 'TL+36+iG/RNeofj8Jle/szIjMSNxNDY5anY='
            },
            {
                'PlatformBranchSummaryList': [
                    {'PlatformName': 'Python', 'BranchName': 'Python 2.6 running on 32bit Amazon Linux', 'LifecycleState': 'Retired'},
                    {'PlatformName': 'Python', 'BranchName': 'Python 2.6 running on 64bit Amazon Linux', 'LifecycleState': 'Deprecated'}
                ],
            }
        ]
        expected_result = api_responses[0]['PlatformBranchSummaryList']\
                        + api_responses[1]['PlatformBranchSummaryList']\
                        + api_responses[2]['PlatformBranchSummaryList']

        _make_api_call_mock.side_effect = api_responses

        result = elasticbeanstalk.list_platform_branches()

        _make_api_call_mock.assert_has_calls(
            [
                mock.call('list_platform_branches'),
                mock.call('list_platform_branches', NextToken=api_responses[0]['NextToken']),
                mock.call('list_platform_branches', NextToken=api_responses[1]['NextToken']),
            ],
            any_order=False
        )
        self.assertEqual(result, expected_result)

    @mock.patch('ebcli.lib.elasticbeanstalk.describe_configuration_options')
    def test_list_application_load_balancers__no_vpc(
        self,
        describe_configuration_options_mock
    ):
        PlatformArn =  "arn:aws:elasticbeanstalk:us-east-1::platform/Python 3.6 running on 64bit Amazon Linux/2.9.12"
        vpc = None
        api_response = {
            'SolutionStackName': '64bit Amazon Linux 2018.03 v2.9.12 running Python 3.6',
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/Python 3.6 running on 64bit Amazon Linux/2.9.12',
            'Tier': {'Name': 'WebServer', 'Type': 'Standard', 'Version': '1.0'},
            'Options': [
                {
                    'Namespace': 'aws:elbv2:loadbalancer',
                    'Name': 'SharedLoadBalancer',
                    'ChangeSeverity': 'Unknown',
                    'UserDefined': False,
                    'ValueType': 'Scalar',
                    'ValueOptions': [
                        'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-1/72074d479748b405',
                        'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-2/5a957e362e1339a9',
                        'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-3/3dfc9ab663f79319',
                        'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-4/5791574adb5d39c4'],
                    'Description': 'The arn of an existing load balancer to use for environment Load Balancer.'
                },
                {
                    'Namespace': 'aws:elbv2:listener',
                    'Name': 'Rules',
                    'ChangeSeverity': 'Unknown',
                    'UserDefined': False,
                    'ValueType': 'List',
                    'Description': 'List of rules to apply for the listener. These rules are defined in aws:elbv2:listenerrule namespace.'
                }
            ],
            'ResponseMetadata': {'RequestId': '0538eaa9-5dc2-4976-81e0-c485da2f9234', 'HTTPStatusCode': 200, 'date': 'Tue, 07 Jul 2020 18:52:17 GMT', 'RetryAttempts': 0}
        }

        kwargs = {
            'OptionSettings': [
                {'Namespace': 'aws:elasticbeanstalk:environment', 'OptionName': 'LoadBalancerType', 'Value': 'application'},
                {'Namespace': 'aws:elasticbeanstalk:environment', 'OptionName': 'LoadBalancerIsShared', 'Value': 'true'}
            ],
            'Options': [
                {'Namespace': 'aws:elbv2:loadbalancer', 'OptionName': 'SharedLoadBalancer'}
            ],
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/Python 3.6 running on 64bit Amazon Linux/2.9.12'}

        describe_configuration_options_mock.return_value = api_response
        expected_result = api_response['Options'][0]['ValueOptions']

        result = elasticbeanstalk.list_application_load_balancers(PlatformArn, vpc)

        describe_configuration_options_mock.assert_called_once_with(**kwargs)
        self.assertEqual(
                expected_result, result
            )

    @mock.patch('ebcli.lib.elasticbeanstalk.describe_configuration_options')
    def test_list_application_load_balancers__with_vpc(
        self,
        describe_configuration_options_mock
    ):
        PlatformArn =  "arn:aws:elasticbeanstalk:us-east-1::platform/Python 3.6 running on 64bit Amazon Linux/2.9.12"
        vpc = {'id': 'vpc-00252f9da55164b47', 'ec2subnets': 'subnet-018b695a5badc7ec7,subnet-07ce18248accbe5c9'}

        api_response = {
            'SolutionStackName': '64bit Amazon Linux 2018.03 v2.9.12 running Python 3.6',
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/Python 3.6 running on 64bit Amazon Linux/2.9.12',
            'Tier': {'Name': 'WebServer', 'Type': 'Standard', 'Version': '1.0'},
            'Options': [
                {
                    'Namespace': 'aws:elbv2:loadbalancer',
                    'Name': 'SharedLoadBalancer',
                    'ChangeSeverity': 'Unknown',
                    'UserDefined': False,
                    'ValueType': 'Scalar',
                    'ValueOptions': [
                        'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-vpc1/a2f730eefb8aab29',
                        'arn:aws:elasticloadbalancing:us-east-1:881508045124:loadbalancer/app/alb-vpc2/43ca57d4b9462ba6'],
                    'Description': 'The arn of an existing load balancer to use for environment Load Balancer.'
                },
                {
                    'Namespace': 'aws:elbv2:listener',
                    'Name': 'Rules',
                    'ChangeSeverity': 'Unknown',
                    'UserDefined': False,
                    'ValueType': 'List',
                    'Description': 'List of rules to apply for the listener. These rules are defined in aws:elbv2:listenerrule namespace.'
                }
            ],
            'ResponseMetadata': {'RequestId': '6a823882-f6af-46b4-8fa3-ccc8004766c8', 'HTTPStatusCode': 200, 'date': 'Tue, 07 Jul 2020 20:26:26 GMT', 'RetryAttempts': 0}
        }
        kwargs = {
            'OptionSettings': [
                {'Namespace': 'aws:elasticbeanstalk:environment', 'OptionName': 'LoadBalancerType', 'Value': 'application'},
                {'Namespace': 'aws:elasticbeanstalk:environment', 'OptionName': 'LoadBalancerIsShared', 'Value': 'true'},
                {'Namespace': 'aws:ec2:vpc', 'OptionName': 'VPCId', 'Value': 'vpc-00252f9da55164b47'},
                {'Namespace': 'aws:ec2:vpc', 'OptionName': 'Subnets', 'Value': 'subnet-018b695a5badc7ec7,subnet-07ce18248accbe5c9'}
            ],
            'Options': [
                {'Namespace': 'aws:elbv2:loadbalancer', 'OptionName': 'SharedLoadBalancer'}
            ],
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/Python 3.6 running on 64bit Amazon Linux/2.9.12'}

        describe_configuration_options_mock.return_value = api_response
        expected_result = api_response['Options'][0]['ValueOptions']

        result = elasticbeanstalk.list_application_load_balancers(PlatformArn, vpc)
        describe_configuration_options_mock.assert_called_once_with(**kwargs)
        self.assertEqual(
                expected_result, result
            )
