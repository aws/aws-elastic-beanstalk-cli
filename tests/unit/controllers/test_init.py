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

import unittest
import mock

from .basecontrollertest import BaseControllerTest

from ebcli.core import fileoperations
from ebcli.core.ebcore import EB
from ebcli.objects.exceptions import NotInitializedError, NoRegionError
from ebcli.objects.solutionstack import SolutionStack
from ebcli.objects.buildconfiguration import BuildConfiguration


class TestInit(BaseControllerTest):
    solution = SolutionStack('64bit Amazon Linux 2014.03 '
                             'v1.0.6 running PHP 5.5')
    app_name = 'ebcli-intTest-app'

    def setUp(self):
        self.module_name = 'initialize'
        super(TestInit, self).setUp()
        self.patcher_sshops = mock.patch('ebcli.controllers.initialize.sshops')
        self.patcher_elasticbeanstalk = mock.patch('ebcli.controllers.initialize.elasticbeanstalk')
        self.mock_sshops = self.patcher_sshops.start()
        self.mock_eb = self.patcher_elasticbeanstalk.start()

    def tearDown(self):
        self.patcher_sshops.stop()
        self.patcher_elasticbeanstalk.stop()

        super(TestInit, self).tearDown()

    @mock.patch('ebcli.objects.sourcecontrol.Git')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    def test_init_standard(self, mock_sourcecontrol, mock_git):
        """
                testing for:
                1. Prompt for a region
                2. Prompt for app name: no apps exist
            """
        # Set up mock responses
        # 1. Get Credentials: throw no region error
        # 2. Get Credentials: good
        # 3. Create app
        self.mock_commonops.get_application_names.return_value = list()
        self.mock_operations.credentials_are_valid.side_effect = [
            NoRegionError,
            True,
        ]
        self.mock_commonops.prompt_for_solution_stack.return_value = \
            self.solution
        self.mock_sshops.prompt_for_ec2_keyname.return_value = 'test'
        self.mock_commonops.get_current_branch_environment.side_effect = \
            NotInitializedError,
        self.mock_eb.application_exist.return_value = False
        self.mock_commonops.create_app.return_value = None, None
        self.mock_commonops.get_default_keyname.return_value = ''
        self.mock_commonops.get_default_region.return_value = ''
        self.mock_commonops.get_default_solution_stack.return_value = ''
        # Mock out source control so we don't depend on git
        mock_sourcecontrol.get_source_control.return_value = mock_git
        mock_git.is_setup.return_value = None

        self.mock_input.side_effect = [
            '3',  # region number
            self.app_name,  # Application name
            '1',  # Platform selection
            '1',  # Platform version selection
            'n',  # Set up ssh selection
        ]

        # run cmd
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['init'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # make sure setup was called correctly
        self.mock_operations.setup.assert_called_with(self.app_name,
                                                      'us-west-2',
                                                      'PHP 5.5', branch=None, dir_path=None, repository=None)

    @mock.patch('ebcli.objects.sourcecontrol.Git')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    def test_init_interactive(self, mock_sourcecontrol, mock_git):
        """
        Tests that interactive mode correctly asks for all new values
        """

        # First, set up config file to contain all values
        fileoperations.create_config_file('app1', 'us-west-1', 'random')

        # Set up mock responses
        # 1. Get solution stacks
        # 2. Get solution stacks again
        # 3. Create app
        self.mock_commonops.get_application_names.return_value = list()
        self.mock_operations.credentials_are_valid.return_value = True
        self.mock_eb.application_exist.return_value = False
        self.mock_commonops.create_app.return_value = 'ss-stack', 'key'
        self.mock_commonops.prompt_for_solution_stack.return_value = \
            self.solution
        self.mock_sshops.prompt_for_ec2_keyname.return_value = 'test'

        self.mock_input.side_effect = [
            '3',  # region number
            self.app_name,  # Application name
            '1',  # Platform selection
            '1',  # Platform version selection'
            'n',  # Set up ssh selection
        ]

        # Mock out source control so we don't depend on git
        mock_sourcecontrol.get_source_control.return_value = mock_git
        mock_git.is_setup.return_value = None

        # run cmd
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['init', '-i'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # make sure setup was called correctly
        self.mock_operations.setup.assert_called_with(self.app_name,
                                                      'us-west-2',
                                                      'PHP 5.5', branch=None, dir_path=None, repository=None)

    @mock.patch('ebcli.objects.sourcecontrol.Git')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    def test_init_no_creds(self, mock_sourcecontrol, mock_git):
        """
        Test that we prompt for credentials
        """

        # setup mock response
        self.mock_operations.credentials_are_valid.return_value = False
        self.mock_commonops.prompt_for_solution_stack.return_value = \
            self.solution
        self.mock_sshops.prompt_for_ec2_keyname.return_value = 'test'
        self.mock_commonops.get_current_branch_environment.side_effect = \
            NotInitializedError,
        self.mock_eb.application_exist.return_value = True
        self.mock_commonops.pull_down_app_info.return_value = 'ss-stack', 'key'
        self.mock_commonops.get_default_keyname.return_value = ''
        self.mock_commonops.get_default_region.return_value = ''
        self.mock_commonops.get_default_solution_stack.return_value = ''

        # Mock out source control so we don't depend on git
        mock_sourcecontrol.get_source_control.return_value = mock_git
        mock_git.is_setup.return_value = None

        # run cmd
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['init',
                            self.app_name,
                            '-r', 'us-west-2'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # make sure we setup credentials
        self.mock_operations.setup_credentials.assert_called_with()
        self.mock_operations.setup.assert_called_with(self.app_name,
                                                      'us-west-2',
                                                      'ss-stack', branch=None, dir_path=None, repository=None)

    @mock.patch('ebcli.objects.sourcecontrol.Git')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    def test_init_script_mode(self, mock_sourcecontrol, mock_git):
        """
        Test that we prompt for credentials
        """

        # setup mock response
        self.mock_operations.credentials_are_valid.side_effect = [
            NoRegionError,
            True
        ]
        self.mock_commonops.prompt_for_solution_stack.return_value = Exception
        self.mock_sshops.prompt_for_ec2_keyname.return_value = Exception
        self.mock_commonops.get_current_branch_environment.side_effect = \
            NotInitializedError,
        self.mock_eb.application_exist.return_value = True
        self.mock_commonops.pull_down_app_info.return_value = 'ss-stack', 'key'
        self.mock_commonops.get_default_keyname.return_value = ''
        self.mock_commonops.get_default_region.return_value = 'us-west-2'
        self.mock_commonops.get_default_solution_stack.return_value = ''

        # Mock out source control so we don't depend on git
        mock_sourcecontrol.get_source_control.return_value = mock_git
        mock_git.is_setup.return_value = None

        # run cmd
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['init', '-p', 'php'])
        self.app.setup()
        self.app.run()
        self.app.close()

        self.mock_operations.setup.assert_called_with('testDir',
                                                      'us-west-2',
                                                      'php', branch=None, dir_path=None, repository=None)

    @mock.patch('ebcli.objects.sourcecontrol.Git')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    def test_init_with_codecommit_source(self, mock_sourcecontrol, mock_git):
        """
        Test that we prompt for
        """

        # setup mock response
        self.mock_operations.credentials_are_valid.side_effect = [
            NoRegionError,
            True
        ]
        self.mock_commonops.prompt_for_solution_stack.return_value = Exception
        self.mock_sshops.prompt_for_ec2_keyname.return_value = Exception
        self.mock_commonops.get_current_branch_environment.side_effect = \
            NotInitializedError,
        self.mock_eb.application_exist.return_value = False
        self.mock_commonops.create_app.return_value = None, None
        self.mock_commonops.get_default_keyname.return_value = ''
        self.mock_commonops.get_default_region.return_value = ''
        self.mock_commonops.get_default_solution_stack.return_value = ''

        # Mock out source control so we don't depend on git
        mock_sourcecontrol.get_source_control.return_value = mock_git
        mock_git.is_setup.return_value = None

        # run cmd
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['init', '-p', 'ruby', '--source', 'CodeCommit/my-repo/prod', '--region', 'us-east-1'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # assert we ran the methods we intended too
        self.mock_operations.setup.assert_called_with('testDir',
                                                      'us-east-1',
                                                      'ruby', dir_path=None, repository='my-repo', branch='prod')

        mock_sourcecontrol.setup_codecommit_cred_config.assert_not_called()

    @mock.patch('ebcli.objects.sourcecontrol.Git')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    @mock.patch('ebcli.controllers.initialize.fileoperations.write_config_setting')
    @mock.patch('ebcli.controllers.initialize.codecommit')
    @mock.patch('ebcli.operations.gitops')
    def test_init_with_codecommit_prompt(self, mock_gitops, mock_codecommit, mock_fileoperations, mock_sourcecontrol, mock_git):
        """
        Tests that interactive mode correctly asks for all new values
        """
        # First, set up config file to contain all values
        fileoperations.create_config_file('app1', 'us-west-1', 'random')

        # Set up mock responses
        # 1. Get solution stacks
        # 2. Get solution stacks again
        # 3. Create app
        self.mock_operations.credentials_are_valid.return_value = True
        self.mock_commonops.pull_down_app_info.return_value = None, None
        self.mock_commonops.create_app.return_value = None, None
        self.mock_commonops.get_default_solution_stack.return_value = ''
        self.mock_commonops.prompt_for_solution_stack.return_value = \
            self.solution

        # Mocks for getting into CodeCommit interactive mode
        mock_gitops.git_management_enabled.return_value = False

        mock_codecommit.list_repositories.return_value = {'repositories': [{'repositoryName': 'only-repo'}]}
        mock_codecommit.list_branches.return_value = {'branches': ['only-branch']}
        mock_codecommit.get_repository.return_value =\
            {'repositoryMetadata': {'cloneUrlHttp': 'https://git-codecommit.fake.amazonaws.com/v1/repos/only-repo'}}

        # Mocks for setting up SSH
        self.mock_sshops.prompt_for_ec2_keyname.return_value = 'test'


        self.mock_input.side_effect = [
            'y',  # Yes to setup CodeCommit
            '2',  # Pick to create new repo
            'new-repo',  # set repo name
            '2',  # Pick first option for branch
            'devo',  #
            'n',  # Set up ssh selection
        ]

        # Mock out source control so we don't depend on git
        mock_sourcecontrol.get_source_control.return_value = mock_git
        mock_git.is_setup.return_value = 'GitSetup'
        mock_git.get_current_commit.return_value = 'CommitId'

        # run cmd
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['init', '--region', 'us-east-1', 'my-app'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # assert we ran the methods we intended too
        self.mock_operations.setup.assert_called_with('my-app',
                                                      'us-east-1',
                                                      'PHP 5.5', dir_path=None, repository='new-repo', branch='devo')


        mock_codecommit.create_repository.assert_called_once_with('new-repo','Created with EB CLI')
        mock_git.setup_new_codecommit_branch.assert_called_once_with(branch_name='devo')
        mock_codecommit.create_branch.assert_called_once_with('new-repo', 'devo', 'CommitId')

    @mock.patch('ebcli.objects.sourcecontrol.Git')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    @mock.patch('ebcli.controllers.initialize.fileoperations')
    def test_init_with_codebuild_buildspec_interactive_choice(self, mock_fileops, mock_sourcecontrol, mock_git):
        """
        Tests that interactive mode correctly asks for all new values
        """
        # Setup variables
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
        self.mock_commonops.get_application_names.return_value = list()
        self.mock_operations.credentials_are_valid.return_value = True
        self.mock_commonops.prompt_for_solution_stack.return_value = \
            self.solution
        mock_fileops.env_yaml_exists.return_value = None

        # Mock out operations for Codebuild Integration
        self.mock_eb.application_exist.return_value = False
        self.mock_commonops.create_app.return_value = None, None
        mock_fileops.build_spec_exists.return_value = True
        mock_fileops.get_build_configuration.return_value = build_config
        mock_fileops.buildspec_config_header = fileoperations.buildspec_config_header
        mock_fileops.buildspec_name = fileoperations.buildspec_name

        self.mock_operations.get_codebuild_image_from_platform.return_value = \
            [{u'name': u'aws/codebuild/eb-java-7-amazonlinux-64:2.1.6', u'description': u'Java 7 Running on Amazon Linux 64bit '},
             {u'name': expected_image, u'description': u'Java 8 Running on Amazon Linux 64bit '},
             {u'name': u'aws/codebuild/eb-ruby-1.9-amazonlinux-64:2.1.6', u'description': u'Ruby 1.9 Running on Amazon Linux 64bit '}]

        # Mock out getting the application information
        self.mock_sshops.prompt_for_ec2_keyname.return_value = 'test'
        self.mock_commonops.pull_down_app_info.return_value = 'something', 'smthing'

        self.mock_input.side_effect = [
            '3',  # region number
            self.app_name,  # Application name
            '2',  # Image Platform selection
            '2',  # Platform version selection
            'n',  # Set up ssh selection
        ]

        # Mock out source control so we don't depend on git
        mock_sourcecontrol.get_source_control.return_value = mock_git
        mock_git.is_setup.return_value = None

        # run cmd
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['init', '-i'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # make sure setup was called correctly
        self.mock_operations.setup.assert_called_with(self.app_name,
                                                      'us-west-2',
                                                      'PHP 5.5', branch=None, dir_path=None, repository=None)
        self.mock_operations.get_codebuild_image_from_platform.assert_called_with('PHP 5.5')

        write_config_calls = [mock.call('global', 'profile', 'eb-cli'),
                              mock.call(fileoperations.buildspec_config_header,
                                        'Image',
                                        expected_image,
                                        file=fileoperations.buildspec_name),
                              mock.call('global', 'default_ec2_keyname', 'test'),]
        mock_fileops.write_config_setting.assert_has_calls(write_config_calls)

    @mock.patch('ebcli.objects.sourcecontrol.Git')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    @mock.patch('ebcli.controllers.initialize.fileoperations')
    def test_init_with_codebuild_buildspec_non_interactive_choice(self, mock_fileops, mock_sourcecontrol, mock_git):
        """
        Tests that interactive mode correctly asks for all new values
        """
        # Setup variables
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
        self.mock_commonops.get_application_names.return_value = list()
        self.mock_operations.credentials_are_valid.return_value = True
        self.mock_commonops.prompt_for_solution_stack.return_value = \
            self.solution
        mock_fileops.env_yaml_exists.return_value = None

        # Mock out operations for Codebuild Integration
        self.mock_eb.application_exist.return_value = False
        self.mock_commonops.create_app.return_value = None, None
        self.mock_eb.application_exist.return_value = False
        mock_fileops.get_build_configuration.return_value = build_config
        mock_fileops.buildspec_config_header = fileoperations.buildspec_config_header
        mock_fileops.buildspec_name = fileoperations.buildspec_name

        self.mock_operations.get_codebuild_image_from_platform.return_value = \
             {u'name': expected_image, u'description': u'Java 8 Running on Amazon Linux 64bit '}

        # Mock out getting the application information
        self.mock_sshops.prompt_for_ec2_keyname.return_value = 'test'
        self.mock_commonops.pull_down_app_info.return_value = 'something', 'smthing'

        self.mock_input.side_effect = [
            '3',  # region number
            self.app_name,  # Application name
            '2',  # Platform version selection
            'n',  # Set up ssh selection
        ]

        # Mock out source control so we don't depend on git
        mock_sourcecontrol.get_source_control.return_value = mock_git
        mock_git.is_setup.return_value = None

        # run cmd
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['init', '-i'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # make sure setup was called correctly
        self.mock_operations.setup.assert_called_with(self.app_name,
                                                      'us-west-2',
                                                      'PHP 5.5', branch=None, dir_path=None, repository=None)
        self.mock_operations.get_codebuild_image_from_platform.assert_called_with('PHP 5.5')

        write_config_calls = [mock.call('global', 'profile', 'eb-cli'),
                              mock.call(fileoperations.buildspec_config_header,
                                        'Image',
                                        expected_image,
                                        file=fileoperations.buildspec_name),
                              mock.call('global', 'default_ec2_keyname', 'test'), ]
        mock_fileops.write_config_setting.assert_has_calls(write_config_calls)

    @mock.patch('ebcli.objects.sourcecontrol.Git')
    @mock.patch('ebcli.controllers.initialize.fileoperations')
    @mock.patch('ebcli.controllers.initialize.SourceControl')
    def test_init_with_codecommit_source_and_codebuild(self, mock_sourcecontrol, mock_fileops, mock_git):
        """
        Test that we prompt for
        """
        # Setup variables
        expected_image = 'aws/codebuild/eb-java-8-amazonlinux-64:2.1.6'
        compute_type = 'BUILD_GENERAL1_SMALL'
        service_role = 'eb-test'
        timeout = 60
        build_config = BuildConfiguration(image=None, compute_type=compute_type,
                                          service_role=service_role, timeout=timeout)

        # setup mock response
        # Mock out operations for Codebuild Integration
        mock_fileops.get_application_name.return_value = 'testDir'
        mock_fileops.get_platform_from_env_yaml.return_value = 'PHP 5.5'
        mock_fileops.build_spec_exists.return_value = True
        mock_fileops.get_build_configuration.return_value = build_config
        mock_fileops.buildspec_config_header = fileoperations.buildspec_config_header
        mock_fileops.buildspec_name = fileoperations.buildspec_name

        self.mock_operations.get_codebuild_image_from_platform.return_value = \
            {u'name': expected_image, u'description': u'PHP 5.5 Running on Amazon Linux 64bit '}

        # mockout other methods
        self.mock_operations.credentials_are_valid.side_effect = [
            NoRegionError,
            True
        ]
        self.mock_commonops.prompt_for_solution_stack.return_value = Exception
        self.mock_sshops.prompt_for_ec2_keyname.return_value = Exception
        self.mock_commonops.get_current_branch_environment.side_effect = \
            NotInitializedError,
        self.mock_eb.application_exist.return_value = False
        self.mock_commonops.create_app.return_value = None, None
        self.mock_commonops.get_default_keyname.return_value = ''
        self.mock_commonops.get_default_region.return_value = ''
        self.mock_commonops.get_default_solution_stack.return_value = ''

        # run cmd
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['init', '--source', 'CodeCommit/my-repo/prod', '--region', 'us-east-1'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # assert we ran the methods we intended too
        self.mock_operations.setup.assert_called_with('testDir',
                                                      'us-east-1',
                                                      'PHP 5.5', dir_path=None, repository='my-repo', branch='prod')

        mock_sourcecontrol.setup_codecommit_cred_config.assert_not_called()
        self.mock_operations.get_codebuild_image_from_platform.assert_called_with('PHP 5.5')
