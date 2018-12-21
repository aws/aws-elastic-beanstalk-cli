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

import mock
import unittest
from pytest_socket import disable_socket, enable_socket

from ebcli.controllers import create
from ebcli.core import fileoperations
from ebcli.core.ebcore import EB
from ebcli.objects.exceptions import AlreadyExistsError, InvalidOptionsError, NotFoundError
from ebcli.objects.requests import CreateEnvironmentRequest
from ebcli.objects.solutionstack import SolutionStack
from ebcli.objects.tier import Tier


class TestCreateBase(unittest.TestCase):
    solution = SolutionStack('64bit Amazon Linux 2014.03 v1.0.6 running PHP 5.5')
    app_name = 'ebcli-intTest-app'
    env_name = 'create-env'
    tier = Tier.get_default()

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

    def assertEnvironmentRequestsEqual(self, expected_request, actual_request):
        error_message = os.linesep.join(
            [
                'Expected::',
                '{}'.format(expected_request.__dict__),
                '',
                'Actual::',
                '{}'.format(actual_request.__dict__),
            ]
        )

        self.assertEqual(expected_request, actual_request, error_message)


class TestCreate(TestCreateBase):
    @mock.patch('ebcli.controllers.create.solution_stack_ops.find_solution_stack_from_string')
    def test_create__invalid_platform(
            self,
            find_solution_stack_from_string_mock
    ):
        self.app = EB(argv=['create', '--platform', 'invalid_platform'])
        self.app.setup()

        find_solution_stack_from_string_mock.side_effect = NotFoundError

        with self.assertRaises(NotFoundError):
            self.app.run()

    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    def test_create__cname_is_not_unique__raises_exception(self, is_cname_available_mock, find_solution_stack_from_string_mock):
        is_cname_available_mock.return_value = False
        find_solution_stack_from_string_mock.return_value = 'PHP 7.1'

        self.app = EB(argv=['create', '--cname', 'already-take-cname-prefix'])
        self.app.setup()

        with self.assertRaises(AlreadyExistsError) as context_manager:
            self.app.run()

        self.assertEqual(
            'The CNAME prefix already-take-cname-prefix is already in use.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    def test_create__tier_name_is_invalid__raises_exception(self, find_solution_stack_from_string_mock):
        find_solution_stack_from_string_mock.return_value = 'PHP 7.1'

        self.app = EB(argv=['create', '--tier', 'invalid_tier'])
        self.app.setup()

        with self.assertRaises(NotFoundError) as context_manager:
            self.app.run()

        self.assertEqual(
            'Provided tier "invalid_tier" does not appear to be valid',
            str(context_manager.exception)
        )

    def test_create__sample_and_version_arguments_passed_in__raises_exception(self):
        self.app = EB(argv=['create', '--sample', '--version', 'my_pp_version_label'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            'You cannot use the "--sample" and "--version" options together.',
            str(context_manager.exception)
        )

    def test_create__single_and_scale_together_provided_cause_an_exception(self):
        self.app = EB(argv=['create', '--single', '--scale', '1'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            'You cannot use the "--single" and "--scale" options together.',
            str(context_manager.exception)
        )

    def test_create__single_and_elb_type_together_provided_cause_an_exception(self):
        self.app = EB(argv=['create', '--single', '--elb-type', 'application'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            'You cannot use the "--single" and "--elb-type" options together.',
            str(context_manager.exception)
        )

    def test_create__worker_tier_with_elbsubnets_argument(self):
        self.app = EB(argv=['create', '--tier', 'worker', '--vpc.elbsubnets', 'my-subnet'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            'You can\'t use the "--tier worker" argument with the "--vpc.publicip", "--vpc.elbsubnets", or "--vpc.elbpublic" arguments.',
            str(context_manager.exception)
        )

    def test_create__worker_tier_with_elbpublic_argument(self):
        self.app = EB(argv=['create', '--tier', 'worker', '--vpc.elbpublic'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            'You can\'t use the "--tier worker" argument with the "--vpc.publicip", "--vpc.elbsubnets", or "--vpc.elbpublic" arguments.',
            str(context_manager.exception)
        )

    def test_create__single_instance_webserver_tier_with_elbsubnets_argument(self):
        self.app = EB(argv=['create', '--tier', 'webserver', '--single', '--vpc.elbsubnets', 'my-subnet'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            'You can\'t use the "--single" argument with the "--vpc.elbsubnets" or "--vpc.elbpublic" arguments.',
            str(context_manager.exception)
        )

    def test_create__single_instance_webserver_tier_with_elbpublic_argument(self):
        self.app = EB(argv=['create', '--tier', 'webserver', '--single', '--vpc.elbpublic'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            'You can\'t use the "--single" argument with the "--vpc.elbsubnets" or "--vpc.elbpublic" arguments.',
            str(context_manager.exception)
        )

    def test_create__single_instance_webserver_tier_with_elbsubnets_argument__tier_is_not_specified(self):
        self.app = EB(argv=['create', '--single', '--vpc.elbsubnets', 'my-subnet'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            'You can\'t use the "--single" argument with the "--vpc.elbsubnets" or "--vpc.elbpublic" arguments.',
            str(context_manager.exception)
        )

    def test_create__single_instance_webserver_tier_with_elbpublic_argument__tier_is_not_specified(self):
        self.app = EB(argv=['create', '--single', '--vpc.elbpublic'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            'You can\'t use the "--single" argument with the "--vpc.elbsubnets" or "--vpc.elbpublic" arguments.',
            str(context_manager.exception)
        )

    def test_create__worker_tier_with_publicip_argument(self):
        self.app = EB(argv=['create', '--tier', 'worker', '--vpc.publicip'])
        self.app.setup()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app.run()

        self.assertEqual(
            'You can\'t use the "--tier worker" argument with the "--vpc.publicip", "--vpc.elbsubnets", or "--vpc.elbpublic" arguments.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.core.io.get_input')
    @mock.patch('ebcli.controllers.create.get_unique_cname')
    @mock.patch('ebcli.controllers.create.get_unique_environment_name')
    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.operations.commonops.get_default_keyname')
    def test_create_interactive_standard(
            self,
            get_default_keyname_mock,
            is_cname_available_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
            get_unique_environment_name_mock,
            get_unique_cname_mock,
            get_input_mock
    ):
        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        is_cname_available_mock.return_value = True
        get_default_keyname_mock.return_value = None
        get_unique_environment_name_mock.return_value = self.app_name + '-dev'
        get_unique_cname_mock.return_value = 'my-awesome-env'

        env_name = 'my-awesome-env'
        cname_prefix = env_name
        load_balancer_choice = '1'

        get_input_mock.side_effect = [
            env_name,
            cname_prefix,
            load_balancer_choice,
        ]

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=env_name,
            cname=cname_prefix,
            platform=self.solution,
            elb_type='classic'
        )

        self.app = EB(argv=['create'])
        self.app.setup()
        self.app.run()

        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]

        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)
        self.assertEqual(3, get_input_mock.call_count)

    @mock.patch('ebcli.core.io.get_input')
    @mock.patch('ebcli.controllers.create.get_unique_cname')
    @mock.patch('ebcli.controllers.create.get_unique_environment_name')
    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.operations.commonops.get_default_keyname')
    def test_create_interactive_standard__webserver_single_instance(
            self,
            get_default_keyname_mock,
            is_cname_available_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
            get_unique_environment_name_mock,
            get_unique_cname_mock,
            get_input_mock
    ):
        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        is_cname_available_mock.return_value = True
        get_default_keyname_mock.return_value = None
        get_unique_environment_name_mock.return_value = self.app_name + '-dev'
        get_unique_cname_mock.return_value = 'my-awesome-env'

        env_name = 'my-awesome-env'
        cname_prefix = env_name

        get_input_mock.side_effect = [
            env_name,
            cname_prefix
        ]

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=env_name,
            cname=cname_prefix,
            platform=self.solution,
            single_instance=True
        )

        self.app = EB(argv=['create', '--single'])
        self.app.setup()
        self.app.run()

        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]

        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)
        self.assertEqual(2, get_input_mock.call_count)

    @mock.patch('ebcli.core.io.get_input')
    @mock.patch('ebcli.controllers.create.get_unique_environment_name')
    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.operations.commonops.get_default_keyname')
    def test_create_interactive_standard__worker_tier(
            self,
            get_default_keyname_mock,
            is_cname_available_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
            get_unique_environment_name_mock,
            get_input_mock
    ):
        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        is_cname_available_mock.return_value = True
        get_default_keyname_mock.return_value = None
        get_unique_environment_name_mock.return_value = self.app_name + '-dev'

        env_name = 'my-awesome-env'

        get_input_mock.side_effect = [
            env_name
        ]

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=env_name,
            platform=self.solution,
            tier=Tier.from_raw_string('worker'),
        )

        self.app = EB(argv=['create', '--tier', 'worker'])
        self.app.setup()
        self.app.run()

        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]

        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)
        self.assertEqual(1, get_input_mock.call_count)

    @mock.patch('ebcli.core.io.get_input')
    @mock.patch('ebcli.controllers.create.get_unique_environment_name')
    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.operations.commonops.get_default_keyname')
    def test_create_interactive_standard__worker_single_instance(
            self,
            get_default_keyname_mock,
            is_cname_available_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
            get_unique_environment_name_mock,
            get_input_mock
    ):
        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        is_cname_available_mock.return_value = True
        get_default_keyname_mock.return_value = None
        get_unique_environment_name_mock.return_value = self.app_name + '-dev'

        env_name = 'my-awesome-env'

        get_input_mock.side_effect = [
            env_name
        ]

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=env_name,
            platform=self.solution,
            single_instance=True,
            tier=Tier.from_raw_string('worker'),
        )

        self.app = EB(argv=['create', '--single', '--tier', 'worker'])
        self.app.setup()
        self.app.run()

        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]

        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)
        self.assertEqual(1, get_input_mock.call_count)

    @mock.patch('ebcli.core.io.get_input')
    @mock.patch('ebcli.controllers.create.get_unique_environment_name')
    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.operations.commonops.get_default_keyname')
    @mock.patch('ebcli.controllers.create.get_unique_cname')
    def test_create_interactive__simulate_hitting_enter_on_all_input_prompts_to_show_defaults_will_be_picked(
            self,
            get_unique_cname_mock,
            get_default_keyname_mock,
            is_cname_available_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
            get_unique_environment_name_mock,
            get_input_mock
    ):
        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.find_solution_stack_from_string.return_value = self.solution
        is_cname_available_mock.return_value = True
        get_default_keyname_mock.return_value = None
        get_unique_environment_name_mock.return_value = self.app_name + '-dev'
        get_unique_cname_mock.return_value = self.app_name + '-dev'
        get_input_mock.return_value = None

        self.app = EB(argv=['create', '--elb-type', 'classic'])
        self.app.setup()
        self.app.run()

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=self.app_name + '-dev',
            cname=self.app_name + '-dev',
            platform=self.solution,
            elb_type='classic'
        )
        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]
        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)
        self.assertEqual(2, get_input_mock.call_count)

    @mock.patch('ebcli.core.io.get_input')
    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    def test_create_non_interactive_mode(
            self,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
            get_input_mock
    ):
        """
        Provide env name and tier and elb_type as command line options.
        Command should now no longer be interactive and it should ask no questions.
        """
        env_name = 'my-awesome-env'
        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution

        self.app = EB(argv=['create', env_name, '--elb-type', 'classic'])
        self.app.setup()
        self.app.run()

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=env_name,
            cname=None,
            platform=self.solution,
            elb_type='classic'
        )
        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]
        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)
        self.assertEqual(0, get_input_mock.call_count)

    @mock.patch('ebcli.core.io.get_input')
    @mock.patch('ebcli.controllers.create.get_unique_environment_name')
    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.createops.get_and_validate_tags')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.operations.commonops.get_default_keyname')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    def test_non_interactive_mode__all_options(
            self,
            is_cname_available_mock,
            get_default_keyname_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            get_and_validate_tags_mock,
            make_new_env_mock,
            get_unique_environment_name_mock,
            get_input_mock
    ):
        env_name = 'my-awesome-env'
        cname_prefix = env_name + '1'
        application_load_balancer_choice = '1'
        profile = 'myprofile'
        tier = 'webserver'
        itype = 'c3.large'
        keyname ='mykey'
        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        get_default_keyname_mock.return_value = True
        is_cname_available_mock.return_value = True

        get_and_validate_tags_mock.return_value = [
            {'Key': 'a', 'Value': '1'},
            {'Key': 'b', 'Value': '2'}
        ]
        get_input_mock.side_effect = [
            env_name,
            cname_prefix,
            application_load_balancer_choice,
        ]
        get_unique_environment_name_mock.return_value = self.app_name + '-dev'

        self.app = EB(
            argv=[
                'create', env_name,
                '-c', cname_prefix,
                '-ip', profile,
                '-r', 'us-east-1',
                '-t', 'webserver',
                '-i', itype,
                '-p', self.solution.name,
                '-k', keyname,
                '--scale', '3',
                '--tags', 'a=1,b=2', '--elb-type', 'classic',
                '--envvars', 'DB_USER="root",DB_PASSWORD="password"',
                '-d',
                '--sample',
            ]
        )
        self.app.setup()
        self.app.run()

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=env_name,
            cname=cname_prefix,
            platform=self.solution,
            instance_profile=profile,
            tier=Tier.from_raw_string(tier),
            sample_application=True,
            instance_type=itype,
            key_name=keyname,
            scale=3,
            tags=[{'Key': 'a', 'Value': '1'}, {'Key': 'b', 'Value': '2'}],
            elb_type='classic'
        )
        expected_environment_request.option_settings = [
            {
             'Namespace': 'aws:elasticbeanstalk:application:environment',
             'OptionName': 'DB_USER',
             'Value': 'root'
            },
            {
             'Namespace': 'aws:elasticbeanstalk:application:environment',
             'OptionName': 'DB_PASSWORD',
             'Value': 'password'
            }
        ]

        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]

        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)
        self.assertEqual(kwargs['branch_default'], True)

    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.operations.commonops.get_default_keyname')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    def test_create_non_interactively__with_process_flag(
            self,
            is_cname_available_mock,
            get_default_keyname_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
    ):
        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        is_cname_available_mock.return_value = True
        get_default_keyname_mock.return_value = None

        self.app = EB(argv=['create', '--process', self.env_name])
        self.app.setup()
        self.app.run()

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=self.env_name,
            platform=self.solution,
        )
        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]
        self.assertEqual(actual_environment_request, expected_environment_request)
        make_new_env_mock.assert_called_with(
            expected_environment_request,
            branch_default=False,
            process_app_version=True,
            nohang=False,
            interactive=False,
            timeout=None,
            source=None
        )

    @mock.patch('ebcli.core.io.get_input')
    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    def test_create__env_yaml_present__environment_name_present_in_yaml_file__group_name_is_passed(
            self,
            is_cname_available_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
            get_input_mock
    ):
        with open('env.yaml', 'w') as env_yaml:
            env_yaml.write("""AWSConfigurationTemplateVersion: 1.1.0.0
SolutionStack: 64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)
CName: front-A08G28LG+
EnvironmentName: front+""")

        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        is_cname_available_mock.return_value = True

        self.app = EB(argv=['create', '--elb-type', 'network', '--cname', 'available-cname', '--env-group-suffix', 'dev'])
        self.app.setup()
        self.app.run()

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name='front-dev',
            cname='available-cname',
            platform=self.solution,
            elb_type='network',
            group_name='dev',
        )
        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]

        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)
        self.assertEqual(0, get_input_mock.call_count)

    @mock.patch('ebcli.core.io.get_input')
    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    def test_create__env_yaml_present__environment_name_present_in_yaml_file__group_name_is_passed__worker_tier(
            self,
            is_cname_available_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
            get_input_mock
    ):
        with open('env.yaml', 'w') as env_yaml:
            env_yaml.write("""AWSConfigurationTemplateVersion: 1.1.0.0
SolutionStack: 64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)
CName: front-A08G28LG+
EnvironmentName: front+""")

        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        is_cname_available_mock.return_value = True

        self.app = EB(argv=['create', '--tier', 'worker', '--env-group-suffix', 'dev'])
        self.app.setup()
        self.app.run()

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name='front-dev',
            platform=self.solution,
            group_name='dev',
            tier=Tier.from_raw_string('worker'),
        )
        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]
        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)
        self.assertEqual(0, get_input_mock.call_count)

    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    def test_create__env_yaml_present__environment_name_present_in_yaml_file__group_name_not_specified(
            self,
            is_cname_available_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
    ):
        with open('env.yaml', 'w') as env_yaml:
            env_yaml.write("""AWSConfigurationTemplateVersion: 1.1.0.0
SolutionStack: 64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)
CName: front-A08G28LG+
EnvironmentName: front+""")

        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        is_cname_available_mock.return_value = True

        with self.assertRaises(InvalidOptionsError) as context_manager:
            self.app = EB(argv=['create', '--elb-type', 'network', '--cname', 'available-cname'])
            self.app.setup()
            self.app.run()

        self.assertEqual(
            "The environment name specified in env.yaml ends with a '+', but no group suffix was provided. Please pass the --env-group-suffix argument.",
            str(context_manager.exception)
        )
        make_new_env_mock.assert_not_called()

    @mock.patch('ebcli.core.io.get_input')
    @mock.patch('ebcli.controllers.create.get_unique_environment_name')
    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    def test_create__env_yaml_present__environment_name_absent_in_yaml_file__customer_is_prompted_for_input__group_suffix_discarded(
            self,
            is_cname_available_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
            get_unique_environment_name_mock,
            get_input_mock
    ):
        with open('env.yaml', 'w') as env_yaml:
            env_yaml.write("""AWSConfigurationTemplateVersion: 1.1.0.0
SolutionStack: 64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)
CName: front-A08G28LG+""")

        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        is_cname_available_mock.return_value = True
        get_unique_environment_name_mock.return_value = self.app_name + '-dev'

        get_input_mock.side_effect = [
            'my-environment-name'
        ]
        self.app = EB(argv=['create', '--elb-type', 'network', '--cname', 'available-cname', '--env-group-suffix', 'dev'])
        self.app.setup()
        self.app.run()

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name='my-environment-name',
            cname='available-cname',
            platform=self.solution,
            elb_type='network',
            group_name='dev',
        )
        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]

        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)
        self.assertEqual(1, get_input_mock.call_count)


