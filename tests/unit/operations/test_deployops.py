# -*- coding: utf-8 -*-

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
from ebcli.objects.buildconfiguration import BuildConfiguration
from ebcli.operations import deployops


class TestDeployOperations(unittest.TestCase):
    app_name = 'ebcli-app'
    app_version_name = 'ebcli-app-version'
    env_name = 'ebcli-env'
    description = 'ebcli testing app'
    s3_bucket = 'app_bucket'
    s3_key = 'app_bucket_key'

    repository = 'my-repo'
    branch = 'my-branch'
    commit_id = '123456789'

    image = 'aws/codebuild/eb-java-8-amazonlinux-64:2.1.3'
    compute_type = 'BUILD_GENERAL1_SMALL'
    service_role = 'eb-test'
    timeout = 60
    build_config = BuildConfiguration(image=image, compute_type=compute_type,
                                      service_role=service_role, timeout=timeout)

    request_id = 'foo-foo-foo-foo'

    @mock.patch('ebcli.operations.deployops.elasticbeanstalk')
    @mock.patch('ebcli.operations.deployops.commonops')
    @mock.patch('ebcli.operations.deployops.gitops')
    @mock.patch('ebcli.operations.deployops.aws')
    @mock.patch('ebcli.operations.deployops.fileoperations')
    def test_plain_deploy(self, mock_fileops, mock_aws, mock_gitops, mock_commonops, mock_beanstalk):
        mock_aws.get_region_name.return_value = 'us-east-1'
        mock_fileops.build_spec_exists.return_value = False
        mock_gitops.git_management_enabled.return_value = False
        mock_commonops.create_app_version.return_value = self.app_version_name
        mock_beanstalk.update_env_application_version.return_value = self.request_id

        deployops.deploy(self.app_name, self.env_name, None, self.app_version_name, self.description)

        mock_commonops.create_app_version.assert_called_with(self.app_name, process=False,
                                                             label=self.app_version_name, message=self.description,
                                                             staged=False, build_config=None)
        mock_beanstalk.update_env_application_version.assert_called_with(self.env_name, self.app_version_name, None)
        mock_commonops.wait_for_success_events.assert_called_with(
            self.request_id,
            can_abort=True,
            env_name='ebcli-env',
            timeout_in_minutes=5,
        )

    @mock.patch('ebcli.operations.deployops.elasticbeanstalk')
    @mock.patch('ebcli.operations.deployops.commonops')
    @mock.patch('ebcli.operations.deployops.gitops')
    @mock.patch('ebcli.operations.deployops.aws')
    @mock.patch('ebcli.operations.deployops.fileoperations')
    def test_deploy_with_specified_version(self, mock_fileops, mock_aws, mock_gitops, mock_commonops, mock_beanstalk):
        mock_aws.get_region_name.return_value = 'us-east-1'
        mock_fileops.build_spec_exists.return_value = False
        mock_beanstalk.update_env_application_version.return_value = self.request_id

        deployops.deploy(self.app_name, self.env_name, self.app_version_name, None, self.description)

        mock_commonops.create_app_version.assert_not_called()
        mock_beanstalk.update_env_application_version.assert_called_with(self.env_name, self.app_version_name, None)
        mock_commonops.wait_for_success_events.assert_called_with(
            self.request_id,
            can_abort=True,
            env_name='ebcli-env',
            timeout_in_minutes=5
        )

    @mock.patch('ebcli.operations.deployops.elasticbeanstalk')
    @mock.patch('ebcli.operations.deployops.commonops')
    @mock.patch('ebcli.operations.deployops.gitops')
    @mock.patch('ebcli.operations.deployops.aws')
    @mock.patch('ebcli.operations.deployops.fileoperations')
    def test_deployment_with_source(self, mock_fileops, mock_aws, mock_gitops, mock_commonops, mock_beanstalk):
        given_source = 'codecommit/test-repo/foo-branch'

        mock_aws.get_region_name.return_value = 'us-east-1'
        mock_fileops.build_spec_exists.return_value = False
        mock_commonops.create_app_version_from_source.return_value = self.app_version_name
        mock_commonops.wait_for_processed_app_versions.return_value = True
        mock_beanstalk.update_env_application_version.return_value = self.request_id

        deployops.deploy(self.app_name, self.env_name, None, self.app_version_name, self.description,
                         source=given_source, timeout=10)

        mock_commonops.create_app_version_from_source.assert_called_with(self.app_name, given_source, process=False,
                                                             label=self.app_version_name, message=self.description,
                                                             build_config=None)
        mock_commonops.wait_for_processed_app_versions.assert_called_with(self.app_name, [self.app_version_name], timeout=10)
        mock_beanstalk.update_env_application_version.assert_called_with(self.env_name, self.app_version_name, None)
        mock_commonops.wait_for_success_events.assert_called_with(
            self.request_id,
            can_abort=True,
            env_name='ebcli-env',
            timeout_in_minutes=10
        )

    @mock.patch('ebcli.operations.deployops.elasticbeanstalk')
    @mock.patch('ebcli.operations.deployops.commonops')
    @mock.patch('ebcli.operations.deployops.gitops')
    @mock.patch('ebcli.operations.deployops.aws')
    @mock.patch('ebcli.operations.deployops.fileoperations')
    def test_deploy_with_codecommit(self, mock_fileops, mock_aws, mock_gitops, mock_commonops, mock_beanstalk):
        mock_aws.get_region_name.return_value = 'us-east-1'
        mock_fileops.build_spec_exists.return_value = False
        mock_gitops.git_management_enabled.return_value = True
        mock_commonops.wait_for_processed_app_versions.return_value = True
        mock_commonops.create_codecommit_app_version.return_value = self.app_version_name
        mock_beanstalk.update_env_application_version.return_value = self.request_id

        deployops.deploy(self.app_name, self.env_name, None, self.app_version_name, self.description)

        mock_commonops.create_codecommit_app_version.assert_called_with(self.app_name, process=False,
                                                                        label=self.app_version_name,
                                                                        message=self.description, build_config=None)
        mock_commonops.wait_for_processed_app_versions.assert_called_with(self.app_name, [self.app_version_name], timeout=5)
        mock_beanstalk.update_env_application_version.assert_called_with(self.env_name, self.app_version_name, None)
        mock_commonops.wait_for_success_events.assert_called_with(
            self.request_id,
            can_abort=True,
            env_name='ebcli-env',
            timeout_in_minutes=5
        )

    @mock.patch('ebcli.operations.deployops.buildspecops')
    @mock.patch('ebcli.operations.deployops.elasticbeanstalk')
    @mock.patch('ebcli.operations.deployops.commonops')
    @mock.patch('ebcli.operations.deployops.gitops')
    @mock.patch('ebcli.operations.deployops.aws')
    @mock.patch('ebcli.operations.deployops.fileoperations')
    def test_plain_deploy_with_codebuild_buildspec(self, mock_fileops, mock_aws, mock_gitops, mock_commonops,
                                                   mock_beanstalk, mock_buildspecops):
        mock_aws.get_region_name.return_value = 'us-east-1'
        mock_fileops.build_spec_exists.return_value = True
        mock_build_config = self.build_config
        mock_build_config.timeout = 60
        mock_fileops.get_build_configuration.return_value = mock_build_config 
        mock_gitops.git_management_enabled.return_value = False
        mock_commonops.create_app_version.return_value = self.app_version_name
        mock_beanstalk.get_application_versions.return_value = [{"BuildArn": "arn::build:project"}]
        mock_beanstalk.update_env_application_version.return_value = self.request_id

        deployops.deploy(self.app_name, self.env_name, None, self.app_version_name, self.description)

        mock_buildspecops.stream_build_configuration_app_version_creation.assert_called_with(self.app_name, self.app_version_name, mock_build_config)
        mock_commonops.create_app_version.assert_called_with(self.app_name, process=False,
                                                             label=self.app_version_name, message=self.description,
                                                             staged=False, build_config=mock_build_config)
        mock_beanstalk.update_env_application_version.assert_called_with(self.env_name, self.app_version_name, None)
        mock_commonops.wait_for_success_events.assert_called_with(
            self.request_id,
            can_abort=True,
            env_name='ebcli-env',
            timeout_in_minutes=5
        )
