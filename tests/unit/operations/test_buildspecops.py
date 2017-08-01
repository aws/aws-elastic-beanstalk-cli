# Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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
from mock import MagicMock
import copy

from datetime import datetime
from ebcli.operations import buildspecops
from ebcli.objects.buildconfiguration import BuildConfiguration
from ebcli.objects.exceptions import ServiceError, ValidationError


class TestBuildSpecOps(unittest.TestCase):
    app_name = 'foo-app'
    version_label = 'foo-version-label'
    image = 'aws/codebuild/eb-java-7-amazonlinux-64:2.1.6'
    service_role = 'aws-codebuild-role'
    build_config = BuildConfiguration(image=image, service_role=service_role)
    app_version_raw_response = {'ApplicationVersions': [{u'ApplicationName': app_name,
                                                         u'Status': 'BUILDING',
                                                         u'VersionLabel': version_label,
                                                         u'SourceBuildInformation':
                                                             {
                                                                 u'SourceLocation': 'elasticbeanstalk-us-east-1-123456789098/cli-playground/app-598f-170216_154204.zip',
                                                                 u'SourceType': 'Zip',
                                                                 u'SourceRepository': 'S3'},
                                                         u'Description': 'Update paramter values',
                                                         u'DateCreated': datetime(2017, 2, 16, 23, 42, 7, 341000),
                                                         u'DateUpdated': datetime(2017, 2, 16, 23, 42, 7, 341000),
                                                         u'SourceBundle': {},
                                                         u'BuildArn': 'arn:aws:codebuild:us-east-1:123456789098:build/Elastic-Beanstalk-cli-playground-app-598f-170216_154204-NfPSh:91f82fc0-9de0-4ed0-a458-dc317a7c1771'
                                                         }]
                                }
    build_response = {u'builds':
        [
            {u'buildComplete': False,
             u'logs': {
                 u'groupName': u'/aws/codebuild/Elastic-Beanstalk-cli-playground-app-598f-170216_162002-rKVFA',
                 u'deepLink': u'https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#logEvent:group=/aws/codebuild/Elastic-Beanstalk-cli-playground-app-598f-170216_162002-rKVFA;stream=2e4c797a-440c-45e0-9992-eb2cfe0be161',
                 u'streamName': u'2e4c797a-440c-45e0-9992-eb2cfe0be161'}}
        ]
    }
    list_roles_response = [{u'AssumeRolePolicyDocument':
                                           {u'Version': u'2012-10-17', u'Statement': [
                                               {u'Action': u'sts:AssumeRole', u'Effect': u'Allow',
                                                u'Principal': {u'Service': u'codebuild.amazonaws.com'}}]},
                                       u'RoleName': 'aws-codebuild-role',
                                       u'Path': '/service-role/',
                                       u'Arn': 'arn:aws:iam::123456789098:role/service-role/aws-codebuild-role'
                                       }]

    def setUp(self):
        self.patcher_beanstalk = mock.patch('ebcli.operations.buildspecops.elasticbeanstalk')
        self.patcher_codebuild = mock.patch('ebcli.operations.buildspecops.codebuild')
        self.mock_beanstalk = self.patcher_beanstalk.start()
        self.mock_codebuild = self.patcher_codebuild.start()

    def tearDown(self):
        self.patcher_beanstalk.stop()
        self.patcher_codebuild.stop()

    @mock.patch('ebcli.operations.commonops.wait_for_success_events')
    @mock.patch('ebcli.operations.buildspecops.wait_for_app_version_attribute')
    def test_stream_build_config_app_creation_happy_case(self, mock_wait_attribute, mock_success_events):
        # Setup mock returns
        mock_wait_attribute.return_value = True
        self.mock_beanstalk.get_application_versions.return_value = self.app_version_raw_response
        self.mock_codebuild.batch_get_builds.return_value = self.build_response

        build_spec = MagicMock()
        build_spec.timeout = 364

        # Make actual call we want to test
        buildspecops.stream_build_configuration_app_version_creation(self.app_name, self.version_label, build_spec)

        # Assert we made the correct calls
        mock_wait_attribute.assert_called_with(self.app_name, [self.version_label], 'BuildArn', timeout=1)
        self.mock_beanstalk.get_application_versions.assert_called_with(self.app_name,
                                                                        version_labels=[self.version_label])
        self.mock_codebuild.batch_get_builds.assert_called_with(
            [self.app_version_raw_response['ApplicationVersions'][0]['BuildArn']])
        mock_success_events.assert_called_with(None, timeout_in_minutes=364, can_abort=False,
                                               version_label=self.version_label)

    @mock.patch('ebcli.operations.commonops.wait_for_success_events')
    @mock.patch('ebcli.operations.buildspecops.wait_for_app_version_attribute')
    def test_stream_build_config_app_creation__no_timeout_specified__timeout_defaults_to_60_Minutes(self, mock_wait_attribute, mock_success_events):
        # Setup mock returns
        mock_wait_attribute.return_value = True
        self.mock_beanstalk.get_application_versions.return_value = self.app_version_raw_response
        self.mock_codebuild.batch_get_builds.return_value = self.build_response

        build_spec = MagicMock()
        build_spec.timeout = None

        # Make actual call we want to test
        buildspecops.stream_build_configuration_app_version_creation(self.app_name, self.version_label, build_spec)

        # Assert we made the correct calls
        mock_wait_attribute.assert_called_with(self.app_name, [self.version_label], 'BuildArn', timeout=1)
        self.mock_beanstalk.get_application_versions.assert_called_with(self.app_name,
                                                                        version_labels=[self.version_label])
        self.mock_codebuild.batch_get_builds.assert_called_with(
            [self.app_version_raw_response['ApplicationVersions'][0]['BuildArn']])
        mock_success_events.assert_called_with(None, timeout_in_minutes=60, can_abort=False,
                                               version_label=self.version_label)

    @mock.patch('ebcli.operations.commonops.wait_for_success_events')
    @mock.patch('ebcli.operations.buildspecops.wait_for_app_version_attribute')
    def test_stream_build_config_app_creation_no_build_arn_failed_to_create(self, mock_wait_attribute,
                                                                            mock_success_events):
        # Setup mock returns
        mock_wait_attribute.return_value = False
        self.mock_beanstalk.get_application_versions.return_value = self.app_version_raw_response
        mock_success_events.side_effect = ServiceError('Failed to create application version')

        build_spec = MagicMock()
        build_spec.timeout = 60

        # Make actual call we want to test
        self.assertRaises(ServiceError,
                          buildspecops.stream_build_configuration_app_version_creation,
                          self.app_name, self.version_label, build_spec)

        # Assert we made the correct calls
        mock_wait_attribute.assert_called_with(self.app_name, [self.version_label], 'BuildArn', timeout=1)
        self.mock_beanstalk.get_application_versions.assert_called_with(self.app_name,
                                                                        version_labels=[self.version_label])
        self.mock_codebuild.batch_get_builds.assert_not_called()
        mock_success_events.assert_called_with(None, timeout_in_minutes=60, can_abort=False,
                                               version_label=self.version_label)
        self.mock_beanstalk.delete_application_version.assert_called_with(self.app_name, self.version_label)

    def test_validate_build_config_without_service_role(self):
        # Mock out methods called
        build_config = copy.deepcopy(self.build_config)
        build_config.service_role = None
        build_config.timeout = 60

        # Make the call we want to test
        self.assertRaises(ValidationError, buildspecops.validate_build_config, build_config)

    @mock.patch('ebcli.lib.iam.get_roles')
    def test_validate_build_config_without_image(self, mock_get_roles):
        # Mock out methods called
        build_config = copy.deepcopy(self.build_config)
        build_config.image = None
        mock_get_roles.return_value = self.list_roles_response

        # Make the call we want to test
        self.assertRaises(ValidationError, buildspecops.validate_build_config, build_config)

        # Assert we made the correct calls
        mock_get_roles.assert_called_with()


    @mock.patch('ebcli.lib.iam.get_roles')
    def test_validate_build_config_with_invalid_role(self, mock_get_roles):
        build_config = copy.deepcopy(self.build_config)
        build_config.service_role = 'bad-role'
        # Mock out methods called
        mock_get_roles.return_value = self.list_roles_response

        # Make the call we want to test
        self.assertRaises(ValidationError, buildspecops.validate_build_config, build_config)

        # Assert we made the correct calls
        mock_get_roles.assert_called_with()

    @mock.patch('ebcli.lib.iam.get_roles')
    def test_validate_build_config_happy_case(self, mock_get_roles):
        # Mock out methods called
        mock_get_roles.return_value = self.list_roles_response

        # Make the call we want to test
        buildspecops.validate_build_config(self.build_config)

        # Assert we made the correct calls
        mock_get_roles.assert_called_with()

    def test_wait_for_app_version_attribute_happy_case(self):
        # Mock out methods called
        self.mock_beanstalk.get_application_versions.return_value = self.app_version_raw_response

        # Make the call we want to test
        buildspecops.wait_for_app_version_attribute(self.app_name, [self.version_label], 'BuildArn')

        # Assert we made the correct calls
        self.mock_beanstalk.get_application_versions.assert_called_with(self.app_name, [])