class TestCreateWithDatabaseAndVPC(TestCreateBase):
    @mock.patch('ebcli.core.io.get_input')
    @mock.patch('ebcli.controllers.create.get_unique_cname')
    @mock.patch('ebcli.controllers.create.get_unique_environment_name')
    @mock.patch('ebcli.core.io.get_pass')
    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.operations.commonops.get_default_keyname')
    def test_create_interactively_with_database__db_argument_triggers_interactive_database_options(
            self,
            get_default_keyname_mock,
            is_cname_available_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
            get_pass_mock,
            get_unique_environment_name_mock,
            get_unique_cname_mock,
            get_input_mock
    ):
        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        is_cname_available_mock.return_value = True
        get_default_keyname_mock.return_value = None
        get_unique_environment_name_mock.return_value = self.app_name + '-dev'
        get_unique_cname_mock.return_value = 'my-awesome-env'

        env_name = 'my-awesome-env'
        cname_prefix = env_name
        load_balancer_choice = '1'
        database_user_name = 'root'
        database_password = 'password'

        get_input_mock.side_effect = [
            env_name,
            cname_prefix,
            load_balancer_choice,
            database_user_name
        ]
        get_pass_mock.side_effect = [
            database_password
        ]

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=env_name,
            cname=cname_prefix,
            platform=self.solution,
            elb_type='classic',
            database={
                'username': 'root',
                'password': 'password',
                'engine': None,
                'size': None,
                'instance': None,
                'version': None
            },
        )

        self.app = EB(argv=['create', '-db'])
        self.app.setup()
        self.app.run()

        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]

        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)
        self.assertEqual(4, get_input_mock.call_count)
        self.assertEqual(1, get_pass_mock.call_count)

    @mock.patch('ebcli.core.io.get_input')
    @mock.patch('ebcli.core.io.get_pass')
    @mock.patch('ebcli.controllers.create.get_unique_cname')
    @mock.patch('ebcli.controllers.create.get_unique_environment_name')
    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.operations.commonops.get_default_keyname')
    def test_create_interactively_with_database__db_username_passed_in_password_requested(
            self,
            get_default_keyname_mock,
            is_cname_available_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
            get_unique_environment_name_mock,
            get_unique_cname_mock,
            get_pass_mock,
            get_input_mock
    ):
        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        is_cname_available_mock.return_value = True
        get_default_keyname_mock.return_value = None
        get_unique_cname_mock.return_value = 'my-awesome-env'
        get_unique_environment_name_mock.return_value = self.app_name + '-dev'

        env_name = 'my-awesome-env'
        cname_prefix = env_name
        load_balancer_choice = '1'
        database_password = 'password'

        get_input_mock.side_effect = [
            env_name,
            cname_prefix,
            load_balancer_choice
        ]
        get_pass_mock.side_effect = [
            database_password
        ]

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=env_name,
            cname=cname_prefix,
            platform=self.solution,
            elb_type='classic',
            database={
                'username': 'root',
                'password': 'password',
                'engine': None,
                'size': None,
                'instance': None,
                'version': None
            },
        )

        self.app = EB(argv=['create', '-db.user', 'root'])
        self.app.setup()
        self.app.run()

        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]

        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)
        self.assertEqual(3, get_input_mock.call_count)
        self.assertEqual(1, get_pass_mock.call_count)

    @mock.patch('ebcli.core.io.get_input')
    @mock.patch('ebcli.controllers.create.get_unique_cname')
    @mock.patch('ebcli.controllers.create.get_unique_environment_name')
    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.operations.commonops.get_default_keyname')
    def test_create_interactively_with_database__db_username_password_and_other_arguments_passed(
            self,
            get_default_keyname_mock,
            is_cname_available_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
            get_unique_environment_name_mock,
            get_unique_cname_mock,
            get_input_mock
    ):
        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        is_cname_available_mock.return_value = True
        get_default_keyname_mock.return_value = None
        get_unique_cname_mock.return_value = 'my-awesome-env'
        get_unique_environment_name_mock.return_value = self.app_name + '-dev'

        env_name = 'my-awesome-env'
        cname_prefix = env_name
        load_balancer_choice = '1'

        get_input_mock.side_effect = [
            env_name,
            cname_prefix,
            load_balancer_choice
        ]

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=env_name,
            cname=cname_prefix,
            platform=self.solution,
            elb_type='classic',
            database={
                'username': 'root',
                'password': 'password',
                'engine': 'mysql',
                'size': None,
                'instance': None,
                'version': '5.6.35'
            },
        )

        self.app = EB(argv=['create', '-db.user', 'root', '-db.pass', 'password', '-db.engine', 'mysql', '-db.version', '5.6.35'])
        self.app.setup()
        self.app.run()

        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]

        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)
        self.assertEqual(3, get_input_mock.call_count)

    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.operations.commonops.get_default_keyname')
    def test_create_non_interactively_with_database__db_username_password_and_other_arguments_passed(
            self,
            get_default_keyname_mock,
            is_cname_available_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
    ):
        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        is_cname_available_mock.return_value = True
        get_default_keyname_mock.return_value = None

        env_name = 'my-awesome-env'

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=env_name,
            platform=self.solution,
            elb_type='application',
            database={
                'username': 'root',
                'password': 'password',
                'engine': 'mysql',
                'size': '10',
                'instance': 'db.t2.micro',
                'version': '5.6.35'
            },
        )

        self.app = EB(
            argv=[
                'create', env_name,
                '--elb-type', 'application',
                '-db.user', 'root',
                '-db.pass', 'password',
                '-db.engine', 'mysql',
                '-db.version', '5.6.35',
                '-db.size', '10',
                '-db.i', 'db.t2.micro',
            ]
        )
        self.app.setup()
        self.app.run()

        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]

        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)

    @mock.patch('ebcli.core.io.get_input')
    @mock.patch('ebcli.controllers.create.get_unique_cname')
    @mock.patch('ebcli.controllers.create.get_unique_environment_name')
    @mock.patch('ebcli.core.io.get_boolean_response')
    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.operations.commonops.get_default_keyname')
    def test_create_interactively_with_custom_vpc__vpc_argument_triggers_interactive_vpc_options(
            self,
            get_default_keyname_mock,
            is_cname_available_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
            get_boolean_response_mock,
            get_unique_environment_name_mock,
            get_unique_cname_mock,
            get_input_mock
    ):
        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        is_cname_available_mock.return_value = True
        get_default_keyname_mock.return_value = None
        get_unique_environment_name_mock.return_value = self.app_name + '-dev'
        get_unique_cname_mock.return_value = 'my-awesome-env'

        env_name = 'my-awesome-env'
        cname_prefix = env_name
        load_balancer_choice = '1'
        vpc_id = 'my-vpc-id'
        ec2subnets = 'subnet-1,subnet-2,subnet-3'
        is_publicip = 'y'
        elbsubnets = 'subnet-1,subnet-2,subnet-3'
        securitygroups = 'security-group-1,security-group-2'
        is_elbpublic = 'n'

        get_input_mock.side_effect = [
            env_name,
            cname_prefix,
            load_balancer_choice,
            vpc_id,
            ec2subnets,
            elbsubnets,
            securitygroups
        ]
        get_boolean_response_mock.side_effect = [
            is_publicip,
            is_elbpublic
        ]

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=env_name,
            cname=cname_prefix,
            platform=self.solution,
            elb_type='classic',
            vpc={
                'id': 'my-vpc-id',
                'ec2subnets': 'subnet-1,subnet-2,subnet-3',
                'elbsubnets': 'subnet-1,subnet-2,subnet-3',
                'elbscheme': 'public',
                'publicip': 'true',
                'securitygroups': 'security-group-1,security-group-2',
                'dbsubnets': None
            }
        )

        self.app = EB(argv=['create', '--vpc'])
        self.app.setup()
        self.app.run()

        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]

        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)
        self.assertEqual(7, get_input_mock.call_count)
        self.assertEqual(2, get_boolean_response_mock.call_count)

    @mock.patch('ebcli.core.io.get_input')
    @mock.patch('ebcli.controllers.create.get_unique_environment_name')
    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.operations.commonops.get_default_keyname')
    def test_create_interactively_with_custom_vpc__vpc_argument_triggers_interactive_vpc_options__tier_type_worker(
            self,
            get_default_keyname_mock,
            is_cname_available_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
            get_unique_environment_name_mock,
            get_input_mock
    ):
        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        is_cname_available_mock.return_value = True
        get_default_keyname_mock.return_value = None
        get_unique_environment_name_mock.return_value = self.app_name + '-dev'

        env_name = 'my-awesome-env'
        vpc_id = 'my-vpc-id'
        ec2subnets = 'subnet-1,subnet-2,subnet-3'
        securitygroups = 'security-group-1,security-group-2'

        get_input_mock.side_effect = [
            env_name,
            vpc_id,
            ec2subnets,
            securitygroups
        ]

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=env_name,
            platform=self.solution,
            tier=Tier.from_raw_string('worker'),
            vpc={
                'id': 'my-vpc-id',
                'ec2subnets': 'subnet-1,subnet-2,subnet-3',
                'elbsubnets': None,
                'elbscheme': None,
                'publicip': None,
                'securitygroups': 'security-group-1,security-group-2',
                'dbsubnets': None
            }
        )

        self.app = EB(argv=['create', '--vpc', '--tier', 'worker'])
        self.app.setup()
        self.app.run()

        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]

        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)
        self.assertEqual(4, get_input_mock.call_count)

    @mock.patch('ebcli.core.io.get_input')
    @mock.patch('ebcli.controllers.create.get_unique_cname')
    @mock.patch('ebcli.controllers.create.get_unique_environment_name')
    @mock.patch('ebcli.core.io.get_boolean_response')
    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.operations.commonops.get_default_keyname')
    def test_create_interactively_with_custom_vpc__vpc_argument_triggers_interactive_vpc_options__single_instance_webserver(
            self,
            get_default_keyname_mock,
            is_cname_available_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
            get_boolean_response_mock,
            get_unique_environment_name_mock,
            get_unique_cname_mock,
            get_input_mock
    ):
        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        is_cname_available_mock.return_value = True
        get_default_keyname_mock.return_value = None
        get_unique_environment_name_mock.return_value = self.app_name + '-dev'
        get_unique_cname_mock.return_value = 'my-awesome-env'

        env_name = 'my-awesome-env'
        cname_prefix = env_name
        load_balancer_choice = '1'
        vpc_id = 'my-vpc-id'
        ec2subnets = 'subnet-1,subnet-2,subnet-3'
        is_publicip = 'y'
        securitygroups = 'security-group-1,security-group-2'

        get_input_mock.side_effect = [
            env_name,
            cname_prefix,
            vpc_id,
            ec2subnets,
            securitygroups
        ]
        get_boolean_response_mock.side_effect = [
            is_publicip,
        ]

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=env_name,
            cname=cname_prefix,
            platform=self.solution,
            single_instance=True,
            vpc={
                'id': 'my-vpc-id',
                'ec2subnets': 'subnet-1,subnet-2,subnet-3',
                'elbsubnets': None,
                'elbscheme': None,
                'publicip': 'true',
                'securitygroups': 'security-group-1,security-group-2',
                'dbsubnets': None
            }
        )

        self.app = EB(argv=['create', '--vpc', '--single'])
        self.app.setup()
        self.app.run()

        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]

        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)
        self.assertEqual(5, get_input_mock.call_count)
        self.assertEqual(1, get_boolean_response_mock.call_count)

    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.operations.commonops.get_default_keyname')
    def test_create_interactively_with_custom_vpc__vpc_argument_triggers_interactive_vpc_prompts__some_vpc_arguments_already_passed_in(
            self,
            get_default_keyname_mock,
            is_cname_available_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
    ):
        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        is_cname_available_mock.return_value = True
        get_default_keyname_mock.return_value = None

        env_name = 'my-awesome-env'

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=env_name,
            platform=self.solution,
            vpc={
                'id': 'my-vpc-id',
                'ec2subnets': 'subnet-1,subnet-2,subnet-3',
                'elbsubnets': 'subnet-1,subnet-2,subnet-3',
                'elbscheme': 'public',
                'publicip': 'true',
                'securitygroups': None,
                'dbsubnets': None
            }
        )

        self.app = EB(
            argv=[
                'create', env_name,
                '--vpc.id', 'my-vpc-id',
                '--vpc.ec2subnets', 'subnet-1,subnet-2,subnet-3',
                '--vpc.publicip',
                '--vpc.elbsubnets', 'subnet-1,subnet-2,subnet-3',
                '--vpc.elbpublic'
            ]
        )

        self.app.setup()
        self.app.run()

        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]

        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)

    @mock.patch('ebcli.core.io.get_input')
    @mock.patch('ebcli.core.io.get_boolean_response')
    @mock.patch('ebcli.core.io.get_pass')
    @mock.patch('ebcli.controllers.create.get_unique_cname')
    @mock.patch('ebcli.controllers.create.get_unique_environment_name')
    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.operations.commonops.get_default_keyname')
    def test_create_interactively_with_database_and_vpc_arguments(
            self,
            get_default_keyname_mock,
            is_cname_available_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
            get_unique_environment_name_mock,
            get_unique_cname_mock,
            get_pass_mock,
            get_boolean_response_mock,
            get_input_mock,
    ):
        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        is_cname_available_mock.return_value = True
        get_default_keyname_mock.return_value = None
        get_unique_environment_name_mock.return_value = self.app_name + '-dev'

        env_name = 'my-awesome-env'
        cname_prefix = env_name
        get_unique_cname_mock.return_value = cname_prefix
        load_balancer_choice = '1'
        database_user_name = 'root'
        database_password = 'password'

        vpc_id = 'my-vpc-id'
        ec2subnets = 'subnet-1,subnet-2,subnet-3'
        is_ec2_public = 'y'
        elbsubnets = 'subnet-1,subnet-2,subnet-3'
        securitygroups = 'security-group-1,security-group-2'
        is_elb_public = 'y'
        rdssubnets = 'subnet-1,subnet-2,subnet-3'

        get_input_mock.side_effect = [
            env_name,
            cname_prefix,
            load_balancer_choice,

            database_user_name,

            vpc_id,
            ec2subnets,
            elbsubnets,
            securitygroups,
            rdssubnets
        ]
        get_boolean_response_mock.side_effect = [
            is_ec2_public,
            is_elb_public
        ]
        get_pass_mock.side_effect = [
            database_password
        ]

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=env_name,
            cname=env_name,
            platform=self.solution,
            elb_type='classic',
            database={
                'username': 'root',
                'password': 'password',
                'engine': None,
                'size': None,
                'instance': None,
                'version': None
            },
            vpc={
                'id': 'my-vpc-id',
                'ec2subnets': 'subnet-1,subnet-2,subnet-3',
                'elbsubnets': 'subnet-1,subnet-2,subnet-3',
                'elbscheme': 'public',
                'publicip': 'true',
                'securitygroups': 'security-group-1,security-group-2',
                'dbsubnets': 'subnet-1,subnet-2,subnet-3',
            }
        )

        self.app = EB(
            argv=[
                'create', '-db', '--vpc',
            ]
        )

        self.app.setup()
        self.app.run()

        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]

        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)

    @mock.patch('ebcli.operations.createops.make_new_env')
    @mock.patch('ebcli.operations.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.operations.solution_stack_ops.get_solution_stack_from_customer')
    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.operations.commonops.get_default_keyname')
    def test_create_non_interactively_with_database_and_vpc_arguments(
            self,
            get_default_keyname_mock,
            is_cname_available_mock,
            find_solution_stack_from_string_mock,
            get_solution_stack_from_customer_mock,
            make_new_env_mock,
    ):
        get_solution_stack_from_customer_mock.return_value = self.solution
        find_solution_stack_from_string_mock.return_value = self.solution
        is_cname_available_mock.return_value = True
        get_default_keyname_mock.return_value = None

        env_name = 'my-awesome-env'

        self.app = EB(
            argv=[
                'create', env_name,

                '-db',
                '-db.user', 'root',
                '-db.pass', 'password',
                '-db.i', 'db.t2.micro',
                '-db.version', '5.6.35',
                '-db.size', '10',
                '-db.engine', 'mysql',

                '--vpc',
                '--vpc.id', 'my-vpc-id',
                '--vpc.ec2subnets', 'subnet-1,subnet-2,subnet-3',
                '--vpc.publicip',
                '--vpc.elbsubnets', 'subnet-1,subnet-2,subnet-3',
                '--vpc.securitygroups', 'security-group-1,security-group-2',
                '--vpc.elbpublic',
                '--vpc.dbsubnets', 'subnet-1,subnet-2,subnet-3',
            ]
        )

        expected_environment_request = CreateEnvironmentRequest(
            app_name=self.app_name,
            env_name=env_name,
            platform=self.solution,
            database={
                'username': 'root',
                'password': 'password',
                'engine': 'mysql',
                'size': '10',
                'instance': 'db.t2.micro',
                'version': '5.6.35'
            },
            vpc={
                'id': 'my-vpc-id',
                'ec2subnets': 'subnet-1,subnet-2,subnet-3',
                'elbsubnets': 'subnet-1,subnet-2,subnet-3',
                'elbscheme': 'public',
                'publicip': 'true',
                'securitygroups': 'security-group-1,security-group-2',
                'dbsubnets': 'subnet-1,subnet-2,subnet-3',
            }
        )

        self.app.setup()
        self.app.run()

        call_args, kwargs = make_new_env_mock.call_args
        actual_environment_request = call_args[0]

        self.assertEnvironmentRequestsEqual(expected_environment_request, actual_environment_request)


