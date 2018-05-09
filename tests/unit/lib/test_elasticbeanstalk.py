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

from ebcli.lib import elasticbeanstalk
from ebcli.objects.buildconfiguration import BuildConfiguration

from .. import mock_responses


DESCRIBE_ENVIRONMENTS_RESPONSE = {
    'Environments': [
        {
            'HealthStatus': 'Severe',
            'ApplicationName': 'my-application',
            'VersionLabel': 'app-171013_210522',
            'PlatformArn': 'arn:aws:elasticbeanstalk:us-east-1::platform/PHP 5.4 running on 64bit Amazon Linux (TEST)/0.0.2',
            'DateUpdated': '2018-04-12T23:13:47.539Z',
            'Alerts': [],
            'EnvironmentArn': 'arn:aws:elasticbeanstalk:us-east-1:123123123123:environment/my-application/my-environment',
            'DateCreated': '2017-10-13T21:05:28.754Z',
            'AbortableOperationInProgress': False,
            'Health': 'Red',
            'EnvironmentLinks': [],
            'SolutionStackName': '64bit Amazon Linux 2017.03 v0.0.2 running PHP 5.4',
            'EnvironmentId': 'e-rewrwrwer',
            'Status': 'Ready',
            'Tier': {
                'Type': 'Standard',
                'Version': ' ',
                'Name': 'Webserver'
            },
            'Description': 'Environment created from the EB CLI using \'eb create\'',
            'EnvironmentName': 'my-environment'
        }
    ]
}


