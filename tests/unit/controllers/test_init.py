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
import mock

from ebcli.controllers import initialize
from ebcli.core import fileoperations
from ebcli.core.ebcore import EB
from ebcli.objects.exceptions import InvalidProfileError
from ebcli.objects.solutionstack import SolutionStack
from ebcli.objects.platform import PlatformVersion
from ebcli.objects.buildconfiguration import BuildConfiguration

from .. import mock_responses


class TestInit(unittest.TestCase):
    solution = SolutionStack('64bit Amazon Linux 2014.03 v1.0.6 running PHP 5.5')
    app_name = 'ebcli-intTest-app'

    def setUp(self):
        self.root_dir = os.getcwd()
        if os.path.exists('testDir'):
            shutil.rmtree('testDir')
        os.mkdir('testDir')
        os.chdir('testDir')

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

    def test_init__attempt_to_initialize_in_platform_workspace(self):
        fileoperations.create_config_file(
            'my-app',
            'us-west-2',
            'my-custom-platform',
            workspace_type='Platform'
        )
        app = EB(argv=['init'])
        app.setup()

        with self.assertRaises(EnvironmentError) as context_manager:
            app.run()

        self.assertEqual(
            'This directory is already initialized with a platform workspace.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.controllers.initialize.get_solution_stack')
    @mock.patch('ebcli.controllers.initialize.sshops')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk')
    @mock.patch('ebcli.controllers.initialize.set_default_env')
    @mock.patch('ebcli.controllers.initialize.create_app_or_use_existing_one')
    @mock.patch('ebcli.controllers.initialize.get_app_name')
    def test_init__interactive_mode(
            self,
            get_app_name_mock,
            create_app_or_use_existing_one_mock,
            set_default_env_mock,
            elasticbeanstalk_mock,
            commonops_mock,
            initops_mock,
            sshops_mock,
            get_solution_stack_mock
    ):
        get_app_name_mock.return_value = 'my-application'
        commonops_mock.credentials_are_valid.return_value = True
        sshops_mock.prompt_for_ec2_keyname.return_value = 'test'
        set_default_env_mock.return_value = None
        elasticbeanstalk_mock.application_exist.return_value = False
        create_app_or_use_existing_one_mock.return_value = None, None
        commonops_mock.get_default_keyname.return_value = ''
        commonops_mock.get_default_region.return_value = ''
        commonops_mock.check_credentials.return_value = (None, 'us-west-2')
        commonops_mock.set_region_for_application.return_value = 'us-west-2'
        get_solution_stack_mock.return_value = 'PHP 5.5'

        app = EB(argv=['init'])
        app.setup()
        app.run()

        initops_mock.setup.assert_called_with(
            'my-application',
            'us-west-2',
            'PHP 5.5',
            branch=None,
            dir_path=None,
            repository=None
        )
        get_app_name_mock.assert_called_once_with([], False, False)
        get_solution_stack_mock.assert_called_once_with(None, None, False)

    @mock.patch('ebcli.controllers.initialize.get_solution_stack')
    @mock.patch('ebcli.controllers.initialize.sshops')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk')
    @mock.patch('ebcli.controllers.initialize.io.get_input')
    @mock.patch('ebcli.controllers.initialize.set_default_env')
    @mock.patch('ebcli.controllers.initialize.create_app_or_use_existing_one')
    @mock.patch('ebcli.controllers.initialize.get_app_name')
    def test_init__force_interactive_mode_using_argument(
            self,
            get_app_name_mock,
            create_app_or_use_existing_one_mock,
            set_default_env_mock,
            get_input_mock,
            elasticbeanstalk_mock,
            commonops_mock,
            initops_mock,
            sshops_mock,
            get_solution_stack_mock
    ):
        get_app_name_mock.return_value = 'my-application'
        fileoperations.create_config_file('app1', 'us-west-1', 'random')
        commonops_mock.credentials_are_valid.return_value = True
        elasticbeanstalk_mock.application_exist.return_value = False
        create_app_or_use_existing_one_mock.return_value = (None, None)
        commonops_mock.get_default_keyname.side_effect = initialize.NotInitializedError
        commonops_mock.get_region.return_value = 'us-west-2'
        commonops_mock.check_credentials.return_value = (None, 'us-west-2')
        commonops_mock.set_region_for_application.return_value = 'us-west-2'
        sshops_mock.prompt_for_ec2_keyname.return_value = 'test'
        get_solution_stack_mock.return_value = 'PHP 5.5'

        get_input_mock.side_effect = [
            '3',  # region number
            self.app_name,  # Application name
            'n',  # Set up ssh selection
        ]

        app = EB(argv=['init', '-i'])
        app.setup()
        app.run()

        initops_mock.setup.assert_called_with(
            'my-application',
            'us-west-2',
            'PHP 5.5',
            branch=None,
            dir_path=None,
            repository=None
        )
        get_app_name_mock.assert_called_once_with([], True, False)
        get_solution_stack_mock.assert_called_once_with(None, None, True)

    @mock.patch('ebcli.controllers.initialize.get_solution_stack')
    @mock.patch('ebcli.controllers.initialize.sshops')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk')
    @mock.patch('ebcli.controllers.initialize.set_default_env')
    @mock.patch('ebcli.controllers.initialize.create_app_or_use_existing_one')
    @mock.patch('ebcli.controllers.initialize.get_app_name')
    def test_init_no_creds(
            self,
            get_app_name_mock,
            create_app_or_use_existing_one_mock,
            set_default_env_mock,
            elasticbeanstalk_mock,
            commonops_mock,
            initops_mock,
            sshops_mock,
            get_solution_stack_mock
    ):
        get_app_name_mock.return_value = self.app_name
        commonops_mock.credentials_are_valid.return_value = False
        commonops_mock.get_region.return_value = 'us-west-2'
        sshops_mock.prompt_for_ec2_keyname.return_value = 'test'
        set_default_env_mock.return_value = None
        elasticbeanstalk_mock.application_exist.return_value = True
        create_app_or_use_existing_one_mock.return_value = (None, None)
        commonops_mock.get_default_keyname.return_value = ''
        commonops_mock.get_default_region.return_value = ''
        commonops_mock.check_credentials.return_value = (None, 'us-west-2')
        commonops_mock.set_region_for_application.return_value = 'us-west-2'
        get_solution_stack_mock.return_value = 'PHP 5.5'

        EB.Meta.exit_on_close = False
        app = EB(
            argv=[
                'init', self.app_name,
                '-r', 'us-west-2'
            ]
        )
        app.setup()
        app.run()

        commonops_mock.set_up_credentials.assert_called_once_with(None, 'us-west-2', False)
        initops_mock.setup.assert_called_with(
            self.app_name,
            'us-west-2',
            'PHP 5.5',
            branch=None,
            dir_path=None,
            repository=None
        )
        get_solution_stack_mock.assert_called_once_with(None, None, False)

    @mock.patch('ebcli.controllers.initialize.get_solution_stack')
    @mock.patch('ebcli.controllers.initialize.sshops')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk')
    @mock.patch('ebcli.controllers.initialize.set_default_env')
    @mock.patch('ebcli.controllers.initialize.create_app_or_use_existing_one')
    @mock.patch('ebcli.controllers.initialize.get_app_name')
    def test_init__force_non_interactive_mode_using_platform_argument(
            self,
            get_app_name_mock,
            create_app_or_use_existing_one_mock,
            set_default_env_mock,
            elasticbeanstalk_mock,
            commonops_mock,
            initops_mock,
            sshops_mock,
            get_solution_stack_mock
    ):
        get_app_name_mock.return_value = self.app_name
        sshops_mock.prompt_for_ec2_keyname.return_value = Exception
        set_default_env_mock.return_value = None
        elasticbeanstalk_mock.application_exist.return_value = True
        create_app_or_use_existing_one_mock.return_value = 'ss-stack', 'key'
        commonops_mock.get_default_keyname.return_value = ''
        commonops_mock.get_region.return_value = 'us-west-2'
        commonops_mock.check_credentials.return_value = (None, 'us-west-2')
        commonops_mock.set_region_for_application.return_value = 'us-west-2'
        get_solution_stack_mock.return_value = 'php'

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
        get_solution_stack_mock.assert_called_once_with('php', 'ss-stack', False)

    @mock.patch('ebcli.controllers.initialize.get_solution_stack')
    @mock.patch('ebcli.controllers.initialize.sshops')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk')
    @mock.patch('ebcli.controllers.initialize.set_default_env')
    @mock.patch('ebcli.controllers.initialize.create_app_or_use_existing_one')
    @mock.patch('ebcli.controllers.initialize.should_prompt_customer_to_opt_into_codecommit')
    @mock.patch('ebcli.controllers.initialize.configure_codecommit')
    @mock.patch('ebcli.controllers.initialize.get_app_name')
    def test_init__non_interactive_mode__with_codecommit(
            self,
            get_app_name_mock,
            configure_codecommit_mock,
            should_prompt_customer_to_opt_into_codecommit_mock,
            create_app_or_use_existing_one_mock,
            set_default_env_mock,
            elasticbeanstalk_mock,
            commonops_mock,
            initops_mock,
            sshops_mock,
            get_solution_stack_mock,
    ):
        get_app_name_mock.return_value = self.app_name
        sshops_mock.prompt_for_ec2_keyname.return_value = Exception
        set_default_env_mock.return_value = None
        elasticbeanstalk_mock.application_exist.return_value = False
        create_app_or_use_existing_one_mock.return_value = None, None
        commonops_mock.get_default_keyname.return_value = ''
        commonops_mock.get_region.return_value = 'us-east-1'
        commonops_mock.credentials_are_valid.return_value = True
        commonops_mock.check_credentials.return_value = (None, 'us-east-1')
        commonops_mock.set_region_for_application.return_value = 'us-east-1'
        should_prompt_customer_to_opt_into_codecommit_mock.return_value = True
        configure_codecommit_mock.return_value = ('my-repo', 'prod/mybranch')
        get_solution_stack_mock.return_value = 'ruby'

        app = EB(
            argv=[
                'init',
                '-p', 'ruby',
                '--source', 'codecommit/my-repo/prod/mybranch',
                '--region', 'us-east-1'
            ]
        )
        app.setup()
        app.run()

        initops_mock.setup.assert_called_with(
            'ebcli-intTest-app',
            'us-east-1',
            'ruby',
            dir_path=None,
            repository='my-repo',
            branch='prod/mybranch'
        )
        configure_codecommit_mock.assert_called_once_with('codecommit/my-repo/prod/mybranch')
        get_solution_stack_mock.assert_called_once_with('ruby', None, False)

    @mock.patch('ebcli.controllers.initialize.get_solution_stack')
    @mock.patch('ebcli.controllers.initialize.sshops')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.create_app_or_use_existing_one')
    @mock.patch('ebcli.controllers.initialize.should_prompt_customer_to_opt_into_codecommit')
    @mock.patch('ebcli.controllers.initialize.configure_codecommit')
    @mock.patch('ebcli.controllers.initialize.get_app_name')
    def test_init__interactive_mode__with_codecommit(
            self,
            get_app_name_mock,
            configure_codecommit_mock,
            should_prompt_customer_to_opt_into_codecommit_mock,
            create_app_or_use_existing_one_mock,
            commonops_mock,
            initops_mock,
            sshops_mock,
            get_solution_stack_mock
    ):
        get_app_name_mock.return_value = 'my-app'
        fileoperations.create_config_file('app1', 'us-west-1', 'random')
        commonops_mock.credentials_are_valid.return_value = True
        create_app_or_use_existing_one_mock.return_value = None, None
        commonops_mock.get_default_keyname.return_value = 'ec2-keyname'
        commonops_mock.get_region.return_value = 'us-east-1'
        commonops_mock.check_credentials.return_value = (None, 'us-east-1')
        commonops_mock.set_region_for_application.return_value = 'us-east-1'
        should_prompt_customer_to_opt_into_codecommit_mock.return_value = True
        configure_codecommit_mock.return_value = ('new-repo', 'devo')
        sshops_mock.prompt_for_ec2_keyname.return_value = 'test'
        get_solution_stack_mock.return_value = 'PHP 5.5'

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

        configure_codecommit_mock.assert_called_once_with(None)
        get_solution_stack_mock.assert_called_once_with(None, None, False)

    @mock.patch('ebcli.controllers.initialize.fileoperations')
    @mock.patch('ebcli.controllers.initialize.get_solution_stack')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.create_app_or_use_existing_one')
    @mock.patch('ebcli.controllers.initialize.handle_buildspec_image')
    @mock.patch('ebcli.controllers.initialize.get_keyname')
    @mock.patch('ebcli.controllers.initialize.get_app_name')
    @mock.patch('ebcli.controllers.initialize.should_prompt_customer_to_opt_into_codecommit')
    def test_init__interactive_mode__with_codebuild_buildspec(
            self,
            should_prompt_customer_to_opt_into_codecommit_mock,
            get_app_name_mock,
            get_keyname_mock,
            handle_buildspec_image_mock,
            create_app_or_use_existing_one_mock,
            commonops_mock,
            initops_mock,
            get_solution_stack_mock,
            fileoperations_mock,
    ):
        should_prompt_customer_to_opt_into_codecommit_mock.return_value = False
        commonops_mock.set_region_for_application.return_value = 'us-west-2'
        get_app_name_mock.return_value = self.app_name
        initops_mock.credentials_are_valid.return_value = True
        fileoperations_mock.env_yaml_exists.return_value = None
        get_keyname_mock.return_value = 'test'
        get_solution_stack_mock.return_value = 'PHP 5.5'
        commonops_mock.check_credentials.return_value = ('eb-cli', 'us-west-2')
        commonops_mock.set_region_for_application.return_value = 'us-west-2'

        create_app_or_use_existing_one_mock.return_value = (None, None)

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
        handle_buildspec_image_mock.assert_called_once_with('PHP 5.5', False)

        write_config_calls = [
            mock.call('global', 'default_ec2_keyname', 'test'),
            mock.call('global', 'include_git_submodules', True)
        ]
        fileoperations_mock.write_config_setting.assert_has_calls(write_config_calls)
        get_solution_stack_mock.assert_called_once_with(None, None, True)

    @mock.patch('ebcli.controllers.initialize.get_solution_stack')
    @mock.patch('ebcli.controllers.initialize.sshops')
    @mock.patch('ebcli.controllers.initialize.initializeops')
    @mock.patch('ebcli.controllers.initialize.commonops')
    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk')
    @mock.patch('ebcli.controllers.initialize.fileoperations.get_platform_from_env_yaml')
    @mock.patch('ebcli.controllers.initialize.set_default_env')
    @mock.patch('ebcli.controllers.initialize.create_app_or_use_existing_one')
    @mock.patch('ebcli.controllers.initialize.handle_buildspec_image')
    @mock.patch('ebcli.controllers.initialize.get_keyname')
    @mock.patch('ebcli.controllers.initialize.should_prompt_customer_to_opt_into_codecommit')
    @mock.patch('ebcli.controllers.initialize.configure_codecommit')
    @mock.patch('ebcli.controllers.initialize.get_app_name')
    def test_init_with_codecommit_source_and_codebuild(
            self,
            get_app_name_mock,
            configure_codecommit_mock,
            should_prompt_customer_to_opt_into_codecommit_mock,
            get_keyname_mock,
            handle_buildspec_image_mock,
            create_app_or_use_existing_one_mock,
            set_default_env_mock,
            get_platform_from_env_yaml_mock,
            elasticbeanstalk_mock,
            commonops_mock,
            initops_mock,
            sshops_mock,
            get_solution_stack_mock
    ):
        get_app_name_mock.return_value = 'testDir'
        get_platform_from_env_yaml_mock.return_value = 'PHP 5.5'
        get_keyname_mock.return_value = 'keyname'
        get_solution_stack_mock.return_value = '64bit Amazon Linux 2014.03 v1.0.6 running PHP 5.5'
        sshops_mock.prompt_for_ec2_keyname.return_value = Exception
        set_default_env_mock.return_value = None
        elasticbeanstalk_mock.application_exist.return_value = False
        create_app_or_use_existing_one_mock.return_value = None, None
        commonops_mock.get_default_keyname.return_value = ''
        commonops_mock.get_region.return_value = 'us-east-1'
        commonops_mock.check_credentials.return_value = (None, 'us-east-1')
        commonops_mock.set_region_for_application.return_value = 'us-east-1'
        should_prompt_customer_to_opt_into_codecommit_mock.return_value = True
        configure_codecommit_mock.return_value = ('my-repo', 'prod')

        app = EB(argv=['init', '--source', 'codecommit/my-repo/prod', '--region', 'us-east-1'])
        app.setup()
        app.run()

        initops_mock.setup.assert_called_with(
            'testDir',
            'us-east-1',
            '64bit Amazon Linux 2014.03 v1.0.6 running PHP 5.5',
            branch='prod',
            dir_path=None,
            repository='my-repo'
        )
        handle_buildspec_image_mock.assert_called_once_with(
            '64bit Amazon Linux 2014.03 v1.0.6 running PHP 5.5',
            False
        )
        configure_codecommit_mock.assert_called_once_with('codecommit/my-repo/prod')
        get_solution_stack_mock.assert_called_once_with(None, None, False)