class TestCreateModule(unittest.TestCase):
    def setUp(self):
        if not os.path.exists('testDir'):
            os.makedirs('testDir')
        os.chdir('testDir')

    def tearDown(self):
        os.chdir(os.path.pardir)
        if os.path.exists('testDir'):
            shutil.rmtree('testDir')

    @mock.patch('ebcli.operations.saved_configs.resolve_config_location')
    def test_get_template_name__config_file_name_not_passed__defaul_config_file_location_not_resolved(
            self,
            resolve_config_location_mock
    ):
        resolve_config_location_mock.return_value = None

        self.assertIsNone(create.get_template_name('some_app', None))

    @mock.patch('ebcli.operations.saved_configs.resolve_config_location')
    @mock.patch('ebcli.operations.saved_configs.resolve_config_name')
    def test_get_template_name__config_file_name_not_passed__defaul_config_file_location_resolved(
            self,
            resolve_config_name,
            resolve_config_location_mock
    ):
        resolve_config_location_mock.return_value = 'default'
        resolve_config_name.return_value = 'default'

        self.assertEqual('default', create.get_template_name('some_app', None))

    @mock.patch('ebcli.operations.saved_configs.resolve_config_name')
    def test_get_template_name__config_file_name_passed_in(
            self,
            resolve_config_name_mock
    ):
        resolve_config_name_mock.return_value = 'some_cfg'

        self.assertEqual('some_cfg', create.get_template_name('some_app', 'some_cfg'))

    def test_get_elb_type_from_customer__single_instance_environment(self):
        self.assertIsNone(
            create.get_elb_type_from_customer(
                interactive=True,
                single=True,
                tier=Tier.from_raw_string('webserver')
            )
        )

    def test_get_elb_type_from_customer__non_interactive_mode(self):
        self.assertIsNone(
            create.get_elb_type_from_customer(
                interactive=False,
                single=True,
                tier=Tier.from_raw_string('webserver')
            )
        )

    @mock.patch('ebcli.lib.utils.prompt_for_item_in_list')
    def test_get_elb_type_from_customer__interactive_mode__load_balanced_environment(
            self,
            prompt_for_item_in_list_mock
    ):
        prompt_for_item_in_list_mock.return_value = 'application'
        self.assertEqual(
            'application',
            create.get_elb_type_from_customer(
                interactive=True,
                single=None,
                tier=Tier.from_raw_string('webserver')
            )
        )
        prompt_for_item_in_list_mock.assert_called_once_with(
            ['classic', 'application', 'network'],
            default=2
        )

    def test_get_elb_type_from_customer__interactive_mode__not_applicable_for_worker_tier(self):
        self.assertIsNone(
            create.get_elb_type_from_customer(
                interactive=True,
                single=None,
                tier=Tier.from_raw_string('worker')
            )
        )

    def test_get_environment_name__env_yaml_exists__env_name_present__group_name_is_provided(self):
        with open('env.yaml', 'w') as env_yaml:
            env_yaml.write("""AWSConfigurationTemplateVersion: 1.1.0.0
SolutionStack: 64bit Amazon Linux 2017.03 v2.7.5 running Multi-container Docker 17.03.2-ce (Generic)
EnvironmentName: my-test-environment+
"""
                           )

            env_yaml.close()

        group_name = 'production'
        self.assertEqual(
            'my-test-environment-production',
            create.get_environment_name('my-application', group_name)
        )

    @mock.patch('ebcli.core.io.echo')
    def test_get_environment_name__env_yaml_exists__env_name_present_but_not_suffixed_with_plus(
            self,
            echo_mock
    ):
        with open('env.yaml', 'w') as env_yaml:
            env_yaml.write("""AWSConfigurationTemplateVersion: 1.1.0.0
SolutionStack: 64bit Amazon Linux 2017.03 v2.7.5 running Multi-container Docker 17.03.2-ce (Generic)
EnvironmentName: my-test-environment
"""
                           )

            env_yaml.close()

        group_name = 'production'

        with self.assertRaises(InvalidOptionsError) as context_manager:
            create.get_environment_name('my-application', group_name)

        self.assertEqual(
            "The environment name specified in env.yaml does not end with a '+', but a group suffix was provided. Please add a trailing '+' to the environment name",
            str(context_manager.exception)
        )

    def test_get_environment_name__env_yaml_exists__env_name_present__group_name_not_provided(self):
        with open('env.yaml', 'w') as env_yaml:
            env_yaml.write("""AWSConfigurationTemplateVersion: 1.1.0.0
SolutionStack: 64bit Amazon Linux 2017.03 v2.7.5 running Multi-container Docker 17.03.2-ce (Generic)
EnvironmentName: my-test-environment+
"""
                           )

            env_yaml.close()

        with self.assertRaises(InvalidOptionsError) as context_manager:
            create.get_environment_name('my-application', None)

        self.assertEqual(
            "The environment name specified in env.yaml ends with a '+', but no group "
            "suffix was provided. Please pass the --env-group-suffix argument.",
            str(context_manager.exception)
        )

    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    def test_get_unique_cname(
            self,
            is_cname_available_mock
    ):
        is_cname_available_mock.return_value = True

        self.assertEqual('my-env', create.get_unique_cname('my-env'))

    @mock.patch('ebcli.controllers.create.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.controllers.create._sleep')
    @mock.patch('ebcli.controllers.create.utils.get_unique_name')
    def test_get_unique_cname__unique_cname_derived_after_multiple_attempts(
            self,
            get_unique_name_mock,
            _sleep_mock,
            is_cname_available_mock
    ):
        is_cname_available_mock.side_effect = [
            False,
            False,
            False,
            True
        ]
        _sleep_mock.side_effect = None
        get_unique_name_mock.side_effect = [
            'my-env-1',
            'my-env-2',
            'my-env-3'
        ]

        self.assertEqual('my-env-3', create.get_unique_cname('my-env'))
