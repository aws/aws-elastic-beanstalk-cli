# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

