# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

from ebcli.controllers import clone
from ebcli.core import fileoperations
from ebcli.core.ebcore import EB
from ebcli.objects.environment import Environment
from ebcli.objects.platform import PlatformVersion

from .. import mock_responses


def environment_from_mock_responses(environment_name):
    all_available_environments = Environment.json_to_environment_objects_array(
        mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments']
    )

    return [
        environment for environment in all_available_environments if environment.name == environment_name
    ][0]


class TestClone(unittest.TestCase):
    platform = PlatformVersion(
        'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5'
    )

    def setUp(self):
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')

        os.chdir('testDir')

        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            self.platform.name
        )

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')


class TestErrorConditions(TestClone):
    @mock.patch('ebcli.controllers.clone.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.controllers.clone.CloneController.get_env_name')
    def test_clone__cname_specified_for_worker_tier__raises_exception(
            self,
            get_env_name_mock,
            get_environment_mock
    ):
        get_env_name_mock.return_value = 'environment-4'
        get_environment_mock.return_value = environment_from_mock_responses('environment-4')

        app = EB(argv=['clone', '--cname', 'some-cname'])
        app.setup()

        with self.assertRaises(clone.InvalidOptionsError) as context_manager:
            app.run()

        self.assertEqual(
            'Worker tiers do not support a CNAME.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.controllers.clone.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.controllers.clone.CloneController.get_env_name')
    @mock.patch('ebcli.controllers.clone.elasticbeanstalk.is_cname_available')
    def test_clone__cname_already_taken(
            self,
            is_cname_available_mock,
            get_env_name_mock,
            get_environment_mock
    ):
        is_cname_available_mock.return_value = False
        get_env_name_mock.return_value = 'environment-1'
        get_environment_mock.return_value = environment_from_mock_responses('environment-1')

        app = EB(argv=['clone', '--cname', 'in-use-cname'])
        app.setup()

        with self.assertRaises(clone.AlreadyExistsError) as context_manager:
            app.run()

        self.assertEqual(
            'The CNAME prefix in-use-cname is already in use.',
            str(context_manager.exception)
        )


