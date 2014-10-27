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

from controllers.basecontrollertest import BaseControllerTest

from ebcli.core.ebcore import EB
from ebcli.objects.solutionstack import SolutionStack
from ebcli.core import fileoperations
from ebcli.objects.exceptions import NotInitializedError, NoRegionError


class TestInit(BaseControllerTest):
    solution = SolutionStack('64bit Amazon Linux 2014.03 '
                             'v1.0.6 running PHP 5.5')
    app_name = 'ebcli-intTest-app'

    def setUp(self):
        self.module_name = 'initialize'
        super(TestInit, self).setUp()

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
        self.mock_operations.get_application_names.return_value = list()
        self.mock_operations.credentials_are_valid.side_effect = [
            NoRegionError,
            True,
        ]
        self.mock_operations.prompt_for_solution_stack.return_value = \
            self.solution
        self.mock_operations.prompt_for_ec2_keyname.return_value = 'test'
        self.mock_operations.get_current_branch_environment.side_effect = \
            NotInitializedError,
        self.mock_operations.create_app.return_value = None, None

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
                                                      'PHP 5.5')

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
        self.mock_operations.get_application_names.return_value = list()
        self.mock_operations.credentials_are_valid.return_value = True
        self.mock_operations.prompt_for_solution_stack.return_value = \
            self.solution
        self.mock_operations.prompt_for_ec2_keyname.return_value = 'test'
        self.mock_operations.create_app.return_value = 'something', 'smthing'

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
                                                      'PHP 5.5')

    def test_init_no_creds(self):
        """
        Test that we prompt for credentials
        """

        # setup mock response
        self.mock_operations.credentials_are_valid.return_value = False
        self.mock_operations.prompt_for_solution_stack.return_value = \
            self.solution
        self.mock_operations.prompt_for_ec2_keyname.return_value = 'test'
        self.mock_operations.get_current_branch_environment.side_effect = \
            NotInitializedError,
        self.mock_operations.create_app.return_value = None, None

        # run cmd
        self.app = EB(argv=['init',
                            self.app_name,
                            '-r', 'us-west-2'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # make sure we setup credentials
        self.mock_operations.setup_credentials.assert_called()
        self.mock_operations.setup.assert_called_with(self.app_name,
                                                      'us-west-2',
                                                      'PHP 5.5')

    def test_init_script_mode(self):
        """
        Test that we prompt for credentials
        """

        # setup mock response
        self.mock_operations.credentials_are_valid.side_effect = [
            NoRegionError,
            True
        ]
        self.mock_operations.prompt_for_solution_stack.return_value = Exception
        self.mock_operations.prompt_for_ec2_keyname.return_value = Exception
        self.mock_operations.get_current_branch_environment.side_effect = \
            NotInitializedError,
        self.mock_operations.create_app.return_value = None, None

        # run cmd
        self.app = EB(argv=['init', '-p', 'php'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # make sure we setup credentials
        self.mock_operations.setup_credentials.assert_called()
        self.mock_operations.setup.assert_called_with('testDir',
                                                      'us-west-2',
                                                      'php')