class TestInitModule(unittest.TestCase):
    solution = SolutionStack('64bit Amazon Linux 2014.03 v1.0.6 running PHP 5.5')
    app_name = 'ebcli-intTest-app'

    def setUp(self):
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
        prompt_for_item_in_list_mock.return_value = 2  # initialize with 'master' branch

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

    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk.application_exist')
    @mock.patch('ebcli.controllers.initialize.commonops.pull_down_app_info')
    @mock.patch('ebcli.controllers.initialize.commonops.create_app')
    def test_create_app_or_use_existing_one__application_exists(
            self,
            create_app_mock,
            pull_down_app_info_mock,
            application_exist_mock,
    ):
        application_exist_mock.return_value = True
        pull_down_app_info_mock.return_value = ('php-5.5', 'keyname')

        self.assertEqual(
            ('php-5.5', 'keyname'),
            initialize.create_app_or_use_existing_one('app_name', 'default_env')
        )

        application_exist_mock.assert_called_once_with('app_name')
        pull_down_app_info_mock.assert_called_once_with('app_name', default_env='default_env')
        create_app_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.elasticbeanstalk.application_exist')
    @mock.patch('ebcli.controllers.initialize.commonops.pull_down_app_info')
    @mock.patch('ebcli.controllers.initialize.commonops.create_app')
    def test_create_app_or_use_existing_one__application_does_not_exist(
            self,
            create_app_mock,
            pull_down_app_info_mock,
            application_exist_mock,
    ):
        application_exist_mock.return_value = False
        create_app_mock.return_value = ('php-5.5', 'keyname')

        self.assertEqual(
            ('php-5.5', 'keyname'),
            initialize.create_app_or_use_existing_one('app_name', 'default_env')
        )

        application_exist_mock.assert_called_once_with('app_name')
        create_app_mock.assert_called_once_with('app_name', default_env='default_env')
        pull_down_app_info_mock.assert_not_called()

    def test_set_default_env__force_non_interactive(self):
        self.assertEqual('/ni', initialize.set_default_env(False, True))

    def test_set_default_env__interactive_mode(self):
        self.assertIsNone(initialize.set_default_env(True, False))

    def test_set_default_env__non_interactive(self):
        self.assertIsNone(initialize.set_default_env(False, False))

    @mock.patch('ebcli.controllers.initialize.fileoperations.get_platform_from_env_yaml')
    def test_extract_solution_stack_from_env_yaml__platform_exists(
            self,
            get_platform_from_env_yaml_mock
    ):
        get_platform_from_env_yaml_mock.return_value = '64bit Amazon Linux 2014.03 v1.0.6 running PHP 5.5'
        self.assertEqual(
            'PHP 5.5',
            initialize.extract_solution_stack_from_env_yaml()
        )

    @mock.patch('ebcli.controllers.initialize.fileoperations.get_platform_from_env_yaml')
    def test_extract_solution_stack_from_env_yaml__platform_absent(
            self,
            get_platform_from_env_yaml_mock
    ):
        get_platform_from_env_yaml_mock.return_value = None
        self.assertIsNone(initialize.extract_solution_stack_from_env_yaml())

    @mock.patch('ebcli.controllers.initialize.fileoperations.get_build_configuration')
    @mock.patch('ebcli.controllers.initialize.fileoperations.build_spec_exists')
    def test_handle_buildspec_image__force_non_interactive(
            self,
            build_spec_exists_mock,
            get_build_configuration_mock
    ):
        build_spec_exists_mock.return_value = False

        self.assertIsNone(initialize.handle_buildspec_image('PHP 5.5', True))

        get_build_configuration_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.fileoperations.get_build_configuration')
    @mock.patch('ebcli.controllers.initialize.initializeops.get_codebuild_image_from_platform')
    @mock.patch('ebcli.controllers.initialize.fileoperations.write_buildspec_config_header')
    @mock.patch('ebcli.controllers.initialize.fileoperations.build_spec_exists')
    def test_handle_buildspec_image__force_non_interactive(
            self,
            build_spec_exists_mock,
            write_buildspec_config_header_mock,
            get_codebuild_image_from_platform_mock,
            get_build_configuration_mock
    ):
        compute_type = 'BUILD_GENERAL1_SMALL'
        service_role = 'eb-test'
        timeout = 60
        build_config = BuildConfiguration(
            image=None,
            compute_type=compute_type,
            service_role=service_role,
            timeout=timeout
        )
        build_spec_exists_mock.return_value = True
        get_build_configuration_mock.return_value = build_config

        self.assertIsNone(initialize.handle_buildspec_image('PHP 5.5', True))

        get_codebuild_image_from_platform_mock.assert_not_called()
        write_buildspec_config_header_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.fileoperations.get_build_configuration')
    @mock.patch('ebcli.controllers.initialize.initializeops.get_codebuild_image_from_platform')
    @mock.patch('ebcli.controllers.initialize.fileoperations.write_buildspec_config_header')
    @mock.patch('ebcli.controllers.initialize.fileoperations.build_spec_exists')
    def test_handle_buildspec_image__no_image_in_buildspec(
            self,
            build_spec_exists_mock,
            write_buildspec_config_header_mock,
            get_codebuild_image_from_platform_mock,
            get_build_configuration_mock
    ):
        build_spec_exists_mock.return_value = True
        build_config = BuildConfiguration()
        get_build_configuration_mock.return_value = build_config

        self.assertIsNone(initialize.handle_buildspec_image('PHP 5.5', True))

        get_codebuild_image_from_platform_mock.assert_not_called()
        write_buildspec_config_header_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.fileoperations.get_build_configuration')
    @mock.patch('ebcli.controllers.initialize.initializeops.get_codebuild_image_from_platform')
    @mock.patch('ebcli.controllers.initialize.fileoperations.write_buildspec_config_header')
    @mock.patch('ebcli.controllers.initialize.io.echo')
    @mock.patch('ebcli.controllers.initialize.utils.prompt_for_index_in_list')
    @mock.patch('ebcli.controllers.initialize.fileoperations.build_spec_exists')
    def test_handle_buildspec_image__multiple_matching_images_for_platform(
            self,
            build_spec_exists_mock,
            prompt_for_index_in_list_mock,
            echo_mock,
            write_buildspec_config_header_mock,
            get_codebuild_image_from_platform_mock,
            get_build_configuration_mock
    ):
        compute_type = 'BUILD_GENERAL1_SMALL'
        service_role = 'eb-test'
        timeout = 60
        build_config = BuildConfiguration(
            image=None,
            compute_type=compute_type,
            service_role=service_role,
            timeout=timeout
        )
        build_spec_exists_mock.return_value = True
        get_build_configuration_mock.return_value = build_config
        get_codebuild_image_from_platform_mock.return_value = [
            {
                'name': 'aws/codebuild/eb-java-8-amazonlinux-64:2.1.6',
                'description': 'Java 8 Running on Amazon Linux 64bit '
            },
            {
                'name': 'aws/codebuild/eb-java-8-amazonlinux-32:2.1.6',
                'description': 'Java 8 Running on Amazon Linux 32bit '
            }
        ]
        prompt_for_index_in_list_mock.return_value = 'Java 8 Running on Amazon Linux 32bit '

        self.assertIsNone(initialize.handle_buildspec_image('Java 8', False))

        get_codebuild_image_from_platform_mock.assert_called_once_with('Java 8')
        write_buildspec_config_header_mock.assert_called_once_with(
            'Image',
            'aws/codebuild/eb-java-8-amazonlinux-32:2.1.6'
        )
        echo_mock.assert_has_calls(
            [
                mock.call(
                    'Could not determine best image for buildspec file please select from list.\n '
                    'Current chosen platform: Java 8'
                )
            ]
        )
        prompt_for_index_in_list_mock.assert_called_once_with('Java 8 Running on Amazon Linux 64bit ')

    @mock.patch('ebcli.controllers.initialize.fileoperations.get_build_configuration')
    @mock.patch('ebcli.controllers.initialize.initializeops.get_codebuild_image_from_platform')
    @mock.patch('ebcli.controllers.initialize.fileoperations.write_buildspec_config_header')
    @mock.patch('ebcli.controllers.initialize.io.echo')
    @mock.patch('ebcli.controllers.initialize.utils.prompt_for_index_in_list')
    @mock.patch('ebcli.controllers.initialize.fileoperations.build_spec_exists')
    def test_handle_buildspec_image__single_image_matches(
            self,
            build_spec_exists_mock,
            prompt_for_index_in_list_mock,
            echo_mock,
            write_buildspec_config_header_mock,
            get_codebuild_image_from_platform_mock,
            get_build_configuration_mock
    ):
        compute_type = 'BUILD_GENERAL1_SMALL'
        service_role = 'eb-test'
        timeout = 60
        build_config = BuildConfiguration(
            image=None,
            compute_type=compute_type,
            service_role=service_role,
            timeout=timeout
        )
        build_spec_exists_mock.return_value = True
        get_build_configuration_mock.return_value = build_config
        get_codebuild_image_from_platform_mock.return_value = {
            'name': 'aws/codebuild/eb-java-8-amazonlinux-64:2.1.6',
            'description': 'Java 8 Running on Amazon Linux 64bit '
        }
        prompt_for_index_in_list_mock.return_value = 'Java 8 Running on Amazon Linux 32bit '

        self.assertIsNone(initialize.handle_buildspec_image('Java 8', False))

        get_codebuild_image_from_platform_mock.assert_called_once_with('Java 8')
        write_buildspec_config_header_mock.assert_called_once_with(
            'Image',
            'aws/codebuild/eb-java-8-amazonlinux-64:2.1.6'
        )
        echo_mock.assert_called_once_with(
            'Buildspec file is present but no image is specified; using latest image for selected platform: Java 8'
        )
        prompt_for_index_in_list_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.establish_codecommit_repository')
    @mock.patch('ebcli.controllers.initialize.establish_codecommit_branch')
    def test_establish_codecommit_repository_and_branch(
            self,
            establish_codecommit_branch_mock,
            establish_codecommit_repository_mock
    ):
        establish_codecommit_repository_mock.return_value = 'my-repository'
        establish_codecommit_branch_mock.return_value = 'my-branch'

        self.assertEqual(
            ('my-repository', 'my-branch'),
            initialize.establish_codecommit_repository_and_branch(
                True,
                'us-west-2',
                False,
                'https://codecommit.edu.git'
            )
        )

        establish_codecommit_repository_mock.assert_called_once_with(True, False, 'https://codecommit.edu.git')
        establish_codecommit_branch_mock.assert_called_once_with(
            'my-repository',
            'us-west-2',
            False,
            'https://codecommit.edu.git'
        )

    @mock.patch('ebcli.controllers.initialize.get_repository_interactive')
    @mock.patch('ebcli.controllers.initialize.setup_codecommit_remote_repo')
    def test_establish_codecommit_repository__repository_argument_is_none(
            self,
            setup_codecommit_remote_repo_mock,
            get_repository_interactive_mock
    ):
        source_control_mock = mock.MagicMock()
        source_location = 'https://codecommit.edu.git'
        get_repository_interactive_mock.return_value = 'my-repository'

        self.assertEqual(
            'my-repository',
            initialize.establish_codecommit_repository(None, source_control_mock, source_location)
        )

        get_repository_interactive_mock.assert_called_once_with()
        setup_codecommit_remote_repo_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.get_repository_interactive')
    @mock.patch('ebcli.controllers.initialize.setup_codecommit_remote_repo')
    @mock.patch('ebcli.controllers.initialize.create_codecommit_repository')
    def test_establish_codecommit_repository__repository_argument_is_not_none_but_is_non_existent__repository_is_setup(
            self,
            create_codecommit_repository_mock,
            setup_codecommit_remote_repo_mock,
            get_repository_interactive_mock
    ):
        source_control_mock = mock.MagicMock()
        source_location = 'https://codecommit.edu.git'
        get_repository_interactive_mock.return_value = 'my-repository'
        setup_codecommit_remote_repo_mock.side_effect = [
            initialize.ServiceError,
            None
        ]

        self.assertEqual(
            'my-repository',
            initialize.establish_codecommit_repository('my-repository', source_control_mock, source_location)
        )

        setup_codecommit_remote_repo_mock.assert_has_calls(
            [
                mock.call('my-repository', source_control_mock),
                mock.call('my-repository', source_control_mock)
            ]
        )
        create_codecommit_repository_mock.assert_called_once_with('my-repository')
        get_repository_interactive_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.get_repository_interactive')
    @mock.patch('ebcli.controllers.initialize.setup_codecommit_remote_repo')
    @mock.patch('ebcli.controllers.initialize.create_codecommit_repository')
    def test_establish_codecommit_repository__repository_argument_is_not_none__repository_exists_and_is_pulled(
            self,
            create_codecommit_repository_mock,
            setup_codecommit_remote_repo_mock,
            get_repository_interactive_mock
    ):
        source_control_mock = mock.MagicMock()
        source_location = 'https://codecommit.edu.git'
        get_repository_interactive_mock.return_value = 'my-repository'
        setup_codecommit_remote_repo_mock.side_effect = None

        self.assertEqual(
            'my-repository',
            initialize.establish_codecommit_repository('my-repository', source_control_mock, source_location)
        )

        setup_codecommit_remote_repo_mock.assert_called_once_with('my-repository', source_control_mock)
        get_repository_interactive_mock.assert_not_called()
        create_codecommit_repository_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.get_branch_interactive')
    def test_establish_codecommit_branch__branch_argument_is_none(
            self,
            get_branch_interactive_mock
    ):
        source_control_mock = mock.MagicMock()
        source_location = 'https://codecommit.edu.git'
        get_branch_interactive_mock.return_value = 'my-branch'
        self.assertEqual(
            'my-branch',
            initialize.establish_codecommit_branch('my-repository', None, source_control_mock, source_location)
        )
        source_control_mock.setup_existing_codecommit_branch.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.codecommit.get_branch')
    @mock.patch('ebcli.controllers.initialize.get_branch_interactive')
    def test_establish_codecommit_branch__branch_already_exists(
            self,
            get_branch_interactive_mock,
            get_branch_mock
    ):
        source_control_mock = mock.MagicMock()
        source_location = 'https://codecommit.edu.git'

        self.assertEqual(
            'my-branch',
            initialize.establish_codecommit_branch('my-repository', 'my-branch', source_control_mock, source_location)
        )

        get_branch_mock.assert_called_once_with('my-repository', 'my-branch')
        get_branch_interactive_mock.assert_not_called()
        source_control_mock.setup_existing_codecommit_branch.assert_called_once_with('my-branch', None)

    @mock.patch('ebcli.controllers.initialize.codecommit.get_branch')
    @mock.patch('ebcli.controllers.initialize.get_branch_interactive')
    @mock.patch('ebcli.controllers.initialize.create_codecommit_branch')
    def test_establish_codecommit_branch__branch_does_not_exist__new_branch_created(
            self,
            create_codecommit_branch_mock,
            get_branch_interactive_mock,
            get_branch_mock
    ):
        source_control_mock = mock.MagicMock()
        source_location = 'https://codecommit.edu.git'
        get_branch_mock.side_effect = initialize.ServiceError

        self.assertEqual(
            'my-branch',
            initialize.establish_codecommit_branch('my-repository', 'my-branch', source_control_mock, source_location)
        )

        get_branch_mock.assert_called_once_with('my-repository', 'my-branch')
        create_codecommit_branch_mock.assert_called_once_with(source_control_mock, 'my-branch')
        get_branch_interactive_mock.assert_not_called()
        source_control_mock.setup_existing_codecommit_branch.assert_called_once_with()

    @mock.patch('ebcli.controllers.initialize.codecommit.get_branch')
    @mock.patch('ebcli.controllers.initialize.get_branch_interactive')
    @mock.patch('ebcli.controllers.initialize.create_codecommit_branch')
    @mock.patch('ebcli.controllers.initialize.io.log_error')
    def test_establish_codecommit_branch__branch_does_not_exist__new_branch_created(
            self,
            log_error_mock,
            create_codecommit_branch_mock,
            get_branch_interactive_mock,
            get_branch_mock
    ):
        source_control_mock = mock.MagicMock()
        get_branch_mock.side_effect = initialize.ServiceError

        with self.assertRaises(initialize.ServiceError):
            initialize.establish_codecommit_branch('my-repository', 'my-branch', source_control_mock, None)

        get_branch_mock.assert_called_once_with('my-repository', 'my-branch')
        log_error_mock.assert_called_once_with('Branch does not exist in CodeCommit')
        create_codecommit_branch_mock.assert_not_called()
        get_branch_interactive_mock.assert_not_called()
        source_control_mock.setup_existing_codecommit_branch.assert_not_called()

    def test_get_keyname__keyname_passed_through_command_line__force_non_interactive(self):
        self.assertEqual(
            'keyname',
            initialize.get_keyname('keyname', 'previously-chosen-keyname', False, True)
        )

    @mock.patch('ebcli.controllers.initialize.commonops.upload_keypair_if_needed')
    def test_get_keyname__keyname_passed_through_command_line__interactive(
            self,
            upload_keypair_if_needed_mock
    ):
        self.assertEqual(
            'keyname',
            initialize.get_keyname('keyname', 'previously-chosen-keyname', True, False)
        )
        upload_keypair_if_needed_mock.assert_called_once_with('keyname')

    def test_get_keyname__keyname_not_passed_through_command_line__using_previously_set_keyname__force_non_interactive(self):
        self.assertEqual(
            'previously-chosen-keyname',
            initialize.get_keyname(None, 'previously-chosen-keyname', False, True)
        )

    @mock.patch('ebcli.controllers.initialize.sshops.prompt_for_ec2_keyname')
    @mock.patch('ebcli.controllers.initialize.commonops.upload_keypair_if_needed')
    def test_get_keyname__keyname_not_passed_through_command_line__using_previously_set_keyname__interactive__prompts_for_new_keyname_anyway(
            self,
            upload_keypair_if_needed_mock,
            prompt_for_ec2_keyname_mock
    ):
        prompt_for_ec2_keyname_mock.return_value = 'keyname'

        self.assertEqual(
            'keyname',
            initialize.get_keyname(None, 'previously-chosen-keyname', True, False)
        )

        prompt_for_ec2_keyname_mock.assert_called_once_with()
        upload_keypair_if_needed_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.commonops.get_default_keyname')
    def test_get_keyname__use_default_keyname__force_non_interactive(
            self,
            get_default_keyname_mock
    ):
        get_default_keyname_mock.return_value = 'keyname'
        self.assertEqual(
            'keyname',
            initialize.get_keyname(None, None, False, True)
        )

    @mock.patch('ebcli.controllers.initialize.commonops.get_default_keyname')
    @mock.patch('ebcli.controllers.initialize.commonops.upload_keypair_if_needed')
    @mock.patch('ebcli.controllers.initialize.sshops.prompt_for_ec2_keyname')
    def test_get_keyname__use_default_keyname__interactive(
            self,
            prompt_for_ec2_keyname_mock,
            upload_keypair_if_needed_mock,
            get_default_keyname_mock
    ):
        get_default_keyname_mock.return_value = 'default-keyname'
        prompt_for_ec2_keyname_mock.return_value = 'keyname'

        self.assertEqual(
            'keyname',
            initialize.get_keyname(None, None, True, False)
        )
        prompt_for_ec2_keyname_mock.assert_called_once_with()
        upload_keypair_if_needed_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.sshops.prompt_for_ec2_keyname')
    def test_get_keyname__prompt_for_ec2_keyname(
            self,
            prompt_for_ec2_keyname_mock
    ):
        prompt_for_ec2_keyname_mock.return_value = 'keyname'
        self.assertEqual(
            'keyname',
            initialize.get_keyname(None, None, True, False)
        )
        prompt_for_ec2_keyname_mock.assert_called_once_with()

    @mock.patch('ebcli.controllers.initialize.get_keyname')
    @mock.patch('ebcli.controllers.initialize.fileoperations.write_config_setting')
    def test_configure_keyname(
            self,
            write_config_setting_mock,
            get_keyname_mock
    ):
        get_keyname_mock.return_value = 'keyname'

        initialize.configure_keyname('PHP 5.5', 'keyname', None, False, False)

        get_keyname_mock.assert_called_once_with('keyname', None, False, False)
        write_config_setting_mock.assert_called_once_with('global', 'default_ec2_keyname', 'keyname')

    @mock.patch('ebcli.controllers.initialize.get_keyname')
    @mock.patch('ebcli.controllers.initialize.fileoperations.write_config_setting')
    def test_configure_keyname__keyname_was_not_found(
            self,
            write_config_setting_mock,
            get_keyname_mock
    ):
        get_keyname_mock.return_value = -1

        initialize.configure_keyname('PHP 5.5', None, None, False, False)

        get_keyname_mock.assert_called_once_with(None, None, False, False)
        write_config_setting_mock.assert_called_once_with('global', 'default_ec2_keyname', None)

    @mock.patch('ebcli.controllers.initialize.get_keyname')
    @mock.patch('ebcli.controllers.initialize.fileoperations.write_config_setting')
    def test_configure_keyname__iis_platform(
            self,
            write_config_setting_mock,
            get_keyname_mock
    ):
        initialize.configure_keyname('IIS 10', None, None, False, False)

        get_keyname_mock.assert_not_called()
        write_config_setting_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.io.validate_action')
    def test_configure_codecommit__source_location_not_specified__customer_opts_out(
            self,
            validate_action_mock
    ):
        validate_action_mock.side_effect = initialize.ValidationError

        initialize.configure_codecommit(None)

        validate_action_mock.assert_called_once_with(
            'Do you wish to continue with CodeCommit? (y/N) (default is n)',
            'y'
        )

    @mock.patch('ebcli.controllers.initialize.io.validate_action')
    @mock.patch('ebcli.controllers.initialize.establish_codecommit_repository_and_branch')
    @mock.patch('ebcli.controllers.initialize.SourceControl.get_source_control')
    def test_configure_codecommit__source_location_not_specified__customer_opts_in(
            self,
            get_source_control_mock,
            establish_codecommit_repository_and_branch_mock,
            validate_action_mock
    ):
        source_control_mock = mock.MagicMock()
        get_source_control_mock.return_value = source_control_mock
        validate_action_mock.side_effect = None
        establish_codecommit_repository_and_branch_mock.return_value = ('repository', 'branch')

        initialize.configure_codecommit(None)

        validate_action_mock.assert_called_once_with(
            'Do you wish to continue with CodeCommit? (y/N) (default is n)',
            'y'
        )
        source_control_mock.setup_codecommit_cred_config.assert_called_once_with()
        establish_codecommit_repository_and_branch_mock.assert_called_once_with(
            None, None, source_control_mock, None
        )

    @mock.patch('ebcli.controllers.initialize.io.validate_action')
    @mock.patch('ebcli.controllers.initialize.establish_codecommit_repository_and_branch')
    @mock.patch('ebcli.controllers.initialize.SourceControl.get_source_control')
    def test_configure_codecommit__source_location_specified(
            self,
            get_source_control_mock,
            establish_codecommit_repository_and_branch_mock,
            validate_action_mock,
    ):
        source_control_mock = mock.MagicMock()
        get_source_control_mock.return_value = source_control_mock
        validate_action_mock.side_effect = None
        establish_codecommit_repository_and_branch_mock.return_value = ('repository', 'branch')

        initialize.configure_codecommit('codecommit/repository/branch')

        validate_action_mock.assert_not_called()
        source_control_mock.setup_codecommit_cred_config.assert_called_once_with()
        establish_codecommit_repository_and_branch_mock.assert_called_once_with(
            'repository', 'branch', source_control_mock, 'codecommit'
        )

    @mock.patch('ebcli.controllers.initialize.fileoperations.get_application_name')
    @mock.patch('ebcli.controllers.initialize.fileoperations.get_current_directory_name')
    @mock.patch('ebcli.controllers.initialize._get_application_name_interactive')
    def test_get_app_name__app_name_passed_in_as_positional_argument__interactive_mode(
            self,
            _get_application_name_interactive_mock,
            get_current_directory_name_mock,
            get_application_name_mock
    ):
        self.assertEqual(
            'my-application',
            initialize.get_app_name('my-application', True, False)
        )

        get_application_name_mock.assert_not_called()
        get_current_directory_name_mock.assert_not_called()
        _get_application_name_interactive_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.fileoperations.get_application_name')
    @mock.patch('ebcli.controllers.initialize.fileoperations.get_current_directory_name')
    @mock.patch('ebcli.controllers.initialize._get_application_name_interactive')
    def test_get_app_name__app_name_passed_in_as_positional_argument__force_non_interactive_mode(
            self,
            _get_application_name_interactive_mock,
            get_current_directory_name_mock,
            get_application_name_mock
    ):
        self.assertEqual(
            'my-application',
            initialize.get_app_name('my-application', True, False)
        )

        get_application_name_mock.assert_not_called()
        get_current_directory_name_mock.assert_not_called()
        _get_application_name_interactive_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.fileoperations.get_application_name')
    @mock.patch('ebcli.controllers.initialize.fileoperations.get_current_directory_name')
    @mock.patch('ebcli.controllers.initialize._get_application_name_interactive')
    def test_get_app_name__app_name_passed_in_as_positional_argument__neither_platform_nor_interactive_arguments_were_specified(
            self,
            _get_application_name_interactive_mock,
            get_current_directory_name_mock,
            get_application_name_mock
    ):
        self.assertEqual(
            'my-application',
            initialize.get_app_name('my-application', False, False)
        )

        get_application_name_mock.assert_not_called()
        get_current_directory_name_mock.assert_not_called()
        _get_application_name_interactive_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.fileoperations.get_application_name')
    @mock.patch('ebcli.controllers.initialize.fileoperations.get_current_directory_name')
    @mock.patch('ebcli.controllers.initialize._get_application_name_interactive')
    def test_get_app_name__app_name_not_passed__interactive_mode__directory_not_previously_initialized(
            self,
            _get_application_name_interactive_mock,
            get_current_directory_name_mock,
            get_application_name_mock
    ):
        get_application_name_mock.side_effect = initialize.NotInitializedError
        _get_application_name_interactive_mock.return_value = 'my-application'
        self.assertEqual(
            'my-application',
            initialize.get_app_name(None, True, False)
        )

        get_application_name_mock.assert_called_once_with(default=None)
        get_current_directory_name_mock.assert_not_called()
        _get_application_name_interactive_mock.assert_called_once_with()

    @mock.patch('ebcli.controllers.initialize.fileoperations.get_application_name')
    @mock.patch('ebcli.controllers.initialize.fileoperations.get_current_directory_name')
    @mock.patch('ebcli.controllers.initialize._get_application_name_interactive')
    def test_get_app_name__app_name_not_passed__interactive_mode__directory_previously_initialized_but_customer_is_prompted_for_name_anyway(
            self,
            _get_application_name_interactive_mock,
            get_current_directory_name_mock,
            get_application_name_mock
    ):
        get_application_name_mock.return_value = 'my-app'
        _get_application_name_interactive_mock.return_value = 'my-application'
        self.assertEqual(
            'my-application',
            initialize.get_app_name(None, True, False)
        )

        get_application_name_mock.assert_called_once_with(default=None)
        get_current_directory_name_mock.assert_not_called()
        _get_application_name_interactive_mock.assert_called_once_with()

    @mock.patch('ebcli.controllers.initialize.fileoperations.get_application_name')
    @mock.patch('ebcli.controllers.initialize.fileoperations.get_current_directory_name')
    @mock.patch('ebcli.controllers.initialize._get_application_name_interactive')
    def test_get_app_name__app_name_not_passed__force_non_interactive_mode__directory_not_previously_initialized(
            self,
            _get_application_name_interactive_mock,
            get_current_directory_name_mock,
            get_application_name_mock
    ):
        get_application_name_mock.side_effect = initialize.NotInitializedError
        get_current_directory_name_mock.return_value = 'my-application-dir'
        self.assertEqual(
            'my-application-dir',
            initialize.get_app_name(None, False, True)
        )

        get_application_name_mock.assert_called_once_with(default=None)
        get_current_directory_name_mock.assert_called_once_with()
        _get_application_name_interactive_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.fileoperations.get_application_name')
    @mock.patch('ebcli.controllers.initialize.fileoperations.get_current_directory_name')
    @mock.patch('ebcli.controllers.initialize._get_application_name_interactive')
    def test_get_app_name__app_name_not_passed__force_non_interactive_mode__directory_previously_initialized(
            self,
            _get_application_name_interactive_mock,
            get_current_directory_name_mock,
            get_application_name_mock
    ):
        get_application_name_mock.return_value = 'my-application'
        get_current_directory_name_mock.return_value = 'my-application-dir'
        self.assertEqual(
            'my-application-dir',
            initialize.get_app_name(None, False, True)
        )

        get_application_name_mock.assert_called_once_with(default=None)
        get_current_directory_name_mock.assert_called_once_with()
        _get_application_name_interactive_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_default_solution_stack')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.controllers.initialize.extract_solution_stack_from_env_yaml')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_solution_stack_from_customer')
    def test_get_solution_stack__platform_argument_passed_in_through_the_command_line(
            self,
            get_solution_stack_from_customer_mock,
            extract_solution_stack_from_env_yaml_mock,
            find_solution_stack_from_string_mock,
            get_default_solution_stack_mock
    ):
        self.assertEqual(
            'php-5.5',
            initialize.get_solution_stack('php-5.5', 'php-5.4', False)
        )

        get_default_solution_stack_mock.assert_not_called()
        find_solution_stack_from_string_mock.assert_called_once_with('php-5.5')
        get_solution_stack_from_customer_mock.assert_not_called()
        extract_solution_stack_from_env_yaml_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_default_solution_stack')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.controllers.initialize.fileoperations.env_yaml_exists')
    @mock.patch('ebcli.controllers.initialize.extract_solution_stack_from_env_yaml')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_solution_stack_from_customer')
    def test_get_solution_stack__platform_argument_not_passed_in_through_the_command_line__application_not_previously_initialized_or_created__no_env_yaml(
            self,
            get_solution_stack_from_customer_mock,
            extract_solution_stack_from_env_yaml_mock,
            env_yaml_exists_mock,
            find_solution_stack_from_string_mock,
            get_default_solution_stack_mock
    ):
        get_default_solution_stack_mock.side_effect = initialize.NotInitializedError
        env_yaml_exists_mock.return_value = False

        initialize.get_solution_stack(None, None, False)

        get_default_solution_stack_mock.assert_called_once_with()
        find_solution_stack_from_string_mock.assert_not_called()
        extract_solution_stack_from_env_yaml_mock.assert_not_called()
        get_solution_stack_from_customer_mock.assert_called_once_with()

    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_default_solution_stack')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.controllers.initialize.fileoperations.env_yaml_exists')
    @mock.patch('ebcli.controllers.initialize.extract_solution_stack_from_env_yaml')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_solution_stack_from_customer')
    def test_get_solution_stack__platform_argument_not_passed_in__application_previously_initialized(
            self,
            get_solution_stack_from_customer_mock,
            extract_solution_stack_from_env_yaml_mock,
            env_yaml_exists_mock,
            find_solution_stack_from_string_mock,
            get_default_solution_stack_mock
    ):
        get_default_solution_stack_mock.return_value = 'php 7.1'
        env_yaml_exists_mock.return_value = True

        self.assertEqual(
            'php 7.1',
            initialize.get_solution_stack(None, None, False)
        )

        get_default_solution_stack_mock.assert_called_once_with()
        find_solution_stack_from_string_mock.assert_called_once_with('php 7.1')
        extract_solution_stack_from_env_yaml_mock.assert_not_called()
        get_solution_stack_from_customer_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_default_solution_stack')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.controllers.initialize.fileoperations.env_yaml_exists')
    @mock.patch('ebcli.controllers.initialize.extract_solution_stack_from_env_yaml')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_solution_stack_from_customer')
    def test_get_solution_stack__fallback_to_keyname_associated_with_application(
            self,
            get_solution_stack_from_customer_mock,
            extract_solution_stack_from_env_yaml_mock,
            env_yaml_exists_mock,
            find_solution_stack_from_string_mock,
            get_default_solution_stack_mock
    ):
        get_default_solution_stack_mock.side_effect = initialize.NotInitializedError
        env_yaml_exists_mock.return_value = False

        self.assertEqual(
            'php 5.4',
            initialize.get_solution_stack(None, 'php 5.4', False)
        )

        get_default_solution_stack_mock.assert_called_once_with()
        find_solution_stack_from_string_mock.assert_not_called()
        extract_solution_stack_from_env_yaml_mock.assert_not_called()
        get_solution_stack_from_customer_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_default_solution_stack')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.controllers.initialize.fileoperations.env_yaml_exists')
    @mock.patch('ebcli.controllers.initialize.extract_solution_stack_from_env_yaml')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_solution_stack_from_customer')
    def test_get_solution_stack__fallback_to_keyname_in_env_yaml(
            self,
            get_solution_stack_from_customer_mock,
            extract_solution_stack_from_env_yaml_mock,
            env_yaml_exists_mock,
            find_solution_stack_from_string_mock,
            get_default_solution_stack_mock
    ):
        get_default_solution_stack_mock.side_effect = initialize.NotInitializedError
        env_yaml_exists_mock.return_value = True
        extract_solution_stack_from_env_yaml_mock.return_value = 'php 5.6'

        self.assertEqual(
            'php 5.6',
            initialize.get_solution_stack(None, None, False)
        )

        get_default_solution_stack_mock.assert_called_once_with()
        find_solution_stack_from_string_mock.assert_not_called()
        extract_solution_stack_from_env_yaml_mock.assert_called_once_with()
        get_solution_stack_from_customer_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_default_solution_stack')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.controllers.initialize.fileoperations.env_yaml_exists')
    @mock.patch('ebcli.controllers.initialize.extract_solution_stack_from_env_yaml')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_solution_stack_from_customer')
    def test_get_solution_stack__interactive_flow__but_platform_command_line_argument_was_passed(
            self,
            get_solution_stack_from_customer_mock,
            extract_solution_stack_from_env_yaml_mock,
            env_yaml_exists_mock,
            find_solution_stack_from_string_mock,
            get_default_solution_stack_mock
    ):
        env_yaml_exists_mock.return_value = False

        self.assertEqual(
            'php-5.5',
            initialize.get_solution_stack('php-5.5', None, True)
        )

        get_default_solution_stack_mock.assert_not_called()
        find_solution_stack_from_string_mock.assert_called_once_with('php-5.5')
        extract_solution_stack_from_env_yaml_mock.assert_not_called()
        get_solution_stack_from_customer_mock.assert_not_called()

    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_default_solution_stack')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.controllers.initialize.fileoperations.env_yaml_exists')
    @mock.patch('ebcli.controllers.initialize.extract_solution_stack_from_env_yaml')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_solution_stack_from_customer')
    def test_get_solution_stack__interactive_flow__platform_command_line_argument_was_not_passed__platform_name_from_config_yml_found_but_disregarded(
            self,
            get_solution_stack_from_customer_mock,
            extract_solution_stack_from_env_yaml_mock,
            env_yaml_exists_mock,
            find_solution_stack_from_string_mock,
            get_default_solution_stack_mock
    ):
        get_default_solution_stack_mock.return_value = 'php 7.1'
        get_solution_stack_from_customer_mock.return_value = self.solution
        env_yaml_exists_mock.return_value = True

        self.assertEqual(
            'PHP 5.5',
            initialize.get_solution_stack(None, None, True)
        )

        get_default_solution_stack_mock.assert_called_once_with()
        find_solution_stack_from_string_mock.assert_called_once_with('php 7.1')
        extract_solution_stack_from_env_yaml_mock.assert_not_called()
        get_solution_stack_from_customer_mock.assert_called_once_with()

    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_default_solution_stack')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.controllers.initialize.fileoperations.env_yaml_exists')
    @mock.patch('ebcli.controllers.initialize.extract_solution_stack_from_env_yaml')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_solution_stack_from_customer')
    def test_get_solution_stack__interactive_flow__platform_name_found_in_env_yaml_but_disregarded(
            self,
            get_solution_stack_from_customer_mock,
            extract_solution_stack_from_env_yaml_mock,
            env_yaml_exists_mock,
            find_solution_stack_from_string_mock,
            get_default_solution_stack_mock
    ):
        get_default_solution_stack_mock.side_effect = initialize.NotInitializedError
        get_solution_stack_from_customer_mock.return_value = self.solution
        env_yaml_exists_mock.return_value = True
        extract_solution_stack_from_env_yaml_mock.return_value = 'PHP 7.1'

        self.assertEqual(
            'PHP 5.5',
            initialize.get_solution_stack(None, None, True)
        )

        get_default_solution_stack_mock.assert_called_once_with()
        find_solution_stack_from_string_mock.assert_not_called()
        extract_solution_stack_from_env_yaml_mock.assert_called_once_with()
        get_solution_stack_from_customer_mock.assert_called_once_with()

    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_default_solution_stack')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.find_solution_stack_from_string')
    @mock.patch('ebcli.controllers.initialize.fileoperations.env_yaml_exists')
    @mock.patch('ebcli.controllers.initialize.extract_solution_stack_from_env_yaml')
    @mock.patch('ebcli.controllers.initialize.solution_stack_ops.get_solution_stack_from_customer')
    def test_get_solution_stack__interactive_flow__platform_command_line_argument_was_not_passed(
            self,
            get_solution_stack_from_customer_mock,
            extract_solution_stack_from_env_yaml_mock,
            env_yaml_exists_mock,
            find_solution_stack_from_string_mock,
            get_default_solution_stack_mock
    ):
        get_solution_stack_from_customer_mock.return_value = self.solution
        get_default_solution_stack_mock.side_effect = initialize.NotInitializedError
        env_yaml_exists_mock.return_value = False

        self.assertEqual(
            'PHP 5.5',
            initialize.get_solution_stack(None, None, True)
        )

        get_default_solution_stack_mock.assert_called_once_with()
        find_solution_stack_from_string_mock.assert_not_called()
        extract_solution_stack_from_env_yaml_mock.assert_not_called()
        get_solution_stack_from_customer_mock.assert_called_once_with()

    def test_should_prompt_customer_to_opt_into_codecommit__force_non_interactive(self):
        self.assertFalse(
            initialize.should_prompt_customer_to_opt_into_codecommit(
                True,
                'us-west-2',
                'codecommit/repository/branch'
            )
        )

    def test_should_prompt_customer_to_opt_into_codecommit__no_source(self):
        self.assertFalse(
            initialize.should_prompt_customer_to_opt_into_codecommit(False, 'us-west-2', None)
        )

    @mock.patch('ebcli.controllers.initialize.codecommit.region_supported')
    def test_should_prompt_customer_to_opt_into_codecommit__unsupported_region(
            self,
            region_supported_mock
    ):
        region_supported_mock.return_value = False

        self.assertFalse(
            initialize.should_prompt_customer_to_opt_into_codecommit(
                False,
                'us-west-10',
                'codecommit/repository/branch'
            )
        )

        region_supported_mock.assert_called_once_with()

    @mock.patch('ebcli.controllers.initialize.codecommit.region_supported')
    def test_should_prompt_customer_to_opt_into_codecommit__unsupported_region(
            self,
            region_supported_mock
    ):
        region_supported_mock.return_value = False

        self.assertFalse(
            initialize.should_prompt_customer_to_opt_into_codecommit(
                False,
                'us-west-10',
                'codecommit/repository/branch'
            )
        )

        region_supported_mock.assert_called_once_with('us-west-10')

    @mock.patch('ebcli.controllers.initialize.codecommit.region_supported')
    @mock.patch('ebcli.controllers.initialize.fileoperations.is_git_directory_present')
    @mock.patch('ebcli.controllers.initialize.io.echo')
    def test_should_prompt_customer_to_opt_into_codecommit__directory_is_not_git_inited(
            self,
            echo_mock,
            is_git_directory_present_mock,
            region_supported_mock
    ):
        region_supported_mock.return_value = True
        is_git_directory_present_mock.return_value = False

        self.assertFalse(
            initialize.should_prompt_customer_to_opt_into_codecommit(
                False,
                'us-west-2',
                'codecommit/repository/branch'
            )
        )

        region_supported_mock.assert_called_once_with('us-west-2')
        echo_mock.assert_called_once_with(
            'Cannot setup CodeCommit because there is no Source Control setup, continuing with initialization'
        )

    @mock.patch('ebcli.controllers.initialize.codecommit.region_supported')
    @mock.patch('ebcli.controllers.initialize.fileoperations.is_git_directory_present')
    @mock.patch('ebcli.controllers.initialize.fileoperations.program_is_installed')
    @mock.patch('ebcli.controllers.initialize.io.echo')
    def test_should_prompt_customer_to_opt_into_codecommit__git_not_installed(
            self,
            echo_mock,
            program_is_installed_mock,
            is_git_directory_present_mock,
            region_supported_mock
    ):
        region_supported_mock.return_value = True
        is_git_directory_present_mock.return_value = True
        program_is_installed_mock.return_value = False

        self.assertFalse(
            initialize.should_prompt_customer_to_opt_into_codecommit(
                False,
                'us-west-2',
                'codecommit/repository/branch'
            )
        )

        region_supported_mock.assert_called_once_with('us-west-2')
        program_is_installed_mock.assert_called_once_with('git')
        echo_mock.assert_called_once_with(
            'Cannot setup CodeCommit because there is no Source Control setup, continuing with initialization'
        )

    @mock.patch('ebcli.controllers.initialize.codecommit.region_supported')
    @mock.patch('ebcli.controllers.initialize.fileoperations.is_git_directory_present')
    @mock.patch('ebcli.controllers.initialize.fileoperations.program_is_installed')
    @mock.patch('ebcli.controllers.initialize.io.echo')
    @mock.patch('ebcli.controllers.initialize.directory_is_already_associated_with_a_branch')
    def test_should_prompt_customer_to_opt_into_codecommit__directory_is_already_set_up_to_use_codecommit(
            self,
            directory_is_already_associated_with_a_branch_mock,
            echo_mock,
            program_is_installed_mock,
            is_git_directory_present_mock,
            region_supported_mock
    ):
        region_supported_mock.return_value = True
        is_git_directory_present_mock.return_value = True
        program_is_installed_mock.return_value = True
        directory_is_already_associated_with_a_branch_mock.return_value = True

        self.assertFalse(
            initialize.should_prompt_customer_to_opt_into_codecommit(
                False,
                'us-west-2',
                'codecommit/repository/branch'
            )
        )

        region_supported_mock.assert_called_once_with('us-west-2')
        program_is_installed_mock.assert_called_once_with('git')
        echo_mock.assert_not_called()
        directory_is_already_associated_with_a_branch_mock.assert_called_once_with()

    @mock.patch('ebcli.controllers.initialize.codecommit.region_supported')
    @mock.patch('ebcli.controllers.initialize.fileoperations.is_git_directory_present')
    @mock.patch('ebcli.controllers.initialize.fileoperations.program_is_installed')
    @mock.patch('ebcli.controllers.initialize.io.echo')
    @mock.patch('ebcli.controllers.initialize.directory_is_already_associated_with_a_branch')
    def test_should_prompt_customer_to_opt_into_codecommit__returns_true(
            self,
            directory_is_already_associated_with_a_branch_mock,
            echo_mock,
            program_is_installed_mock,
            is_git_directory_present_mock,
            region_supported_mock
    ):
        region_supported_mock.return_value = True
        is_git_directory_present_mock.return_value = True
        program_is_installed_mock.return_value = True
        directory_is_already_associated_with_a_branch_mock.return_value = False

        self.assertTrue(
            initialize.should_prompt_customer_to_opt_into_codecommit(
                False,
                'us-west-2',
                'codecommit/repository/branch'
            )
        )

        region_supported_mock.assert_called_once_with('us-west-2')
        program_is_installed_mock.assert_called_once_with('git')
        echo_mock.assert_not_called()
        directory_is_already_associated_with_a_branch_mock.assert_called_once_with()

    def test_customer_is_avoiding_non_interactive_flow(self):
        self.assertTrue(initialize.customer_is_avoiding_non_interactive_flow('php-7.2'))

    def test_customer_is_avoiding_non_interactive_flow__false(self):
        self.assertFalse(initialize.customer_is_avoiding_non_interactive_flow(None))

    @mock.patch('ebcli.controllers.initialize.SourceControl.get_source_control')
    @mock.patch('ebcli.controllers.initialize.fileoperations.get_current_directory_name')
    @mock.patch('ebcli.controllers.initialize.codecommit.list_repositories')
    @mock.patch('ebcli.controllers.initialize.io.echo')
    @mock.patch('ebcli.controllers.initialize.utils.prompt_for_item_in_list')
    def test_get_repository_interactive__one_or_more_repositories_retrieved_from_codecommit__choose_existing_repository(
            self,
            prompt_for_item_in_list_mock,
            echo_mock,
            list_repositories_mock,
            get_current_directory_name_mock,
            get_source_control_mock
    ):
        get_source_control_mock.current_repository.return_value = 'current-repository'
        list_repositories_mock.return_value = mock_responses.LIST_REPOSITORIES_RESPONSE
        prompt_for_item_in_list_mock.return_value = 'my-other-repository'

        self.assertEqual('my-other-repository', initialize.get_repository_interactive())

        get_current_directory_name_mock.assert_not_called()
        echo_mock.assert_has_calls(
            [
                mock.call(),
                mock.call('Select a repository')
            ]
        )

    @mock.patch('ebcli.controllers.initialize.SourceControl.get_source_control')
    @mock.patch('ebcli.controllers.initialize.fileoperations.get_current_directory_name')
    @mock.patch('ebcli.controllers.initialize.codecommit.list_repositories')
    @mock.patch('ebcli.controllers.initialize.io.echo')
    @mock.patch('ebcli.controllers.initialize.utils.prompt_for_item_in_list')
    @mock.patch('ebcli.controllers.initialize.io.prompt_for_unique_name')
    @mock.patch('ebcli.controllers.initialize.create_codecommit_repository')
    def test_get_repository_interactive__one_or_more_repositories_retrieved_from_codecommit__customer_chooses_to_create_new_repository(
            self,
            create_codecommit_repository_mock,
            prompt_for_unique_name_mock,
            prompt_for_item_in_list_mock,
            echo_mock,
            list_repositories_mock,
            get_current_directory_name_mock,
            get_source_control_mock
    ):
        get_source_control_mock.current_repository.return_value = 'current-repository'
        list_repositories_mock.return_value = mock_responses.LIST_REPOSITORIES_RESPONSE
        prompt_for_item_in_list_mock.return_value = '[ Create new Repository ]'
        prompt_for_unique_name_mock.return_value = 'new-repository-name'

        self.assertEqual('new-repository-name', initialize.get_repository_interactive())

        get_current_directory_name_mock.assert_not_called()
        echo_mock.assert_has_calls(
            [
                mock.call(),
                mock.call('Select a repository'),
                mock.call(),
                mock.call('Enter Repository Name')
            ]
        )
        create_codecommit_repository_mock.assert_called_once_with('new-repository-name')

    @mock.patch('ebcli.controllers.initialize.SourceControl.get_source_control')
    @mock.patch('ebcli.controllers.initialize.fileoperations.get_current_directory_name')
    @mock.patch('ebcli.controllers.initialize.codecommit.list_repositories')
    @mock.patch('ebcli.controllers.initialize.io.echo')
    @mock.patch('ebcli.controllers.initialize.io.prompt_for_unique_name')
    @mock.patch('ebcli.controllers.initialize.create_codecommit_repository')
    def test_get_repository_interactive__no_repositories_retrieved_from_codecommit__customer_chooses_to_create_new_repository(
            self,
            create_codecommit_repository_mock,
            prompt_for_unique_name_mock,
            echo_mock,
            list_repositories_mock,
            get_current_directory_name_mock,
            get_source_control_mock
    ):
        get_source_control_mock.current_repository.return_value = 'current-repository'
        list_repositories_mock.return_value = {
            'repositories': []
        }
        prompt_for_unique_name_mock.return_value = 'new-repository-name'

        self.assertEqual('new-repository-name', initialize.get_repository_interactive())

        get_current_directory_name_mock.assert_not_called()
        echo_mock.assert_has_calls(
            [
                mock.call(),
                mock.call('Enter Repository Name')
            ]
        )
        create_codecommit_repository_mock.assert_called_once_with('new-repository-name')


