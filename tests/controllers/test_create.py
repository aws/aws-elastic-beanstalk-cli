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

from controllers.basecontrollertest import BaseControllerTest

from ebcli.core.ebcore import EB
from ebcli.objects.solutionstack import SolutionStack
from ebcli.core import fileoperations
from ebcli.objects.tier import Tier


class TestCreate(BaseControllerTest):
    solution = SolutionStack('64bit Amazon Linux 2014.03 '
                             'v1.0.6 running PHP 5.5')
    app_name = 'ebcli-intTest-app'
    tier = Tier.get_latest_tiers()[0]

    def setUp(self):
        self.module_name = 'create'
        super(TestCreate, self).setUp()
        fileoperations.create_config_file(self.app_name, 'us-west-2',
                                          self.solution.string)

    def test_create_standard(self):
        """
                testing for:
                1. Prompt for env_name
                2. Prompt for cname prefix
                2. Prompt for environment tier
            """
        env_name = 'my-awesome-env'
        cname_prefix = 'myenv-cname'
        self.mock_operations.select_tier.return_value = self.tier
        self.mock_operations.get_solution_stack.return_value = self.solution
        self.mock_operations.is_cname_available.return_value = True

        self.mock_input.side_effect = [
            env_name,
            cname_prefix,
            '1',  # tier selection
        ]

        # run cmd
        self.app = EB(argv=['create'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # make sure make_new_env was called correctly
        self.mock_operations.make_new_env.assert_called_with(
            self.app_name,  #app name
            env_name,   # env name
            'us-west-2',  # region
            cname_prefix,  # cname
            self.solution,  # solution
            self.tier,  #tier
            None,  # label
            None,  # profile
            False,  # single
            None,  # key_name
            False,  # branch_default
            False,  # sample
            False,  # nohang
        )

    def test_create_defaults(self):
        """
                testing for:
                1. Return None on all prompts (Using defaults),
                as if just hitting enter
            """
        env_name = 'my-awesome-env'
        cname_prefix = 'myenv-cname'
        self.mock_operations.select_tier.return_value = self.tier
        self.mock_operations.get_solution_stack.return_value = self.solution
        self.mock_operations.is_cname_available.return_value = True

        self.mock_input.return_value = None

        # run cmd
        self.app = EB(argv=['create'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # make sure make_new_env was called correctly
        self.mock_operations.make_new_env.assert_called_with(
            self.app_name,  #app name
            self.app_name + '-dev',   # env name
            'us-west-2',  # region
            None,  # cname
            self.solution,  # solution
            self.tier,  #tier
            None,  # label
            None,  # profile
            False,  # single
            None,  # key_name
            False,  # branch_default
            False,  # sample
            False,  # nohang
        )

    @mock.patch('ebcli.core.io.log_error')
    def test_create_sample_and_label(self, mock_error):
        """
                Pass in sample and and  version label
                Should get an error
            """
        env_name = 'my-awesome-env'
        cname_prefix = 'myenv-cname'
        self.mock_operations.select_tier.return_value = self.tier
        self.mock_operations.get_solution_stack.return_value = self.solution
        self.mock_operations.is_cname_available.return_value = True

        self.mock_input.return_value = None

        # run cmd
        self.app = EB(argv=['create', '--sample', '--versionlabel', 'myVers'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # Make sure error happened
        mock_error.assert_called()
        self.assertEqual(self.mock_operations.make_new_env.call_count, 0)

    def test_create_scriptability(self):
        """
        Provide env name and tier as command line options.
        Command should now no longer be interactive and it should ask no questions.
        """
        env_name = 'my-awesome-env'
        self.mock_operations.select_tier.return_value = self.tier
        self.mock_operations.get_solution_stack.return_value = self.solution

        self.app = EB(argv=['create', '--env_name', env_name, '--tier',
                            self.tier.string])
        self.app.setup()
        self.app.run()
        self.app.close()

        # Make sure input was never called
        self.assertEqual(self.mock_input.call_count, 0)