class TestCloneInteractive(TestClone):
    @mock.patch('ebcli.controllers.clone.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.controllers.clone.elasticbeanstalk.get_environment_names')
    @mock.patch('ebcli.controllers.clone.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.controllers.clone.io.prompt_for_environment_name')
    @mock.patch('ebcli.controllers.clone.cloneops.make_cloned_env')
    @mock.patch('ebcli.controllers.clone.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.controllers.clone.CloneEnvironmentRequest')
    @mock.patch('ebcli.controllers.clone.CloneController.get_app_name')
    @mock.patch('ebcli.controllers.clone.CloneController.get_env_name')
    def test_clone__clone_name_not_specified_for_webserver_tier__prompts_customer_for_clone_name(
            self,
            get_app_name_mock,
            get_env_name_mock,
            clone_environment_request_mock,
            find_solution_stack_from_string_mock,
            make_cloned_env_mock,
            prompt_for_environment_name_mock,
            is_cname_available_mock,
            get_environment_names_mock,
            get_environment_mock
    ):
        is_cname_available_mock.return_value = True
        find_solution_stack_from_string_mock.return_value = self.platform
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'
        prompt_for_environment_name_mock.return_value = 'environment-1-clone'
        get_environment_names_mock.return_value = Environment.json_to_environment_objects_array(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments']
        )
        get_environment_mock.return_value = environment_from_mock_responses('environment-1')
        clone_environment_request_mock.return_value = mock.MagicMock()
        clone_environment_request = clone_environment_request_mock.return_value

        app = EB(argv=['clone', '--cname', 'some-cname'])
        app.setup()
        app.run()

        prompt_for_environment_name_mock.assert_called_once_with(
            default_name='my-application-clone',
            prompt_text='Enter name for Environment Clone'
        )
        clone_environment_request_mock.assert_called_once_with(
            app_name='environment-1',
            cname='some-cname',
            env_name='environment-1-clone',
            original_name='my-application',
            platform=self.platform,
            scale=None,
            tags=[]
        )
        make_cloned_env_mock.assert_called_once_with(
            clone_environment_request,
            nohang=False,
            timeout=None
        )

    @mock.patch('ebcli.controllers.clone.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.controllers.clone.elasticbeanstalk.get_environment_names')
    @mock.patch('ebcli.controllers.clone.io.prompt_for_environment_name')
    @mock.patch('ebcli.controllers.clone.get_cname_from_customer')
    @mock.patch('ebcli.controllers.clone.CloneEnvironmentRequest')
    @mock.patch('ebcli.controllers.clone.cloneops.make_cloned_env')
    @mock.patch('ebcli.controllers.clone.CloneController.get_app_name')
    @mock.patch('ebcli.controllers.clone.CloneController.get_env_name')
    @mock.patch('ebcli.controllers.clone.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.controllers.clone.solution_stack_ops.find_solution_stack_from_string')
    def test_clone__neither_clone_name_nor_cname_provided__customer_is_prompted_for_both(
            self,
            find_solution_stack_from_string_mock,
            is_cname_available_mock,
            get_app_name_mock,
            get_env_name_mock,
            make_cloned_env_mock,
            clone_environment_request_mock,
            get_cname_from_customer,
            prompt_for_environment_name_mock,
            get_environment_names_mock,
            get_environment_mock
    ):
        is_cname_available_mock.return_value = True
        find_solution_stack_from_string_mock.return_value = self.platform
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'
        get_cname_from_customer.return_value = 'my-cname'
        prompt_for_environment_name_mock.return_value = 'environment-1-clone'
        get_environment_names_mock.return_value = Environment.json_to_environment_objects_array(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments']
        )
        get_environment_mock.return_value = environment_from_mock_responses('environment-1')
        clone_environment_request_mock.return_value = mock.MagicMock()
        clone_environment_request = clone_environment_request_mock.return_value

        app = EB(argv=['clone'])
        app.setup()
        app.run()

        prompt_for_environment_name_mock.assert_called_once_with(
            default_name='my-application-clone',
            prompt_text='Enter name for Environment Clone'
        )
        clone_environment_request_mock.assert_called_once_with(
            app_name='environment-1',
            cname='my-cname',
            env_name='environment-1-clone',
            original_name='my-application',
            platform=self.platform,
            scale=None,
            tags=[]
        )
        make_cloned_env_mock.assert_called_once_with(
            clone_environment_request,
            nohang=False,
            timeout=None
        )

    @mock.patch('ebcli.controllers.clone.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.controllers.clone.elasticbeanstalk.get_environment_names')
    @mock.patch('ebcli.controllers.clone.io.prompt_for_environment_name')
    @mock.patch('ebcli.controllers.clone.CloneEnvironmentRequest')
    @mock.patch('ebcli.controllers.clone.cloneops.make_cloned_env')
    @mock.patch('ebcli.controllers.clone.CloneController.get_app_name')
    @mock.patch('ebcli.controllers.clone.CloneController.get_env_name')
    @mock.patch('ebcli.controllers.clone.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.controllers.clone.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.controllers.clone.utils.prompt_for_item_in_list')
    def test_clone__prompt_for_choice_between_current_and_latest_platform_arn_in_interactive_mode(
            self,
            prompt_for_item_in_list_mock,
            find_solution_stack_from_string_mock,
            is_cname_available_mock,
            get_app_name_mock,
            get_env_name_mock,
            make_cloned_env_mock,
            clone_environment_request_mock,
            prompt_for_environment_name_mock,
            get_environment_names_mock,
            get_environment_mock
    ):
        is_cname_available_mock.return_value = True
        find_solution_stack_from_string_mock.return_value = PlatformVersion(
            'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.2 running on 64bit Amazon Linux/2.6.5'
        )
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'
        prompt_for_environment_name_mock.return_value = 'environment-1-clone'
        get_environment_names_mock.return_value = Environment.json_to_environment_objects_array(
            mock_responses.DESCRIBE_ENVIRONMENTS_RESPONSE['Environments']
        )
        get_environment_mock.return_value = environment_from_mock_responses('environment-1')
        prompt_for_item_in_list_mock.return_value = 'Latest  (arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.2 running on 64bit Amazon Linux/2.6.5)'
        clone_environment_request_mock.return_value = mock.MagicMock()
        clone_environment_request = clone_environment_request_mock.return_value

        app = EB(argv=['clone', '--cname', 'some-cname'])
        app.setup()
        app.run()

        prompt_for_environment_name_mock.assert_called_once_with(
            default_name='my-application-clone',
            prompt_text='Enter name for Environment Clone'
        )
        prompt_for_item_in_list_mock.assert_called_once_with(
            [
                'Latest  (arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.2 running on 64bit Amazon Linux/2.6.5)',
                'Same    (arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5)'
            ]
        )
        clone_environment_request_mock.assert_called_once_with(
            app_name='environment-1',
            cname='some-cname',
            env_name='environment-1-clone',
            original_name='my-application',
            platform=PlatformVersion(
                'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.2 running on 64bit Amazon Linux/2.6.5'
            ),
            scale=None,
            tags=[]
        )
        make_cloned_env_mock.assert_called_once_with(
            clone_environment_request,
            nohang=False,
            timeout=None
        )