class TestElasticBeanstalk(unittest.TestCase):
    app_name = 'ebcli-app'
    app_version_name = 'ebcli-app-version'
    env_name = 'ebcli-env'
    description = 'ebcli testing app'
    s3_bucket = 'app_bucket'
    s3_key = 'app_bucket_key'

    repository = 'my-repo'
    commit_id = '123456789'

    image = 'aws/codebuild/eb-java-8-amazonlinux-64:2.1.3'
    compute_type = 'BUILD_GENERAL1_SMALL'
    service_role = 'eb-test'
    timeout = 60
    build_config = BuildConfiguration(image=image, compute_type=compute_type,
                                      service_role=service_role, timeout=timeout)

    def setUp(self):
        self.patcher_aws = mock.patch('ebcli.lib.elasticbeanstalk.aws')
        self.mock_elasticbeanstalk_aws = self.patcher_aws.start()

    def tearDown(self):
        self.patcher_aws.stop()

    def test_create_application_version(self):
        expected_response = {'200'}

        self.mock_elasticbeanstalk_aws.make_api_call.return_value = expected_response

        actual_response = elasticbeanstalk.create_application_version(self.app_name, self.app_version_name,
                                                                      self.description,
                                                                      self.s3_bucket, self.s3_key)

        self.assertEqual(expected_response, actual_response,
                         "Expected response '{0}' but was: {1}".format(expected_response, actual_response))
        self.mock_elasticbeanstalk_aws.make_api_call.assert_called_with('elasticbeanstalk',
                                                                        'create_application_version',
                                                                        ApplicationName=self.app_name,
                                                                        Description=self.description,
                                                                        Process=False,
                                                                        SourceBundle={'S3Bucket': self.s3_bucket,
                                                                                      'S3Key': self.s3_key},
                                                                        VersionLabel=self.app_version_name,)

    def test_create_application_version_with_codecommit(self):
        expected_response = {'200'}

        self.mock_elasticbeanstalk_aws.make_api_call.return_value = expected_response

        actual_response = elasticbeanstalk.create_application_version(self.app_name, self.app_version_name,
                                                                      self.description,
                                                                      None, None, repository=self.repository,
                                                                      commit_id=self.commit_id)

        self.assertEqual(expected_response, actual_response,
                         "Expected response '{0}' but was: {1}".format(expected_response, actual_response))
        self.mock_elasticbeanstalk_aws.make_api_call.assert_called_with('elasticbeanstalk',
                                                                        'create_application_version',
                                                                        ApplicationName=self.app_name,
                                                                        Description=self.description,
                                                                        Process=True,
                                                                        SourceBuildInformation={'SourceType': 'Git',
                                                                                                'SourceRepository': 'CodeCommit',
                                                                                                'SourceLocation': "{0}/{1}".format(self.repository, self.commit_id)},
                                                                        VersionLabel=self.app_version_name,)

    def test_create_application_version_with_codebuild(self):
        expected_response = {'200'}

        self.mock_elasticbeanstalk_aws.make_api_call.return_value = expected_response

        actual_response = elasticbeanstalk.create_application_version(self.app_name, self.app_version_name,
                                                                      self.description,
                                                                      self.s3_bucket, self.s3_key,
                                                                      build_configuration=self.build_config)

        self.assertEqual(expected_response, actual_response,
                         "Expected response '{0}' but was: {1}".format(expected_response, actual_response))
        self.mock_elasticbeanstalk_aws.make_api_call.assert_called_with('elasticbeanstalk',
                                                                        'create_application_version',
                                                                        ApplicationName=self.app_name,
                                                                        Description=self.description,
                                                                        Process=True,
                                                                        SourceBuildInformation={'SourceType': 'Zip',
                                                                                                'SourceRepository': 'S3',
                                                                                                'SourceLocation': "{0}/{1}".format(self.s3_bucket, self.s3_key)},
                                                                        BuildConfiguration={'CodeBuildServiceRole': self.service_role,
                                                                                            'Image': self.image,
                                                                                            'ComputeType': self.compute_type,
                                                                                            'TimeoutInMinutes': self.timeout},
                                                                        VersionLabel=self.app_version_name,)

    @mock.patch('ebcli.lib.elasticbeanstalk._make_api_call')
    def test_get_environments__attempting_to_match_single_env__match_found(
            self,
            _make_api_call_mock
    ):
        _make_api_call_mock.return_value = DESCRIBE_ENVIRONMENTS_RESPONSE

        environments = elasticbeanstalk.get_environments(['my-environment'])
        self.assertEqual('Environment', environments[0].__class__.__name__)

    @mock.patch('ebcli.lib.elasticbeanstalk._make_api_call')
    def test_get_environments__attempting_to_match_single_env__match_not_found(
            self,
            _make_api_call_mock
    ):
        _make_api_call_mock.return_value = {
            'Environments': []
        }

        with self.assertRaises(elasticbeanstalk.NotFoundError) as context_manager:
            elasticbeanstalk.get_environments(['my-environment'])

        self.assertEqual(
            'Could not find any environments from the list: my-environment',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.lib.elasticbeanstalk._make_api_call')
    def test_get_environments__attempting_to_match_multiple_env__match_not_found(
            self,
            _make_api_call_mock
    ):
        _make_api_call_mock.return_value = {
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

    @mock.patch('ebcli.lib.elasticbeanstalk._make_api_call')
    def test_get_environments__attempting_to_match_multiple_env__partial_match_found(
            self,
            _make_api_call_mock
    ):
        _make_api_call_mock.return_value = DESCRIBE_ENVIRONMENTS_RESPONSE

        environments = elasticbeanstalk.get_environments(
            [
                'my-environment',
                'my-absent-environment'
            ]
        )

        self.assertEqual(1, len(environments))
        self.assertEqual('Environment', environments[0].__class__.__name__)

    @mock.patch('ebcli.lib.elasticbeanstalk._make_api_call')
    def test_get_app_version_labels(
            self,
            _make_api_call_mock
    ):
        _make_api_call_mock.return_value = mock_responses.DESCRIBE_APPLICATION_VERSIONS_RESPONSE

        version_labels = elasticbeanstalk.get_app_version_labels('my-application')

        self.assertEqual(
            [
                'version-label-1',
                'version-label-2',
            ],
            version_labels
        )

    @mock.patch('ebcli.lib.elasticbeanstalk._make_api_call')
    def test_get_app_version_labels__no_version_labels(
            self,
            _make_api_call_mock
    ):
        _make_api_call_mock.return_value = {
            'ApplicationVersions': []
        }

        version_labels = elasticbeanstalk.get_app_version_labels('my-application')

        self.assertEqual(
            [],
            version_labels
        )
