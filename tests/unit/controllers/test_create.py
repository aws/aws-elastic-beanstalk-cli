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

from ebcli.controllers.create import elb_types
from ebcli.core import fileoperations
from ebcli.core.ebcore import EB
from ebcli.objects.exceptions import InvalidOptionsError
from ebcli.objects.requests import CreateEnvironmentRequest
from ebcli.objects.solutionstack import SolutionStack
from ebcli.objects.tier import Tier
from ebcli.operations import commonops


class TestCreate(BaseControllerTest):
    solution = SolutionStack('64bit Amazon Linux 2014.03 '
                             'v1.0.6 running PHP 5.5')
    app_name = 'ebcli-intTest-app'
    env_name = 'create-env'
    tier = Tier.get_all_tiers()[0]

    nlb_supported_regions = [
        'us-east-1',
        'us-west-1',
        'us-west-2',
        'eu-west-1',
        'eu-central-1',
        'ap-south-1',
        'ap-southeast-1',
        'ap-southeast-2',
        'ap-northeast-1',
        'ap-northeast-2',
        'sa-east-1',
        'us-east-2',
        'ca-central-1',
        'eu-west-2'
    ]

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
        cname_prefix = env_name
        self.mock_commonops.get_solution_stack.return_value = self.solution
        self.mock_commonops.is_cname_available.return_value = True
        self.mock_commonops.get_default_keyname = commonops.get_default_keyname

        self.mock_input.side_effect = [
            env_name,
            cname_prefix,
            '1',  # tier selection
        ]

        # run cmd
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['create'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # make sure make_new_env was called correctly
        env_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=env_name,
            cname=cname_prefix,
            platform=self.solution,
            elb_type='classic'
        )
        args, kwargs = self.mock_operations.make_new_env.call_args
        self.assertEqual(args[0], env_request)

    def test_create_defaults(self):
        """
                testing for:
                1. Return None on all prompts (Using defaults),
                as if just hitting enter
            """
        env_name = 'my-awesome-env'
        cname_prefix = 'myenv-cname'
        self.mock_commonops.get_solution_stack.return_value = self.solution
        self.mock_commonops.is_cname_available.return_value = True
        self.mock_commonops.get_default_keyname = commonops.get_default_keyname

        self.mock_input.return_value = None

        # run cmd
        # (don't test elb_type prompt as None causes it to fail)
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['create', '--elb-type', 'classic'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # make sure make_new_env was called correctly
        env_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=self.app_name + '-dev',
            cname=self.app_name + '-dev',
            platform=self.solution,
            elb_type='classic'
        )
        args, kwargs = self.mock_operations.make_new_env.call_args
        self.assertEqual(args[0], env_request)

    @mock.patch('ebcli.core.io.log_error')
    def test_create_sample_and_label(self, mock_error):
        """
                Pass in sample and and  version label
                Should get an error
            """
        env_name = 'my-awesome-env'
        cname_prefix = 'myenv-cname'
        self.mock_commonops.get_solution_stack.return_value = self.solution
        self.mock_commonops.is_cname_available.return_value = True

        self.mock_input.return_value = None

        # run cmd
        try:
            EB.Meta.exit_on_close = False
            self.app = EB(argv=['create', '--sample', '--version', 'myVers'])
            self.app.setup()
            self.app.run()
            self.app.close()
        except InvalidOptionsError:
            #Expected
            pass
        else:
            # Make sure error happened
            self.fail("Expected call to throw an InvalidOptionsError")

        self.assertEqual(self.mock_operations.make_new_env.call_count, 0)

    def test_create_script_mode(self):
        """
        Provide env name and tier and elb_type as command line options.
        Command should now no longer be interactive and it should ask no questions.
        """
        env_name = 'my-awesome-env'
        self.mock_commonops.get_solution_stack.return_value = self.solution

        EB.Meta.exit_on_close = False
        self.app = EB(argv=['create', env_name, '--elb-type', 'classic'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # Make sure input was never called
        self.assertEqual(self.mock_input.call_count, 0)

    def test_all_options(self):
        env_name = 'my-awesome-env'
        cname_prefix = env_name + '1'
        profile = 'myprofile'
        tier = self.tier
        itype = 'c3.large'
        keyname ='mykey'
        self.mock_commonops.get_solution_stack.return_value = self.solution
        self.mock_commonops.is_cname_available.return_value = True
        self.mock_operations.get_and_validate_tags.return_value = [{'Key': 'a', 'Value': '1'}, {'Key': 'b', 'Value': '2'}]

        self.mock_input.side_effect = [
            env_name,
            cname_prefix,
            '1',  # tier selection
        ]

        # run cmd
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['create', env_name, '-c', cname_prefix,
                            '-ip', profile, '-r', 'us-east-1',
                            '-t', 'web', '-i', itype, '-p', self.solution.name,
                            '--sample', '-d', '-k', keyname, '--scale', '3',
                            '--tags', 'a=1,b=2', '--elb-type', 'classic'])
        self.app.setup()
        self.app.run()
        self.app.close()

        # make sure make_new_env was called correctly
        env_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=env_name,
            cname=cname_prefix,
            platform=self.solution,
            instance_profile=profile,
            tier=tier,
            sample_application=True,
            instance_type=itype,
            key_name=keyname,
            scale=3,
            tags=[{'Key': 'a', 'Value': '1'}, {'Key': 'b', 'Value': '2'}],
            elb_type='classic'
        )
        args, kwargs = self.mock_operations.make_new_env.call_args
        self.assertEqual(args[0], env_request)
        self.assertEqual(kwargs['branch_default'], True)

    def test_create_with_process_flag(self):
        self.mock_commonops.get_solution_stack.return_value = self.solution
        self.mock_commonops.is_cname_available.return_value = True
        self.mock_commonops.get_default_keyname = commonops.get_default_keyname

        # run cmd
        EB.Meta.exit_on_close = False
        self.app = EB(argv=['create', '--process', self.env_name])
        self.app.setup()
        self.app.run()
        self.app.close()

        # make sure make_new_env was called correctly
        env_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=self.env_name,
            platform=self.solution,
        )
        args, kwargs = self.mock_operations.make_new_env.call_args
        self.assertEqual(args[0], env_request)
        self.mock_operations.make_new_env.assert_called_with(env_request,
                                                             branch_default=False,
                                                             process_app_version=True,
                                                             nohang=False,
                                                             interactive=False,
                                                             timeout=None,
                                                             source=None)

    def test_elb_types__region_explicitly_passed_in__nlb_restricted_regions(self):
        for region in ['cn-north-1', 'us-gov-west-1']:
            self.assertEqual(['classic', 'application'], elb_types(region))

    def test_elb_types__region_explicitly_passed_in__nlb_allowed_regions(self):
        for region in self.nlb_supported_regions:
            self.assertEqual(['classic', 'application', 'network'], elb_types(region))

    def test_elb_types__region_not_passed_in_through_command_line__nlb_restricted_regions(self):
        for region in ['cn-north-1', 'us-gov-west-1']:
            self.mock_commonops.get_default_region.return_value = region

            self.assertEqual(['classic', 'application'], elb_types(None))

    def test_elb_types__region_not_passed_in_through_command_line__nlb_allowed_regions(self):
        for region in self.nlb_supported_regions:
            self.mock_commonops.get_default_region.return_value = region

            self.assertEqual(['classic', 'application', 'network'], elb_types(None))