class TestCloneNonInteractive(TestClone):
    @mock.patch('ebcli.controllers.clone.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.controllers.clone.CloneController.get_app_name')
    @mock.patch('ebcli.controllers.clone.CloneController.get_env_name')
    @mock.patch('ebcli.controllers.clone.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.controllers.clone.CloneEnvironmentRequest')
    @mock.patch('ebcli.controllers.clone.cloneops.make_cloned_env')
    def test_clone__clone_name_provided_by_customer__exact_platform_version_as_original_requested(
            self,
            make_cloned_env_mock,
            clone_environment_request_mock,
            is_cname_available_mock,
            get_env_name_mock,
            get_app_name_mock,
            get_environment_mock
    ):
        is_cname_available_mock.return_value = True
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'
        get_environment_mock.return_value = environment_from_mock_responses('environment-1')
        clone_environment_request_mock.return_value = mock.MagicMock()
        clone_environment_request = clone_environment_request_mock.return_value

        app = EB(argv=[
            'clone',
            '--cname', 'available-cname',
            '--clone_name', 'environment-1-clone',
            '--exact'
        ])
        app.setup()
        app.run()

        clone_environment_request_mock.assert_called_once_with(
            app_name='my-application',
            cname='available-cname',
            env_name='environment-1-clone',
            original_name='environment-1',
            platform=None,
            scale=None,
            tags=[]
        )
        make_cloned_env_mock.assert_called_once_with(
            clone_environment_request,
            nohang=False,
            timeout=None
        )

    @mock.patch('ebcli.controllers.clone.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.controllers.clone.CloneController.get_app_name')
    @mock.patch('ebcli.controllers.clone.CloneController.get_env_name')
    @mock.patch('ebcli.controllers.clone.CloneEnvironmentRequest')
    @mock.patch('ebcli.controllers.clone.cloneops.make_cloned_env')
    def test_clone__clone_name_provided_by_customer__exact_platform_version_as_original_requested__cname_not_provided(
            self,
            make_cloned_env_mock,
            clone_environment_request_mock,
            get_env_name_mock,
            get_app_name_mock,
            get_environment_mock
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'
        get_environment_mock.return_value = environment_from_mock_responses('environment-1')
        clone_environment_request_mock.return_value = mock.MagicMock()
        clone_environment_request = clone_environment_request_mock.return_value

        app = EB(argv=[
            'clone',
            '--clone_name', 'environment-1-clone',
            '--exact'
        ])
        app.setup()
        app.run()

        clone_environment_request_mock.assert_called_once_with(
            app_name='my-application',
            cname=None,
            env_name='environment-1-clone',
            original_name='environment-1',
            platform=None,
            scale=None,
            tags=[]
        )
        make_cloned_env_mock.assert_called_once_with(
            clone_environment_request,
            nohang=False,
            timeout=None
        )

    @mock.patch('ebcli.controllers.clone.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.controllers.clone.CloneController.get_app_name')
    @mock.patch('ebcli.controllers.clone.CloneController.get_env_name')
    @mock.patch('ebcli.controllers.clone.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.controllers.clone.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.controllers.clone.CloneEnvironmentRequest')
    @mock.patch('ebcli.controllers.clone.cloneops.make_cloned_env')
    @mock.patch('ebcli.controllers.clone.io.log_warning')
    def test_clone__clone_name_provided_by_customer__exact_argument_specified__old_and_new_platforms_match(
            self,
            log_warning_mock,
            make_cloned_env_mock,
            clone_environment_request_mock,
            find_solution_stack_from_string_mock,
            is_cname_available_mock,
            get_env_name_mock,
            get_app_name_mock,
            get_environment_mock
    ):
        find_solution_stack_from_string_mock.return_value = self.platform
        is_cname_available_mock.return_value = True
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'
        get_environment_mock.return_value = environment_from_mock_responses('environment-1')
        clone_environment_request_mock.return_value = mock.MagicMock()
        clone_environment_request = clone_environment_request_mock.return_value

        app = EB(argv=[
            'clone',
            '--cname', 'available-cname',
            '--clone_name', 'environment-1-clone'
        ])
        app.setup()
        app.run()

        log_warning_mock.assert_not_called()
        clone_environment_request_mock.assert_called_once_with(
            app_name='my-application',
            cname='available-cname',
            env_name='environment-1-clone',
            original_name='environment-1',
            platform=self.platform,
            scale=None,
            tags=[]
        )
        make_cloned_env_mock.assert_called_once_with(
            clone_environment_request,
            nohang=False,
            timeout=None
        )

    @mock.patch('ebcli.controllers.clone.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.controllers.clone.CloneController.get_app_name')
    @mock.patch('ebcli.controllers.clone.CloneController.get_env_name')
    @mock.patch('ebcli.controllers.clone.elasticbeanstalk.is_cname_available')
    @mock.patch('ebcli.controllers.clone.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.controllers.clone.CloneEnvironmentRequest')
    @mock.patch('ebcli.controllers.clone.cloneops.make_cloned_env')
    @mock.patch('ebcli.controllers.clone.io.log_warning')
    def test_clone__clone_name_provided_by_customer__exact_argument_not_specified__old_and_new_platforms_match(
            self,
            log_warning_mock,
            make_cloned_env_mock,
            clone_environment_request_mock,
            find_solution_stack_from_string_mock,
            is_cname_available_mock,
            get_env_name_mock,
            get_app_name_mock,
            get_environment_mock
    ):
        find_solution_stack_from_string_mock.return_value = 'some dummy platform'
        is_cname_available_mock.return_value = True
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'
        get_environment_mock.return_value = environment_from_mock_responses('environment-1')
        clone_environment_request_mock.return_value = mock.MagicMock()
        clone_environment_request = clone_environment_request_mock.return_value

        app = EB(argv=[
            'clone',
            '--cname', 'available-cname',
            '--clone_name', 'environment-1-clone'
        ])
        app.setup()
        app.run()

        log_warning_mock.assert_called_once_with(
            'Launching environment clone on most recent platform version. Override this behavior by using the "--exact" option.'
        )
        clone_environment_request_mock.assert_called_once_with(
            app_name='my-application',
            cname='available-cname',
            env_name='environment-1-clone',
            original_name='environment-1',
            platform='some dummy platform',
            scale=None,
            tags=[]
        )
        make_cloned_env_mock.assert_called_once_with(
            clone_environment_request,
            nohang=False,
            timeout=None
        )
