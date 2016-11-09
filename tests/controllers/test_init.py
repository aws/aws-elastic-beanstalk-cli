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

from .basecontrollertest import BaseControllerTest

from ebcli.core import fileoperations
from ebcli.core.ebcore import EB
from ebcli.objects.exceptions import NotInitializedError, NoRegionError
from ebcli.objects.solutionstack import SolutionStack


class TestInit(BaseControllerTest):
    solution = SolutionStack('64bit Amazon Linux 2014.03 '
                             'v1.0.6 running PHP 5.5')
    app_name = 'ebcli-intTest-app'

    def setUp(self):
        self.module_name = 'initialize'
        super(TestInit, self).setUp()
        self.patcher_sshops = mock.patch('ebcli.controllers.initialize.sshops')
        self.mock_sshops = self.patcher_sshops.start()

    def tearDown(self):
        self.patcher_sshops.stop()
        super(TestInit, self).tearDown()

    def test_init_standard(self):
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
        self.mock_commonops.pull_down_app_info.return_value = None, None
        self.mock_commonops.get_default_keyname.return_value = ''
        self.mock_commonops.get_default_region.return_value = ''
        self.mock_commonops.get_default_solution_stack.return_value = ''

        self.mock_input.side_effect = [
            '3',  # region number
            self.app_name,  # Application name
            '1',  # Platform selection
            '1',  # Platform version selection
            'n',  # Set up ssh selection
        ]

        # run cmd
        self.app = EB(argv=['init'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # make sure setup was called correctly
        self.mock_operations.setup.assert_called_with(self.app_name,
                                                      'us-west-2',
                                                      'PHP 5.5', None, None, None)

    def test_init_interactive(self):
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
        self.mock_commonops.prompt_for_solution_stack.return_value = \
            self.solution
        self.mock_sshops.prompt_for_ec2_keyname.return_value = 'test'
        self.mock_commonops.pull_down_app_info.return_value = 'something', 'smthing'

        self.mock_input.side_effect = [
            '3',  # region number
            self.app_name,  # Application name
            '1',  # Platform selection
            '1',  # Platform version selection'
            'n',  # Set up ssh selection
        ]

        # run cmd
        self.app = EB(argv=['init', '-i'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # make sure setup was called correctly
        self.mock_operations.setup.assert_called_with(self.app_name,
                                                      'us-west-2',
                                                      'PHP 5.5', None, None, None)

    def test_init_no_creds(self):
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
        self.mock_commonops.create_app.return_value = None, None
        self.mock_commonops.get_default_keyname.return_value = ''
        self.mock_commonops.get_default_region.return_value = ''
        self.mock_commonops.get_default_solution_stack.return_value = ''

        # run cmd
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
                                                      'PHP 5.5', None, None, None)

    def test_init_script_mode(self):
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
        self.mock_commonops.create_app.return_value = None, None
        self.mock_commonops.get_default_keyname.return_value = ''
        self.mock_commonops.get_default_region.return_value = ''
        self.mock_commonops.get_default_solution_stack.return_value = ''

        # run cmd
        self.app = EB(argv=['init', '-p', 'php'])
        self.app.setup()
        self.app.run()
        self.app.close()

        self.mock_operations.setup.assert_called_with('testDir',
                                                      'us-west-2',
                                                      'php', None, None, None)

    @mock.patch('ebcli.controllers.initialize.SourceControl')
    def test_init_with_codecommit_source(self, mock_sourcecontrol):
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
        self.mock_commonops.create_app.return_value = None, None
        self.mock_commonops.get_default_keyname.return_value = ''
        self.mock_commonops.get_default_region.return_value = ''
        self.mock_commonops.get_default_solution_stack.return_value = ''

        # run cmd
        self.app = EB(argv=['init', '-p', 'ruby', '--source', 'CodeCommit/my-repo/prod', '--region', 'us-east-1'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # assert we ran the methods we intended too
        self.mock_operations.setup.assert_called_with('testDir',
                                                      'us-east-1',
                                                      'ruby', None, 'my-repo', 'prod')

        mock_sourcecontrol.setup_codecommit_cred_config.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.fileoperations.write_config_setting')
    @mock.patch('ebcli.controllers.initialize.codecommit')
    @mock.patch('ebcli.operations.gitops')
    def test_init_with_codecommit_prompt(self, mock_gitops, mock_codecommit, mock_fileoperations):
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
        self.mock_commonops.create_app.return_value = None, None
        self.mock_commonops.get_default_solution_stack.return_value = ''
        self.mock_commonops.pull_down_app_info.return_value = 'something', 'smthing'
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

        with mock.patch('ebcli.objects.sourcecontrol.Git') as MockGitClass:
            mock_git_sourcecontrol = MockGitClass.return_value
            mock_git_sourcecontrol.is_setup.return_value = "SourceControlObject"
            mock_git_sourcecontrol.get_current_commit.return_value = "CommitId"
            with mock.patch('ebcli.controllers.initialize.SourceControl') as MockSourceControlClass:
                mock_sourcecontrol = MockSourceControlClass.return_value
                mock_sourcecontrol.get_source_control.return_value = mock_git_sourcecontrol

            # run cmd
            self.app = EB(argv=['init', '--region', 'us-east-1', 'my-app'])
            self.app.setup()
            self.app.run()
            self.app.close()

        # assert we ran the methods we intended too
        self.mock_operations.setup.assert_called_with('my-app',
                                                      'us-east-1',
                                                      'PHP 5.5', None, 'new-repo', 'devo')


        mock_codecommit.create_repository.assert_called_once_with('new-repo','Created with EB CLI')
        mock_git_sourcecontrol.setup_new_codecommit_branch.assert_called_once_with(branch_name='devo')
        mock_codecommit.create_branch.assert_called_once_with('new-repo', 'devo', 'CommitId')
