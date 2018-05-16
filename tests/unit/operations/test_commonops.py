# -*- coding: utf-8 -*-

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
import os
import sys
import shutil

import mock
from mock import Mock
import unittest

from ebcli.core import fileoperations
from ebcli.objects.exceptions import NotAuthorizedError
from ebcli.objects.event import Event
from ebcli.operations import commonops
from ebcli.lib.aws import InvalidParameterValueError
from ebcli.objects.buildconfiguration import BuildConfiguration
from ebcli.resources.strings import strings, responses
from ebcli.resources.statics import iam_documents, iam_attributes


class TestCommonOperations(unittest.TestCase):
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
    service_role_arn = 'arn:testcli:eb-test'
    timeout = 60
    build_config = BuildConfiguration(image=image, compute_type=compute_type,
                                      service_role=service_role, timeout=timeout)

    def setUp(self):
        # set up test directory
        if not os.path.exists('testDir'):
            os.makedirs('testDir')
        os.chdir('testDir')

        # set up mock elastic beanstalk directory
        if not os.path.exists(fileoperations.beanstalk_directory):
            os.makedirs(fileoperations.beanstalk_directory)

        # set up mock home dir
        if not os.path.exists('home'):
            os.makedirs('home')

        # change directory to mock home
        fileoperations.aws_config_folder = 'home' + os.path.sep
        fileoperations.aws_config_location \
            = fileoperations.aws_config_folder + 'config'

        # Create local
        fileoperations.create_config_file('ebcli-test', 'us-east-1',
                                          'my-solution-stack')

    def tearDown(self):
        os.chdir(os.path.pardir)
        if os.path.exists('testDir'):
            if sys.platform.startswith('win'):
                os.system('rmdir /S /Q testDir')
            else:
                shutil.rmtree('testDir')

    def test_is_success_event(self):
        self.assertTrue(commonops._is_success_event('Environment health has been set to GREEN'))
        self.assertTrue(commonops._is_success_event('Successfully launched environment: my-env'))
        self.assertTrue(commonops._is_success_event('Pulled logs for environment instances.'))
        self.assertTrue(commonops._is_success_event('terminateEnvironment completed successfully.'))

    def test_raise_if_error_event(self):
        with self.assertRaises(commonops.ServiceError):
            commonops._raise_if_error_event(
                'Environment health has been set to RED'
            )

        with self.assertRaises(commonops.ServiceError):
            commonops._raise_if_error_event(
                'Failed to pull logs for environment instances.'
            )

    @mock.patch('ebcli.operations.commonops.SourceControl')
    def test_return_global_default_if_no_branch_default(self, mock):
        sc_mock = Mock()
        sc_mock.get_current_branch.return_value = 'none'
        mock.get_source_control.return_value = sc_mock

        result = commonops.get_config_setting_from_branch_or_default('default_region')
        assert sc_mock.get_current_branch.called, 'Should have been called'
        self.assertEqual(result, 'us-east-1')

        fileoperations.write_config_setting('global', 'default_region', 'brazil')
        fileoperations.write_config_setting('global', 'profile', 'monica')
        fileoperations.write_config_setting('global', 'moop', 'meep')
        fileoperations.write_config_setting('branch-defaults', 'my-branch', {'profile': 'chandler',
            'environment': 'my-env', 'boop': 'beep'})

        result = commonops.get_current_branch_environment()
        self.assertEqual(result, None)

        # get default profile name
        result = commonops.get_default_profile()
        self.assertEqual(result, 'monica')

        result = commonops.get_config_setting_from_branch_or_default('moop')
        self.assertEqual(result, 'meep')


    @mock.patch('ebcli.operations.commonops.SourceControl')
    def test_return_branch_default_if_set(self, mock):
        sc_mock = Mock()
        sc_mock.get_current_branch.return_value = 'my-branch'
        mock.get_source_control.return_value = sc_mock

        fileoperations.write_config_setting('global', 'default_region', 'brazil')
        fileoperations.write_config_setting('global', 'profile', 'monica')
        fileoperations.write_config_setting('global', 'moop', 'meep')
        fileoperations.write_config_setting('branch-defaults', 'my-branch', {'profile': 'chandler',
            'environment': 'my-env', 'boop': 'beep'})

        # get default region name
        result = commonops.get_default_region()
        self.assertEqual(result, 'brazil')

        # get branch-specific default environment name
        result = commonops.get_current_branch_environment()
        self.assertEqual(result, 'my-env')

        # get branch-specific default profile name
        result = commonops.get_default_profile()
        self.assertEqual(result, 'chandler')

        # get branch-specific generic default
        result = commonops.get_config_setting_from_branch_or_default('boop')
        self.assertEqual(result, 'beep')

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk')
    def test_create_application_version_wrapper(self, mock_beanstalk):
        # Make the actual call
        actual_return = commonops._create_application_version(self.app_name, self.app_version_name,
                                              self.description, self.s3_bucket, self.s3_key)

        # Assert return and methods were called for the correct workflow
        self.assertEqual(self.app_version_name, actual_return, "Expected {0} but got: {1}"
                         .format(self.app_version_name, actual_return))
        mock_beanstalk.create_application_version.assert_called_with(self.app_name, self.app_version_name,
                                                                     self.description, self.s3_bucket, self.s3_key,
                                                                     False, None, None, None)

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk')
    def test_create_application_version_wrapper_app_version_already_exists(self, mock_beanstalk):
        # Mock out methods
        mock_beanstalk.create_application_version.side_effect = InvalidParameterValueError('Application Version {0} already exists.'
                                                                .format(self.app_version_name))

        # Make the actual call
        actual_return = commonops._create_application_version(self.app_name, self.app_version_name,
                                              self.description, self.s3_bucket, self.s3_key)

        # Assert return and methods were called for the correct workflow
        self.assertEqual(self.app_version_name, actual_return, "Expected {0} but got: {1}"
                         .format(self.app_version_name, actual_return))
        mock_beanstalk.create_application_version.assert_called_with(self.app_name, self.app_version_name,
                                                                     self.description, self.s3_bucket, self.s3_key,
                                                                     False, None, None, None)

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk')
    @mock.patch('ebcli.operations.commonops.fileoperations')
    def test_create_application_version_wrapper_app_does_not_exist(self, mock_fileoperations, mock_beanstalk):
        # Mock out methods
        mock_beanstalk.create_application_version.side_effect = [InvalidParameterValueError(responses['app.notexists'].replace(
                                                                '{app-name}', '\'' + self.app_name + '\'')), None]

        with mock.patch('ebcli.objects.sourcecontrol.Git') as MockGitClass:
            mock_git_sourcecontrol = MockGitClass.return_value
            mock_git_sourcecontrol.get_current_branch.return_value = self.branch
            with mock.patch('ebcli.operations.commonops.SourceControl') as MockSourceControlClass:
                mock_sourcecontrol = MockSourceControlClass.return_value
                mock_sourcecontrol.get_source_control.return_value = mock_git_sourcecontrol

            # Make the actual call
            actual_return = commonops._create_application_version(self.app_name, self.app_version_name,
                                          self.description, self.s3_bucket, self.s3_key)

        # Assert return and methods were called for the correct workflow
        self.assertEqual(self.app_version_name, actual_return, "Expected {0} but got: {1}"
                         .format(self.app_version_name, actual_return))
        mock_beanstalk.create_application_version.assert_called_with(self.app_name, self.app_version_name,
                                                                     self.description, self.s3_bucket, self.s3_key,
                                                                     False, None, None, None)
        mock_beanstalk.create_application.assert_called_with(self.app_name, strings['app.description'])

        write_config_calls = [mock.call('branch-defaults', self.branch, {'environment': None}),
                             mock.call('branch-defaults', self.branch, {'group_suffix': None})]
        mock_fileoperations.write_config_setting.assert_has_calls(write_config_calls)

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk')
    def test_create_application_version_wrapper_app_version_throws_unknown_exception(self, mock_beanstalk):
        # Mock out methods
        mock_beanstalk.create_application_version.side_effect = Exception("FooException")

        # Make the actual call
        self.assertRaises(Exception, commonops._create_application_version, self.app_name, self.app_version_name,
                          self.description, self.s3_bucket, self.s3_key)

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk')
    def test_create_application_version_wrapper_with_build_config(self, mock_beanstalk):
        # Mock out methods
        with mock.patch('ebcli.lib.iam.get_roles') as mock_iam_get_roles:
            mock_iam_get_roles.return_value = [{'RoleName': self.service_role, 'Arn': self.service_role_arn},
                                               {'RoleName': self.service_role, 'Arn': self.service_role_arn}]

            # Make the actual call
            actual_return = commonops._create_application_version(self.app_name, self.app_version_name,
                                                  self.description, self.s3_bucket, self.s3_key, build_config=self.build_config)

        # Assert return and methods were called for the correct workflow
        self.assertEqual(self.app_version_name, actual_return, "Expected {0} but got: {1}"
                         .format(self.app_version_name, actual_return))
        mock_beanstalk.create_application_version.assert_called_with(self.app_name, self.app_version_name,
                                                                     self.description, self.s3_bucket, self.s3_key,
                                                                     False, None, None, self.build_config)

    @mock.patch('ebcli.operations.commonops.iam')
    @mock.patch('ebcli.operations.commonops.io')
    def test_create_default_instance_profile_successful(self, _, mock_iam):
        commonops.create_default_instance_profile()

        mock_iam.create_instance_profile.assert_called_once_with(iam_attributes.DEFAULT_ROLE_NAME)
        mock_iam.create_role_with_policy.assert_called_once_with(iam_attributes.DEFAULT_ROLE_NAME, iam_documents.EC2_ASSUME_ROLE_PERMISSION, iam_attributes.DEFAULT_ROLE_POLICIES)
        mock_iam.add_role_to_profile.assert_called_once_with(iam_attributes.DEFAULT_ROLE_NAME, iam_attributes.DEFAULT_ROLE_NAME)
        mock_iam.put_role_policy.assert_not_called()

    @mock.patch('ebcli.operations.commonops.iam')
    @mock.patch('ebcli.operations.commonops.io')
    def test_create_instance_profile_successful(self, _, mock_iam):
        commonops.create_instance_profile('pname', 'policies', 'rname')

        mock_iam.create_instance_profile.assert_called_once_with('pname')
        mock_iam.create_role_with_policy.assert_called_once_with('rname', iam_documents.EC2_ASSUME_ROLE_PERMISSION, 'policies')
        mock_iam.add_role_to_profile.assert_called_once_with('pname', 'rname')
        mock_iam.put_role_policy.assert_not_called()

    @mock.patch('ebcli.operations.commonops.iam')
    @mock.patch('ebcli.operations.commonops.io')
    def test_create_instance_profile_successful_with_inline_policy(self, _, mock_iam):
        commonops.create_instance_profile('pname', 'policies', role_name='rname', inline_policy_name='inline_name', inline_policy_doc='{inline_json}')

        mock_iam.create_instance_profile.assert_called_once_with('pname')
        mock_iam.create_role_with_policy.assert_called_once_with('rname', iam_documents.EC2_ASSUME_ROLE_PERMISSION, 'policies')
        mock_iam.put_role_policy.assert_called_once_with('rname', 'inline_name', '{inline_json}')
        mock_iam.add_role_to_profile.assert_called_once_with('pname', 'rname')

    @mock.patch('ebcli.operations.commonops.iam')
    @mock.patch('ebcli.operations.commonops.io')
    def test_create_instance_profile_successful_omitting_role_name(self, _, mock_iam):
        commonops.create_instance_profile('pname', ['policies'])

        mock_iam.create_instance_profile.assert_called_once_with('pname')
        mock_iam.create_role_with_policy.assert_called_once_with('pname', iam_documents.EC2_ASSUME_ROLE_PERMISSION, ['policies'])
        mock_iam.add_role_to_profile.assert_called_once_with('pname', 'pname')
        mock_iam.put_role_policy.assert_not_called()

    @mock.patch('ebcli.operations.commonops.iam')
    @mock.patch('ebcli.operations.commonops.io')
    def test_create_instance_profile_without_permission(self, mock_io, mock_iam):
        mock_iam.create_instance_profile.side_effect = NotAuthorizedError()
        commonops.create_instance_profile('pname', 'policies', 'rname')

        mock_iam.create_instance_profile.assert_called_once_with('pname')
        mock_iam.create_role_with_policy.assert_not_called()
        mock_iam.put_role_policy.assert_not_called()
        mock_iam.add_role_to_profile.assert_not_called()

        mock_io.log_warning.assert_called_once()

    def test_filter_events__match_all_by_default__return_all_events_passed_in(self):
        describe_events_response = {
            "Events": [{}, {}]
        }

        events = self.__convert_to_event_objects(describe_events_response)
        filtered_events = commonops.filter_events(events)

        self.assertEqual(events, filtered_events)

    def test_filter_events__match_by_environment_name(self):
        describe_events_response = {
            "Events": [
                {"EnvironmentName": "env_1"},
                {"EnvironmentName": "env_2"}
            ]
        }

        events = self.__convert_to_event_objects(describe_events_response)
        filtered_events = commonops.filter_events(events, env_name='env_1')

        self.assertEqual(1, len(filtered_events))
        self.assertEqual('env_1', filtered_events[0].environment_name)

    def test_filter_events__match_by_request_id(self):
        describe_events_response = {
            "Events": [
                {"RequestId": "request_id_1"},
                {"RequestId": "request_id_2"}
            ]
        }

        events = self.__convert_to_event_objects(describe_events_response)
        filtered_events = commonops.filter_events(events, request_id='request_id_1')

        self.assertEqual(1, len(filtered_events))
        self.assertEqual('request_id_1', filtered_events[0].request_id)

    def test_filter_events__match_by_version_label(self):
        describe_events_response = {
            "Events": [
                {"VersionLabel": "version_label_1"},
                {"VersionLabel": "version_label_2"}
            ]
        }

        events = self.__convert_to_event_objects(describe_events_response)
        filtered_events = commonops.filter_events(events, version_label='version_label_1')

        self.assertEqual(1, len(filtered_events))
        self.assertEqual('version_label_1', filtered_events[0].version_label)

    def test_filter_events__match_by_environment_name_and_request_id(self):
        describe_events_response = {
            "Events": [
                {
                    "EnvironmentName": "env_1",
                    "RequestId": "request_id_1",
                },
                {
                    "EnvironmentName": "env_1",
                    "RequestId": "request_id_1_1",
                },
                {
                    "EnvironmentName": "env_2",
                    "RequestId": "request_id_2",
                }
            ]
        }

        events = self.__convert_to_event_objects(describe_events_response)
        filtered_events = commonops.filter_events(events, env_name='env_1', request_id='request_id_1')

        self.assertEqual(1, len(filtered_events))
        self.assertEqual('request_id_1', filtered_events[0].request_id)
        self.assertEqual('env_1', filtered_events[0].environment_name)

    def test_filter_events__match_by_environment_name_and_version_label(self):
        describe_events_response = {
            "Events": [
                {
                    "EnvironmentName": "env_1",
                    "VersionLabel": "version_label_1",
                },
                {
                    "EnvironmentName": "env_1",
                    "VersionLabel": "version_label_1_1",
                },
                {
                    "EnvironmentName": "env_2",
                    "VersionLabel": "version_label_2",
                }
            ]
        }

        events = self.__convert_to_event_objects(describe_events_response)
        filtered_events = commonops.filter_events(events, env_name='env_1', version_label='version_label_1')

        self.assertEqual(1, len(filtered_events))
        self.assertEqual('version_label_1', filtered_events[0].version_label)
        self.assertEqual('env_1', filtered_events[0].environment_name)

    def test_filter_events__match_by_request_id_and_version_label(self):
        describe_events_response = {
            "Events": [
                {
                    "RequestId": "request_id_1",
                    "VersionLabel": "version_label_1",
                },
                {
                    "RequestId": "request_id_1_1",
                    "VersionLabel": "version_label_1_1",
                },
                {
                    "RequestId": "request_id_2",
                    "VersionLabel": "version_label_2",
                }
            ]
        }

        events = self.__convert_to_event_objects(describe_events_response)
        filtered_events = commonops.filter_events(events, version_label='version_label_1', request_id='request_id_1')

        self.assertEqual(1, len(filtered_events))
        self.assertEqual('version_label_1', filtered_events[0].version_label)
        self.assertEqual('request_id_1', filtered_events[0].request_id)

    def __convert_to_event_objects(self, describe_events_response):
        events = []
        for event in describe_events_response['Events']:

            events.append(
                Event(
                    app_name=event.get('ApplicationName'),
                    environment_name=event.get('EnvironmentName'),
                    event_date=event.get('EventDate'),
                    message=event.get('Message'),
                    platform=event.get('PlatformArn'),
                    request_id=event.get('RequestId'),
                    severity=event.get('Severity'),
                    version_label=event.get('VersionLabel')
                )
            )

        return events
