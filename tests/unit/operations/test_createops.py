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

from ebcli.core import io
from ebcli.lib import cloudformation, elasticbeanstalk
from ebcli.objects.environment import Environment
from ebcli.objects.requests import CreateEnvironmentRequest
from ebcli.objects.solutionstack import SolutionStack
from ebcli.objects.buildconfiguration import BuildConfiguration
from ebcli.objects.exceptions import NotFoundError
from ebcli.operations import createops
from ebcli.operations.tagops.taglist import TagList


class TestCreateOps(unittest.TestCase):
    @mock.patch('ebcli.operations.createops.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.operations.createops.cloudformation.wait_until_stack_exists')
    @mock.patch('ebcli.operations.createops.cloudformation.get_template')
    def test_retrieve_application_version_url__successfully_returns_sample_app_url(
            self,
            get_template_mock,
            wait_until_stack_exists_mock,
            get_environment_mock
    ):
        get_template_response = {
            "TemplateBody": {
                "Parameters": {
                    "AppSource": {
                        "NoEcho": "true",
                        "Type": "String",
                        "Description": "The url of the application source.",
                        "Default": "http://sample-app-location/python-sample.zip"
                    },
                },
                "Description": "AWS Elastic Beanstalk environment (Name: 'my_env_name'  Id: 'my_env_id')",
            }
        }
        get_environment_mock.return_value = Environment(name='my_env_name', id='my_env_id')
        get_template_mock.return_value = get_template_response

        self.assertEqual(
            "http://sample-app-location/python-sample.zip",
            createops.retrieve_application_version_url('my_env_name')
        )

    @mock.patch('ebcli.operations.createops.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.operations.createops.cloudformation.wait_until_stack_exists')
    @mock.patch('ebcli.operations.createops.cloudformation.get_template')
    def test_retrieve_application_version_url__empty_response__raises_not_found_error(
            self,
            get_template_mock,
            wait_until_stack_exists_mock,
            get_environment_mock
    ):
        get_template_response = {}

        io._log_warning = io.log_warning
        io.log_warning = mock.MagicMock()

        get_environment_mock.return_value = Environment(name='my_env_name', id='my_env_id')
        get_template_mock.return_value = get_template_response


    @mock.patch('ebcli.operations.createops.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.operations.createops.cloudformation.wait_until_stack_exists')
    @mock.patch('ebcli.operations.createops.cloudformation.get_template')
    def test_retrieve_application_version_url__app_version_url_not_found_in_app_source__raises_not_found_error(
            self,
            get_template_mock,
            wait_until_stack_exists_mock,
            get_environment_mock
    ):
        io._log_warning = io.log_warning
        io.log_warning = mock.MagicMock()

        get_template_response = {
            "TemplateBody": {
                "Parameters": {
                    "AppSource": {
                        "NoEcho": "true",
                        "Type": "String",
                        "Description": "The url of the application source."
                    }
                },
                "Description": "AWS Elastic Beanstalk environment (Name: 'my_env_name'  Id: 'my_env_id')",
            }
        }

        get_environment_mock.return_value = Environment(name='my_env_name', id='my_env_id')
        get_template_mock.return_value = get_template_response

        createops.retrieve_application_version_url('my_env_name')

        io.log_warning.assert_called_with('Cannot find app source for environment. ')

        io.log_warning = io._log_warning

    @mock.patch('ebcli.operations.createops.commonops.create_default_instance_profile')
    @mock.patch('ebcli.operations.createops.get_service_role')
    def test_resolve_roles__non_interactive_mode__request_does_not_contain_profile__existing_role_retrieved_from_service(
            self,
            get_service_role_mock,
            create_default_instance_profile_mock
    ):
        create_default_instance_profile_mock.return_value = 'default-profile'
        get_service_role_mock.return_value = 'service-role'
        env_request = CreateEnvironmentRequest(
            app_name='my-application',
            env_name='environment-1',
            cname='cname-1',
            platform=SolutionStack('64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)'),
            elb_type='network',
            group_name='dev',
        )

        createops.resolve_roles(env_request, False)
        create_default_instance_profile_mock.assert_called_once_with()
        self.assertEqual(
            'service-role',
            env_request.service_role
        )

    @mock.patch('ebcli.operations.createops.commonops.create_default_instance_profile')
    @mock.patch('ebcli.operations.createops.get_service_role')
    def test_resolve_roles__non_interactive_mode__profile_passed_is_default_role_name__existing_role_retrieved_from_service(
            self,
            get_service_role_mock,
            create_default_instance_profile_mock
    ):
        create_default_instance_profile_mock.return_value = 'default-profile'
        get_service_role_mock.return_value = 'service-role'
        env_request = CreateEnvironmentRequest(
            app_name='my-application',
            env_name='environment-1',
            cname='cname-1',
            platform=SolutionStack('64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)'),
            elb_type='network',
            group_name='dev',
            instance_profile='aws-elasticbeanstalk-ec2-role'
        )

        createops.resolve_roles(env_request, False)
        create_default_instance_profile_mock.assert_called_once_with()

    @mock.patch('ebcli.operations.createops.commonops.create_default_instance_profile')
    @mock.patch('ebcli.operations.createops.get_service_role')
    def test_resolve_roles__non_interactive_mode__profile_passed_is_other_role_name_other_than_service_role__existing_role_retrieved_from_service(
            self,
            get_service_role_mock,
            create_default_instance_profile_mock
    ):
        get_service_role_mock.return_value = 'service-role'
        env_request = CreateEnvironmentRequest(
            app_name='my-application',
            env_name='environment-1',
            cname='cname-1',
            platform=SolutionStack('64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)'),
            elb_type='network',
            group_name='dev',
            instance_profile='developer'
        )

        createops.resolve_roles(env_request, False)

        create_default_instance_profile_mock.assert_not_called()

    @mock.patch('ebcli.operations.createops.commonops.create_default_instance_profile')
    @mock.patch('ebcli.operations.createops.get_service_role')
    def test_resolve_roles__non_interactive_mode__no_healthd_support_for_platform__service_role_cannot_determined(
            self,
            get_service_role_mock,
            create_default_instance_profile_mock
    ):
        env_request = CreateEnvironmentRequest(
            app_name='my-application',
            env_name='environment-1',
            cname='cname-1',
            platform=SolutionStack('64bit Windows Server Core 2016 v1.2.0 running IIS 10.0'),
            elb_type='network',
            group_name='dev',
            instance_profile='developer'
        )

        createops.resolve_roles(env_request, False)

        get_service_role_mock.assert_not_called()
        create_default_instance_profile_mock.assert_not_called()
        self.assertIsNone(env_request.service_role)

    @mock.patch('ebcli.operations.createops.commonops.create_default_instance_profile')
    @mock.patch('ebcli.operations.createops.get_service_role')
    def test_resolve_roles__non_interactive_mode__no_healthd_support_for_platform__service_role_already_assigned_to_create_environment_request(
            self,
            get_service_role_mock,
            create_default_instance_profile_mock
    ):
        env_request = CreateEnvironmentRequest(
            app_name='my-application',
            env_name='environment-1',
            cname='cname-1',
            platform=SolutionStack('64bit Windows Server Core 2016 v1.2.0 running IIS 10.0'),
            elb_type='network',
            group_name='dev',
            instance_profile='developer',
            service_role='aws-elasticbeanstalk-service-role'
        )

        createops.resolve_roles(env_request, False)

        get_service_role_mock.assert_not_called()
        create_default_instance_profile_mock.assert_not_called()
        self.assertEqual(
            'aws-elasticbeanstalk-service-role',
            env_request.service_role
        )

    @mock.patch('ebcli.operations.createops.commonops.create_default_instance_profile')
    @mock.patch('ebcli.operations.createops.get_service_role')
    @mock.patch('ebcli.operations.createops.create_default_service_role')
    @mock.patch('ebcli.operations.createops.io.get_input')
    @mock.patch('ebcli.operations.createops.iam.get_managed_policy_document')
    def test_resolve_roles__interactive_mode__service_role_could_not_be_found__simulate_customer_viewing_policies(
            self,
            get_managed_policy_document_mock,
            get_input_mock,
            create_default_service_role_mock,
            get_service_role_mock,
            create_default_instance_profile_mock
    ):
        get_managed_policy_document_mock.side_effect = [
            {
                "PolicyVersion": {
                    "Document": {}
                }
            },
            {
                "PolicyVersion": {
                    "Document": {}
                }
            },
        ]
        get_input_mock.side_effect = [
            'view',
            '\n'
        ]
        create_default_instance_profile_mock.return_value = 'default-profile'
        get_service_role_mock.return_value = None
        create_default_service_role_mock.return_value = 'aws-elasticbeanstalk-service-role'
        env_request = CreateEnvironmentRequest(
            app_name='my-application',
            env_name='environment-1',
            cname='cname-1',
            platform=SolutionStack('64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)'),
            elb_type='network',
            group_name='dev',
        )

        createops.resolve_roles(env_request, True)
        self.assertEqual(
            'aws-elasticbeanstalk-service-role',
            env_request.service_role
        )

    @mock.patch('ebcli.operations.createops.commonops.create_default_instance_profile')
    @mock.patch('ebcli.operations.createops.get_service_role')
    @mock.patch('ebcli.operations.createops.create_default_service_role')
    @mock.patch('ebcli.operations.createops.io.get_input')
    @mock.patch('ebcli.operations.createops.iam.get_managed_policy_document')
    def test_resolve_roles__interactive_mode__service_role_could_not_be_found__customer_enters_wrong_input__profile_view_not_shown(
            self,
            get_managed_policy_document_mock,
            get_input_mock,
            create_default_service_role_mock,
            get_service_role_mock,
            create_default_instance_profile_mock
    ):
        get_input_mock.side_effect = ['show']
        create_default_instance_profile_mock.return_value = 'default-profile'
        get_service_role_mock.return_value = None
        create_default_service_role_mock.return_value = 'aws-elasticbeanstalk-service-role'
        env_request = CreateEnvironmentRequest(
            app_name='my-application',
            env_name='environment-1',
            cname='cname-1',
            platform=SolutionStack('64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)'),
            elb_type='network',
            group_name='dev',
        )

        createops.resolve_roles(env_request, True)

        get_managed_policy_document_mock.assert_not_called()
        self.assertEqual(
            'aws-elasticbeanstalk-service-role',
            env_request.service_role
        )

    @mock.patch('ebcli.operations.createops._get_default_service_trust_document')
    @mock.patch('ebcli.operations.createops.iam.create_role_with_policy')
    def test_create_default_service_role(
            self,
            create_role_with_policy_mock,
            _get_default_service_trust_document_mock
    ):
        trust_document_mock = mock.MagicMock()
        _get_default_service_trust_document_mock.return_value = trust_document_mock

        self.assertEqual(
            'aws-elasticbeanstalk-service-role',
            createops.create_default_service_role()
        )

        create_role_with_policy_mock.assert_called_once_with(
            'aws-elasticbeanstalk-service-role',
            trust_document_mock,
            [
                'arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkEnhancedHealth',
                'arn:aws:iam::aws:policy/AWSElasticBeanstalkManagedUpdatesCustomerRolePolicy'
            ]
        )

    @mock.patch('ebcli.operations.createops._get_default_service_trust_document')
    @mock.patch('ebcli.operations.createops.iam.create_role_with_policy')
    def test_create_default_service_role__not_authorized_to_create_role_with_required_policies(
            self,
            create_role_with_policy_mock,
            _get_default_service_trust_document_mock
    ):
        trust_document_mock = mock.MagicMock()
        _get_default_service_trust_document_mock.return_value = trust_document_mock
        create_role_with_policy_mock.side_effect = createops.NotAuthorizedError

        with self.assertRaises(createops.NotAuthorizedError) as context_manager:
            createops.create_default_service_role()

        self.assertEqual(
            """No permissions to create a role. Create an IAM role called "aws-elasticbeanstalk-service-role" with appropriate permissions to continue, or specify a role with --service-role.
See http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/concepts-roles.html for more info.
Actual error: """,
            str(context_manager.exception)
        )
        create_role_with_policy_mock.assert_called_once_with(
            'aws-elasticbeanstalk-service-role',
            trust_document_mock,
            [
                'arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkEnhancedHealth',
                'arn:aws:iam::aws:policy/AWSElasticBeanstalkManagedUpdatesCustomerRolePolicy'
            ]
        )

    @mock.patch('ebcli.operations.createops.iam.get_role_names')
    def test_get_service_role__default_service_role_is_absent__returns_none(
            self,
            get_role_names_mock
    ):
        get_role_names_mock.return_value = [
            'my-iam-role-1',
            'my-iam-role-2'
        ]

        self.assertIsNone(createops.get_service_role())

    @mock.patch('ebcli.operations.createops.iam.get_role_names')
    def test_get_service_role__default_service_role_found__returns_default_service_role(
            self,
            get_role_names_mock
    ):
        get_role_names_mock.return_value = [
            'my-iam-role-1',
            'my-iam-role-2',
            'aws-elasticbeanstalk-service-role'
        ]

        self.assertEqual(
            'aws-elasticbeanstalk-service-role',
            createops.get_service_role()
        )

    @mock.patch('ebcli.operations.createops.iam.get_role_names')
    def test_get_service_role__fails_to_get_iam_role__assumes_default_service_role_is_found_and_returns_it(
            self,
            get_role_names_mock
    ):
        get_role_names_mock.side_effect = createops.NotAuthorizedError

        self.assertEqual(
            'aws-elasticbeanstalk-service-role',
            createops.get_service_role()
        )

    @mock.patch('ebcli.operations.createops.utils.get_data_from_url')
    @mock.patch('ebcli.operations.createops.fileoperations.write_to_data_file')
    def test_download_application_version(
            self,
            write_to_data_file_mock,
            get_data_from_url_mock
    ):
        get_data_from_url_mock.return_value = 'data'

        createops.download_application_version(
            'http://my-app.com',
            'path/to/zip/file.zip'
        )

        get_data_from_url_mock.assert_called_once_with(
            'http://my-app.com',
            timeout=30
        )
        write_to_data_file_mock.assert_called_once_with(
            'path/to/zip/file.zip',
            'data'
        )

    @mock.patch('ebcli.operations.createops.retrieve_application_version_url')
    @mock.patch('ebcli.operations.createops.download_application_version')
    @mock.patch('ebcli.operations.createops.ZipFile')
    @mock.patch('ebcli.operations.createops.os.remove')
    @mock.patch('ebcli.operations.createops.io.echo')
    def test_download_and_extract_sample_app__successfully_downloads_and_extracts(
            self,
            echo_mock,
            remove_mock,
            ZipFile_mock,
            download_application_version_mock,
            retrieve_application_version_url_mock
    ):
        zipfile_mock = mock.MagicMock()
        ZipFile_mock.return_value = zipfile_mock
        retrieve_application_version_url_mock.return_value = 'http://app-server.com'

        createops.download_and_extract_sample_app('my-environment')

        retrieve_application_version_url_mock.assert_called_once_with('my-environment')
        download_application_version_mock.assert_called_once_with(
            'http://app-server.com',
            '.elasticbeanstalk/.sample_app_download.zip'
        )
        ZipFile_mock.assert_called_once_with(
            '.elasticbeanstalk/.sample_app_download.zip',
            'r',
            allowZip64=True
        )
        zipfile_mock.extractallassert_called_once_with()
        remove_mock.assert_called_once_with('.elasticbeanstalk/.sample_app_download.zip')
        echo_mock.assert_has_calls(
            [
                mock.call('INFO: Downloading sample application to the current directory.'),
                mock.call('INFO: Download complete.')
            ]
        )

    @mock.patch('ebcli.operations.createops.retrieve_application_version_url')
    @mock.patch('ebcli.operations.createops.download_application_version')
    @mock.patch('ebcli.operations.createops.ZipFile')
    @mock.patch('ebcli.operations.createops.os.remove')
    @mock.patch('ebcli.operations.createops.io.echo')
    @mock.patch('ebcli.operations.createops.io.log_warning')
    def test_download_and_extract_sample_app__lacks_permissions_to_query_cloudformation(
            self,
            lgo_warning_mock,
            echo_mock,
            remove_mock,
            ZipFile_mock,
            download_application_version_mock,
            retrieve_application_version_url_mock
    ):
        retrieve_application_version_url_mock.return_value = 'http://app-server.com'
        download_application_version_mock.side_effect = createops.NotAuthorizedError

        createops.download_and_extract_sample_app('my-environment')

        lgo_warning_mock.assert_called_once_with(' Continuing environment creation.')
        retrieve_application_version_url_mock.assert_called_once_with('my-environment')
        download_application_version_mock.assert_called_once_with(
            'http://app-server.com',
            '.elasticbeanstalk/.sample_app_download.zip'
        )
        ZipFile_mock.assert_not_called()
        remove_mock.assert_not_called()
        echo_mock.assert_called_once_with(
            'INFO: Downloading sample application to the current directory.'
        )

    @mock.patch('ebcli.operations.createops.heuristics.directory_is_empty')
    def test_should_download_sample_app__directory_is_not_empty(
            self,
            directory_id_empty_mock
    ):
        directory_id_empty_mock.return_value = False

        self.assertFalse(createops.should_download_sample_app())

    @mock.patch('ebcli.operations.createops.heuristics.directory_is_empty')
    @mock.patch('ebcli.operations.createops.io.echo')
    @mock.patch('ebcli.operations.createops.io.get_boolean_response')
    def test_should_download_sample_app(
            self,
            get_boolean_response_mock,
            echo_mock,
            directory_is_empty_mock
    ):
        directory_is_empty_mock.return_value = True

        get_boolean_response_mock.return_value = True
        self.assertTrue(createops.should_download_sample_app())

        get_boolean_response_mock.return_value = False
        self.assertFalse(createops.should_download_sample_app())

    @mock.patch('ebcli.operations.createops.statusops.alert_environment_status')
    @mock.patch('ebcli.operations.createops.resolve_roles')
    @mock.patch('ebcli.operations.createops.fileoperations.get_build_configuration')
    @mock.patch('ebcli.operations.createops.fileoperations.build_spec_exists')
    @mock.patch('ebcli.operations.createops.gitops.git_management_enabled')
    @mock.patch('ebcli.operations.createops.io.log_info')
    @mock.patch('ebcli.operations.createops.create_env')
    @mock.patch('ebcli.operations.createops.commonops.get_current_branch_environment')
    @mock.patch('ebcli.operations.createops.commonops.wait_for_success_events')
    @mock.patch('ebcli.operations.createops.commonops.upload_keypair_if_needed')
    @mock.patch('ebcli.operations.createops.commonops.create_app_version')
    @mock.patch('ebcli.operations.createops.buildspecops.stream_build_configuration_app_version_creation')
    @mock.patch('ebcli.operations.createops.download_and_extract_sample_app')
    def test_make_new_env_from_code_in_directory__non_interactive_mode__buildspec_present__using_application_code_in_directory_to_create_app_version(
            self,
            download_and_extract_sample_app_mock,
            stream_build_configuration_app_version_creation_mock,
            create_app_version_mock,
            upload_keypair_if_needed_mock,
            wait_for_success_events_mock,
            get_current_branch_environment_mock,
            create_env_mock,
            log_info_mock,
            git_management_enabled_mock,
            build_spec_exists_mock,
            get_build_configuration_mock,
            resolve_roles_mock,
            alert_environment_status_mock,
    ):
        resolve_roles_mock.side_effect = None
        build_spec_exists_mock.return_value = True
        build_config = BuildConfiguration(
            compute_type='t2.micro',
            image='java-ami',
            service_role='codebuild-service-role',
            timeout=10
        )
        get_build_configuration_mock.return_value = build_config
        git_management_enabled_mock.return_value = False
        create_environment_result_mock = mock.MagicMock()
        create_environment_result_mock.name = 'result'
        create_env_mock.return_value = (create_environment_result_mock, 'request-id')
        get_current_branch_environment_mock.return_value = 'environment-1'
        env_request = CreateEnvironmentRequest(
            app_name='my-application',
            env_name='environment-1',
            cname='cname-1',
            platform=SolutionStack('64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)'),
            elb_type='network',
            group_name='dev',
            key_name='aws-eb-us-west-2'
        )
        create_app_version_mock.return_value = 'version-label-1'

        createops.make_new_env(env_request, interactive=True)

        stream_build_configuration_app_version_creation_mock.assert_called_once_with(
            'my-application',
            'version-label-1',
            build_config
        )
        create_environment_result_mock.print_env_details.assert_called_once_with(
            createops.io.echo,
            createops.elasticbeanstalk.get_environments,
            createops.elasticbeanstalk.get_environment_resources,
            health=False
        )
        alert_environment_status_mock.assert_called_once_with(create_environment_result_mock)
        wait_for_success_events_mock.assert_called_once_with('request-id', timeout_in_minutes=None)
        create_env_mock.assert_called_once_with(env_request, interactive=True)
        upload_keypair_if_needed_mock.assert_called_once_with('aws-eb-us-west-2')
        create_app_version_mock.assert_called_once_with(
            'my-application',
            build_config=build_config,
            process=False
        )
        log_info_mock.assert_has_calls(
            [
                mock.call('Creating new application version using project code'),
                mock.call('Creating new environment')
            ]
        )
        download_and_extract_sample_app_mock.assert_not_called()

    @mock.patch('ebcli.operations.createops.statusops.alert_environment_status')
    @mock.patch('ebcli.operations.createops.resolve_roles')
    @mock.patch('ebcli.operations.createops.fileoperations.build_spec_exists')
    @mock.patch('ebcli.operations.createops.gitops.git_management_enabled')
    @mock.patch('ebcli.operations.createops.io.log_info')
    @mock.patch('ebcli.operations.createops.create_env')
    @mock.patch('ebcli.operations.createops.commonops.get_current_branch_environment')
    @mock.patch('ebcli.operations.createops.commonops.wait_for_success_events')
    @mock.patch('ebcli.operations.createops.commonops.upload_keypair_if_needed')
    @mock.patch('ebcli.operations.createops.commonops.create_app_version')
    @mock.patch('ebcli.operations.createops.commonops.wait_for_processed_app_versions')
    def test_make_new_env_from_code_in_directory__process_app_version(
            self,
            wait_for_processed_app_versions_mock,
            create_app_version_mock,
            upload_keypair_if_needed_mock,
            wait_for_success_events_mock,
            get_current_branch_environment_mock,
            create_env_mock,
            log_info_mock,
            git_management_enabled_mock,
            build_spec_exists_mock,
            resolve_roles_mock,
            alert_environment_status_mock,
    ):
        resolve_roles_mock.side_effect = None
        build_spec_exists_mock.return_value = False
        git_management_enabled_mock.return_value = False
        create_environment_result_mock = mock.MagicMock()
        create_environment_result_mock.name = 'result'
        create_env_mock.return_value = (create_environment_result_mock, 'request-id')
        get_current_branch_environment_mock.return_value = 'environment-1'
        wait_for_processed_app_versions_mock.return_value = True
        env_request = CreateEnvironmentRequest(
            app_name='my-application',
            env_name='environment-1',
            cname='cname-1',
            platform=SolutionStack('64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)'),
            elb_type='network',
            group_name='dev',
            key_name='aws-eb-us-west-2'
        )
        create_app_version_mock.return_value = 'version-label-1'

        createops.make_new_env(env_request, process_app_version=True, timeout=10)

        create_environment_result_mock.print_env_details.assert_called_once_with(
            createops.io.echo,
            createops.elasticbeanstalk.get_environments,
            createops.elasticbeanstalk.get_environment_resources,
            health=False
        )
        alert_environment_status_mock.assert_called_once_with(create_environment_result_mock)
        wait_for_success_events_mock.assert_called_once_with('request-id', timeout_in_minutes=10)
        create_env_mock.assert_called_once_with(env_request, interactive=True)
        upload_keypair_if_needed_mock.assert_called_once_with('aws-eb-us-west-2')
        wait_for_processed_app_versions_mock.assert_called_once_with(
            'my-application',
            ['version-label-1'],
            timeout=10
        )
        create_app_version_mock.assert_called_once_with(
            'my-application',
            build_config=None,
            process=True
        )
        log_info_mock.assert_has_calls(
            [
                mock.call('Creating new application version using project code'),
                mock.call('Creating new environment')
            ]
        )

    @mock.patch('ebcli.operations.createops.statusops.alert_environment_status')
    @mock.patch('ebcli.operations.createops.resolve_roles')
    @mock.patch('ebcli.operations.createops.fileoperations.build_spec_exists')
    @mock.patch('ebcli.operations.createops.gitops.git_management_enabled')
    @mock.patch('ebcli.operations.createops.io.log_info')
    @mock.patch('ebcli.operations.createops.create_env')
    @mock.patch('ebcli.operations.createops.commonops.get_current_branch_environment')
    @mock.patch('ebcli.operations.createops.commonops.wait_for_success_events')
    @mock.patch('ebcli.operations.createops.commonops.upload_keypair_if_needed')
    @mock.patch('ebcli.operations.createops.commonops.create_app_version')
    @mock.patch('ebcli.operations.createops.commonops.wait_for_processed_app_versions')
    def test_make_new_env_from_code_in_directory__process_app_version_failed(
            self,
            wait_for_processed_app_versions_mock,
            create_app_version_mock,
            upload_keypair_if_needed_mock,
            wait_for_success_events_mock,
            get_current_branch_environment_mock,
            create_env_mock,
            log_info_mock,
            git_management_enabled_mock,
            build_spec_exists_mock,
            resolve_roles_mock,
            alert_environment_status_mock,
    ):
        resolve_roles_mock.side_effect = None
        build_spec_exists_mock.return_value = False
        git_management_enabled_mock.return_value = False
        create_environment_result_mock = mock.MagicMock()
        create_environment_result_mock.name = 'result'
        create_env_mock.return_value = (create_environment_result_mock, 'request-id')
        get_current_branch_environment_mock.return_value = 'environment-1'
        wait_for_processed_app_versions_mock.return_value = False
        env_request = CreateEnvironmentRequest(
            app_name='my-application',
            env_name='environment-1',
            cname='cname-1',
            platform=SolutionStack('64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)'),
            elb_type='network',
            group_name='dev',
            key_name='aws-eb-us-west-2'
        )
        create_app_version_mock.return_value = 'version-label-1'

        createops.make_new_env(env_request, process_app_version=True, timeout=5)

        wait_for_processed_app_versions_mock.assert_called_once_with(
            'my-application',
            ['version-label-1'],
            timeout=5
        )
        create_app_version_mock.assert_called_once_with(
            'my-application',
            build_config=None,
            process=True
        )
        log_info_mock.assert_has_calls(
            [
                mock.call('Creating new application version using project code'),
            ]
        )
        alert_environment_status_mock.assert_not_called()
        create_environment_result_mock.print_env_details.assert_not_called()
        wait_for_success_events_mock.assert_not_called()
        create_env_mock.assert_not_called()
        upload_keypair_if_needed_mock.assert_not_called()

    @mock.patch('ebcli.operations.createops.statusops.alert_environment_status')
    @mock.patch('ebcli.operations.createops.resolve_roles')
    @mock.patch('ebcli.operations.createops.fileoperations.build_spec_exists')
    @mock.patch('ebcli.operations.createops.gitops.git_management_enabled')
    @mock.patch('ebcli.operations.createops.io.log_info')
    @mock.patch('ebcli.operations.createops.io.echo')
    @mock.patch('ebcli.operations.createops.commonops.create_codecommit_app_version')
    @mock.patch('ebcli.operations.createops.create_env')
    @mock.patch('ebcli.operations.createops.commonops.get_current_branch_environment')
    @mock.patch('ebcli.operations.createops.commonops.wait_for_success_events')
    @mock.patch('ebcli.operations.createops.commonops.upload_keypair_if_needed')
    @mock.patch('ebcli.operations.createops.commonops.create_app_version')
    @mock.patch('ebcli.operations.createops.commonops.wait_for_processed_app_versions')
    def test_make_new_env_from_code_in_directory__use_codecommit__process_app_version(
            self,
            wait_for_processed_app_versions_mock,
            create_app_version_mock,
            upload_keypair_if_needed_mock,
            wait_for_success_events_mock,
            get_current_branch_environment_mock,
            create_env_mock,
            create_codecommit_app_version_mock,
            echo_mock,
            log_info_mock,
            git_management_enabled_mock,
            build_spec_exists_mock,
            resolve_roles_mock,
            alert_environment_status_mock,
    ):
        build_spec_exists_mock.return_value = False
        git_management_enabled_mock.return_value = True
        create_environment_result_mock = mock.MagicMock()
        create_environment_result_mock.name = 'result'
        create_env_mock.return_value = (create_environment_result_mock, 'request-id')
        get_current_branch_environment_mock.return_value = 'environment-1'
        env_request = CreateEnvironmentRequest(
            app_name='my-application',
            env_name='environment-1',
            cname='cname-1',
            platform=SolutionStack('64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)'),
            elb_type='network',
            group_name='dev',
            key_name='aws-eb-us-west-2'
        )
        create_app_version_mock.return_value = 'version-label-1'
        wait_for_processed_app_versions_mock.return_value = True
        create_codecommit_app_version_mock.return_value = 'version-label-1'

        createops.make_new_env(env_request, process_app_version=True)

        create_codecommit_app_version_mock.assert_called_once_with(
            'my-application',
            build_config=None,
            process=True
        )
        create_environment_result_mock.print_env_details.assert_called_once_with(
            createops.io.echo,
            createops.elasticbeanstalk.get_environments,
            createops.elasticbeanstalk.get_environment_resources,
            health=False
        )
        alert_environment_status_mock.assert_called_once_with(create_environment_result_mock)
        wait_for_success_events_mock.assert_called_once_with('request-id', timeout_in_minutes=None)
        create_env_mock.assert_called_once_with(env_request, interactive=True)
        upload_keypair_if_needed_mock.assert_called_once_with('aws-eb-us-west-2')
        wait_for_processed_app_versions_mock.assert_called_once_with(
            'my-application',
            ['version-label-1'],
            timeout=5
        )
        log_info_mock.assert_has_calls(
            [
                mock.call('Creating new application version using CodeCommit'),
                mock.call('Creating new environment')
            ]
        )
        echo_mock.assert_has_calls(
            [
                mock.call('Starting environment deployment via CodeCommit'),
                mock.call('Printing Status:')
            ]
        )

    @mock.patch('ebcli.operations.createops.statusops.alert_environment_status')
    @mock.patch('ebcli.operations.createops.resolve_roles')
    @mock.patch('ebcli.operations.createops.fileoperations.build_spec_exists')
    @mock.patch('ebcli.operations.createops.gitops.git_management_enabled')
    @mock.patch('ebcli.operations.createops.io.log_info')
    @mock.patch('ebcli.operations.createops.io.echo')
    @mock.patch('ebcli.operations.createops.commonops.create_app_version_from_source')
    @mock.patch('ebcli.operations.createops.create_env')
    @mock.patch('ebcli.operations.createops.commonops.get_current_branch_environment')
    @mock.patch('ebcli.operations.createops.commonops.wait_for_success_events')
    @mock.patch('ebcli.operations.createops.commonops.upload_keypair_if_needed')
    @mock.patch('ebcli.operations.createops.commonops.create_app_version')
    @mock.patch('ebcli.operations.createops.commonops.wait_for_processed_app_versions')
    def test_make_new_env_from_code_in_directory__use_source__process_app_version(
            self,
            wait_for_processed_app_versions_mock,
            create_app_version_mock,
            upload_keypair_if_needed_mock,
            wait_for_success_events_mock,
            get_current_branch_environment_mock,
            create_env_mock,
            create_app_version_from_source_mock,
            echo_mock,
            log_info_mock,
            git_management_enabled_mock,
            build_spec_exists_mock,
            resolve_roles_mock,
            alert_environment_status_mock
    ):
        build_spec_exists_mock.return_value = False
        git_management_enabled_mock.return_value = False
        create_environment_result_mock = mock.MagicMock()
        create_environment_result_mock.name = 'result'
        create_env_mock.return_value = (create_environment_result_mock, 'request-id')
        get_current_branch_environment_mock.return_value = 'environment-1'
        env_request = CreateEnvironmentRequest(
            app_name='my-application',
            env_name='environment-1',
            cname='cname-1',
            platform=SolutionStack('64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)'),
            elb_type='network',
            group_name='dev',
            key_name='aws-eb-us-west-2'
        )
        create_app_version_mock.return_value = 'version-label-1'
        wait_for_processed_app_versions_mock.return_value = True
        create_app_version_from_source_mock.return_value = 'version-label-1'

        createops.make_new_env(
            env_request,
            source='codecommit/my-repository/my-branch'
        )

        create_app_version_from_source_mock.assert_called_once_with(
            'my-application',
            'codecommit/my-repository/my-branch',
            build_config=None,
            label=None,
            process=False
        )
        create_environment_result_mock.print_env_details.assert_called_once_with(
            createops.io.echo,
            createops.elasticbeanstalk.get_environments,
            createops.elasticbeanstalk.get_environment_resources,
            health=False
        )
        alert_environment_status_mock.assert_called_once_with(create_environment_result_mock)
        wait_for_success_events_mock.assert_called_once_with('request-id', timeout_in_minutes=None)
        create_env_mock.assert_called_once_with(env_request, interactive=True)
        upload_keypair_if_needed_mock.assert_called_once_with('aws-eb-us-west-2')
        wait_for_processed_app_versions_mock.assert_called_once_with(
            'my-application',
            ['version-label-1'],
            timeout=5
        )
        log_info_mock.assert_has_calls(
            [
                mock.call('Creating new application version using remote source'),
                mock.call('Creating new environment')
            ]
        )
        echo_mock.assert_has_calls(
            [
                mock.call('Starting environment deployment via remote source'),
                mock.call('Printing Status:')
            ]
        )

    @mock.patch('ebcli.operations.createops.statusops.alert_environment_status')
    @mock.patch('ebcli.operations.createops.resolve_roles')
    @mock.patch('ebcli.operations.createops.fileoperations.build_spec_exists')
    @mock.patch('ebcli.operations.createops.gitops.git_management_enabled')
    @mock.patch('ebcli.operations.createops.io.log_info')
    @mock.patch('ebcli.operations.createops.io.echo')
    @mock.patch('ebcli.operations.createops.create_env')
    @mock.patch('ebcli.operations.createops.commonops.get_current_branch_environment')
    @mock.patch('ebcli.operations.createops.commonops.wait_for_success_events')
    @mock.patch('ebcli.operations.createops.commonops.upload_keypair_if_needed')
    @mock.patch('ebcli.operations.createops.commonops.create_dummy_app_version')
    def test_make_new_env_from_code_in_directory__use_sample_application(
            self,
            create_dummy_app_version_mock,
            upload_keypair_if_needed_mock,
            wait_for_success_events_mock,
            get_current_branch_environment_mock,
            create_env_mock,
            echo_mock,
            log_info_mock,
            git_management_enabled_mock,
            build_spec_exists_mock,
            resolve_roles_mock,
            alert_environment_status_mock,
    ):
        build_spec_exists_mock.return_value = False
        git_management_enabled_mock.return_value = False
        create_environment_result_mock = mock.MagicMock()
        create_environment_result_mock.name = 'result'
        create_env_mock.return_value = (create_environment_result_mock, 'request-id')
        get_current_branch_environment_mock.return_value = 'environment-1'
        env_request = CreateEnvironmentRequest(
            app_name='my-application',
            env_name='environment-1',
            cname='cname-1',
            platform=SolutionStack('64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)'),
            elb_type='network',
            group_name='dev',
            key_name='aws-eb-us-west-2',
            sample_application=True
        )

        createops.make_new_env(env_request)

        create_environment_result_mock.print_env_details.assert_called_once_with(
            createops.io.echo,
            createops.elasticbeanstalk.get_environments,
            createops.elasticbeanstalk.get_environment_resources,
            health=False
        )
        alert_environment_status_mock.assert_called_once_with(create_environment_result_mock)
        wait_for_success_events_mock.assert_called_once_with('request-id', timeout_in_minutes=None)
        create_env_mock.assert_called_once_with(env_request, interactive=True)
        upload_keypair_if_needed_mock.assert_called_once_with('aws-eb-us-west-2')
        create_dummy_app_version_mock.assert_called_once_with('my-application')
        log_info_mock.assert_has_calls(
            [
                mock.call('Creating new environment')
            ]
        )
        echo_mock.assert_has_calls(
            [
                mock.call('Printing Status:')
            ]
        )
