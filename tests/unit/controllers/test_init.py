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
import os

import shutil

import unittest
from pytest_socket import disable_socket, enable_socket
import mock

from ebcli.controllers import initialize
from ebcli.core import fileoperations
from ebcli.core.ebcore import EB
from ebcli.objects.exceptions import NotInitializedError, NoRegionError, ServiceError, InvalidProfileError
from ebcli.objects.solutionstack import SolutionStack
from ebcli.objects.platform import PlatformVersion
from ebcli.objects.buildconfiguration import BuildConfiguration


class TestInit(unittest.TestCase):
    solution = SolutionStack('64bit Amazon Linux 2014.03 v1.0.6 running PHP 5.5')
    app_name = 'ebcli-intTest-app'

    def setUp(self):
        disable_socket()
        self.root_dir = os.getcwd()
        if os.path.exists('testDir'):
            shutil.rmtree('testDir')
        os.mkdir('testDir')
        os.chdir('testDir')

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

        enable_socket()

    @mock.patch('ebcli.controllers.initialize.SourceControl.Git')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk.get_application_names')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops')
    @mock.patch('ebcli.controllers.initialize.sshops')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk')
    @mock.patch('ebcli.controllers.initialize.io.get_input')
    @mock.patch('ebcli.controllers.initialize.set_region_for_application')
    def test_init__interactive_mode(
            self,
            set_region_for_application_mock,
            get_input_mock,
            elasticbeanstalk_mock,
            commonops_mock,
            initops_mock,
            sshops_mock,
            solution_stack_ops_mock,
            get_application_names_mock,
            sourcecontrol_mock,
            git_mock
    ):
        get_application_names_mock.get_application_names.return_value = list()
        initops_mock.credentials_are_valid.return_value = True
        solution_stack_ops_mock.get_solution_stack_from_customer.return_value = self.solution
        sshops_mock.prompt_for_ec2_keyname.return_value = 'test'
        commonops_mock.get_current_branch_environment.side_effect = NotInitializedError
        elasticbeanstalk_mock.application_exist.return_value = False
        commonops_mock.create_app.return_value = None, None
        commonops_mock.get_default_keyname.return_value = ''
        commonops_mock.get_default_region.return_value = ''
        solution_stack_ops_mock.get_default_solution_stack.return_value = ''
        sourcecontrol_mock.get_source_control.return_value = git_mock
        git_mock.is_setup.return_value = None
        set_region_for_application_mock.return_value = 'us-west-2'

        get_input_mock.side_effect = [
            self.app_name,  # Application name
            '2',  # Platform selection
            '2',  # Platform version selection
            'n',  # Set up ssh selection
        ]

        app = EB(argv=['init'])
        app.setup()
        app.run()

        # make sure setup was called correctly
        initops_mock.setup.assert_called_with(
            self.app_name,
            'us-west-2',
            'PHP 5.5',
            branch=None,
            dir_path=None,
            repository=None
        )

    @mock.patch('ebcli.controllers.initialize.SourceControl.Git')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk.get_application_names')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops')
    @mock.patch('ebcli.controllers.initialize.sshops')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk')
    @mock.patch('ebcli.controllers.initialize.io.get_input')
    def test_init__force_interactive_mode_using_argument(
            self,
            get_input_mock,
            elasticbeanstalk_mock,
            commonops_mock,
            initops_mock,
            sshops_mock,
            solution_stack_ops_mock,
            get_application_names_mock,
            sourcecontrol_mock,
            git_mock
    ):
        fileoperations.create_config_file('app1', 'us-west-1', 'random')
        get_application_names_mock.return_value = list()
        initops_mock.credentials_are_valid.return_value = True
        elasticbeanstalk_mock.application_exist.return_value = False
        commonops_mock.create_app.return_value = 'ss-stack', 'key'
        solution_stack_ops_mock.get_solution_stack_from_customer.return_value = self.solution
        sshops_mock.prompt_for_ec2_keyname.return_value = 'test'

        get_input_mock.side_effect = [
            '3',  # region number
            self.app_name,  # Application name
            '2',  # Platform selection
            '2',  # Platform version selection'
            'n',  # Set up ssh selection
        ]

        # Mock out source control so we don't depend on git
        sourcecontrol_mock.get_source_control.return_value = git_mock
        git_mock.is_setup.return_value = None

        app = EB(argv=['init', '-i'])
        app.setup()
        app.run()

        # make sure setup was called correctly
        initops_mock.setup.assert_called_with(
            self.app_name,
            'us-west-2',
            'PHP 5.5',
            branch=None,
            dir_path=None,
            repository=None
        )

    @mock.patch('ebcli.controllers.initialize.SourceControl.Git')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops')
    @mock.patch('ebcli.controllers.initialize.sshops')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk')
    def test_init_no_creds(
            self,
            elasticbeanstalk_mock,
            commonops_mock,
            initops_mock,
            sshops_mock,
            solution_stack_ops_mock,
            sourcecontrol_mock,
            git_mock
    ):
        initops_mock.credentials_are_valid.return_value = False
        solution_stack_ops_mock.get_solution_stack_from_customer.return_value = self.solution
        sshops_mock.prompt_for_ec2_keyname.return_value = 'test'
        commonops_mock.get_current_branch_environment.side_effect = NotInitializedError
        elasticbeanstalk_mock.application_exist.return_value = True
        commonops_mock.pull_down_app_info.return_value = 'ss-stack', 'key'
        commonops_mock.get_default_keyname.return_value = ''
        commonops_mock.get_default_region.return_value = ''
        solution_stack_ops_mock.get_default_solution_stack.return_value = ''

        sourcecontrol_mock.get_source_control.return_value = git_mock
        git_mock.is_setup.return_value = None

        EB.Meta.exit_on_close = False
        app = EB(
            argv=[
                'init', self.app_name,
                '-r', 'us-west-2'
            ]
        )
        app.setup()
        app.run()

        # make sure we setup credentials
        initops_mock.setup_credentials.assert_called_with()
        initops_mock.setup.assert_called_with(
            self.app_name,
            'us-west-2',
            'ss-stack',
            branch=None,
            dir_path=None,
            repository=None
        )

    @mock.patch('ebcli.controllers.initialize.SourceControl.Git')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops')
    @mock.patch('ebcli.controllers.initialize.sshops')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk')
    def test_init__force_non_interactive_mode_using_platform_argument(
            self,
            elasticbeanstalk_mock,
            commonops_mock,
            initops_mock,
            sshops_mock,
            solution_stack_ops_mock,
            sourcecontrol_mock,
            git_mock
    ):
        solution_stack_ops_mock.get_solution_stack_from_customer.return_value = Exception
        sshops_mock.prompt_for_ec2_keyname.return_value = Exception
        commonops_mock.get_current_branch_environment.side_effect = NotInitializedError
        elasticbeanstalk_mock.application_exist.return_value = True
        commonops_mock.pull_down_app_info.return_value = 'ss-stack', 'key'
        commonops_mock.get_default_keyname.return_value = ''
        commonops_mock.get_default_region.return_value = 'us-west-2'
        solution_stack_ops_mock.get_default_solution_stack.return_value = ''

        sourcecontrol_mock.get_source_control.return_value = git_mock
        git_mock.is_setup.return_value = None

        EB.Meta.exit_on_close = False
        app = EB(argv=['init', '-p', 'php'])
        app.setup()
        app.run()

        initops_mock.setup.assert_called_with(
            'testDir',
            'us-west-2',
            'php',
            branch=None,
            dir_path=None,
            repository=None
        )

    @mock.patch('ebcli.controllers.initialize.SourceControl.Git')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops')
    @mock.patch('ebcli.controllers.initialize.sshops')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk')
    def test_init__non_interactive_mode__with_codecommit(
            self,
            elasticbeanstalk_mock,
            commonops_mock,
            initops_mock,
            sshops_mock,
            solution_stack_ops_mock,
            sourcecontrol_mock,
            git_mock
    ):
        solution_stack_ops_mock.get_solution_stack_from_customer.return_value = Exception
        sshops_mock.prompt_for_ec2_keyname.return_value = Exception
        commonops_mock.get_current_branch_environment.side_effect = NotInitializedError
        elasticbeanstalk_mock.application_exist.return_value = False
        commonops_mock.create_app.return_value = None, None
        commonops_mock.get_default_keyname.return_value = ''
        commonops_mock.get_default_region.return_value = ''
        initops_mock.credentials_are_valid.return_value = True
        solution_stack_ops_mock.get_default_solution_stack.return_value = ''

        sourcecontrol_mock.get_source_control.return_value = git_mock
        git_mock.is_setup.return_value = None

        app = EB(
            argv=[
                'init',
                '-p', 'ruby',
                '--source', 'codecommit/my-repo/prod',
                '--region', 'us-east-1'
            ]
        )
        app.setup()
        app.run()

        initops_mock.setup.assert_called_with(
            'testDir',
            'us-east-1',
            'ruby',
            dir_path=None,
            repository='my-repo',
            branch='prod'
        )

        sourcecontrol_mock.setup_codecommit_cred_config.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.SourceControl.Git')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops')
    @mock.patch('ebcli.controllers.initialize.sshops')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk')
    @mock.patch('ebcli.controllers.initialize.fileoperations.old_eb_config_present')
    @mock.patch('ebcli.controllers.initialize.fileoperations.get_values_from_old_eb')
    def test_init__get_application_information_from_old_config(
            self,
            get_values_from_old_eb_mock,
            old_eb_config_present_mock,
            elasticbeanstalk_mock,
            commonops_mock,
            initops_mock,
            sshops_mock,
            solution_stack_ops_mock,
            sourcecontrol_mock,
            git_mock
    ):
        old_eb_config_present_mock.return_value = True
        get_values_from_old_eb_mock.return_value = {
            'app_name': 'my-application',
            'access_id': 'my-access-id',
            'secret_key': 'my-secret-key',
            'default_env': 'default_env',
            'platform': self.solution.name,
            'region': 'us-east-1'
        }
        solution_stack_ops_mock.get_solution_stack_from_customer.return_value = Exception
        sshops_mock.prompt_for_ec2_keyname.return_value = Exception
        commonops_mock.get_current_branch_environment.side_effect = NotInitializedError
        elasticbeanstalk_mock.application_exist.return_value = False
        commonops_mock.create_app.return_value = None, None
        commonops_mock.get_default_keyname.return_value = ''
        commonops_mock.get_default_region.return_value = ''
        initops_mock.credentials_are_valid.return_value = True
        solution_stack_ops_mock.get_default_solution_stack.return_value = ''

        sourcecontrol_mock.get_source_control.return_value = git_mock
        git_mock.is_setup.return_value = None

        EB.Meta.exit_on_close = False
        self.app = EB(argv=['init'])
        self.app.setup()
        self.app.run()
        self.app.close()

        initops_mock.setup_credentials.assert_called_once_with(
            access_id='my-access-id',
            secret_key='my-secret-key'
        )
        initops_mock.setup.assert_called_with(
            'my-application',
            'us-east-1',
            '64bit Amazon Linux 2014.03 v1.0.6 running PHP 5.5',
            dir_path=None,
            repository=None,
            branch=None
        )

        sourcecontrol_mock.setup_codecommit_cred_config.assert_not_called()

    @mock.patch('ebcli.objects.sourcecontrol.Git')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk.application_exist')
    @mock.patch('ebcli.controllers.initialize.codecommit')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops')
    @mock.patch('ebcli.controllers.initialize.sshops')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.gitops')
    @mock.patch('ebcli.controllers.initialize.io.get_input')
    def test_init__interactive_mode__with_codecommit(
            self,
            get_input_mock,
            gitops_mock,
            commonops_mock,
            initops_mock,
            sshops_mock,
            solution_stack_ops_mock,
            sourcecontrol_mock,
            codecommit_mock,
            application_exist_mock,
            git_mock
    ):
        fileoperations.create_config_file('app1', 'us-west-1', 'random')
        initops_mock.credentials_are_valid.return_value = True
        commonops_mock.pull_down_app_info.return_value = None, None
        commonops_mock.create_app.return_value = None, None
        commonops_mock.get_default_keyname.return_value = 'ec2-keyname'
        solution_stack_ops_mock.get_default_solution_stack.return_value = ''
        solution_stack_ops_mock.get_solution_stack_from_customer.return_value = self.solution
        application_exist_mock.return_value = False

        gitops_mock.git_management_enabled.return_value = False

        codecommit_mock.list_repositories.return_value = {
            'repositories': [
                {
                    'repositoryName': 'only-repo'
                }
            ]
        }
        codecommit_mock.list_branches.return_value = {
            'branches': [
                'only-branch'
            ]
        }
        codecommit_mock.get_repository.return_value = {
            'repositoryMetadata': {
                'cloneUrlHttp': 'https://git-codecommit.fake.amazonaws.com/v1/repos/only-repo'
            }
        }

        sshops_mock.prompt_for_ec2_keyname.return_value = 'test'

        get_input_mock.side_effect = [
            'y',  # Yes to setup codecommit
            '2',  # Pick to create new repo
            'new-repo',  # set repo name
            '2',  # Pick first option for branch
            'devo',  #
            'n',  # Set up ssh selection
        ]

        sourcecontrol_mock.get_source_control.return_value = git_mock
        git_mock.is_setup.return_value = 'GitSetup'
        git_mock.get_current_commit.return_value = 'CommitId'

        app = EB(
            argv=['init', '--region', 'us-east-1', 'my-app'])
        app.setup()
        app.run()

        initops_mock.setup.assert_called_with(
            'my-app',
            'us-east-1',
            'PHP 5.5',
            dir_path=None,
            repository='new-repo',
            branch='devo'
        )

        codecommit_mock.create_repository.assert_called_once_with('new-repo', 'Created with EB CLI')
        git_mock.setup_new_codecommit_branch.assert_called_once_with(branch_name='devo')
        sourcecontrol_mock.setup_new_codecommit_branch('devo')

    @mock.patch('ebcli.controllers.initialize.SourceControl.Git')
    @mock.patch('ebcli.controllers.initialize.fileoperations')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk.get_application_names')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops')
    @mock.patch('ebcli.controllers.initialize.sshops')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk')
    @mock.patch('ebcli.core.io.get_input')
    def test_init__interactive_mode__with_codebuild_buildspec(
            self,
            get_input_mock,
            elasticbeanstalk_mock,
            commonops_mock,
            initops_mock,
            sshops_mock,
            solution_stack_ops_mock,
            get_application_names_mock,
            sourcecontrol_mock,
            fileoperations_mock,
            git_mock
    ):
        expected_image = 'aws/codebuild/eb-java-8-amazonlinux-64:2.1.6'
        compute_type = 'BUILD_GENERAL1_SMALL'
        service_role = 'eb-test'
        timeout = 60
        build_config = BuildConfiguration(
            image=None,
            compute_type=compute_type,
            service_role=service_role,
            timeout=timeout
        )

        fileoperations.create_config_file('app1', 'us-west-1', 'random')

        get_application_names_mock.get_application_names.return_value = list()
        initops_mock.credentials_are_valid.return_value = True
        solution_stack_ops_mock.get_solution_stack_from_customer.return_value = self.solution
        fileoperations_mock.env_yaml_exists.return_value = None

        elasticbeanstalk_mock.application_exist.return_value = False
        commonops_mock.create_app.return_value = None, None
        fileoperations_mock.build_spec_exists.return_value = True
        fileoperations_mock.get_build_configuration.return_value = build_config
        fileoperations_mock.buildspec_config_header = fileoperations.buildspec_config_header
        fileoperations_mock.buildspec_name = fileoperations.buildspec_name

        initops_mock.get_codebuild_image_from_platform.return_value = [
            {
                u'name': u'aws/codebuild/eb-java-7-amazonlinux-64:2.1.6',
                u'description': u'Java 7 Running on Amazon Linux 64bit '
            },
            {
                u'name': expected_image,
                u'description': u'Java 8 Running on Amazon Linux 64bit '
            },
            {
                u'name': u'aws/codebuild/eb-ruby-1.9-amazonlinux-64:2.1.6',
                u'description': u'Ruby 1.9 Running on Amazon Linux 64bit '
            }
        ]

        sshops_mock.prompt_for_ec2_keyname.return_value = 'test'
        commonops_mock.pull_down_app_info.return_value = 'something', 'smthing'

        get_input_mock.side_effect = [
            '3',  # region number
            self.app_name,  # Application name
            '2',  # Image Platform selection
            '2',  # Platform version selection
            'n',  # Set up ssh selection
        ]

        sourcecontrol_mock.get_source_control.return_value = git_mock
        git_mock.is_setup.return_value = None

        app = EB(argv=['init', '-i'])
        app.setup()
        app.run()

        initops_mock.setup.assert_called_with(
            self.app_name,
            'us-west-2',
            'PHP 5.5',
            branch=None,
            dir_path=None,
            repository=None
        )
        initops_mock.get_codebuild_image_from_platform.assert_called_with('PHP 5.5')

        write_config_calls = [
            mock.call('global', 'profile', 'eb-cli'),
            mock.call(
                fileoperations.buildspec_config_header,
                'Image',
                expected_image,
                file=fileoperations.buildspec_name
            ),
            mock.call('global', 'default_ec2_keyname', 'test'),
        ]
        fileoperations_mock.write_config_setting.assert_has_calls(write_config_calls)

    @mock.patch('ebcli.controllers.initialize.SourceControl.Git')
    @mock.patch('ebcli.controllers.initialize.fileoperations')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk.get_application_names')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops')
    @mock.patch('ebcli.controllers.initialize.sshops')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk')
    @mock.patch('ebcli.controllers.initialize.io.get_input')
    def test_init__non_interactive_mode__with_codebuild_buildspec(
            self,
            get_input_mock,
            elasticbeanstalk_mock,
            commonops_mock,
            initops_mock,
            sshops_mock,
            solution_stack_ops_mock,
            get_application_names_mock,
            sourcecontrol_mock,
            fileoperations_mock,
            git_mock
    ):
        expected_image = 'aws/codebuild/eb-java-8-amazonlinux-64:2.1.6'
        compute_type = 'BUILD_GENERAL1_SMALL'
        service_role = 'eb-test'
        timeout = 60
        build_config = BuildConfiguration(
            image=None,
            compute_type=compute_type,
            service_role=service_role,
            timeout=timeout
        )

        fileoperations.create_config_file('app1', 'us-west-1', 'random')
        get_application_names_mock.return_value = list()
        initops_mock.credentials_are_valid.return_value = True
        solution_stack_ops_mock.get_solution_stack_from_customer.return_value = \
            self.solution
        fileoperations_mock.env_yaml_exists.return_value = None

        elasticbeanstalk_mock.application_exist.return_value = False
        commonops_mock.create_app.return_value = None, None
        elasticbeanstalk_mock.application_exist.return_value = False
        fileoperations_mock.get_build_configuration.return_value = build_config
        fileoperations_mock.buildspec_config_header = fileoperations.buildspec_config_header
        fileoperations_mock.buildspec_name = fileoperations.buildspec_name

        initops_mock.get_codebuild_image_from_platform.return_value = {
            u'name': expected_image,
            u'description': u'Java 8 Running on Amazon Linux 64bit '
        }

        sshops_mock.prompt_for_ec2_keyname.return_value = 'test'
        commonops_mock.pull_down_app_info.return_value = 'something', 'smthing'

        get_input_mock.side_effect = [
            '3',  # region number
            self.app_name,  # Application name
            '2',  # Platform version selection
            'n',  # Set up ssh selection
        ]

        sourcecontrol_mock.get_source_control.return_value = git_mock
        git_mock.is_setup.return_value = None

        app = EB(argv=['init', '-i'])
        app.setup()
        app.run()

        initops_mock.setup.assert_called_with(
            self.app_name,
            'us-west-2',
            'PHP 5.5',
            branch=None,
            dir_path=None,
            repository=None
        )
        initops_mock.get_codebuild_image_from_platform.assert_called_with('PHP 5.5')

        write_config_calls = [
            mock.call('global', 'profile', 'eb-cli'),
            mock.call(
                fileoperations.buildspec_config_header,
                'Image',
                expected_image,
                file=fileoperations.buildspec_name
            ),
            mock.call('global', 'default_ec2_keyname', 'test'),
        ]
        fileoperations_mock.write_config_setting.assert_has_calls(write_config_calls)

    @mock.patch('ebcli.controllers.initialize.codecommit')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops')
    @mock.patch('ebcli.controllers.initialize.sshops')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk')
    @mock.patch('ebcli.controllers.initialize.fileoperations.get_application_name')
    @mock.patch('ebcli.controllers.initialize.fileoperations.get_platform_from_env_yaml')
    @mock.patch('ebcli.controllers.initialize.fileoperations.build_spec_exists')
    @mock.patch('ebcli.controllers.initialize.fileoperations.get_build_configuration')
    @mock.patch('ebcli.controllers.initialize.fileoperations.buildspec_config_header')
    @mock.patch('ebcli.controllers.initialize.fileoperations.buildspec_name')
    @mock.patch('ebcli.controllers.initialize.fileoperations.write_config_setting')
    def test_init_with_codecommit_source_and_codebuild(
            self,
            write_config_setting_mock,
            buildspec_name_mock,
            buildspec_config_header_mock,
            get_build_configuration_mock,
            build_spec_exists_mock,
            get_platform_from_env_yaml_mock,
            get_application_name_mock,
            elasticbeanstalk_mock,
            commonops_mock,
            initops_mock,
            sshops_mock,
            solution_stack_ops_mock,
            sourcecontrol_mock,
            codecommit_mock
    ):
        expected_image = 'aws/codebuild/eb-java-8-amazonlinux-64:2.1.6'
        compute_type = 'BUILD_GENERAL1_SMALL'
        service_role = 'eb-test'
        timeout = 60
        build_config = BuildConfiguration(
            image=None,
            compute_type=compute_type,
            service_role=service_role,
            timeout=timeout
        )

        codecommit_mock.side_effect = None
        get_application_name_mock.return_value = 'testDir'
        get_platform_from_env_yaml_mock.return_value = 'PHP 5.5'
        build_spec_exists_mock.return_value = True
        get_build_configuration_mock.return_value = build_config
        buildspec_config_header_mock.return_value = fileoperations.buildspec_config_header
        buildspec_name_mock.return_value = fileoperations.buildspec_name
        codecommit_mock.get_repository.side_effect = [
            ServiceError,
            {
                "repositoryMetadata": {
                    "cloneUrlHttp": "https://codecommit.us-east-1.amazonaws.com/v1/repos/my-repo"
                }
            }
        ]
        sourcecontrol_mock.setup_existing_codecommit_branch = mock.MagicMock()
        initops_mock.get_codebuild_image_from_platform.return_value = {
            u'name': expected_image,
            u'description': u'PHP 5.5 Running on Amazon Linux 64bit '
        }

        solution_stack_ops_mock.get_solution_stack_from_customer.return_value = SolutionStack(
            '64bit Amazon Linux 2014.03 v1.0.6 running PHP 5.5'
        )
        sshops_mock.prompt_for_ec2_keyname.return_value = Exception
        commonops_mock.get_current_branch_environment.side_effect = NotInitializedError
        elasticbeanstalk_mock.application_exist.return_value = False
        commonops_mock.create_app.return_value = None, None
        commonops_mock.get_default_keyname.return_value = ''
        commonops_mock.get_default_region.return_value = ''
        solution_stack_ops_mock.get_default_solution_stack.return_value = ''

        app = EB(argv=['init', '--source', 'codecommit/my-repo/prod', '--region', 'us-east-1'])
        app.setup()
        app.run()

        initops_mock.setup.assert_called_with(
            'testDir',
            'us-east-1',
            'PHP 5.5',
            dir_path=None,
            repository='my-repo',
            branch='prod'
        )

        sourcecontrol_mock.setup_codecommit_cred_config.assert_not_called()
        initops_mock.get_codebuild_image_from_platform.assert_called_with('PHP 5.5')


