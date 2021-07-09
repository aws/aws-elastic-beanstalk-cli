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
from datetime import datetime, timedelta
import os
import sys
import shutil

from dateutil import tz
import mock
from mock import Mock
import unittest

from ebcli.core import fileoperations
from ebcli.objects.exceptions import NotAuthorizedError
from ebcli.objects.event import Event
from ebcli.objects.environment import Environment
from ebcli.objects.region import Region
from ebcli.operations import commonops
from ebcli.lib.aws import InvalidParameterValueError
from ebcli.objects.buildconfiguration import BuildConfiguration
from ebcli.resources.strings import strings, responses
from ebcli.resources.statics import iam_documents, iam_attributes

from .. import mock_responses
from ..test_helper import EnvVarSubstitutor

class CredentialsEnvVarSubstituter(object):
    def __init__(self, access_id, secret_key):
        self.access_id = access_id
        self.secret_key = secret_key

    def __call__(self, func):
        with EnvVarSubstitutor('AWS_ACCESS_KEY_ID', self.access_id):
            with EnvVarSubstitutor('AWS_SECRET_ACCESS_KEY', self.secret_key):
                func()

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
        self.root = os.getcwd()
        if not os.path.exists('testDir'):
            os.makedirs('testDir')
        os.chdir('testDir')

        if not os.path.exists(fileoperations.beanstalk_directory):
            os.makedirs(fileoperations.beanstalk_directory)

        if not os.path.exists('home'):
            os.makedirs('home')

        fileoperations.aws_config_folder = 'home' + os.path.sep
        fileoperations.aws_config_location \
            = fileoperations.aws_config_folder + 'config'

        fileoperations.create_config_file('ebcli-test', 'us-east-1',
                                          'my-solution-stack')

    def tearDown(self):
        os.chdir(self.root)
        shutil.rmtree('testDir')

    def test_is_success_event(self):
        self.assertTrue(commonops._is_success_event('Environment health has been set to GREEN'))
        self.assertTrue(commonops._is_success_event('Successfully launched environment: my-env'))
        self.assertTrue(commonops._is_success_event('Pulled logs for environment instances.'))
        self.assertTrue(commonops._is_success_event('terminateEnvironment completed successfully.'))
        self.assertFalse(commonops._is_success_event('Instance deployment completed successfully.'))

    def test_is_success_event__log_events(self):
        self.assertTrue(commonops._is_success_event('Instance deployment completed successfully.', log_events=True))

    def test_raise_if_error_event(self):
        with self.assertRaises(commonops.ServiceError):
            commonops._raise_if_error_event(
                'Environment health has been set to RED'
            )

        with self.assertRaises(commonops.ServiceError):
            commonops._raise_if_error_event(
                'Launched environment: my-environment. However, there were '
                'issues during launch. See event log for details'
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

        result = commonops.get_default_region()
        self.assertEqual(result, 'brazil')

        result = commonops.get_current_branch_environment()
        self.assertEqual(result, 'my-env')

        result = commonops.get_default_profile()
        self.assertEqual(result, 'chandler')

        result = commonops.get_config_setting_from_branch_or_default('boop')
        self.assertEqual(result, 'beep')

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk')
    def test_create_application_version_wrapper(self, mock_beanstalk):
        actual_return = commonops._create_application_version(self.app_name, self.app_version_name,
                                              self.description, self.s3_bucket, self.s3_key)

        self.assertEqual(self.app_version_name, actual_return, "Expected {0} but got: {1}"
                         .format(self.app_version_name, actual_return))
        mock_beanstalk.create_application_version.assert_called_with(self.app_name, self.app_version_name,
                                                                     self.description, self.s3_bucket, self.s3_key,
                                                                     False, None, None, None)

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk')
    def test_create_application_version_wrapper_app_version_already_exists(self, mock_beanstalk):
        mock_beanstalk.create_application_version.side_effect = InvalidParameterValueError('Application Version {0} already exists.'
                                                                .format(self.app_version_name))

        actual_return = commonops._create_application_version(self.app_name, self.app_version_name,
                                              self.description, self.s3_bucket, self.s3_key)

        self.assertEqual(self.app_version_name, actual_return, "Expected {0} but got: {1}"
                         .format(self.app_version_name, actual_return))
        mock_beanstalk.create_application_version.assert_called_with(self.app_name, self.app_version_name,
                                                                     self.description, self.s3_bucket, self.s3_key,
                                                                     False, None, None, None)

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk')
    @mock.patch('ebcli.operations.commonops.fileoperations')
    def test_create_application_version_wrapper_app_does_not_exist(self, mock_fileoperations, mock_beanstalk):
        mock_beanstalk.create_application_version.side_effect = [InvalidParameterValueError(responses['app.notexists'].replace(
                                                                '{app-name}', '\'' + self.app_name + '\'')), None]

        with mock.patch('ebcli.objects.sourcecontrol.Git') as MockGitClass:
            mock_git_sourcecontrol = MockGitClass.return_value
            mock_git_sourcecontrol.get_current_branch.return_value = self.branch
            with mock.patch('ebcli.operations.commonops.SourceControl') as MockSourceControlClass:
                mock_sourcecontrol = MockSourceControlClass.return_value
                mock_sourcecontrol.get_source_control.return_value = mock_git_sourcecontrol

            actual_return = commonops._create_application_version(self.app_name, self.app_version_name,
                                          self.description, self.s3_bucket, self.s3_key)

        self.assertEqual(self.app_version_name, actual_return, "Expected {0} but got: {1}"
                         .format(self.app_version_name, actual_return))
        mock_beanstalk.create_application_version.assert_called_with(self.app_name, self.app_version_name,
                                                                     self.description, self.s3_bucket, self.s3_key,
                                                                     False, None, None, None)
        mock_beanstalk.create_application.assert_called_with(self.app_name, strings['app.description'], [])

        write_config_calls = [mock.call('branch-defaults', self.branch, {'environment': None}),
                             mock.call('branch-defaults', self.branch, {'group_suffix': None})]
        mock_fileoperations.write_config_setting.assert_has_calls(write_config_calls)

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk')
    def test_create_application_version_wrapper_app_version_throws_unknown_exception(self, mock_beanstalk):
        mock_beanstalk.create_application_version.side_effect = Exception("FooException")

        self.assertRaises(Exception, commonops._create_application_version, self.app_name, self.app_version_name,
                          self.description, self.s3_bucket, self.s3_key)

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk')
    def test_create_application_version_wrapper_with_build_config(self, mock_beanstalk):
        with mock.patch('ebcli.lib.iam.get_roles') as mock_iam_get_roles:
            mock_iam_get_roles.return_value = [{'RoleName': self.service_role, 'Arn': self.service_role_arn},
                                               {'RoleName': self.service_role, 'Arn': self.service_role_arn}]

            actual_return = commonops._create_application_version(self.app_name, self.app_version_name,
                                                  self.description, self.s3_bucket, self.s3_key, build_config=self.build_config)

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
    @mock.patch('ebcli.lib.aws.get_region_name')
    def test_create_instance_profile_successful_in_China(self, mock_get_region_name, _, mock_iam):
        mock_get_region_name.return_value = 'cn-north-1'
        commonops.create_instance_profile('pname', 'policies', 'rname')

        mock_iam.create_instance_profile.assert_called_once_with('pname')
        mock_iam.create_role_with_policy.assert_called_once_with('rname', iam_documents.EC2_ASSUME_ROLE_PERMISSION_CN,
                                                                 'policies')
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

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_environment_resources')
    def test_get_instance_ids(
            self,
            get_environment_resources_mock
    ):
        get_environment_resources_mock.return_value = mock_responses.DESCRIBE_ENVIRONMENT_RESOURCES_RESPONSE

        self.assertEqual(
            ['i-23452345346456566', 'i-21312312312312312'],
            commonops.get_instance_ids('some-environment-name')
        )

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_new_events')
    @mock.patch('ebcli.operations.commonops._sleep')
    def test_wait_for_success_events(
            self,
            _sleep_mock,
            get_new_events_mock
    ):
        create_environment_events = Event.json_to_event_objects(
            mock_responses.CREATE_ENVIRONMENT_DESCRIBE_EVENTS['Events']
        )
        get_new_events_mock.side_effect = [[event] for event in reversed(create_environment_events)]
        commonops.wait_for_success_events(create_environment_events[0].request_id)

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_new_events')
    @mock.patch('ebcli.operations.commonops._sleep')
    @mock.patch('ebcli.operations.commonops._timeout_reached')
    def test_wait_for_success_events__timeout_reached(
            self,
            _timeout_reached_mock,
            _sleep_mock,
            get_new_events_mock
    ):
        create_environment_events = Event.json_to_event_objects(
            mock_responses.CREATE_ENVIRONMENT_DESCRIBE_EVENTS['Events']
        )
        get_new_events_mock.side_effect = [[event] for event in reversed(create_environment_events)]

        with self.assertRaises(commonops.TimeoutError) as context_manager:
            commonops.wait_for_success_events(create_environment_events[0].request_id)

        self.assertEqual(
            "The EB CLI timed out after 10 minute(s). The operation might still be running. To keep viewing events, run 'eb events -f'. To set timeout duration, use '--timeout MINUTES'.",
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_new_events')
    @mock.patch('ebcli.operations.commonops._sleep')
    @mock.patch('ebcli.operations.commonops._timeout_reached')
    def test_wait_for_success_events__timeout_reached__timeout_error_message_specified(
            self,
            _timeout_reached_mock,
            _sleep_mock,
            get_new_events_mock
    ):
        create_environment_events = Event.json_to_event_objects(
            mock_responses.CREATE_ENVIRONMENT_DESCRIBE_EVENTS['Events']
        )
        get_new_events_mock.side_effect = [[event] for event in reversed(create_environment_events)]

        with self.assertRaises(commonops.TimeoutError) as context_manager:
            commonops.wait_for_success_events(
                create_environment_events[0].request_id,
                timeout_error_message='timeout message'
            )

        self.assertEqual(
            "timeout message",
            str(context_manager.exception)
        )

    def test_wait_for_success_events__timeout_is_0__returns_immediately(self):
        commonops.wait_for_success_events('some-request-id', timeout_in_minutes=0)

    def test_wait_for_compose_events__timeout_is_0__returns_immediately(self):
        commonops.wait_for_compose_events(
            'some-request-id',
            'my-application',
            ['environment-1', 'environment-2'],
            timeout_in_minutes=0
        )

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_new_events')
    @mock.patch('ebcli.operations.commonops._sleep')
    @mock.patch('ebcli.operations.commonops._timeout_reached')
    @mock.patch('ebcli.operations.commonops.io.log_error')
    def test_wait_for_compose_events(
            self,
            log_error_mock,
            _timeout_reached_mock,
            _sleep_mock,
            get_new_events_mock
    ):
        compose_environments_events = Event.json_to_event_objects(
            mock_responses.COMPOSE_ENVIRONMENTS_DESCRIBE_EVENTS['Events']
        )
        _timeout_reached_mock.return_value = False
        get_new_events_mock.side_effect = [[event] for event in reversed(compose_environments_events)]

        commonops.wait_for_compose_events(
            'c51aac54-01c7-4ae7-8692-d31dd990eba3',
            'my-application',
            ['environment-1', 'environment-2']
        )

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_new_events')
    @mock.patch('ebcli.operations.commonops._sleep')
    @mock.patch('ebcli.operations.commonops._timeout_reached')
    @mock.patch('ebcli.operations.commonops.io.log_error')
    def test_wait_for_compose_events__timeout_is_reached(
            self,
            log_error_mock,
            _timeout_reached_mock,
            _sleep_mock,
            get_new_events_mock
    ):
        compose_environments_events = Event.json_to_event_objects(
            mock_responses.COMPOSE_ENVIRONMENTS_DESCRIBE_EVENTS['Events']
        )
        _timeout_reached_mock.return_value = True
        get_new_events_mock.side_effect = [[event] for event in reversed(compose_environments_events)]

        commonops.wait_for_compose_events(
            'c51aac54-01c7-4ae7-8692-d31dd990eba3',
            'my-application',
            ['environment-1', 'environment-2'],
            timeout_in_minutes=5
        )

        log_error_mock.assert_called_once_with(
            "The EB CLI timed out after {timeout_in_minutes} minute(s). The operation might still be running. To keep viewing events, run 'eb events -f'. To set timeout duration, use '--timeout MINUTES'."
        )

    def test_sleep(self):
        commonops._sleep(0.001)

    def test_timeout_reached(self):
        self.assertTrue(
            commonops._timeout_reached(
                datetime.utcnow() - timedelta(minutes=5),
                timedelta(seconds=300)
            )
        )

    def test_timeout_reached__false(self):
        self.assertFalse(
            commonops._timeout_reached(
                datetime.utcnow() - timedelta(minutes=5),
                timedelta(seconds=301)
            )
        )

    def test_get_event_string(self):
        event = Event.json_to_event_objects(
            [
                {
                    'EventDate': datetime(2018, 7, 19, 21, 50, 21, 623000, tzinfo=tz.tzutc()),
                    'Message': 'Successfully launched environment: eb-locust-example-windows-server-dev',
                    'ApplicationName': 'eb-locust-example-windows-server',
                    'EnvironmentName': 'eb-locust-example-windows-server-dev',
                    'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
                    'Severity': 'INFO'
                }
            ]
        )[0]

        self.assertEqual(
            'INFO: Successfully launched environment: eb-locust-example-windows-server-dev',
            commonops.get_event_string(event)
        )

        self.assertEqual(
            '2018-07-19 21:50:21    INFO    Successfully launched environment: eb-locust-example-windows-server-dev',
            commonops.get_event_string(event, long_format=True)
        )

    def test_get_compose_event_string(self):
        event = Event.json_to_event_objects(
            [
                {
                    'EventDate': datetime(2018, 7, 19, 21, 50, 21, 623000, tzinfo=tz.tzutc()),
                    'Message': 'Successfully launched environment: eb-locust-example-windows-server-dev',
                    'ApplicationName': 'eb-locust-example-windows-server',
                    'EnvironmentName': 'eb-locust-example-windows-server-dev',
                    'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
                    'Severity': 'INFO'
                }
            ]
        )[0]

        self.assertEqual(
            'eb-locust-example-windows-server - INFO: Successfully launched environment: eb-locust-example-windows-server-dev',
            commonops.get_compose_event_string(event)
        )

        self.assertEqual(
            'eb-locust-example-windows-server - 2018-07-19 21:50:21    INFO    Successfully launched environment: eb-locust-example-windows-server-dev',
            commonops.get_compose_event_string(event, long_format=True)
        )

    def test_get_env_event_string(self):
        event = Event.json_to_event_objects(
            [
                {
                    'EventDate': datetime(2018, 7, 19, 21, 50, 21, 623000, tzinfo=tz.tzutc()),
                    'Message': 'Successfully launched environment: eb-locust-example-windows-server-dev',
                    'ApplicationName': 'eb-locust-example-windows-server',
                    'EnvironmentName': 'eb-locust-example-windows-server-dev',
                    'RequestId': 'a28c2685-b6a0-4785-82bf-45de6451bd01',
                    'Severity': 'INFO'
                }
            ]
        )[0]

        self.assertEqual(
            '    eb-locust-example-windows-server-dev - INFO: Successfully launched environment: eb-locust-example-windows-server-dev',
            commonops.get_env_event_string(event)
        )

        self.assertEqual(
            '    eb-locust-example-windows-server-dev - 2018-07-19 21:50:21    INFO    Successfully launched environment: eb-locust-example-windows-server-dev',
            commonops.get_env_event_string(event, long_format=True)
        )

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.application_version_exists')
    def test_get_app_version_s3_location__app_version_exists(
            self,
            application_version_exists_mock
    ):
        application_version_exists_mock.return_value = mock_responses.DESCRIBE_APPLICATION_VERSIONS_RESPONSE['ApplicationVersions'][0]

        self.assertEqual(
            (
                'elasticbeanstalk-us-west-2-123123123123',
                'my-app/9112-stage-150723_224258.war'
            ),
            commonops.get_app_version_s3_location('my-application', 'version-label')
        )

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.application_version_exists')
    def test_get_app_version_s3_location__app_version_does_not_exist(
            self,
            application_version_exists_mock
    ):
        application_version_exists_mock.return_value = []

        self.assertEqual(
            (None, None),
            commonops.get_app_version_s3_location('my-application', 'version-label')
        )

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.create_application')
    @mock.patch('ebcli.operations.commonops.pull_down_app_info')
    def test_create_app__app_already_exists__app_is_pulled_down(
            self,
            pull_down_app_info_mock,
            create_application_mock
    ):
        create_application_mock.side_effect = commonops.AlreadyExistsError
        pull_down_app_info_mock.return_value = ('platform-arn', 'key-name')


        self.assertEqual(
            ('platform-arn', 'key-name'),
            commonops.create_app('my-application', default_env='environment-1')
        )

        pull_down_app_info_mock.assert_called_once_with(
            'my-application',
            default_env='environment-1'
        )

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.create_application')
    @mock.patch('ebcli.operations.commonops.set_environment_for_current_branch')
    @mock.patch('ebcli.operations.commonops.set_group_suffix_for_current_branch')
    @mock.patch('ebcli.operations.commonops.io.echo')
    @mock.patch('ebcli.operations.commonops.io.log_info')
    def test_create_app(
            self,
            log_info_mock,
            echo_mock,
            set_group_suffix_for_current_branch_mock,
            set_environment_for_current_branch_mock,
            create_application_mock
    ):
        self.assertEqual(
            (None, None),
            commonops.create_app('my-application', default_env='environment-1')
        )

        create_application_mock.assert_called_once_with(
            'my-application',
            'Application created from the EB CLI using "eb init"',
            []
        )
        set_group_suffix_for_current_branch_mock.assert_called_once_with(None)
        set_environment_for_current_branch_mock.assert_called_once_with(None)
        echo_mock.assert_called_once_with('Application', 'my-application', 'has been created.')

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.create_application')
    @mock.patch('ebcli.operations.commonops.set_environment_for_current_branch')
    @mock.patch('ebcli.operations.commonops.set_group_suffix_for_current_branch')
    @mock.patch('ebcli.operations.commonops.io.echo')
    @mock.patch('ebcli.operations.commonops.io.log_info')
    def test_create_app_with_tags(
            self,
            log_info_mock,
            echo_mock,
            set_group_suffix_for_current_branch_mock,
            set_environment_for_current_branch_mock,
            create_application_mock
    ):
        self.assertEqual(
            (None, None),
            commonops.create_app(
                'my-application',
                default_env='environment-1',
                tags=[
                    {'Key': 'testkey1', 'Value': 'testvalue1'},
                    {'Key': 'testkey2', 'Value': 'testvalue2'}
                ]
            )
        )

        create_application_mock.assert_called_once_with(
            'my-application',
            'Application created from the EB CLI using "eb init"',
            [
                {'Key': 'testkey1', 'Value': 'testvalue1'},
                {'Key': 'testkey2', 'Value': 'testvalue2'}
            ]
        )
        set_group_suffix_for_current_branch_mock.assert_called_once_with(None)
        set_environment_for_current_branch_mock.assert_called_once_with(None)
        echo_mock.assert_called_once_with('Application', 'my-application', 'has been created.')

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_app_environments')
    @mock.patch('ebcli.operations.commonops.set_environment_for_current_branch')
    def test_pull_down_app_info__no_environments_for_application(
            self,
            set_environment_for_current_branch_mock,
            get_app_environments_mock
    ):
        get_app_environments_mock.return_value = []

        commonops.pull_down_app_info('my-application')

        get_app_environments_mock.assert_called_once_with('my-application')
        set_environment_for_current_branch_mock.assert_called_once_with(None)

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_app_environments')
    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_specific_configuration_for_env')
    @mock.patch('ebcli.operations.commonops.set_environment_for_current_branch')
    @mock.patch('ebcli.operations.commonops.io.log_info')
    def test_pull_down_app_info__exactly_one_environment_for_application(
            self,
            log_info_mock,
            set_environment_for_current_branch_mock,
            get_specific_configuration_for_env_mock,
            get_app_environments_mock
    ):
        get_app_environments_mock.return_value = [
            Environment.json_to_environment_objects_array(
                mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments']
            )[0]
        ]
        get_specific_configuration_for_env_mock.return_value = 'keyname'

        self.assertEqual(
            (
                'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon '
                'Linux/2.6.5',
                'keyname'
            ),
            commonops.pull_down_app_info('my-application')
        )

        get_app_environments_mock.assert_called_once_with('my-application')
        set_environment_for_current_branch_mock.assert_called_once_with('environment-1')
        log_info_mock.assert_has_calls(
            [
                mock.call('Setting only environment "environment-1" as default'),
                mock.call('Pulling down defaults from environment environment-1')
            ]
        )
        get_specific_configuration_for_env_mock.assert_called_once_with(
            'my-application',
            'environment-1',
            'aws:autoscaling:launchconfiguration',
            'EC2KeyName'
        )

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_app_environments')
    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_specific_configuration_for_env')
    @mock.patch('ebcli.operations.commonops.set_environment_for_current_branch')
    @mock.patch('ebcli.operations.commonops.io.log_info')
    def test_pull_down_app_info__keyname_not_found(
            self,
            log_info_mock,
            set_environment_for_current_branch_mock,
            get_specific_configuration_for_env_mock,
            get_app_environments_mock
    ):
        get_app_environments_mock.return_value = [
            Environment.json_to_environment_objects_array(
                mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments']
            )[0]
        ]
        get_specific_configuration_for_env_mock.return_value = None

        self.assertEqual(
            (
                'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5',
                -1
            ),
            commonops.pull_down_app_info('my-application')
        )

        get_app_environments_mock.assert_called_once_with('my-application')
        set_environment_for_current_branch_mock.assert_called_once_with('environment-1')
        log_info_mock.assert_has_calls(
            [
                mock.call('Setting only environment "environment-1" as default'),
                mock.call('Pulling down defaults from environment environment-1')
            ]
        )
        get_specific_configuration_for_env_mock.assert_called_once_with(
            'my-application',
            'environment-1',
            'aws:autoscaling:launchconfiguration',
            'EC2KeyName'
        )

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_app_environments')
    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_specific_configuration_for_env')
    @mock.patch('ebcli.operations.commonops.set_environment_for_current_branch')
    @mock.patch('ebcli.operations.commonops.io.log_info')
    def test_pull_down_app_info__multiple_environments_for_application__non_interactive_mode__first_environment_in_describe_environments_response_selected(
            self,
            log_info_mock,
            set_environment_for_current_branch_mock,
            get_specific_configuration_for_env_mock,
            get_app_environments_mock
    ):
        get_app_environments_mock.return_value = Environment.json_to_environment_objects_array(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments']
        )
        get_specific_configuration_for_env_mock.return_value = 'keyname'

        self.assertEqual(
            (
                'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon '
                'Linux/2.6.5',
                'keyname'
            ),
            commonops.pull_down_app_info('my-application', default_env='/ni')
        )

        get_app_environments_mock.assert_called_once_with('my-application')
        set_environment_for_current_branch_mock.assert_called_once_with('environment-1')
        log_info_mock.assert_called_once_with(
            'Pulling down defaults from environment environment-1'
        )
        get_specific_configuration_for_env_mock.assert_called_once_with(
            'my-application',
            'environment-1',
            'aws:autoscaling:launchconfiguration',
            'EC2KeyName'
        )

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_app_environments')
    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_specific_configuration_for_env')
    @mock.patch('ebcli.operations.commonops.set_environment_for_current_branch')
    @mock.patch('ebcli.operations.commonops.io.log_info')
    def test_pull_down_app_info__multiple_environments_for_application__non_interactive_mode__default_environment_is_valid(
            self,
            log_info_mock,
            set_environment_for_current_branch_mock,
            get_specific_configuration_for_env_mock,
            get_app_environments_mock
    ):
        get_app_environments_mock.return_value = Environment.json_to_environment_objects_array(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments']
        )
        get_specific_configuration_for_env_mock.return_value = 'keyname'

        self.assertEqual(
            (
                'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 5.3 running on 64bit Amazon Linux/0.1.0',
                'keyname'
            ),
            commonops.pull_down_app_info('my-application', default_env='environment-2')
        )

        get_app_environments_mock.assert_called_once_with('my-application')
        set_environment_for_current_branch_mock.assert_called_once_with('environment-2')
        log_info_mock.assert_called_once_with(
            'Pulling down defaults from environment environment-2'
        )
        get_specific_configuration_for_env_mock.assert_called_once_with(
            'my-application',
            'environment-2',
            'aws:autoscaling:launchconfiguration',
            'EC2KeyName'
        )

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_app_environments')
    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_specific_configuration_for_env')
    @mock.patch('ebcli.operations.commonops.set_environment_for_current_branch')
    @mock.patch('ebcli.operations.commonops.io.log_info')
    @mock.patch('ebcli.operations.commonops.utils.prompt_for_item_in_list')
    def test_pull_down_app_info__multiple_environments_for_application__interactive_mode(
            self,
            prompt_for_item_in_list_mock,
            log_info_mock,
            set_environment_for_current_branch_mock,
            get_specific_configuration_for_env_mock,
            get_app_environments_mock
    ):
        get_app_environments_mock.return_value = Environment.json_to_environment_objects_array(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments']
        )
        get_specific_configuration_for_env_mock.return_value = 'keyname'
        prompt_for_item_in_list_mock.return_value = get_app_environments_mock.return_value[1]

        self.assertEqual(
            (
                'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 5.3 running on 64bit Amazon Linux/0.1.0',
                'keyname'
            ),
            commonops.pull_down_app_info('my-application')
        )

        get_app_environments_mock.assert_called_once_with('my-application')
        set_environment_for_current_branch_mock.assert_called_once_with('environment-2')
        log_info_mock.assert_called_once_with(
            'Pulling down defaults from environment environment-2'
        )
        prompt_for_item_in_list_mock.assert_called_once_with(get_app_environments_mock.return_value)
        get_specific_configuration_for_env_mock.assert_called_once_with(
            'my-application',
            'environment-2',
            'aws:autoscaling:launchconfiguration',
            'EC2KeyName'
        )

    @mock.patch('ebcli.operations.commonops._create_application_version')
    def test_create_dummy_app_version(
            self,
            _create_application_version_mock
    ):
        commonops.create_dummy_app_version('my-application')

        _create_application_version_mock.assert_called_once_with(
            'my-application',
            'Sample Application',
            None,
            None,
            None,
            warning=False
        )

    @mock.patch('ebcli.operations.commonops.fileoperations.ProjectRoot.traverse')
    @mock.patch('ebcli.operations.commonops.heuristics.directory_is_empty')
    @mock.patch('ebcli.operations.commonops.io.echo')
    def test_create_app_version__directory_is_empty(
            self,
            echo_mock,
            directory_is_empty_mock,
            traverse_mock
    ):
        directory_is_empty_mock.return_value = True

        self.assertIsNone(commonops.create_app_version('my-application'))

        echo_mock.assert_called_once_with(
            'NOTE: The current directory does not contain any source code. '
            'Elastic Beanstalk is launching the sample application instead.'
        )

    @mock.patch('ebcli.operations.commonops.fileoperations.ProjectRoot.traverse')
    @mock.patch('ebcli.operations.commonops.heuristics.directory_is_empty')
    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.commonops.fileoperations.get_config_setting')
    @mock.patch('ebcli.operations.commonops.get_app_version_s3_location')
    @mock.patch('ebcli.operations.commonops.s3.get_object_info')
    @mock.patch('ebcli.operations.commonops.fileoperations.delete_app_versions')
    @mock.patch('ebcli.operations.commonops._create_application_version')
    def test_create_app_version__app_version_already_exists_in_s3(
            self,
            _create_application_version_mock,
            delete_app_versions_mock,
            get_object_info_mock,
            get_app_version_s3_location_mock,
            get_config_setting_mock,
            get_source_control_mock,
            directory_is_empty_mock,
            traverse_mock
    ):
        directory_is_empty_mock.return_value = False
        source_control_mock = mock.MagicMock()
        source_control_mock.get_version_label.return_value = 'version-label'
        source_control_mock.get_message.return_value = 'label-message'
        get_source_control_mock.return_value = source_control_mock
        get_config_setting_mock.return_value = None  # No artifacts
        get_app_version_s3_location_mock.return_value = ('s3-bucket', 's3-key')
        application_version_mock = mock.MagicMock()
        _create_application_version_mock.return_value = application_version_mock

        self.assertEqual(
            application_version_mock,
            commonops.create_app_version('my-application')
        )

        get_config_setting_mock.assert_called_once_with('deploy', 'artifact')
        get_app_version_s3_location_mock.assert_called_once_with('my-application', 'version-label')
        get_object_info_mock.assert_called_once_with('s3-bucket', 's3-key')
        _create_application_version_mock.assert_called_once_with(
            'my-application',
            'version-label',
            'label-message',
            's3-bucket',
            's3-key',
            False,
            build_config=None
        )

    @mock.patch('ebcli.operations.commonops.fileoperations.ProjectRoot.traverse')
    @mock.patch('ebcli.operations.commonops.heuristics.directory_is_empty')
    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.commonops.fileoperations.get_config_setting')
    @mock.patch('ebcli.operations.commonops.get_app_version_s3_location')
    @mock.patch('ebcli.operations.commonops.s3.get_object_info')
    @mock.patch('ebcli.operations.commonops.fileoperations.delete_app_versions')
    @mock.patch('ebcli.operations.commonops._create_application_version')
    @mock.patch('ebcli.operations.commonops._zip_up_project')
    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_storage_location')
    @mock.patch('ebcli.operations.commonops.s3.upload_application_version')
    def test_create_app_version__app_version_does_not_exist(
            self,
            upload_application_version_mock,
            get_storage_location_mock,
            _zip_up_project_mock,
            _create_application_version_mock,
            delete_app_versions_mock,
            get_object_info_mock,
            get_app_version_s3_location_mock,
            get_config_setting_mock,
            get_source_control_mock,
            directory_is_empty_mock,
            traverse_mock
    ):
        directory_is_empty_mock.return_value = False
        source_control_mock = mock.MagicMock()
        source_control_mock.get_version_label.return_value = 'version-label'
        source_control_mock.get_message.return_value = 'label-message'
        get_source_control_mock.return_value = source_control_mock
        get_config_setting_mock.return_value = None  # No artifacts
        get_app_version_s3_location_mock.return_value = (None, None)
        application_version_mock = mock.MagicMock()
        _create_application_version_mock.return_value = application_version_mock
        _zip_up_project_mock.return_value = ('version-label', 'source-control')
        get_storage_location_mock.return_value = 's3-bucket'
        get_object_info_mock.side_effect = commonops.NotFoundError

        self.assertEqual(
            application_version_mock,
            commonops.create_app_version('my-application')
        )

        get_config_setting_mock.assert_called_once_with('deploy', 'artifact')
        upload_application_version_mock.assert_called_once_with(
            's3-bucket',
            'my-application/version-label',
            'source-control'
        )
        get_app_version_s3_location_mock.assert_called_once_with('my-application', 'version-label')
        get_object_info_mock.assert_called_once_with('s3-bucket', 'my-application/version-label')
        _create_application_version_mock.assert_called_once_with(
            'my-application',
            'version-label',
            'label-message',
            's3-bucket',
            'my-application/version-label',
            False,
            build_config=None
        )

    @mock.patch('ebcli.operations.commonops.fileoperations.ProjectRoot.traverse')
    @mock.patch('ebcli.operations.commonops.heuristics.directory_is_empty')
    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.commonops.fileoperations.get_config_setting')
    @mock.patch('ebcli.operations.commonops.s3.get_object_info')
    @mock.patch('ebcli.operations.commonops.fileoperations.delete_app_versions')
    @mock.patch('ebcli.operations.commonops._create_application_version')
    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_storage_location')
    @mock.patch('ebcli.operations.commonops.s3.upload_application_version')
    def test_create_app_version__deploy_artifact__app_version_does_not_exist__uploaded_to_s3(
            self,
            upload_application_version_mock,
            get_storage_location_mock,
            _create_application_version_mock,
            delete_app_versions_mock,
            get_object_info_mock,
            get_config_setting_mock,
            get_source_control_mock,
            directory_is_empty_mock,
            traverse_mock
    ):
        directory_is_empty_mock.return_value = False
        source_control_mock = mock.MagicMock()
        source_control_mock.get_version_label.return_value = 'version-label'
        source_control_mock.get_message.return_value = 'label-message'
        get_source_control_mock.return_value = source_control_mock
        get_config_setting_mock.return_value = 'src/artifact.zip'  # No artifacts

        application_version_mock = mock.MagicMock()
        _create_application_version_mock.return_value = application_version_mock

        get_storage_location_mock.return_value = 's3-bucket'
        get_object_info_mock.side_effect = commonops.NotFoundError

        self.assertEqual(
            application_version_mock,
            commonops.create_app_version('my-application')
        )

        get_config_setting_mock.assert_called_once_with('deploy', 'artifact')

        upload_application_version_mock.assert_called_once_with(
            's3-bucket',
            'my-application/version-label.zip',
            'src/artifact.zip'
        )
        _create_application_version_mock.assert_called_once_with(
            'my-application',
            'version-label',
            'label-message',
            's3-bucket',
            'my-application/version-label.zip',
            False,
            build_config=None
        )

    @mock.patch('ebcli.operations.commonops.fileoperations.ProjectRoot.traverse')
    @mock.patch('ebcli.operations.commonops.heuristics.directory_is_empty')
    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.commonops.fileoperations.get_config_setting')
    @mock.patch('ebcli.operations.commonops.get_app_version_s3_location')
    @mock.patch('ebcli.operations.commonops.s3.get_object_info')
    @mock.patch('ebcli.operations.commonops.fileoperations.delete_app_versions')
    @mock.patch('ebcli.operations.commonops._create_application_version')
    @mock.patch('ebcli.operations.commonops._zip_up_project')
    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_storage_location')
    @mock.patch('ebcli.operations.commonops.s3.upload_application_version')
    def test_create_app_version__app_version_does_not_exist__upload_to_s3_fails(
            self,
            upload_application_version_mock,
            get_storage_location_mock,
            _zip_up_project_mock,
            _create_application_version_mock,
            delete_app_versions_mock,
            get_object_info_mock,
            get_app_version_s3_location_mock,
            get_config_setting_mock,
            get_source_control_mock,
            directory_is_empty_mock,
            traverse_mock
    ):
        directory_is_empty_mock.return_value = False
        source_control_mock = mock.MagicMock()
        source_control_mock.get_version_label.return_value = 'version-label'
        source_control_mock.get_message.return_value = 'label-message'
        get_source_control_mock.return_value = source_control_mock
        get_config_setting_mock.return_value = None  # No artifacts
        get_app_version_s3_location_mock.return_value = (None, None)
        application_version_mock = mock.MagicMock()
        _create_application_version_mock.return_value = application_version_mock
        _zip_up_project_mock.return_value = ('version-label', 'source-control')
        get_storage_location_mock.return_value = 's3-bucket'
        get_object_info_mock.side_effect = commonops.NotFoundError

        self.assertEqual(
            application_version_mock,
            commonops.create_app_version('my-application')
        )

        get_config_setting_mock.assert_called_once_with('deploy', 'artifact')
        get_app_version_s3_location_mock.assert_called_once_with('my-application', 'version-label')
        upload_application_version_mock.assert_called_once_with(
            's3-bucket',
            'my-application/version-label',
            'source-control'
        )
        _create_application_version_mock.assert_called_once_with(
            'my-application',
            'version-label',
            'label-message',
            's3-bucket',
            'my-application/version-label',
            False,
            build_config=None
        )

    @mock.patch('ebcli.operations.commonops.fileoperations.ProjectRoot.traverse')
    @mock.patch('ebcli.operations.commonops.heuristics.directory_is_empty')
    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.commonops.fileoperations.get_config_setting')
    @mock.patch('ebcli.operations.commonops.get_app_version_s3_location')
    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_storage_location')
    @mock.patch('ebcli.operations.commonops.s3.get_object_info')
    @mock.patch('ebcli.operations.commonops.fileoperations.delete_app_versions')
    @mock.patch('ebcli.operations.commonops._create_application_version')
    def test_create_app_version__other_arguments_passed_in(
            self,
            _create_application_version_mock,
            delete_app_versions_mock,
            get_object_info_mock,
            get_storage_location_mock,
            get_app_version_s3_location_mock,
            get_config_setting_mock,
            get_source_control_mock,
            directory_is_empty_mock,
            traverse_mock
    ):
        directory_is_empty_mock.return_value = False
        source_control_mock = mock.MagicMock()
        get_source_control_mock.return_value = source_control_mock
        get_config_setting_mock.return_value = None  # No artifacts
        get_app_version_s3_location_mock.return_value = ('s3-bucket', 's3-key')
        get_storage_location_mock.return_value = 's3-bucket'
        application_version_mock = mock.MagicMock()
        _create_application_version_mock.return_value = application_version_mock
        build_config_mock = mock.MagicMock()

        self.assertEqual(
            application_version_mock,
            commonops.create_app_version(
                'my-application',
                label='my-version-label',
                message='message ' * 50,
                process=True,
                build_config=build_config_mock
            )
        )

        get_config_setting_mock.assert_called_once_with('deploy', 'artifact')
        get_app_version_s3_location_mock.assert_called_once_with('my-application', 'my-version-label')
        get_object_info_mock.assert_called_once_with('s3-bucket', 's3-key')
        _create_application_version_mock.assert_called_once_with(
            'my-application',
            'my-version-label', 'message message message message message message message message message message message message message message message message message message message message message message message message mes...',
            's3-bucket',
            's3-key',
            True,
            build_config=build_config_mock
        )

    @mock.patch('ebcli.operations.commonops.fileoperations.ProjectRoot.traverse')
    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.commonops._create_application_version')
    @mock.patch('ebcli.operations.gitops.get_default_repository')
    def test_create_codecommit_app_version(
            self,
            get_default_repository_mock,
            _create_application_version_mock,
            get_source_control_mock,
            traverse_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.get_current_commit.return_value = '213123123'
        source_control_mock.get_version_label.return_value = 'version-label'
        source_control_mock.get_message.return_value = 'label-message'
        get_source_control_mock.return_value = source_control_mock
        application_version_mock = mock.MagicMock()
        _create_application_version_mock.return_value = application_version_mock
        get_default_repository_mock.return_value = 'repository'

        self.assertEqual(
            application_version_mock,
            commonops.create_codecommit_app_version('my-application')
        )

        _create_application_version_mock.assert_called_once_with(
            'my-application',
            'version-label',
            'label-message',
            None,
            None,
            False,
            build_config=None,
            commit_id='213123123',
            repository='repository'
        )

    @mock.patch('ebcli.operations.commonops.fileoperations.ProjectRoot.traverse')
    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.commonops._create_application_version')
    @mock.patch('ebcli.operations.commonops.io.log_warning')
    @mock.patch('ebcli.operations.gitops.get_default_repository')
    def test_create_codecommit_app_version__untracked_changes_exist(
            self,
            get_default_repository_mock,
            log_warning_mock,
            _create_application_version_mock,
            get_source_control_mock,
            traverse_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.get_current_commit.return_value = '213123123'
        source_control_mock.untracked_changes_exist.return_value = True
        source_control_mock.get_version_label.return_value = 'version-label'
        source_control_mock.get_message.return_value = 'label-message'
        get_source_control_mock.return_value = source_control_mock
        application_version_mock = mock.MagicMock()
        _create_application_version_mock.return_value = application_version_mock
        get_default_repository_mock.return_value = 'repository'

        self.assertEqual(
            application_version_mock,
            commonops.create_codecommit_app_version('my-application')
        )

        log_warning_mock.assert_called_once_with('You have uncommitted changes.')
        _create_application_version_mock.assert_called_once_with(
            'my-application',
            'version-label',
            'label-message',
            None,
            None,
            False,
            build_config=None,
            commit_id='213123123',
            repository='repository'
        )

    @mock.patch('ebcli.operations.commonops.fileoperations.ProjectRoot.traverse')
    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.commonops._create_application_version')
    @mock.patch('ebcli.operations.commonops.io.log_warning')
    @mock.patch('ebcli.operations.gitops.get_default_repository')
    def test_create_codecommit_app_version__no_commits_exist_yet_in_the_directory__a_new_one_is_created(
            self,
            get_default_repository_mock,
            log_warning_mock,
            _create_application_version_mock,
            get_source_control_mock,
            traverse_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.get_current_commit.side_effect = [None, '213123123']
        source_control_mock.untracked_changes_exist.return_value = True
        source_control_mock.get_version_label.return_value = 'version-label'
        source_control_mock.get_message.return_value = 'label-message'
        source_control_mock.untracked_changes_exist.return_value = False
        get_source_control_mock.return_value = source_control_mock
        application_version_mock = mock.MagicMock()
        _create_application_version_mock.return_value = application_version_mock
        get_default_repository_mock.return_value = 'repository'

        self.assertEqual(
            application_version_mock,
            commonops.create_codecommit_app_version('my-application')
        )

        log_warning_mock.assert_called_once_with(
            'There are no commits for the current branch, attempting to '
            'create an empty commit and launching with the sample application'
        )
        source_control_mock.create_initial_commit.assert_called_once()
        _create_application_version_mock.assert_called_once_with(
            'my-application',
            'version-label',
            'label-message',
            None,
            None,
            False,
            build_config=None,
            commit_id='213123123',
            repository='repository'
        )

    @mock.patch('ebcli.operations.commonops.fileoperations.ProjectRoot.traverse')
    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.commonops._create_application_version')
    @mock.patch('ebcli.operations.gitops.get_default_repository')
    def test_create_codecommit_app_version__with_arguments_eplicitly_passed(
            self,
            get_default_repository_mock,
            _create_application_version_mock,
            get_source_control_mock,
            traverse_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.get_current_commit.return_value = '213123123'
        source_control_mock.untracked_changes_exist.return_value = True
        source_control_mock.get_version_label.return_value = 'version-label'
        source_control_mock.get_message.return_value = 'label-message'
        get_source_control_mock.return_value = source_control_mock
        application_version_mock = mock.MagicMock()
        _create_application_version_mock.return_value = application_version_mock
        get_default_repository_mock.return_value = 'repository'
        build_config_mock = mock.MagicMock()

        self.assertEqual(
            application_version_mock,
            commonops.create_codecommit_app_version(
                'my-application',
                process=True,
                label='version-label',
                message='message ' * 50,
                build_config=build_config_mock
            )
        )

        _create_application_version_mock.assert_called_once_with(
            'my-application',
            'version-label',
            'message message message message message message message message message message message message message message message message message message message message message message message message mes...',
            None,
            None,
            True,
            build_config=build_config_mock,
            commit_id='213123123',
            repository='repository'
        )

    @mock.patch('ebcli.operations.commonops.fileoperations.ProjectRoot.traverse')
    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.commonops._create_application_version')
    @mock.patch('ebcli.operations.gitops.get_default_repository')
    @mock.patch('ebcli.operations.commonops.io.echo')
    @mock.patch('ebcli.operations.commonops.io.log_warning')
    def test_create_codecommit_app_version__push_to_codecommit_failed(
            self,
            log_warning_mock,
            echo_mock,
            get_default_repository_mock,
            _create_application_version_mock,
            get_source_control_mock,
            traverse_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.get_current_commit.return_value = '213123123'
        source_control_mock.untracked_changes_exist.return_value = True
        source_control_mock.get_version_label.return_value = 'version-label'
        source_control_mock.get_message.return_value = 'label-message'
        source_control_mock.push_codecommit_code.side_effect = commonops.CommandError
        get_source_control_mock.return_value = source_control_mock
        application_version_mock = mock.MagicMock()
        _create_application_version_mock.return_value = application_version_mock
        get_default_repository_mock.return_value = 'repository'

        with self.assertRaises(commonops.CommandError):
            commonops.create_codecommit_app_version('my-application')

        echo_mock.assert_called_once_with(
            'Could not push code to the CodeCommit repository:'
        )

        _create_application_version_mock.assert_not_called()

    @mock.patch('ebcli.operations.commonops.fileoperations.ProjectRoot.traverse')
    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.commonops._create_application_version')
    @mock.patch('ebcli.operations.gitops.get_default_repository')
    def test_create_codecommit_app_version__could_not_find_default_repository_information(
            self,
            get_default_repository_mock,
            _create_application_version_mock,
            get_source_control_mock,
            traverse_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.get_current_commit.return_value = '213123123'
        source_control_mock.untracked_changes_exist.return_value = True
        source_control_mock.get_version_label.return_value = 'version-label'
        source_control_mock.get_message.return_value = 'label-message'
        get_source_control_mock.return_value = source_control_mock
        application_version_mock = mock.MagicMock()
        _create_application_version_mock.return_value = application_version_mock
        get_default_repository_mock.return_value = None

        with self.assertRaises(commonops.ServiceError):
            commonops.create_codecommit_app_version('my-application')

        _create_application_version_mock.assert_not_called()


    @mock.patch('ebcli.operations.commonops.fileoperations.ProjectRoot.traverse')
    @mock.patch('ebcli.operations.commonops.heuristics.directory_is_empty')
    @mock.patch('ebcli.operations.commonops.io.echo')
    def test_create_app_version_from_source__directory_is_empty(
            self,
            echo_mock,
            directory_is_empty_mock,
            traverse_mock
    ):
        directory_is_empty_mock.return_value = True

        self.assertIsNone(
            commonops.create_app_version_from_source(
                'my-application',
                'codecommit/my-repository/my-branch'
            )
        )

        echo_mock.assert_called_once_with(
            'NOTE: The current directory does not contain any source code. '
            'Elastic Beanstalk is launching the sample application instead.'
        )

    @mock.patch('ebcli.operations.commonops.fileoperations.ProjectRoot.traverse')
    @mock.patch('ebcli.operations.commonops.heuristics.directory_is_empty')
    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.commonops._create_application_version')
    @mock.patch('ebcli.operations.commonops.codecommit.get_branch')
    def test_create_app_version_from_source(
            self,
            get_branch_mock,
            _create_application_version_mock,
            get_source_control_mock,
            directory_is_empty_mock,
            traverse_mock
    ):
        directory_is_empty_mock.return_value = False
        source_control_mock = mock.MagicMock()
        source_control_mock.get_version_label.return_value = 'version-label'
        source_control_mock.get_message.return_value = 'label-message'
        get_source_control_mock.return_value = source_control_mock
        application_version_mock = mock.MagicMock()
        _create_application_version_mock.return_value = application_version_mock
        get_branch_mock.return_value = {
            'branch': {
                'commitId': '234234123'
            }
        }

        self.assertEqual(
            application_version_mock,
            commonops.create_app_version_from_source(
                'my-application',
                'codecommit/my-repository/my-branch'
            )
        )

        get_branch_mock.assert_called_once_with(
            'my-repository',
            'my-branch'
        )
        _create_application_version_mock.assert_called_once_with(
            'my-application',
            'version-label',
            'label-message',
            None,
            None,
            False,
            build_config=None,
            commit_id='234234123',
            repository='my-repository'
        )

    @mock.patch('ebcli.operations.commonops.fileoperations.ProjectRoot.traverse')
    @mock.patch('ebcli.operations.commonops.heuristics.directory_is_empty')
    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.commonops._create_application_version')
    @mock.patch('ebcli.operations.commonops.codecommit.get_branch')
    def test_create_app_version_from_source__source_is_not_a_codecommit_one(
            self,
            get_branch_mock,
            _create_application_version_mock,
            get_source_control_mock,
            directory_is_empty_mock,
            traverse_mock
    ):
        directory_is_empty_mock.return_value = False
        source_control_mock = mock.MagicMock()
        source_control_mock.get_version_label.return_value = 'version-label'
        source_control_mock.get_message.return_value = 'label-message'
        get_source_control_mock.return_value = source_control_mock
        application_version_mock = mock.MagicMock()
        _create_application_version_mock.return_value = application_version_mock

        with self.assertRaises(commonops.InvalidOptionsError) as context_manager:
            commonops.create_app_version_from_source(
                'my-application',
                'github/my-repository/my-branch'
            )

        self.assertEqual(
            'Source location "github" is not supported by the EBCLI',
            str(context_manager.exception)
        )
        get_branch_mock.assert_not_called()
        _create_application_version_mock.assert_not_called()

    @mock.patch('ebcli.operations.commonops.fileoperations.ProjectRoot.traverse')
    @mock.patch('ebcli.operations.commonops.heuristics.directory_is_empty')
    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.commonops._create_application_version')
    @mock.patch('ebcli.operations.commonops.codecommit.get_branch')
    @mock.patch('ebcli.operations.commonops.io.log_error')
    def test_create_app_version_from_source__failed_to_find_remote_branch(
            self,
            log_error_mock,
            get_branch_mock,
            _create_application_version_mock,
            get_source_control_mock,
            directory_is_empty_mock,
            traverse_mock
    ):
        directory_is_empty_mock.return_value = False
        source_control_mock = mock.MagicMock()
        source_control_mock.get_version_label.return_value = 'version-label'
        source_control_mock.get_message.return_value = 'label-message'
        get_source_control_mock.return_value = source_control_mock
        application_version_mock = mock.MagicMock()
        _create_application_version_mock.return_value = application_version_mock
        get_branch_mock.side_effect = commonops.ServiceError

        with self.assertRaises(commonops.ServiceError) as context_manager:
            commonops.create_app_version_from_source(
                'my-application',
                'codecommit/my-repository/my-branch'
            )

        log_error_mock.assert_called_once_with(
            "Could not get branch 'my-branch' for the repository 'my-repository' because of this error: None"
        )
        get_branch_mock.assert_called_once_with('my-repository', 'my-branch')
        _create_application_version_mock.assert_not_called()

    @mock.patch('ebcli.operations.commonops.fileoperations.ProjectRoot.traverse')
    @mock.patch('ebcli.operations.commonops.heuristics.directory_is_empty')
    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.commonops._create_application_version')
    def test_create_app_version_from_source__source_is_misformatted(
            self,
            _create_application_version_mock,
            get_source_control_mock,
            directory_is_empty_mock,
            traverse_mock
    ):
        directory_is_empty_mock.return_value = False
        source_control_mock = mock.MagicMock()
        source_control_mock.get_version_label.return_value = 'version-label'
        source_control_mock.get_message.return_value = 'label-message'
        get_source_control_mock.return_value = source_control_mock
        application_version_mock = mock.MagicMock()
        _create_application_version_mock.return_value = application_version_mock

        with self.assertRaises(commonops.InvalidOptionsError) as context_manager:
            commonops.create_app_version_from_source(
                'my-application',
                'codecommit/my-branch'
            )
        self.assertEqual(
            'Source argument must be of the form codecommit/repository-name/branch-name',
            str(context_manager.exception)
        )
        _create_application_version_mock.assert_not_called()

    @mock.patch('ebcli.operations.commonops.fileoperations.get_zip_location')
    @mock.patch('ebcli.operations.commonops.fileoperations.file_exists')
    @mock.patch('ebcli.operations.commonops.fileoperations.get_ebignore_list')
    def test_zip_up_project__file_already_exists(
            self,
            get_ebignore_list_mock,
            file_exists_mock,
            get_zip_location_mock
    ):
        get_zip_location_mock.return_value = 'file_path'
        file_exists_mock.return_value = True
        source_control_mock = mock.MagicMock()

        self.assertEqual(
            ('version-label.zip', 'file_path'),
            commonops._zip_up_project(
                'version-label',
                source_control_mock
            )
        )

    @mock.patch('ebcli.operations.commonops.fileoperations.get_zip_location')
    @mock.patch('ebcli.operations.commonops.fileoperations.file_exists')
    @mock.patch('ebcli.operations.commonops.fileoperations.get_ebignore_list')
    def test_zip_up_project__file_doesnt_exist(
            self,
            get_ebignore_list_mock,
            file_exists_mock,
            get_zip_location_mock
    ):
        get_zip_location_mock.return_value = 'file_path'
        file_exists_mock.return_value = False
        source_control_mock = mock.MagicMock()
        get_ebignore_list_mock.return_value = None

        self.assertEqual(
            ('version-label.zip', 'file_path'),
            commonops._zip_up_project(
                'version-label',
                source_control_mock
            )
        )

        source_control_mock.do_zip.assert_called_once_with('file_path', False)

    @mock.patch('ebcli.operations.commonops.fileoperations.get_zip_location')
    @mock.patch('ebcli.operations.commonops.fileoperations.file_exists')
    @mock.patch('ebcli.operations.commonops.fileoperations.get_ebignore_list')
    @mock.patch('ebcli.operations.commonops.fileoperations.zip_up_project')
    def test_zip_up_project__file_doesnt_exist(
            self,
            zip_up_project_mock,
            get_ebignore_list_mock,
            file_exists_mock,
            get_zip_location_mock
    ):
        get_zip_location_mock.return_value = 'file_path'
        file_exists_mock.return_value = False
        source_control_mock = mock.MagicMock()
        get_ebignore_list_mock.return_value = {'index.html'}

        self.assertEqual(
            ('version-label.zip', 'file_path'),
            commonops._zip_up_project(
                'version-label',
                source_control_mock
            )
        )

        zip_up_project_mock.assert_called_once_with('file_path', ignore_list={'index.html'})

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.update_environment')
    @mock.patch('ebcli.operations.commonops.wait_for_success_events')
    def test_update_environment(
            self,
            wait_for_success_events_mock,
            update_environment_mock
    ):
        options_mock = mock.MagicMock()
        remove_mock = mock.MagicMock()
        template_mock = mock.MagicMock()
        template_body_mock = mock.MagicMock()
        solution_stack_name = 'php 7.1'
        update_environment_mock.return_value = 'request-id'

        commonops.update_environment(
            'my-environment',
            options_mock,
            False,
            remove=remove_mock,
            template=template_mock,
            template_body=template_body_mock,
            solution_stack_name=solution_stack_name,
        )

        update_environment_mock.assert_called_once_with(
            'my-environment',
            options_mock,
            platform_arn=None,
            remove=remove_mock,
            solution_stack_name='php 7.1',
            template=template_mock,
            template_body=template_body_mock
        )
        wait_for_success_events_mock.assert_called_once_with(
            'request-id',
            can_abort=True,
            timeout_in_minutes=None
        )

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.update_environment')
    @mock.patch('ebcli.operations.commonops.wait_for_success_events')
    @mock.patch('ebcli.operations.commonops.io.log_error')
    def test_update_environment__invalid_state_error(
            self,
            log_error_mock,
            wait_for_success_events_mock,
            update_environment_mock
    ):
        options_mock = mock.MagicMock()
        remove_mock = mock.MagicMock()
        template_mock = mock.MagicMock()
        template_body_mock = mock.MagicMock()
        solution_stack_name = 'php 7.1'
        update_environment_mock.side_effect = commonops.InvalidStateError

        self.assertIsNone(
            commonops.update_environment(
                'my-environment',
                options_mock,
                False,
                remove=remove_mock,
                template=template_mock,
                template_body=template_body_mock,
                solution_stack_name=solution_stack_name,
            )
        )

        self.assertIsNone(
            update_environment_mock.assert_called_once_with(
                'my-environment',
                options_mock,
                platform_arn=None,
                remove=remove_mock,
                solution_stack_name='php 7.1',
                template=template_mock,
                template_body=template_body_mock
            )
        )
        log_error_mock.assert_called_once_with(
            'The environment update cannot be complete at this time. Try again later.'
        )
        wait_for_success_events_mock.assert_not_called()

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.update_environment')
    @mock.patch('ebcli.operations.commonops.wait_for_success_events')
    @mock.patch('ebcli.operations.commonops.io.log_error')
    def test_update_environment__invalid_syntax_error(
            self,
            log_error_mock,
            wait_for_success_events_mock,
            update_environment_mock
    ):
        options_mock = mock.MagicMock()
        remove_mock = mock.MagicMock()
        template_mock = mock.MagicMock()
        template_body_mock = mock.MagicMock()
        solution_stack_name = 'php 7.1'
        update_environment_mock.side_effect = commonops.InvalidSyntaxError

        self.assertIsNone(
            commonops.update_environment(
                'my-environment',
                options_mock,
                False,
                remove=remove_mock,
                template=template_mock,
                template_body=template_body_mock,
                solution_stack_name=solution_stack_name,
            )
        )

        self.assertIsNone(
            update_environment_mock.assert_called_once_with(
                'my-environment',
                options_mock,
                platform_arn=None,
                remove=remove_mock,
                solution_stack_name='php 7.1',
                template=template_mock,
                template_body=template_body_mock
            )
        )
        log_error_mock.assert_called_once_with(
            'The configuration settings you provided contain an error. The environment will not be updated.\nError = '
        )
        wait_for_success_events_mock.assert_not_called()

    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    def test_write_setting_to_current_branch__get_setting_from_current_branch(
            self,
            get_source_control_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.get_current_branch.return_value = 'branch-1'
        get_source_control_mock.return_value = source_control_mock

        commonops.write_setting_to_current_branch('username', 'thisismyusername')

        self.assertEqual(
            'thisismyusername',
            commonops.get_setting_from_current_branch('username')
        )

    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    def test_get_setting_from_current_branch__current_branch_could_not_be_found(
            self,
            get_source_control_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.get_current_branch.side_effect = commonops.CommandError
        get_source_control_mock.return_value = source_control_mock

        self.assertIsNone(commonops.get_setting_from_current_branch('some-key'))

    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    @mock.patch('ebcli.operations.commonops.fileoperations.get_config_setting')
    def test_get_setting_from_current_branch__current_branch_is_not_registered_in_config_yml(
            self,
            get_config_setting_mock,
            get_source_control_mock
    ):
        get_config_setting_mock.return_value = None
        source_control_mock = mock.MagicMock()
        source_control_mock.get_current_branch.return_value = 'absent_branch'
        get_source_control_mock.return_value = source_control_mock

        self.assertIsNone(commonops.get_setting_from_current_branch('some-key'))

    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    def test_set_environment_for_current_branch__get_current_branch_environment(
            self,
            get_source_control_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.get_current_branch.return_value = 'branch-1'
        get_source_control_mock.return_value = source_control_mock

        commonops.set_environment_for_current_branch('environment-1')

        self.assertEqual(
            'environment-1',
            commonops.get_current_branch_environment()
        )

    @mock.patch('ebcli.operations.commonops.SourceControl.get_source_control')
    def test_set_group_suffix_for_current_branch__get_current_branch_group_suffix(
            self,
            get_source_control_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.get_current_branch.return_value = 'branch-1'
        get_source_control_mock.return_value = source_control_mock

        commonops.set_group_suffix_for_current_branch('dev')

        self.assertEqual(
            'dev',
            commonops.get_current_branch_group_suffix()
        )

    def test_get_default_keyname__default_keyname_is_absent(self):
        self.assertIsNone(commonops.get_default_keyname())

    def test_get_default_keyname(self):
        fileoperations.write_keyname('aws-eb-us-west-2')

        self.assertEqual(
            'aws-eb-us-west-2',
            commonops.get_default_keyname()
        )

    @mock.patch('ebcli.operations.commonops.get_config_setting_from_branch_or_default')
    def test_get_default_profile__branch_default_for_profile_is_none__but_a_default_is_required(
            self,
            get_config_setting_from_branch_or_default_mock
    ):
        get_config_setting_from_branch_or_default_mock.return_value = None

        self.assertEqual(
            'default',
            commonops.get_default_profile(require_default=True)
        )
        get_config_setting_from_branch_or_default_mock.assert_called_once_with('profile')

    @mock.patch('ebcli.operations.commonops.get_config_setting_from_branch_or_default')
    def test_get_default_profile__branch_default_for_profile_is_none__default_is_not_required(
            self,
            get_config_setting_from_branch_or_default_mock
    ):
        get_config_setting_from_branch_or_default_mock.return_value = None

        self.assertIsNone(commonops.get_default_profile())
        get_config_setting_from_branch_or_default_mock.assert_called_once_with('profile')


    @mock.patch('ebcli.operations.commonops.get_config_setting_from_branch_or_default')
    def test_get_default_profile__directory_is_not_initialized(
            self,
            get_config_setting_from_branch_or_default_mock
    ):
        get_config_setting_from_branch_or_default_mock.side_effect = commonops.NotInitializedError

        self.assertIsNone(commonops.get_default_profile())
        get_config_setting_from_branch_or_default_mock.assert_called_once_with('profile')

    @mock.patch('ebcli.operations.commonops.get_config_setting_from_branch_or_default')
    def test_get_default_region(
            self,
            get_config_setting_from_branch_or_default_mock
    ):
        get_config_setting_from_branch_or_default_mock.return_value = 'us-west-2'

        self.assertEqual('us-west-2', commonops.get_default_region())
        get_config_setting_from_branch_or_default_mock.assert_called_once_with('default_region')

    @mock.patch('ebcli.operations.commonops.get_config_setting_from_branch_or_default')
    def test_get_default_region__branch_default_for_region_is_none(
            self,
            get_config_setting_from_branch_or_default_mock
    ):
        get_config_setting_from_branch_or_default_mock.return_value = None

        self.assertIsNone(commonops.get_default_region())
        get_config_setting_from_branch_or_default_mock.assert_called_once_with('default_region')

    @mock.patch('ebcli.operations.commonops.get_config_setting_from_branch_or_default')
    def test_get_default_region__directory_is_not_initialized(
            self,
            get_config_setting_from_branch_or_default_mock
    ):
        get_config_setting_from_branch_or_default_mock.side_effect = commonops.NotInitializedError

        self.assertIsNone(commonops.get_default_region())
        get_config_setting_from_branch_or_default_mock.assert_called_once_with('default_region')

    @mock.patch('ebcli.operations.commonops.ec2.get_key_pairs')
    def test_upload_keypair_if_needed__key_name_already_exists(
            self,
            get_key_pairs_mock
    ):
        get_key_pairs_mock.return_value = mock_responses.DESCRIBE_KEY_PAIRS_RESPONSE['KeyPairs']

        self.assertIsNone(commonops.upload_keypair_if_needed('key_pair_1'))

    @mock.patch('ebcli.operations.commonops.ec2.get_key_pairs')
    @mock.patch('ebcli.operations.commonops._get_public_ssh_key')
    @mock.patch('ebcli.operations.commonops.ec2.import_key_pair')
    def test_upload_keypair_if_needed__race_condition_in_which_key_name_is_created_through_another_client(
            self,
            import_key_pair_mock,
            _get_public_ssh_key_mock,
            get_key_pairs_mock
    ):
        # Creation of `keyname` on EC2 is possible concurrently through another
        # client, but unlikely.
        get_key_pairs_mock.return_value = mock_responses.DESCRIBE_KEY_PAIRS_RESPONSE['KeyPairs']
        _get_public_ssh_key_mock.return_value = 'ssh-rsa BBBBBBBaC1yc2EAAAADAQABAAABAQC91'
        import_key_pair_mock.side_effect = commonops.AlreadyExistsError

        self.assertIsNone(commonops.upload_keypair_if_needed('key_pair_3'))

    @mock.patch('ebcli.operations.commonops.ec2.get_key_pairs')
    @mock.patch('ebcli.operations.commonops._get_public_ssh_key')
    @mock.patch('ebcli.operations.commonops.ec2.import_key_pair')
    @mock.patch('ebcli.operations.commonops.aws.get_region_name')
    @mock.patch('ebcli.operations.commonops.io.log_warning')
    def test_upload_keypair_if_needed(
            self,
            log_warning_mock,
            get_region_name_mock,
            import_key_pair_mock,
            _get_public_ssh_key_mock,
            get_key_pairs_mock
    ):
        # Creation of `keyname` on EC2 is possible concurrently through another
        # client, but unlikely.
        get_key_pairs_mock.return_value = mock_responses.DESCRIBE_KEY_PAIRS_RESPONSE['KeyPairs']
        _get_public_ssh_key_mock.return_value = 'ssh-rsa BBBBBBBaC1yc2EAAAADAQABAAABAQC91'
        get_region_name_mock.return_value = 'us-west-2'

        self.assertIsNone(commonops.upload_keypair_if_needed('key_pair_3'))

        log_warning_mock.assert_called_once_with(
            'Uploaded SSH public key for "key_pair_3" into EC2 for region us-west-2.'
        )

    @mock.patch('ebcli.operations.commonops.fileoperations.get_ssh_folder')
    @mock.patch('ebcli.operations.commonops.exec_cmd')
    def test_get_public_ssh_key__file_by_keypair_name_exists_in_the_ssh_dir(
            self,
            exec_cmd_mock,
            get_ssh_folder_mock
    ):
        os.mkdir('.ssh')
        with open(os.path.join('.ssh', 'aws-eb-us-west-2'), 'w') as keypair_file:
            keypair_file.write("""-----BEGIN RSA PRIVATE KEY-----
asdfhjgksadfKHGHJ12334ASDGAHJSDG123123235/dsfadfakhgksdhjfgasdas
-----END RSA PRIVATE KEY-----""")

        get_ssh_folder_mock.return_value = '.ssh/'

        exec_cmd_mock.return_value = ('ssh-rsa BBBBBBBaC1yc2EAAAADAQABAAABAQC91', '', 0)

        self.assertEqual(
            'ssh-rsa BBBBBBBaC1yc2EAAAADAQABAAABAQC91',
            commonops._get_public_ssh_key(
                keypair_name='aws-eb-us-west-2'
            )
        )

    @mock.patch('ebcli.operations.commonops.fileoperations.get_ssh_folder')
    @mock.patch('ebcli.operations.commonops.exec_cmd')
    def test_get_public_ssh_key__file_by_keypair_name_exists_in_the_ssh_dir_but_as_a_pem_extension(
            self,
            exec_cmd_mock,
            get_ssh_folder_mock
    ):
        os.mkdir('.ssh')
        with open(os.path.join('.ssh', 'aws-eb-us-west-2.pem'), 'w') as keypair_file:
            keypair_file.write("""-----BEGIN RSA PRIVATE KEY-----
asdfhjgksadfKHGHJ12334ASDGAHJSDG123123235/dsfadfakhgksdhjfgasdas
-----END RSA PRIVATE KEY-----""")

        get_ssh_folder_mock.return_value = '.ssh/'

        exec_cmd_mock.return_value = (
            'ssh-rsa BBBBBBBaC1yc2EAAAADAQABAAABAQC91',
            '',
            0
        )

        self.assertEqual(
            'ssh-rsa BBBBBBBaC1yc2EAAAADAQABAAABAQC91',
            commonops._get_public_ssh_key(
                keypair_name='aws-eb-us-west-2'
            )
        )

    @mock.patch('ebcli.operations.commonops.fileoperations.get_ssh_folder')
    @mock.patch('ebcli.operations.commonops.exec_cmd')
    def test_get_public_ssh_key__file_by_keypair_name_does_not_exist_in_the_ssh_dir(
            self,
            exec_cmd_mock,
            get_ssh_folder_mock
    ):
        os.mkdir('.ssh')
        get_ssh_folder_mock.return_value = '.ssh/'
        exec_cmd_mock.return_value = (
            'ssh-rsa BBBBBBBaC1yc2EAAAADAQABAAABAQC91',
            '',
            1
        )

        with self.assertRaises(commonops.NotSupportedError) as context_manager:
            commonops._get_public_ssh_key(
                keypair_name='non-existent-key-name'
            )

        self.assertEqual(
            'The EB CLI cannot find your SSH key file for keyname "non-existent-key-name". Your SSH key file must be located in the .ssh folder in your home directory.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.commonops.fileoperations.get_ssh_folder')
    @mock.patch('ebcli.operations.commonops.exec_cmd')
    def test_get_public_ssh_key__file_by_keypair_name_exists_in_the_ssh_dir__ssh_keygen_generates_OSError(
            self,
            exec_cmd_mock,
            get_ssh_folder_mock
    ):
        os.mkdir('.ssh')
        with open(os.path.join('.ssh', 'aws-eb-us-west-2'), 'w') as keypair_file:
            keypair_file.write("""-----BEGIN RSA PRIVATE KEY-----
asdfhjgksadfKHGHJ12334ASDGAHJSDG123123235/dsfadfakhgksdhjfgasdas
-----END RSA PRIVATE KEY-----""")

        get_ssh_folder_mock.return_value = '.ssh/'

        exec_cmd_mock.side_effect = OSError

        with self.assertRaises(commonops.CommandError) as context_manager:
            commonops._get_public_ssh_key(keypair_name='aws-eb-us-west-2')

        self.assertEqual(
            'SSH is not installed. You must install SSH before continuing.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_application_versions')
    @mock.patch('ebcli.operations.commonops.io.log_error')
    @mock.patch('ebcli.operations.commonops._timeout_reached')
    @mock.patch('ebcli.operations.commonops._sleep')
    def test_wait_for_processed_app_versions__some_application_versions_failed_to_get_processed(
            self,
            _sleep_mock,
            _timeout_reached_mock,
            log_error_mock,
            get_application_versions_mock
    ):
        _timeout_reached_mock.return_value = False
        get_application_versions_mock.side_effect = [
            {
                "ApplicationVersions": []
            },
            {
                "ApplicationVersions": [
                    {
                        "VersionLabel": "version-label-1",
                        "Status": 'PROCESSING',
                    },
                    {
                        "VersionLabel": "version-label-2",
                        "Status": 'PROCESSING',
                    }
                ]
            },
            {
                "ApplicationVersions": [
                    {
                        "VersionLabel": "version-label-1",
                        "Status": 'PROCESSED',
                    },
                    {
                        "VersionLabel": "version-label-2",
                        "Status": 'FAILED',
                    }
                ]
            },
        ]

        self.assertFalse(
            commonops.wait_for_processed_app_versions(
                'my-application',
                ['version-label-1', 'version-label-2']
            )
        )
        log_error_mock.assert_has_calls(
            [
                mock.call('Pre-processing of application version version-label-2 has failed.'),
                mock.call('Some application versions failed to process. Unable to continue deployment.')
            ]
        )

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_application_versions')
    @mock.patch('ebcli.operations.commonops.io.log_error')
    @mock.patch('ebcli.operations.commonops._timeout_reached')
    @mock.patch('ebcli.operations.commonops._sleep')
    def test_wait_for_processed_app_versions__all_app_versions_successfully_processed(
            self,
            _sleep_mock,
            _timeout_reached_mock,
            log_error_mock,
            get_application_versions_mock
    ):
        _timeout_reached_mock.return_value = False
        get_application_versions_mock.side_effect = [
            {
                "ApplicationVersions": []
            },
            {
                "ApplicationVersions": [
                    {
                        "VersionLabel": "version-label-1",
                        "Status": 'PROCESSING',
                    },
                    {
                        "VersionLabel": "version-label-2",
                        "Status": 'PROCESSING',
                    }
                ]
            },
            {
                "ApplicationVersions": [
                    {
                        "VersionLabel": "version-label-1",
                        "Status": 'PROCESSED',
                    },
                    {
                        "VersionLabel": "version-label-2",
                        "Status": 'PROCESSED',
                    }
                ]
            },
        ]

        self.assertTrue(
            commonops.wait_for_processed_app_versions(
                'my-application',
                ['version-label-1', 'version-label-2']
            )
        )
        log_error_mock.assert_not_called()

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_application_versions')
    @mock.patch('ebcli.operations.commonops.io.log_error')
    @mock.patch('ebcli.operations.commonops._timeout_reached')
    @mock.patch('ebcli.operations.commonops._sleep')
    def test_wait_for_processed_app_versions__timeout_reached(
            self,
            _sleep_mock,
            _timeout_reached_mock,
            log_error_mock,
            get_application_versions_mock
    ):
        _timeout_reached_mock.return_value = True
        get_application_versions_mock.side_effect = mock.MagicMock()

        self.assertFalse(
            commonops.wait_for_processed_app_versions(
                'my-application',
                ['version-label-1', 'version-label-2']
            )
        )
        log_error_mock.assert_called_once_with(
            'All application versions have not reached a "Processed" state. Unable to continue with deployment.'
        )

    @mock.patch('ebcli.operations.commonops.elasticbeanstalk.get_application_versions')
    @mock.patch('ebcli.operations.commonops.io.log_error')
    def test_wait_for_processed_app_versions__timeout_is_0_seconds(
            self,
            log_error_mock,
            get_application_versions_mock
    ):
        get_application_versions_mock.side_effect = mock.MagicMock()

        self.assertFalse(
            commonops.wait_for_processed_app_versions(
                'my-application',
                ['version-label-1', 'version-label-2'],
                timeout=0
            )
        )
        log_error_mock.assert_called_once_with(
            'All application versions have not reached a "Processed" state. Unable to continue with deployment.'
        )

    def test_wait_for_processed_app_versions__no_app_versions_to_wait_for(self):
        self.assertTrue(commonops.wait_for_processed_app_versions('my-application', []))

    @mock.patch('ebcli.operations.commonops.io.echo')
    @mock.patch('ebcli.operations.commonops.io.log_info')
    @mock.patch('ebcli.operations.commonops.io.prompt')
    @mock.patch('ebcli.operations.commonops.fileoperations.save_to_aws_config')
    @mock.patch('ebcli.operations.commonops.fileoperations.touch_config_folder')
    @mock.patch('ebcli.operations.commonops.fileoperations.write_config_setting')
    @mock.patch('ebcli.operations.commonops.aws.set_session_creds')
    def test_setup_credentials(
            self,
            set_session_creds_mock,
            write_config_setting_mock,
            touch_config_folder_mock,
            save_to_aws_config_mock,
            prompt_mock,
            log_info_mock,
            echo_mock
    ):
        prompt_mock.side_effect = [
            'access-id',
            'secret-key'
        ]

        commonops.setup_credentials()

        set_session_creds_mock.assert_called_once_with('access-id', 'secret-key')
        write_config_setting_mock.assert_called_once_with('global', 'profile', 'eb-cli')
        touch_config_folder_mock.assert_called_once_with()
        save_to_aws_config_mock.assert_called_once_with('access-id', 'secret-key')
        log_info_mock.assert_called_once_with('Setting up ~/aws/ directory with config file')
        echo_mock.assert_called_once_with(
            'You have not yet set up your credentials or your credentials are incorrect \nYou must provide your credentials.'
        )

    def test_get_region_from_inputs__region_was_passed(self):
        self.assertEqual(
            'us-east-1',
            commonops.get_region_from_inputs('us-east-1')
        )

    @mock.patch('ebcli.operations.commonops.get_default_region')
    def test_get_region_from_inputs__region_not_passed_in__default_region_found(
            self,
            get_default_region_mock
    ):
        get_default_region_mock.return_value = 'us-east-1'
        self.assertEqual(
            'us-east-1',
            commonops.get_region_from_inputs(None)
        )

    @mock.patch('ebcli.operations.commonops.get_default_region')
    def test_get_region_from_inputs__region_not_passed_in__could_not_determine_default_region(
            self,
            get_default_region_mock
    ):
        get_default_region_mock.side_effect = commonops.NotInitializedError
        self.assertIsNone(commonops.get_region_from_inputs(None))

    @mock.patch('ebcli.operations.commonops.get_region_from_inputs')
    @mock.patch('ebcli.objects.region.get_all_regions')
    def test_get_region__valid_arn(
            self,
            get_all_regions_mock,
            get_region_from_inputs_mock,
    ):
        get_region_from_inputs_mock.return_value = None

        self.assertEqual(
            'us-west-2',
            commonops.get_region(
                None,
                False,
                True,
                'arn:aws:elasticbeanstalk:us-west-2::platform/Puma with Ruby 2.4 running on 64bit Amazon Linux/2.9.1',
            )
        )

        get_all_regions_mock.assert_not_called()

    @mock.patch('ebcli.operations.commonops.get_region_from_inputs')
    def test_get_region__language_passed_as_platform(
            self,
            get_region_from_inputs_mock,
    ):
        get_region_from_inputs_mock.return_value = None

        self.assertEqual(
            'us-west-2',
            commonops.get_region(
                None,
                False,
                True,
                'node.js',
            )
        )

    @mock.patch('ebcli.operations.commonops.get_region_from_inputs')
    def test_get_region__solution_stack_passed_as_platform(
            self,
            get_region_from_inputs_mock,
    ):
        get_region_from_inputs_mock.return_value = None

        self.assertEqual(
            'us-west-2',
            commonops.get_region(
                None,
                False,
                True,
                '64bit Amazon Linux 2018.03 v2.9.1 running Ruby 2.4 (Puma)',
            )
        )

    @mock.patch('ebcli.operations.commonops.get_region_from_inputs')
    def test_get_region__solution_stack_shorthand_passed_as_platform(
            self,
            get_region_from_inputs_mock,
    ):
        get_region_from_inputs_mock.return_value = None

        self.assertEqual(
            'us-west-2',
            commonops.get_region(
                None,
                False,
                True,
                'custom_stack',
            )
        )

    @mock.patch('ebcli.operations.commonops.get_region_from_inputs')
    @mock.patch('ebcli.operations.commonops.get_all_regions')
    @mock.patch('ebcli.operations.commonops.utils.prompt_for_item_in_list')
    def test_get_region__determine_region_from_inputs(
            self,
            prompt_for_item_in_list_mock,
            get_all_regions_mock,
            get_region_from_inputs_mock
    ):
        get_region_from_inputs_mock.return_value = 'us-east-1'

        self.assertEqual(
            'us-east-1',
            commonops.get_region('us-east-1', False)
        )

        get_all_regions_mock.assert_not_called()
        prompt_for_item_in_list_mock.assert_not_called()

    @mock.patch('ebcli.operations.commonops.get_region_from_inputs')
    @mock.patch('ebcli.operations.commonops.utils.prompt_for_item_in_list')
    def test_get_region__could_not_determine_region_from_inputs__force_non_interactive__selects_us_west_2_by_default(
            self,
            prompt_for_item_in_list_mock,
            get_region_from_inputs_mock
    ):
        get_region_from_inputs_mock.return_value = None

        self.assertEqual(
            'us-west-2',
            commonops.get_region(None, False, force_non_interactive=True)
        )

        prompt_for_item_in_list_mock.assert_not_called()

    @mock.patch('ebcli.operations.commonops.get_region_from_inputs')
    @mock.patch('ebcli.operations.commonops.utils.prompt_for_item_in_list')
    def test_get_region__could_not_determine_region_from_inputs__in_interactive_mode__prompts_customer_for_region(
            self,
            prompt_for_item_in_list_mock,
            get_region_from_inputs_mock
    ):
        get_region_from_inputs_mock.return_value = None
        prompt_for_item_in_list_mock.return_value = Region('us-west-1', 'US West (N. California)')

        self.assertEqual(
            'us-west-1',
            commonops.get_region(None, True)
        )

    @mock.patch('ebcli.operations.commonops.get_region_from_inputs')
    @mock.patch('ebcli.operations.commonops.utils.prompt_for_item_in_list')
    def test_get_region__could_not_determine_region_from_inputs__not_in_interactive_mode__prompts_customer_for_region_anyway(
            self,
            prompt_for_item_in_list_mock,
            get_region_from_inputs_mock
    ):
        get_region_from_inputs_mock.return_value = None
        prompt_for_item_in_list_mock.return_value = Region('us-west-1', 'US West (N. California)')

        self.assertEqual(
            'us-west-1',
            commonops.get_region(None, False)
        )

    @mock.patch('ebcli.operations.commonops.credentials_are_valid')
    def test_check_credentials__credentials_are_valid(
            self,
            credentials_are_valid_mock
    ):
        credentials_are_valid_mock.return_value = True
        self.assertEqual(
            ('my-profile', 'us-east-1'),
            commonops.check_credentials(
                'my-profile',
                'my-profile',
                'us-east-1',
                False,
                False
            )
        )

    @mock.patch('ebcli.operations.commonops.credentials_are_valid')
    @mock.patch('ebcli.operations.commonops.get_region')
    def test_check_credentials__no_region_error_rescued(
            self,
            get_region_mock,
            credentials_are_valid_mock
    ):
        get_region_mock.return_value = 'us-west-1'
        credentials_are_valid_mock.side_effect = commonops.InvalidProfileError

        with self.assertRaises(commonops.InvalidProfileError):
            commonops.check_credentials(
                'my-profile',
                'my-profile',
                'us-east-1',
                False,
                False
            )

    @mock.patch('ebcli.operations.commonops.credentials_are_valid')
    @mock.patch('ebcli.operations.commonops.get_region')
    def test_check_credentials__invalid_profile_error_raised__profile_not_provided_as_input(
            self,
            get_region_mock,
            credentials_are_valid_mock
    ):
        get_region_mock.return_value = 'us-west-1'
        credentials_are_valid_mock.side_effect = [
            commonops.InvalidProfileError,
            None
        ]

        self.assertEqual(
            (None, 'us-east-1'),
            commonops.check_credentials(
                None,
                None,
                'us-east-1',
                False,
                False
            )
        )

    @mock.patch('ebcli.operations.commonops.check_credentials')
    @mock.patch('ebcli.operations.commonops.credentials_are_valid')
    @mock.patch('ebcli.operations.commonops.setup_credentials')
    @mock.patch('ebcli.controllers.initialize.fileoperations.write_config_setting')
    def test_set_up_credentials__credentials_not_setup(
            self,
            write_config_setting_mock,
            setup_credentials_mock,
            credentials_are_valid_mock,
            check_credentials_mock
    ):
        check_credentials_mock.return_value = ['my-profile', 'us-east-1']
        credentials_are_valid_mock.return_value = False

        commonops.set_up_credentials(
            'my-profile',
            'us-east-1',
            False
        )
        check_credentials_mock.assert_called_once_with(
            'my-profile',
            'my-profile',
            'us-east-1',
            False,
            False
        )
        setup_credentials_mock.assert_called_once()
        write_config_setting_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.aws.set_profile')
    @mock.patch('ebcli.operations.commonops.check_credentials')
    @mock.patch('ebcli.operations.commonops.credentials_are_valid')
    @mock.patch('ebcli.operations.commonops.setup_credentials')
    @mock.patch('ebcli.controllers.initialize.fileoperations.write_config_setting')
    def test_set_up_credentials__eb_cli_is_used_as_default_profile(
            self,
            write_config_setting_mock,
            setup_credentials_mock,
            credentials_are_valid_mock,
            check_credentials_mock,
            set_profile_mock
    ):
        check_credentials_mock.return_value = ['my-profile', 'us-east-1']
        credentials_are_valid_mock.return_value = True

        commonops.set_up_credentials(
            None,
            'us-east-1',
            False
        )
        check_credentials_mock.assert_called_once_with(
            'eb-cli',
            None,
            'us-east-1',
            False,
            False
        )
        set_profile_mock.assert_called_once_with('eb-cli')
        setup_credentials_mock.assert_called_once()
        write_config_setting_mock.assert_called_once_with('global', 'profile', 'eb-cli')

    @mock.patch('ebcli.controllers.initialize.aws.set_profile')
    @mock.patch('ebcli.operations.commonops.check_credentials')
    @mock.patch('ebcli.operations.commonops.credentials_are_valid')
    @mock.patch('ebcli.operations.commonops.setup_credentials')
    @mock.patch('ebcli.controllers.initialize.fileoperations.write_config_setting')
    def test_set_up_credentials__eb_cli_is_used_as_default_profile(
            self,
            write_config_setting_mock,
            setup_credentials_mock,
            credentials_are_valid_mock,
            check_credentials_mock,
            set_profile_mock
    ):
        check_credentials_mock.return_value = ['eb-cli', 'us-east-1']
        credentials_are_valid_mock.return_value = True

        commonops.set_up_credentials(
            None,
            'us-east-1',
            False
        )
        check_credentials_mock.assert_called_once_with(
            'eb-cli',
            None,
            'us-east-1',
            False,
            False
        )
        set_profile_mock.assert_called_once_with('eb-cli')
        setup_credentials_mock.assert_not_called()
        write_config_setting_mock.assert_called_once_with('global', 'profile', 'eb-cli')

    @mock.patch('ebcli.operations.commonops.check_credentials')
    @mock.patch('ebcli.operations.commonops.credentials_are_valid')
    @mock.patch('ebcli.operations.commonops.setup_credentials')
    @mock.patch('ebcli.controllers.initialize.fileoperations.write_config_setting')
    def test_set_up_credentials__env_variables_found(
            self,
            write_config_setting_mock,
            setup_credentials_mock,
            credentials_are_valid_mock,
            check_credentials_mock,
    ):
        check_credentials_mock.return_value = [None, 'us-east-1']
        credentials_are_valid_mock.return_value = True

        @CredentialsEnvVarSubstituter('access_id', 'secret_key')
        def check_creds():
            commonops.set_up_credentials(
                None,
                'us-east-1',
                False
            )
        check_credentials_mock.assert_called_once_with(
                None,
                None,
                'us-east-1',
                False,
                False
            )
        setup_credentials_mock.assert_not_called()
        write_config_setting_mock.assert_called_once_with('global', 'profile', None)

    @mock.patch('ebcli.operations.commonops.get_region_from_inputs')
    @mock.patch('ebcli.controllers.initialize.aws.set_region')
    def test_set_region_for_application(
            self,
            set_region_mock,
            get_region_from_inputs_mock
    ):
        get_region_from_inputs_mock.return_value = 'us-west-2'

        self.assertEqual(
            'us-west-2',
            commonops.set_region_for_application(False, 'us-west-2', False)
        )

        get_region_from_inputs_mock.assert_called_once_with('us-west-2')
        set_region_mock.assert_called_once_with('us-west-2')

    @mock.patch('ebcli.operations.commonops.get_region')
    @mock.patch('ebcli.controllers.initialize.aws.set_region')
    def test_set_region_for_application__interactive(
            self,
            set_region_mock,
            get_region_mock
    ):
        get_region_mock.return_value = 'us-west-2'

        self.assertEqual(
            'us-west-2',
            commonops.set_region_for_application(True, 'us-west-2', False)
        )

        get_region_mock.assert_called_once_with('us-west-2', True, False, None)
        set_region_mock.assert_called_once_with('us-west-2')

    @mock.patch('ebcli.operations.commonops.get_region')
    @mock.patch('ebcli.controllers.initialize.aws.set_region')
    def test_set_region_for_application__non_interactive(
            self,
            set_region_mock,
            get_region_mock
    ):
        get_region_mock.return_value = 'us-west-2'

        self.assertEqual(
            'us-west-2',
            commonops.set_region_for_application(
                True,
                None,
                False,
                'us-west-2'
            )
        )

        get_region_mock.assert_called_once_with(
            None,
            True,
            False,
            'us-west-2'
        )
        set_region_mock.assert_called_once_with('us-west-2')

    def test_raise_if_inside_application_workspace(self):
        with self.assertRaises(EnvironmentError) as context_manager:
            commonops.raise_if_inside_application_workspace()

        self.assertEqual(
            'This directory is already initialized with an application workspace.',
            str(context_manager.exception)
        )

    def test_raise_if_inside_application_workspace__directory_is_not_eb_inited(self):
        shutil.rmtree('.elasticbeanstalk')
        commonops.raise_if_inside_application_workspace()

    def test_raise_if_inside_application_workspace__directory_is_inited_with_platform_workspace(self):
        shutil.rmtree('.elasticbeanstalk')
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            'php',
            workspace_type='Platform'
        )
        commonops.raise_if_inside_application_workspace()

    def test_raise_if_inside_platform_workspace(self):
        shutil.rmtree('.elasticbeanstalk')
        fileoperations.create_config_file(
            'my-platform',
            'us-west-2',
            'php',
            workspace_type='Platform'
        )
        with self.assertRaises(EnvironmentError) as context_manager:
            commonops.raise_if_inside_platform_workspace()

        self.assertEqual(
            'This directory is already initialized with a platform workspace.',
            str(context_manager.exception)
        )

    def test_raise_if_inside_platform_workspace__directory_is_not_eb_inited(self):
        shutil.rmtree('.elasticbeanstalk')
        commonops.raise_if_inside_platform_workspace()

    def test_raise_if_inside_platform_workspace__directory_is_inited_with_application_workspace(self):
        commonops.raise_if_inside_platform_workspace()
