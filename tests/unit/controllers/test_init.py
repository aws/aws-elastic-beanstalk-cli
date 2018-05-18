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

from ebcli.core import fileoperations
from ebcli.core.ebcore import EB
from ebcli.objects.exceptions import NotInitializedError, NoRegionError, ServiceError
from ebcli.objects.solutionstack import SolutionStack
from ebcli.objects.buildconfiguration import BuildConfiguration


class TestInit(unittest.TestCase):
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

    @mock.patch('ebcli.controllers.initialize.SourceControl.Git')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk.get_application_names')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops')
    @mock.patch('ebcli.controllers.initialize.sshops')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk')
    @mock.patch('ebcli.controllers.initialize.io.get_input')
    def test_init__interactive_mode(
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
        get_application_names_mock.get_application_names.return_value = list()
        initops_mock.credentials_are_valid.side_effect = [
            NoRegionError,
            True,
        ]

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

        get_input_mock.side_effect = [
            '3',  # region number
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
        solution_stack_ops_mock.get_solution_stack_from_customer.return_value = \
            self.solution
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
        initops_mock.setup.assert_called_with(self.app_name,
                                                      'us-west-2',
                                                      'PHP 5.5', branch=None, dir_path=None, repository=None)

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
        solution_stack_ops_mock.get_solution_stack_from_customer.return_value = \
            self.solution
        sshops_mock.prompt_for_ec2_keyname.return_value = 'test'
        commonops_mock.get_current_branch_environment.side_effect = \
            NotInitializedError
        elasticbeanstalk_mock.application_exist.return_value = True
        commonops_mock.pull_down_app_info.return_value = 'ss-stack', 'key'
        commonops_mock.get_default_keyname.return_value = ''
        commonops_mock.get_default_region.return_value = ''
        solution_stack_ops_mock.get_default_solution_stack.return_value = ''

        # Mock out source control so we don't depend on git
        sourcecontrol_mock.get_source_control.return_value = git_mock
        git_mock.is_setup.return_value = None

        app = EB(argv=['init',
                            self.app_name,
                            '-r', 'us-west-2'])
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
        initops_mock.credentials_are_valid.side_effect = [
            NoRegionError,
            True
        ]
        solution_stack_ops_mock.get_solution_stack_from_customer.return_value = Exception
        sshops_mock.prompt_for_ec2_keyname.return_value = Exception
        commonops_mock.get_current_branch_environment.side_effect = NotInitializedError,
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
            'ebcli-intTest-app',
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

        # Mock out source control so we don't depend on git
        sourcecontrol_mock.get_source_control.return_value = git_mock
        git_mock.is_setup.return_value = None

        app = EB(argv=['init', '-p', 'ruby', '--source', 'codecommit/my-repo/prod', '--region', 'us-east-1'])
        app.setup()
        app.run()

        # assert we ran the methods we intended too
        initops_mock.setup.assert_called_with(
            'ebcli-intTest-app',
            'us-east-1',
            'ruby',
            dir_path=None,
            repository='my-repo',
            branch='prod'
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

        # Mocks for getting into CodeCommit interactive mode
        gitops_mock.git_management_enabled.return_value = False

        codecommit_mock.list_repositories.return_value = {'repositories': [{'repositoryName': 'only-repo'}]}
        codecommit_mock.list_branches.return_value = {'branches': ['only-branch']}
        codecommit_mock.get_repository.return_value =\
            {'repositoryMetadata': {'cloneUrlHttp': 'https://git-codecommit.fake.amazonaws.com/v1/repos/only-repo'}}

        # Mocks for setting up SSH
        sshops_mock.prompt_for_ec2_keyname.return_value = 'test'

        get_input_mock.side_effect = [
            'y',  # Yes to setup CodeCommit
            '2',  # Pick to create new repo
            'new-repo',  # set repo name
            '2',  # Pick first option for branch
            'devo',  #
            'n',  # Set up ssh selection
        ]

        # Mock out source control so we don't depend on git
        sourcecontrol_mock.get_source_control.return_value = git_mock
        git_mock.is_setup.return_value = 'GitSetup'
        git_mock.get_current_commit.return_value = 'CommitId'

        app = EB(argv=['init', '--region', 'us-east-1', 'my-app'])
        app.setup()
        app.run()

        # assert we ran the methods we intended too
        initops_mock.setup.assert_called_with('my-app',
                                                      'us-east-1',
                                                      'PHP 5.5', dir_path=None, repository='new-repo', branch='devo')

        codecommit_mock.create_repository.assert_called_once_with('new-repo','Created with EB CLI')
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
        build_config = BuildConfiguration(image=None, compute_type=compute_type,
                                          service_role=service_role, timeout=timeout)

        # First, set up config file to contain all values
        fileoperations.create_config_file('app1', 'us-west-1', 'random')

        get_application_names_mock.get_application_names.return_value = list()
        initops_mock.credentials_are_valid.return_value = True
        solution_stack_ops_mock.get_solution_stack_from_customer.return_value = \
            self.solution
        fileoperations_mock.env_yaml_exists.return_value = None

        # Mock out operations for Codebuild Integration
        elasticbeanstalk_mock.application_exist.return_value = False
        commonops_mock.create_app.return_value = None, None
        fileoperations_mock.build_spec_exists.return_value = True
        fileoperations_mock.get_build_configuration.return_value = build_config
        fileoperations_mock.buildspec_config_header = fileoperations.buildspec_config_header
        fileoperations_mock.buildspec_name = fileoperations.buildspec_name

        initops_mock.get_codebuild_image_from_platform.return_value = \
            [{u'name': u'aws/codebuild/eb-java-7-amazonlinux-64:2.1.6', u'description': u'Java 7 Running on Amazon Linux 64bit '},
             {u'name': expected_image, u'description': u'Java 8 Running on Amazon Linux 64bit '},
             {u'name': u'aws/codebuild/eb-ruby-1.9-amazonlinux-64:2.1.6', u'description': u'Ruby 1.9 Running on Amazon Linux 64bit '}]

        # Mock out getting the application information
        sshops_mock.prompt_for_ec2_keyname.return_value = 'test'
        commonops_mock.pull_down_app_info.return_value = 'something', 'smthing'

        get_input_mock.side_effect = [
            '3',  # region number
            self.app_name,  # Application name
            '2',  # Image Platform selection
            '2',  # Platform version selection
            'n',  # Set up ssh selection
        ]

        # Mock out source control so we don't depend on git
        sourcecontrol_mock.get_source_control.return_value = git_mock
        git_mock.is_setup.return_value = None

        app = EB(argv=['init', '-i'])
        app.setup()
        app.run()

        # make sure setup was called correctly
        initops_mock.setup.assert_called_with(self.app_name,
                                                      'us-west-2',
                                                      'PHP 5.5', branch=None, dir_path=None, repository=None)
        initops_mock.get_codebuild_image_from_platform.assert_called_with('PHP 5.5')

        write_config_calls = [mock.call('global', 'profile', 'eb-cli'),
                              mock.call(fileoperations.buildspec_config_header,
                                        'Image',
                                        expected_image,
                                        file=fileoperations.buildspec_name),
                              mock.call('global', 'default_ec2_keyname', 'test'),]
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
        build_config = BuildConfiguration(image=None, compute_type=compute_type,
                                          service_role=service_role, timeout=timeout)

        # First, set up config file to contain all values
        fileoperations.create_config_file('app1', 'us-west-1', 'random')

        # Set up mock responses
        # 1. Get solution stacks
        # 2. Get solution stacks again
        # 3. Create app
        get_application_names_mock.return_value = list()
        initops_mock.credentials_are_valid.return_value = True
        solution_stack_ops_mock.get_solution_stack_from_customer.return_value = \
            self.solution
        fileoperations_mock.env_yaml_exists.return_value = None

        # Mock out operations for Codebuild Integration
        elasticbeanstalk_mock.application_exist.return_value = False
        commonops_mock.create_app.return_value = None, None
        elasticbeanstalk_mock.application_exist.return_value = False
        fileoperations_mock.get_build_configuration.return_value = build_config
        fileoperations_mock.buildspec_config_header = fileoperations.buildspec_config_header
        fileoperations_mock.buildspec_name = fileoperations.buildspec_name

        initops_mock.get_codebuild_image_from_platform.return_value = \
             {u'name': expected_image, u'description': u'Java 8 Running on Amazon Linux 64bit '}

        # Mock out getting the application information
        sshops_mock.prompt_for_ec2_keyname.return_value = 'test'
        commonops_mock.pull_down_app_info.return_value = 'something', 'smthing'

        get_input_mock.side_effect = [
            '3',  # region number
            self.app_name,  # Application name
            '2',  # Platform version selection
            'n',  # Set up ssh selection
        ]

        # Mock out source control so we don't depend on git
        sourcecontrol_mock.get_source_control.return_value = git_mock
        git_mock.is_setup.return_value = None

        app = EB(argv=['init', '-i'])
        app.setup()
        app.run()

        # make sure setup was called correctly
        initops_mock.setup.assert_called_with(self.app_name,
                                                      'us-west-2',
                                                      'PHP 5.5', branch=None, dir_path=None, repository=None)
        initops_mock.get_codebuild_image_from_platform.assert_called_with('PHP 5.5')

        write_config_calls = [mock.call('global', 'profile', 'eb-cli'),
                              mock.call(fileoperations.buildspec_config_header,
                                        'Image',
                                        expected_image,
                                        file=fileoperations.buildspec_name),
                              mock.call('global', 'default_ec2_keyname', 'test'), ]
        fileoperations_mock.write_config_setting.assert_has_calls(write_config_calls)

    @mock.patch('ebcli.controllers.initialize.codecommit')
    @mock.patch('ebcli.controllers.initialize.fileoperations')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops')
    @mock.patch('ebcli.controllers.initialize.sshops')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk')
    def test_init_with_codecommit_source_and_codebuild(
            self,
            elasticbeanstalk_mock,
            commonops_mock,
            initops_mock,
            sshops_mock,
            solution_stack_ops_mock,
            sourcecontrol_mock,
            fileoperations_mock,
            codecommit_mock
    ):
        expected_image = 'aws/codebuild/eb-java-8-amazonlinux-64:2.1.6'
        compute_type = 'BUILD_GENERAL1_SMALL'
        service_role = 'eb-test'
        timeout = 60
        build_config = BuildConfiguration(image=None, compute_type=compute_type,
                                          service_role=service_role, timeout=timeout)

        codecommit_mock.side_effect = None
        fileoperations_mock.get_application_name.return_value = 'testDir'
        fileoperations_mock.get_platform_from_env_yaml.return_value = 'PHP 5.5'
        fileoperations_mock.build_spec_exists.return_value = True
        fileoperations_mock.get_build_configuration.return_value = build_config
        fileoperations_mock.buildspec_config_header = fileoperations.buildspec_config_header
        fileoperations_mock.buildspec_name = fileoperations.buildspec_name
        sourcecontrol_mock.setup_codecommit_remote_repo.side_effect = [
            ServiceError,
            None
        ]
        sourcecontrol_mock.setup_existing_codecommit_branch = mock.MagicMock()
        initops_mock.get_codebuild_image_from_platform.return_value = \
            {u'name': expected_image, u'description': u'PHP 5.5 Running on Amazon Linux 64bit '}

        solution_stack_ops_mock.get_solution_stack_from_customer.return_value = Exception
        sshops_mock.prompt_for_ec2_keyname.return_value = Exception
        commonops_mock.get_current_branch_environment.side_effect = \
            NotInitializedError
        elasticbeanstalk_mock.application_exist.return_value = False
        commonops_mock.create_app.return_value = None, None
        commonops_mock.get_default_keyname.return_value = ''
        commonops_mock.get_default_region.return_value = ''
        solution_stack_ops_mock.get_default_solution_stack.return_value = ''

        app = EB(argv=['init', '--source', 'CodeCommit/my-repo/prod', '--region', 'us-east-1'])
        app.setup()
        app.run()

        # assert we ran the methods we intended too
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