class TestInitModule(unittest.TestCase):
    solution = SolutionStack('64bit Amazon Linux 2014.03 v1.0.6 running PHP 5.5')
    app_name = 'ebcli-intTest-app'

    def setUp(self):
        disable_socket()
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')

        os.chdir('testDir')

        fileoperations.create_config_file(
            self.app_name,
            'us-west-2',
            self.solution.name
        )

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

        enable_socket()

    def test_get_region_from_inputs__region_was_passed(self):
        self.assertEqual(
            'us-east-1',
            initialize.get_region_from_inputs('us-east-1')
        )

    @mock.patch('ebcli.controllers.initialize.commonops.get_default_region')
    def test_get_region_from_inputs__region_not_passed_in__default_region_found(
            self,
            get_default_region_mock
    ):
        get_default_region_mock.return_value = 'us-east-1'
        self.assertEqual(
            'us-east-1',
            initialize.get_region_from_inputs(None)
        )

    @mock.patch('ebcli.controllers.initialize.commonops.get_default_region')
    def test_get_region_from_inputs__region_not_passed_in__could_not_determine_default_region(
            self,
            get_default_region_mock
    ):
        get_default_region_mock.side_effect = NotInitializedError
        self.assertIsNone(initialize.get_region_from_inputs(None))

    @mock.patch('ebcli.controllers.initialize.get_region_from_inputs')
    @mock.patch('ebcli.controllers.initialize.regions.get_all_regions')
    @mock.patch('ebcli.controllers.initialize.utils.prompt_for_item_in_list')
    def test_get_region__determine_region_from_inputs(
            self,
            prompt_for_item_in_list_mock,
            get_all_regions_mock,
            get_region_from_inputs_mock
    ):
        get_region_from_inputs_mock.return_value = 'us-east-1'

        self.assertEqual(
            'us-east-1',
            initialize.get_region('us-east-1', False)
        )

        get_all_regions_mock.assert_not_called()
        prompt_for_item_in_list_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.get_region_from_inputs')
    @mock.patch('ebcli.controllers.initialize.utils.prompt_for_item_in_list')
    def test_get_region__could_not_determine_region_from_inputs__force_non_interactive__selects_us_west_2_by_default(
            self,
            prompt_for_item_in_list_mock,
            get_region_from_inputs_mock
    ):
        get_region_from_inputs_mock.return_value = None

        self.assertEqual(
            'us-west-2',
            initialize.get_region(None, False, force_non_interactive=True)
        )

        prompt_for_item_in_list_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.get_region_from_inputs')
    @mock.patch('ebcli.controllers.initialize.utils.prompt_for_item_in_list')
    def test_get_region__could_not_determine_region_from_inputs__in_interactive_mode__prompts_customer_for_region(
            self,
            prompt_for_item_in_list_mock,
            get_region_from_inputs_mock
    ):
        get_region_from_inputs_mock.return_value = None
        prompt_for_item_in_list_mock.return_value = initialize.regions.Region('us-west-1', 'US West (N. California)')

        self.assertEqual(
            'us-west-1',
            initialize.get_region(None, True)
        )

    @mock.patch('ebcli.controllers.initialize.get_region_from_inputs')
    @mock.patch('ebcli.controllers.initialize.utils.prompt_for_item_in_list')
    def test_get_region__could_not_determine_region_from_inputs__not_in_interactive_mode__prompts_customer_for_region_anyway(
            self,
            prompt_for_item_in_list_mock,
            get_region_from_inputs_mock
    ):
        get_region_from_inputs_mock.return_value = None
        prompt_for_item_in_list_mock.return_value = initialize.regions.Region('us-west-1', 'US West (N. California)')

        self.assertEqual(
            'us-west-1',
            initialize.get_region(None, False)
        )

    @mock.patch('ebcli.controllers.initialize.initializeops.credentials_are_valid')
    def test_check_credentials__credentials_are_valid(
            self,
            credentials_are_valid_mock
    ):
        credentials_are_valid_mock.return_value = True
        self.assertEqual(
            ('my-profile', 'us-east-1'),
            initialize.check_credentials(
                'my-profile',
                'my-profile',
                'us-east-1',
                False,
                False
            )
        )

    @mock.patch('ebcli.controllers.initialize.initializeops.credentials_are_valid')
    @mock.patch('ebcli.controllers.initialize.get_region')
    def test_check_credentials__no_region_error_rescued(
            self,
            get_region_mock,
            credentials_are_valid_mock
    ):
        get_region_mock.return_value = 'us-west-1'
        credentials_are_valid_mock.side_effect = initialize.InvalidProfileError

        with self.assertRaises(initialize.InvalidProfileError):
            initialize.check_credentials(
                'my-profile',
                'my-profile',
                'us-east-1',
                False,
                False
            )

    @mock.patch('ebcli.controllers.initialize.initializeops.credentials_are_valid')
    @mock.patch('ebcli.controllers.initialize.get_region')
    def test_check_credentials__invalid_profile_error_raised__profile_not_provided_as_input(
            self,
            get_region_mock,
            credentials_are_valid_mock
    ):
        get_region_mock.return_value = 'us-west-1'
        credentials_are_valid_mock.side_effect = [
            InvalidProfileError,
            None
        ]

        self.assertEqual(
            (None, 'us-east-1'),
            initialize.check_credentials(
                None,
                None,
                'us-east-1',
                False,
                False
            )
        )

    @mock.patch('ebcli.controllers.initialize.check_credentials')
    @mock.patch('ebcli.controllers.initialize.initializeops.credentials_are_valid')
    @mock.patch('ebcli.controllers.initialize.initializeops.setup_credentials')
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

        self.assertEqual(
            'us-east-1',
            initialize.set_up_credentials(
                'my-profile',
                'us-east-1',
                False
            )
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
    @mock.patch('ebcli.controllers.initialize.check_credentials')
    @mock.patch('ebcli.controllers.initialize.initializeops.credentials_are_valid')
    @mock.patch('ebcli.controllers.initialize.initializeops.setup_credentials')
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

        self.assertEqual(
            'us-east-1',
            initialize.set_up_credentials(
                None,
                'us-east-1',
                False
            )
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
    @mock.patch('ebcli.controllers.initialize.check_credentials')
    @mock.patch('ebcli.controllers.initialize.initializeops.credentials_are_valid')
    @mock.patch('ebcli.controllers.initialize.initializeops.setup_credentials')
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

        self.assertEqual(
            'us-east-1',
            initialize.set_up_credentials(
                None,
                'us-east-1',
                False
            )
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

    @mock.patch('ebcli.controllers.initialize.codecommit.list_branches')
    @mock.patch('ebcli.controllers.initialize.codecommit.get_repository')
    @mock.patch('ebcli.controllers.initialize.SourceControl.get_source_control')
    @mock.patch('ebcli.controllers.initialize.utils.prompt_for_item_in_list')
    def test_get_branch_interactive__one_or_more_branches_already_exist_in_the_repository__initialize_with_existing_repository_and_branch(
            self,
            prompt_for_item_in_list_mock,
            get_source_control_mock,
            get_repository_mock,
            list_branches_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.get_current_branch = mock.MagicMock(return_value='master')
        source_control_mock.setup_codecommit_remote_repo = mock.MagicMock()
        get_source_control_mock.return_value = source_control_mock
        list_branches_mock.return_value = {
            'branches': [
                'develop',
                'master'
            ]
        }
        get_repository_mock.return_value = {
            'repositoryMetadata': {
                'cloneUrlHttp': 'https://git-codecommit.fake.amazonaws.com/v1/repos/my-repo'
            }
        }
        prompt_for_item_in_list_mock.return_value = 2 # initialize with 'master' branch

        initialize.get_branch_interactive('my-repo')

        list_branches_mock.assert_called_once_with('my-repo')
        prompt_for_item_in_list_mock.assert_called_once_with(
            [
                'develop',
                'master',
                '[ Create new Branch with local HEAD ]'
            ],
            default=2
        )
        get_repository_mock.assert_called_once_with('my-repo')
        source_control_mock.setup_codecommit_remote_repo.assert_called_once_with(
            remote_url='https://git-codecommit.fake.amazonaws.com/v1/repos/my-repo'
        )

    @mock.patch('ebcli.controllers.initialize.create_codecommit_branch')
    @mock.patch('ebcli.controllers.initialize.codecommit.list_branches')
    @mock.patch('ebcli.controllers.initialize.codecommit.get_repository')
    @mock.patch('ebcli.controllers.initialize.SourceControl.get_source_control')
    @mock.patch('ebcli.controllers.initialize.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.controllers.initialize.io.prompt_for_unique_name')
    @mock.patch('ebcli.controllers.initialize.io.echo')
    def test_get_branch_interactive__one_or_more_branches_already_exist_in_the_repository__initialize_with_existing_repository_but_with_new_branch_from_HEAD(
            self,
            echo_mock,
            prompt_for_unique_name_mock,
            prompt_for_item_in_list_mock,
            get_source_control_mock,
            get_repository_mock,
            list_branches_mock,
            create_codecommit_branch_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.get_current_branch = mock.MagicMock(return_value='master')
        source_control_mock.setup_codecommit_remote_repo = mock.MagicMock()
        source_control_mock.setup_existing_codecommit_branch = mock.MagicMock(return_value=True)
        get_source_control_mock.return_value = source_control_mock
        list_branches_mock.return_value = {
            'branches': [
                'develop',
                'master'
            ]
        }
        get_repository_mock.return_value = {
            'repositoryMetadata': {
                'cloneUrlHttp': 'https://git-codecommit.fake.amazonaws.com/v1/repos/my-repo'
            }
        }
        create_codecommit_branch_mock.side_effect = None
        prompt_for_unique_name_mock.return_value = 'master2'
        prompt_for_item_in_list_mock.return_value = '[ Create new Branch with local HEAD ]'

        initialize.get_branch_interactive('my-repo')

        list_branches_mock.assert_called_once_with('my-repo')
        prompt_for_item_in_list_mock.assert_called_once_with(
            [
                'develop',
                'master',
                '[ Create new Branch with local HEAD ]'
            ],
            default=2
        )
        get_repository_mock.assert_called_once_with('my-repo')
        source_control_mock.setup_codecommit_remote_repo.assert_called_once_with(
            remote_url='https://git-codecommit.fake.amazonaws.com/v1/repos/my-repo'
        )
        echo_mock.assert_has_calls(
            [
                mock.call('Select a branch'),
                mock.call(),
                mock.call('Enter Branch Name'),
                mock.call('***** Must have at least one commit to create a new branch with CodeCommit *****')
            ]
        )
        create_codecommit_branch_mock.assert_called_once_with(source_control_mock, 'master2')

    @mock.patch('ebcli.controllers.initialize.create_codecommit_branch')
    @mock.patch('ebcli.controllers.initialize.codecommit.list_branches')
    @mock.patch('ebcli.controllers.initialize.codecommit.get_repository')
    @mock.patch('ebcli.controllers.initialize.SourceControl.get_source_control')
    @mock.patch('ebcli.controllers.initialize.io.prompt_for_unique_name')
    @mock.patch('ebcli.controllers.initialize.io.echo')
    def test_get_branch_interactive__repository_has_no_branches__initialize_with_new_branch_from_HEAD(
            self,
            echo_mock,
            prompt_for_unique_name_mock,
            get_source_control_mock,
            get_repository_mock,
            list_branches_mock,
            create_codecommit_branch_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.get_current_branch = mock.MagicMock(return_value='master')
        source_control_mock.setup_codecommit_remote_repo = mock.MagicMock()
        source_control_mock.setup_existing_codecommit_branch = mock.MagicMock(return_value=True)
        get_source_control_mock.return_value = source_control_mock
        list_branches_mock.return_value = {
            'branches': []
        }
        get_repository_mock.return_value = {
            'repositoryMetadata': {
                'cloneUrlHttp': 'https://git-codecommit.fake.amazonaws.com/v1/repos/my-repo'
            }
        }
        create_codecommit_branch_mock.side_effect = None
        prompt_for_unique_name_mock.return_value = 'master2'

        initialize.get_branch_interactive('my-repo')

        list_branches_mock.assert_called_once_with('my-repo')
        get_repository_mock.assert_called_once_with('my-repo')
        source_control_mock.setup_codecommit_remote_repo.assert_called_once_with(
            remote_url='https://git-codecommit.fake.amazonaws.com/v1/repos/my-repo'
        )
        echo_mock.assert_has_calls(
            [
                mock.call(),
                mock.call('Enter Branch Name'),
                mock.call('***** Must have at least one commit to create a new branch with CodeCommit *****')
            ]
        )
        create_codecommit_branch_mock.assert_called_once_with(source_control_mock, 'master2')

    @mock.patch('ebcli.controllers.initialize.create_codecommit_branch')
    @mock.patch('ebcli.controllers.initialize.codecommit.list_branches')
    @mock.patch('ebcli.controllers.initialize.codecommit.get_repository')
    @mock.patch('ebcli.controllers.initialize.SourceControl.get_source_control')
    @mock.patch('ebcli.controllers.initialize.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.controllers.initialize.io.prompt_for_unique_name')
    @mock.patch('ebcli.controllers.initialize.io.echo')
    def test_get_branch_interactive__one_or_more_branches_already_exist_in_the_repository__initialization_with_existing_repository_but_new_branch_from_HEAD_failed(
            self,
            echo_mock,
            prompt_for_unique_name_mock,
            prompt_for_item_in_list_mock,
            get_source_control_mock,
            get_repository_mock,
            list_branches_mock,
            create_codecommit_branch_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.get_current_branch = mock.MagicMock(return_value='master')
        source_control_mock.setup_codecommit_remote_repo = mock.MagicMock()
        source_control_mock.setup_existing_codecommit_branch = mock.MagicMock(return_value=True)
        get_source_control_mock.return_value = source_control_mock
        list_branches_mock.return_value = {
            'branches': [
                'develop',
                'master'
            ]
        }
        get_repository_mock.return_value = {
            'repositoryMetadata': {
                'cloneUrlHttp': 'https://git-codecommit.fake.amazonaws.com/v1/repos/my-repo'
            }
        }
        create_codecommit_branch_mock.side_effect = initialize.ServiceError
        prompt_for_unique_name_mock.return_value = 'master2'
        prompt_for_item_in_list_mock.return_value = '[ Create new Branch with local HEAD ]'

        initialize.get_branch_interactive('my-repo')

        list_branches_mock.assert_called_once_with('my-repo')
        prompt_for_item_in_list_mock.assert_called_once_with(
            [
                'develop',
                'master',
                '[ Create new Branch with local HEAD ]',
            ],
            default=2
        )
        get_repository_mock.assert_called_once_with('my-repo')
        source_control_mock.setup_codecommit_remote_repo.assert_called_once_with(
            remote_url='https://git-codecommit.fake.amazonaws.com/v1/repos/my-repo'
        )
        echo_mock.assert_has_calls(
            [
                mock.call('Select a branch'),
                mock.call(),
                mock.call('Enter Branch Name'),
                mock.call('***** Must have at least one commit to create a new branch with CodeCommit *****'),
                mock.call("Could not set CodeCommit branch with the current commit, run with '--debug' to get the full error")
            ]
        )
        create_codecommit_branch_mock.assert_called_once_with(source_control_mock, 'master2')

    @mock.patch('ebcli.controllers.initialize.io.echo')
    def test_create_codecommit_branch(
            self,
            echo_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.get_current_commit = mock.MagicMock(return_value='ca4aebb896790302561b8b6d0276743afd70c3b6')

        initialize.create_codecommit_branch(source_control_mock, 'master')

        source_control_mock.setup_new_codecommit_branch.assert_called_once_with(branch_name='master')
        echo_mock.assert_called_once_with('Successfully created branch: master')

    @mock.patch('ebcli.controllers.initialize.io.echo')
    def test_create_codecommit_branch__current_commit_could_not_be_determined__staged_files_exist(
            self,
            echo_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.get_current_commit = mock.MagicMock(return_value=None)
        source_control_mock.get_list_of_staged_files.return_value = b"""ebcli/controllers/initialize.py
    tests/unit/controllers/test_init.py
    """

        initialize.create_codecommit_branch(source_control_mock, 'master')

        echo_mock.assert_called_once_with(
            'Could not set create a commit with staged files; cannot setup CodeCommit branch without a commit'
        )

    @mock.patch('ebcli.controllers.initialize.io.echo')
    def test_create_codecommit_branch__current_commit_could_not_be_determined__no_staged_files_exist(
            self,
            echo_mock
    ):
        source_control_mock = mock.MagicMock()
        source_control_mock.get_current_commit = mock.MagicMock(return_value=None)
        source_control_mock.get_list_of_staged_files.return_value = ''

        initialize.create_codecommit_branch(source_control_mock, 'master')

        echo_mock.assert_called_once_with(
            'Successfully created branch: master'
        )
        source_control_mock.create_initial_commit.assert_called_once()

    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk.get_application_names')
    @mock.patch('ebcli.controllers.initialize.fileoperations.get_current_directory_name')
    @mock.patch('ebcli.controllers.initialize.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.controllers.initialize.io.prompt_for_unique_name')
    @mock.patch('ebcli.controllers.initialize.io.echo')
    def test_get_application_name_interactive__no_apps_exist__customer_is_prompted_for_new_app_name(
            self,
            echo_mock,
            prompt_for_unique_name_mock,
            prompt_for_item_in_list_mock,
            get_current_directory_name_mock,
            get_application_names_mock
    ):
        get_application_names_mock.return_value = []
        get_current_directory_name_mock.return_value = 'my-application-dir'
        prompt_for_unique_name_mock.return_value = 'unique-app-name'

        self.assertEqual(
            'unique-app-name',
            initialize._get_application_name_interactive()
        )

        echo_mock.assert_has_calls(
            [
                mock.call(),
                mock.call('Enter Application Name')
            ]
        )
        prompt_for_unique_name_mock.assert_called_once_with(
            'my-application-dir',
            []
        )

    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk.get_application_names')
    @mock.patch('ebcli.controllers.initialize.fileoperations.get_current_directory_name')
    @mock.patch('ebcli.controllers.initialize.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.controllers.initialize.io.prompt_for_unique_name')
    @mock.patch('ebcli.controllers.initialize.io.echo')
    def test_get_application_name_interactive__one_or_more_apps_exist__customer_chooses_to_create_new_app(
            self,
            echo_mock,
            prompt_for_unique_name_mock,
            prompt_for_item_in_list_mock,
            get_current_directory_name_mock,
            get_application_names_mock
    ):
        get_application_names_mock.return_value = [
            'my-app-1',
            'my-app-2',
        ]
        get_current_directory_name_mock.return_value = 'my-application-dir'
        prompt_for_item_in_list_mock.return_value = '[ Create new Application ]'
        prompt_for_unique_name_mock.return_value = 'unique-app-name'

        self.assertEqual(
            'unique-app-name',
            initialize._get_application_name_interactive()
        )

        echo_mock.assert_has_calls(
            [
                mock.call('Select an application to use'),
                mock.call(),
                mock.call('Enter Application Name')
            ]
        )
        prompt_for_unique_name_mock.assert_called_once_with(
            'my-application-dir',
            [
                'my-app-1',
                'my-app-2',
                '[ Create new Application ]'
            ]
        )

    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk.get_application_names')
    @mock.patch('ebcli.controllers.initialize.fileoperations.get_current_directory_name')
    @mock.patch('ebcli.controllers.initialize.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.controllers.initialize.io.prompt_for_unique_name')
    @mock.patch('ebcli.controllers.initialize.io.echo')
    def test_get_application_name_interactive__one_or_more_apps_exist__customer_selects_existing_app(
            self,
            echo_mock,
            prompt_for_unique_name_mock,
            prompt_for_item_in_list_mock,
            get_current_directory_name_mock,
            get_application_names_mock
    ):
        get_application_names_mock.return_value = [
            'my-app-1',
            'my-app-2',
        ]
        get_current_directory_name_mock.return_value = 'my-application-dir'
        prompt_for_item_in_list_mock.return_value = 'my-app-2'

        self.assertEqual(
            'my-app-2',
            initialize._get_application_name_interactive()
        )

        echo_mock.assert_has_calls(
            [
                mock.call('Select an application to use'),
            ]
        )
        prompt_for_unique_name_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.get_region_from_inputs')
    @mock.patch('ebcli.controllers.initialize.aws.set_region')
    def test_set_region_for_application(
            self,
            set_region_mock,
            get_region_from_inputs_mock
    ):
        get_region_from_inputs_mock.return_value = 'us-west-2'

        self.assertEqual(
            'us-west-2',
            initialize.set_region_for_application(False, 'us-west-2', False)
        )

        get_region_from_inputs_mock.assert_called_once_with('us-west-2')
        set_region_mock.assert_called_once_with('us-west-2')

    @mock.patch('ebcli.controllers.initialize.get_region')
    @mock.patch('ebcli.controllers.initialize.aws.set_region')
    def test_set_region_for_application__interactive(
            self,
            set_region_mock,
            get_region_mock
    ):
        get_region_mock.return_value = 'us-west-2'

        self.assertEqual(
            'us-west-2',
            initialize.set_region_for_application(True, 'us-west-2', False)
        )

        get_region_mock.assert_called_once_with('us-west-2', True, False)
        set_region_mock.assert_called_once_with('us-west-2')

    @mock.patch('ebcli.controllers.initialize.get_region')
    @mock.patch('ebcli.controllers.initialize.aws.set_region')
    def test_set_region_for_application__region_not_passed__non_interactive_not_forced(
            self,
            set_region_mock,
            get_region_mock
    ):
        get_region_mock.return_value = 'us-west-2'

        self.assertEqual(
            'us-west-2',
            initialize.set_region_for_application(False, None, False)
        )

        get_region_mock.assert_called_once_with(None, False, False)
        set_region_mock.assert_called_once_with('us-west-2')


class TestInitMultipleModules(unittest.TestCase):
    platform = PlatformVersion(
        'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5'
    )

    def setUp(self):
        disable_socket()
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')

        os.chdir('testDir')

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

        enable_socket()

    def test_multiple_modules__none_of_the_specified_modules_actually_exists(self):
        app = EB(
            argv=[
                'init',
                '--modules', 'module-1', 'module-2',
            ]
        )
        app.setup()
        app.run()

    @mock.patch('ebcli.controllers.initialize.get_region')
    @mock.patch('ebcli.controllers.initialize.fileoperations.write_config_setting')
    @mock.patch('ebcli.controllers.initialize.InitController.get_solution_stack')
    @mock.patch('ebcli.controllers.initialize.InitController.get_app_name')
    @mock.patch('ebcli.controllers.initialize.InitController.get_keyname')
    @mock.patch('ebcli.controllers.initialize.set_up_credentials')
    @mock.patch('ebcli.controllers.initialize.commonops.create_app')
    @mock.patch('ebcli.controllers.initialize.commonops.pull_down_app_info')
    @mock.patch('ebcli.controllers.initialize.aws.set_region')
    @mock.patch('ebcli.controllers.initialize.initializeops.setup')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_solution_stack_from_customer')
    def test_multiple_modules__interactive_mode__solution_stack_in_env_yaml_is_used_when_available(
            self,
            get_solution_stack_from_customer_mock,
            setup_mock,
            set_region_mock,
            pull_down_app_info_mock,
            create_app_mock,
            set_up_credentials_mock,
            get_keyname_mock,
            get_app_name_mock,
            get_solution_stack_mock,
            write_config_setting_mock,
            get_region_mock
    ):
        os.mkdir('module-1')
        os.mkdir('module-2')
        with open(os.path.join('module-1', 'env.yaml'), 'w') as file:
            file.write("""AWSConfigurationTemplateVersion: 1.1.0.0
SolutionStack: 64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)
        """)

        get_app_name_mock.return_value = 'my-application'
        get_region_mock.return_value = 'us-east-1'
        set_up_credentials_mock.return_value = 'us-east-1'
        get_solution_stack_mock.return_value = 'php7.1'
        create_app_mock.return_value = [
            '64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)',
            'my-ec2-key-name'
        ]
        pull_down_app_info_mock.return_value = [
            '64bit Amazon Linux 2014.03 v1.0.6 running PHP 7.1',
            'my-ec2-key-name'
        ]
        get_solution_stack_from_customer_mock.return_value = '64bit Amazon Linux 2014.03 v1.0.6 running PHP 7.1'
        get_keyname_mock.return_value = 'my-ec2-key-name'

        app = EB(
            argv=[
                'init',
                '--modules', 'module-1', 'module-2',
                '--interactive'
            ]
        )
        app.setup()
        app.run()

        setup_mock.assert_has_calls(
            [
                mock.call('my-application', 'us-east-1', 'Multi-container Docker 1.7.1 (Generic)'),
                mock.call('my-application', 'us-east-1', '64bit Amazon Linux 2014.03 v1.0.6 running PHP 7.1')
            ]
        )
        write_config_setting_mock.assert_has_calls(
            [
                mock.call('global', 'default_ec2_keyname', 'my-ec2-key-name'),
                mock.call('global', 'default_ec2_keyname', 'my-ec2-key-name')
            ]
        )
        create_app_mock.assert_called_once_with('my-application', default_env=None)
        pull_down_app_info_mock.assert_called_once_with('my-application', default_env=None)
        self.assertEqual(
            2,
            set_region_mock.call_count
        )

    @mock.patch('ebcli.controllers.initialize.get_region')
    @mock.patch('ebcli.controllers.initialize.fileoperations.write_config_setting')
    @mock.patch('ebcli.controllers.initialize.InitController.get_solution_stack')
    @mock.patch('ebcli.controllers.initialize.InitController.get_app_name')
    @mock.patch('ebcli.controllers.initialize.InitController.get_keyname')
    @mock.patch('ebcli.controllers.initialize.set_up_credentials')
    @mock.patch('ebcli.controllers.initialize.commonops.create_app')
    @mock.patch('ebcli.controllers.initialize.commonops.pull_down_app_info')
    @mock.patch('ebcli.controllers.initialize.aws.set_region')
    @mock.patch('ebcli.controllers.initialize.initializeops.setup')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_solution_stack_from_customer')
    def test_multiple_modules__interactive_mode__solution_stack_in_env_yaml_is_used_when_available(
            self,
            get_solution_stack_from_customer_mock,
            setup_mock,
            set_region_mock,
            pull_down_app_info_mock,
            create_app_mock,
            set_up_credentials_mock,
            get_keyname_mock,
            get_app_name_mock,
            get_solution_stack_mock,
            write_config_setting_mock,
            get_region_mock
    ):
        os.mkdir('module-1')
        os.mkdir('module-2')
        with open(os.path.join('module-1', 'env.yaml'), 'w') as file:
            file.write("""AWSConfigurationTemplateVersion: 1.1.0.0
SolutionStack: 64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)
        """)

        get_app_name_mock.return_value = 'my-application'
        get_region_mock.return_value = 'us-east-1'
        set_up_credentials_mock.return_value = 'us-east-1'
        get_solution_stack_mock.return_value = 'php7.1'
        create_app_mock.return_value = [
            '64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)',
            'my-ec2-key-name'
        ]
        pull_down_app_info_mock.return_value = [
            '64bit Amazon Linux 2014.03 v1.0.6 running PHP 7.1',
            'my-ec2-key-name'
        ]
        get_solution_stack_from_customer_mock.return_value = '64bit Amazon Linux 2014.03 v1.0.6 running PHP 7.1'
        get_keyname_mock.return_value = 'my-ec2-key-name'

        app = EB(
            argv=[
                'init',
                '--modules', 'module-1', 'module-2',
                '--interactive'
            ]
        )
        app.setup()
        app.run()

        setup_mock.assert_has_calls(
            [
                mock.call('my-application', 'us-east-1', 'Multi-container Docker 1.7.1 (Generic)'),
                mock.call('my-application', 'us-east-1', '64bit Amazon Linux 2014.03 v1.0.6 running PHP 7.1')
            ]
        )
        write_config_setting_mock.assert_has_calls(
            [
                mock.call('global', 'default_ec2_keyname', 'my-ec2-key-name'),
                mock.call('global', 'default_ec2_keyname', 'my-ec2-key-name')
            ]
        )
        create_app_mock.assert_called_once_with('my-application', default_env=None)
        pull_down_app_info_mock.assert_called_once_with('my-application', default_env=None)
        self.assertEqual(
            2,
            set_region_mock.call_count
        )

    @mock.patch('ebcli.controllers.initialize.aws.set_region')
    @mock.patch('ebcli.controllers.initialize.fileoperations.write_config_setting')
    @mock.patch('ebcli.controllers.initialize.InitController.get_solution_stack')
    @mock.patch('ebcli.controllers.initialize.InitController.get_app_name')
    @mock.patch('ebcli.controllers.initialize.InitController.get_keyname')
    @mock.patch('ebcli.controllers.initialize.set_up_credentials')
    @mock.patch('ebcli.controllers.initialize.commonops.create_app')
    @mock.patch('ebcli.controllers.initialize.commonops.pull_down_app_info')
    @mock.patch('ebcli.controllers.initialize.get_region_from_inputs')
    @mock.patch('ebcli.controllers.initialize.initializeops.setup')
    def test_multiple_modules__interactive_mode__solution_stack_in_env_yaml_is_used_when_available(
            self,
            setup_mock,
            get_region_from_inputs_mock,
            pull_down_app_info_mock,
            create_app_mock,
            set_up_credentials_mock,
            get_keyname_mock,
            get_app_name_mock,
            get_solution_stack_mock,
            write_config_setting_mock,
            set_region_mock
    ):
        os.mkdir('module-1')
        os.mkdir('module-2')
        with open(os.path.join('module-1', 'env.yaml'), 'w') as file:
            file.write("""AWSConfigurationTemplateVersion: 1.1.0.0
SolutionStack: 64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)
            """)

        get_app_name_mock.return_value = 'my-application'
        get_region_from_inputs_mock.return_value = 'us-east-1'
        set_up_credentials_mock.return_value = 'us-east-1'
        get_solution_stack_mock.return_value = '64bit Amazon Linux 2014.03 v1.0.6 running PHP 7.1'
        create_app_mock.return_value = [
            '64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)',
            'my-ec2-key-name'
        ]
        pull_down_app_info_mock.return_value = [
            '64bit Amazon Linux 2014.03 v1.0.6 running PHP 7.1',
            'my-ec2-key-name'
        ]
        get_keyname_mock.return_value = 'my-ec2-key-name'

        app = EB(
            argv=[
                'init',
                '--modules', 'module-1', 'module-2',
                '--platform', '64bit Amazon Linux 2014.03 v1.0.6 running PHP 7.1'
            ]
        )
        app.setup()
        app.run()

        setup_mock.assert_has_calls(
            [
                mock.call('my-application', 'us-east-1', '64bit Amazon Linux 2014.03 v1.0.6 running PHP 7.1'),
                mock.call('my-application', 'us-east-1', '64bit Amazon Linux 2014.03 v1.0.6 running PHP 7.1')
            ]
        )
        write_config_setting_mock.assert_has_calls(
            [
                mock.call('global', 'default_ec2_keyname', 'my-ec2-key-name'),
                mock.call('global', 'default_ec2_keyname', 'my-ec2-key-name')
            ]
        )
        create_app_mock.assert_called_once_with('my-application', default_env='/ni')
        pull_down_app_info_mock.assert_called_once_with('my-application', default_env='/ni')
        self.assertEqual(
            2,
            set_region_mock.call_count
        )