class TestInitMultipleModules(unittest.TestCase):
    platform = PlatformVersion(
        'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5'
    )

    def setUp(self):
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')

        os.chdir('testDir')

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')

    def test_multiple_modules__none_of_the_specified_modules_actually_exists(self):
        app = EB(
            argv=[
                'init',
                '--modules', 'module-1', 'module-2',
            ]
        )
        app.setup()
        app.run()

    @mock.patch('ebcli.controllers.initialize.commonops.get_region')
    @mock.patch('ebcli.controllers.initialize.get_solution_stack')
    @mock.patch('ebcli.controllers.initialize.get_app_name')
    @mock.patch('ebcli.controllers.initialize.configure_keyname')
    @mock.patch('ebcli.controllers.initialize.commonops.set_up_credentials')
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
            configure_keyname_mock,
            get_app_name_mock,
            get_solution_stack_mock,
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
        get_solution_stack_mock.return_value = None
        create_app_mock.return_value = [
            '64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)',
            'my-ec2-key-name'
        ]
        pull_down_app_info_mock.return_value = [
            '64bit Amazon Linux 2014.03 v1.0.6 running PHP 7.1',
            'my-ec2-key-name'
        ]
        get_solution_stack_from_customer_mock.return_value = '64bit Amazon Linux 2014.03 v1.0.6 running PHP 7.1'

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
                mock.call('my-application', 'us-east-1', '64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)'),
                mock.call('my-application', 'us-east-1', '64bit Amazon Linux 2014.03 v1.0.6 running PHP 7.1')
            ]
        )
        create_app_mock.assert_called_once_with('my-application', default_env=None)
        pull_down_app_info_mock.assert_called_once_with('my-application', default_env=None)
        self.assertEqual(2, set_region_mock.call_count)
        self.assertEqual(2, configure_keyname_mock.call_count)

    @mock.patch('ebcli.controllers.initialize.aws.set_region')
    @mock.patch('ebcli.controllers.initialize.get_solution_stack')
    @mock.patch('ebcli.controllers.initialize.get_app_name')
    @mock.patch('ebcli.controllers.initialize.configure_keyname')
    @mock.patch('ebcli.controllers.initialize.commonops.set_up_credentials')
    @mock.patch('ebcli.controllers.initialize.commonops.create_app')
    @mock.patch('ebcli.controllers.initialize.commonops.pull_down_app_info')
    @mock.patch('ebcli.controllers.initialize.commonops.get_region_from_inputs')
    @mock.patch('ebcli.controllers.initialize.initializeops.setup')
    def test_multiple_modules__interactive_mode__solution_stack_is_passed_through_command_line(
            self,
            setup_mock,
            get_region_from_inputs_mock,
            pull_down_app_info_mock,
            create_app_mock,
            set_up_credentials_mock,
            configure_keyname_mock,
            get_app_name_mock,
            get_solution_stack_mock,
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
        get_solution_stack_mock.return_value = '64bit Amazon Linux 2014.03 v1.0.6 running PHP 7.1'
        create_app_mock.return_value = [
            '64bit Amazon Linux 2015.09 v2.0.6 running Multi-container Docker 1.7.1 (Generic)',
            'my-ec2-key-name'
        ]
        pull_down_app_info_mock.return_value = [
            '64bit Amazon Linux 2014.03 v1.0.6 running PHP 7.1',
            'my-ec2-key-name'
        ]

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
        create_app_mock.assert_called_once_with('my-application', default_env='/ni')
        pull_down_app_info_mock.assert_called_once_with('my-application', default_env='/ni')
        self.assertEqual(
            2,
            set_region_mock.call_count
        )
        self.assertEqual(2, configure_keyname_mock.call_count)
