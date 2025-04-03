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
import zipfile
from unittest.mock import MagicMock

import mock
import unittest

from ebcli.controllers import deploy
from ebcli.core.ebcore import EB
from ebcli.core import fileoperations
from ebcli.objects.environment import Environment
from ebcli.objects.platform import PlatformVersion
from ebcli.objects.exceptions import InvalidOptionsError, NotInitializedError


class TestDeploy(unittest.TestCase):
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


class TestDeploy(TestDeploy):
    @mock.patch('ebcli.controllers.deploy.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.controllers.deploy.statusops.alert_environment_status')
    def test_check_env_lifecycle_state(
        self,
        alert_environment_status_mock,
        get_environment_mock,
    ):
        environment_name = 'environment-1'
        environment = Environment(name=environment_name)
        get_environment_mock.return_value = environment

        deploy._check_env_lifecycle_state(env_name=environment_name)

        get_environment_mock.assert_called_once_with(env_name=environment_name)
        alert_environment_status_mock.assert_called_once_with(environment)


class TestErrorConditions(TestDeploy):
    @mock.patch('ebcli.controllers.deploy._check_env_lifecycle_state')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    def test_deploy__version_and_message_specified_together(
            self,
            get_env_name_mock,
            get_app_name_mock,
            _check_env_lifecycle_state_mock,
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(argv=['deploy', '--version', 'my-app-version', '--message', 'my-message'])
        app.setup()

        with self.assertRaises(deploy.InvalidOptionsError) as context_manager:
            app.run()

        self.assertEqual(
            'You cannot use the "--version" option with either the "--message" or "--label" option.',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.controllers.deploy._check_env_lifecycle_state')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    def test_deploy__version_and_label_specified_together(
            self,
            get_env_name_mock,
            get_app_name_mock,
            _check_env_lifecycle_state_mock,
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(argv=['deploy', '--version', 'my-app-version', '--label', 'my-label'])
        app.setup()

        with self.assertRaises(deploy.InvalidOptionsError) as context_manager:
            app.run()

        self.assertEqual(
            'You cannot use the "--version" option with either the "--message" or "--label" option.',
            str(context_manager.exception)
        )


class TestDeployNormal(TestDeploy):
    @mock.patch('ebcli.controllers.deploy._check_env_lifecycle_state')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock,
            _check_env_lifecycle_state_mock,
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(argv=['deploy'])
        app.setup()
        app.run()

        _check_env_lifecycle_state_mock.assert_called_once_with('environment-1')
        deploy_mock.assert_called_with(
            'my-application',
            'environment-1',
            None,
            None,
            None,
            group_name=None,
            process_app_versions=False,
            source=None,
            staged=False,
            timeout=None,
            source_bundle=None
        )

    @mock.patch('ebcli.controllers.deploy._check_env_lifecycle_state')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy__nohang_sets_timeout_to_zero(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock,
            _check_env_lifecycle_state_mock,
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(argv=['deploy', '--nohang', '--timeout', '5'])
        app.setup()
        app.run()

        _check_env_lifecycle_state_mock.assert_called_once_with('environment-1')
        deploy_mock.assert_called_with(
            'my-application',
            'environment-1',
            None,
            None,
            None,
            group_name=None,
            process_app_versions=False,
            source=None,
            staged=False,
            timeout=0,
            source_bundle=None
        )

    @mock.patch('ebcli.controllers.deploy._check_env_lifecycle_state')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy__with_version_label(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock,
            _check_env_lifecycle_state_mock,
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(argv=['deploy', '--version', 'my-version'])
        app.setup()
        app.run()

        _check_env_lifecycle_state_mock.assert_called_once_with('environment-1')
        deploy_mock.assert_called_with(
            'my-application',
            'environment-1',
            'my-version',
            None,
            None,
            group_name=None,
            process_app_versions=False,
            staged=False,
            timeout=None,
            source=None,
            source_bundle=None
        )

    @mock.patch('ebcli.controllers.deploy._check_env_lifecycle_state')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy__with_label_and_message(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock,
            _check_env_lifecycle_state_mock,
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(
            argv=[
                'deploy',
                '--label', 'my-label',
                '--message', 'This is my message'
            ]
        )
        app.setup()
        app.run()

        _check_env_lifecycle_state_mock.assert_called_once_with('environment-1')
        deploy_mock.assert_called_with(
            'my-application',
            'environment-1',
            None,
            'my-label',
            'This is my message',
            group_name=None,
            process_app_versions=False,
            staged=False,
            timeout=None,
            source=None,
            source_bundle=None
        )

    @mock.patch('ebcli.controllers.deploy._check_env_lifecycle_state')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy__process_app_version_because_env_yaml_exists(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock,
            _check_env_lifecycle_state_mock,
    ):
        open('env.yaml', 'w').close()
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(
            argv=[
                'deploy',
                '--label', 'my-label',
                '--message', 'This is my message'
            ]
        )
        app.setup()
        app.run()

        _check_env_lifecycle_state_mock.assert_called_once_with('environment-1')
        deploy_mock.assert_called_with(
            'my-application',
            'environment-1',
            None,
            'my-label',
            'This is my message',
            group_name=None,
            process_app_versions=True,
            source=None,
            staged=False,
            timeout=None,
            source_bundle=None
        )

    @mock.patch('ebcli.controllers.deploy._check_env_lifecycle_state')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy__process_app_version_because_process_flag_is_specified(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock,
            _check_env_lifecycle_state_mock,
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(
            argv=[
                'deploy',
                '--label', 'my-label',
                '--message', 'This is my message',
                '--process'
            ]
        )
        app.setup()
        app.run()

        _check_env_lifecycle_state_mock.assert_called_once_with('environment-1')
        deploy_mock.assert_called_with(
            'my-application',
            'environment-1',
            None,
            'my-label',
            'This is my message',
            group_name=None,
            process_app_versions=True,
            staged=False,
            timeout=None,
            source=None,
            source_bundle=None
        )

    @mock.patch('ebcli.controllers.deploy._check_env_lifecycle_state')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy__pass_group_name(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock,
            _check_env_lifecycle_state_mock,
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(
            argv=[
                'deploy',
                '--env-group-suffix', 'group-name',
            ]
        )
        app.setup()
        app.run()

        _check_env_lifecycle_state_mock.assert_called_once_with('environment-1')
        deploy_mock.assert_called_with(
            'my-application',
            'environment-1',
            None,
            None,
            None,
            group_name='group-name',
            process_app_versions=False,
            source=None,
            staged=False,
            timeout=None,
            source_bundle=None
        )

    @mock.patch('ebcli.controllers.deploy._check_env_lifecycle_state')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy__specify_codecommit_source(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock,
            _check_env_lifecycle_state_mock,
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(
            argv=[
                'deploy',
                '--source', 'codecommit/my-repository/my-branch'
            ]
        )
        app.setup()
        app.run()

        _check_env_lifecycle_state_mock.assert_called_once_with('environment-1')
        deploy_mock.assert_called_with(
            'my-application',
            'environment-1',
            None,
            None,
            None,
            group_name=None,
            process_app_versions=False,
            staged=False,
            timeout=None,
            source='codecommit/my-repository/my-branch',
            source_bundle=None
        )

    @mock.patch('ebcli.controllers.deploy._check_env_lifecycle_state')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy__specify_codecommit_source_with_forward_slash_in_branch_name(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock,
            _check_env_lifecycle_state_mock,
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(
            argv=[
                'deploy',
                '--source', 'codecommit/my-repository/my-branch/feature'
            ]
        )
        app.setup()
        app.run()

        _check_env_lifecycle_state_mock.assert_called_once_with('environment-1')
        deploy_mock.assert_called_with(
            'my-application',
            'environment-1',
            None,
            None,
            None,
            group_name=None,
            process_app_versions=False,
            staged=False,
            timeout=None,
            source='codecommit/my-repository/my-branch/feature',
            source_bundle=None
        )

    @mock.patch('ebcli.controllers.deploy._check_env_lifecycle_state')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy__indicate_staged_changes_must_be_used(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock,
            _check_env_lifecycle_state_mock,
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(
            argv=[
                'deploy',
                '--process',
                '--staged'
            ]
        )
        app.setup()
        app.run()

        _check_env_lifecycle_state_mock.assert_called_once_with('environment-1')
        deploy_mock.assert_called_with(
            'my-application',
            'environment-1',
            None,
            None,
            None,
            group_name=None,
            process_app_versions=True,
            source=None,
            staged=True,
            timeout=None,
            source_bundle=None
        )

    @mock.patch('ebcli.controllers.deploy.elasticbeanstalk.get_environment')
    @mock.patch('ebcli.controllers.deploy._check_env_lifecycle_state')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    @mock.patch('ebcli.controllers.deploy.get_or_create_source_bundle')
    def test_deploy_with_archive(
            self,
            get_source_bundle_mock,
            deploy_mock,
            _check_env_lifecycle_state_mock,
            get_environment_mock,
    ):
        get_source_bundle_mock.return_value = 'path/to/generated/archive.zip'
        environment_mock = MagicMock()
        environment_mock.app_name = "my-application"
        get_environment_mock.return_value = environment_mock

        app = EB(
            argv=[
                'deploy',
                'environment-1',
                '--archive', 'my-source-directory',
                '--region', 'us-east-1'
            ]
        )
        app.setup()
        app.run()

        _check_env_lifecycle_state_mock.assert_called_once_with('environment-1')
        get_source_bundle_mock.assert_called_once_with(archive='my-source-directory', label=None)
        deploy_mock.assert_called_with(
            'my-application',
            'environment-1',
            None,
            'archive.zip',
            None,
            group_name=None,
            process_app_versions=False,
            source=None,
            staged=False,
            timeout=None,
            source_bundle='path/to/generated/archive.zip'
        )

    def test_deploy_with_archive__fails_without_environment_name(self):
        app = EB(
            argv=[
                'deploy',
                '--archive', 'my-source-directory',
                '--region', 'us-east-1'
            ]
        )
        app.setup()
        try:
            app.run()
        except InvalidOptionsError:
            pass

    def test_deploy_with_archive__fails_without_region_name(self):
        app = EB(
            argv=[
                'deploy',
                'environment-1',
                '--archive', 'my-source-directory',
            ]
        )
        app.setup()
        try:
            app.run()
        except InvalidOptionsError:
            pass

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


class TestGetOrCreateSourceBundle(unittest.TestCase):
    platform = PlatformVersion(
        'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5'
    )
    
    def setUp(self):
        self.root_dir = os.getcwd()
        if not os.path.exists('testDir'):
            os.mkdir('testDir')

        os.chdir('testDir')
        
        # Create test files and directories
        if not os.path.exists('source_dir'):
            os.mkdir('source_dir')
        
        with open(os.path.join('source_dir', 'test_file.txt'), 'w') as f:
            f.write('test content')
            
        # Create a test zip file
        self.test_zip_path = os.path.join(os.getcwd(), 'test_archive.zip')
        with zipfile.ZipFile(self.test_zip_path, 'w') as test_zip:
            test_zip.writestr('test_file.txt', 'test content')

    def tearDown(self):
        os.chdir(self.root_dir)
        shutil.rmtree('testDir')
        
    def create_config_file_in(self, path):
        original_dir = os.getcwd()
        os.chdir(path)
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            self.platform.name
        )
        os.chdir(original_dir)

    @mock.patch('ebcli.controllers.deploy.zipfile.is_zipfile')
    def test_get_or_create_source_bundle_with_zip_file(self, is_zipfile_mock):
        # Setup
        is_zipfile_mock.return_value = True
        archive_path = 'test_archive.zip'
        
        # Execute
        result = deploy.get_or_create_source_bundle(archive=archive_path)
        
        # Verify
        is_zipfile_mock.assert_called_once_with(archive_path)
        self.assertEqual(archive_path, result)

    @mock.patch('ebcli.controllers.deploy.zipfile.is_zipfile')
    @mock.patch('ebcli.controllers.deploy.path.isdir')
    def test_get_or_create_source_bundle_with_invalid_input(self, isdir_mock, is_zipfile_mock):
        # Setup
        is_zipfile_mock.return_value = False
        isdir_mock.return_value = False
        archive_path = 'non_existent_path'
        
        # Execute and verify
        with self.assertRaises(InvalidOptionsError) as context:
            deploy.get_or_create_source_bundle(archive=archive_path)
        
        self.assertIn(
            'The "--archive" option requires a directory or ZIP file as an argument.',
            str(context.exception)
        )
        is_zipfile_mock.assert_called_once_with(archive_path)
        isdir_mock.assert_called_once_with(archive_path)

    @mock.patch('ebcli.controllers.deploy.zipfile.is_zipfile')
    @mock.patch('ebcli.controllers.deploy.path.isdir')
    @mock.patch('ebcli.controllers.deploy.datetime')
    @mock.patch('ebcli.controllers.deploy.fileoperations.zip_up_folder')
    @mock.patch('ebcli.controllers.deploy.makedirs')
    @mock.patch('ebcli.controllers.deploy.path.expanduser')
    def test_get_or_create_source_bundle_with_directory(
            self,
            expanduser_mock,
            makedirs_mock,
            zip_up_folder_mock,
            datetime_mock,
            isdir_mock,
            is_zipfile_mock
    ):
        # Setup
        is_zipfile_mock.return_value = False
        isdir_mock.return_value = True
        expanduser_mock.return_value = '/home/user'
        
        # Mock datetime to return a fixed timestamp
        datetime_mock.datetime.now.return_value.timestamp.return_value = '1712175524.123456'
        datetime_mock.UTC = mock.MagicMock()
        
        archive_path = 'source_dir'
        expected_zip_path = os.path.join(
            '/home/user',
            '.ebartifacts',
            'archives',
            'archives-1712175524.123456.zip'
        )
        
        # Execute
        result = deploy.get_or_create_source_bundle(archive=archive_path)
        
        # Verify
        is_zipfile_mock.assert_called_once_with(archive_path)
        isdir_mock.assert_called_once_with(archive_path)
        makedirs_mock.assert_called_once_with(
            os.path.join('/home/user', '.ebartifacts', 'archives'),
            exist_ok=True
        )
        zip_up_folder_mock.assert_called_once_with(archive_path, expected_zip_path)
        self.assertEqual(expected_zip_path, result)

    @mock.patch('ebcli.controllers.deploy.zipfile.is_zipfile')
    @mock.patch('ebcli.controllers.deploy.path.isdir')
    @mock.patch('ebcli.controllers.deploy.datetime')
    @mock.patch('ebcli.controllers.deploy.fileoperations.zip_up_folder')
    @mock.patch('ebcli.controllers.deploy.makedirs')
    @mock.patch('ebcli.controllers.deploy.path.expanduser')
    def test_get_or_create_source_bundle_with_directory_and_label(
            self,
            expanduser_mock,
            makedirs_mock,
            zip_up_folder_mock,
            datetime_mock,
            isdir_mock,
            is_zipfile_mock
    ):
        # Setup
        is_zipfile_mock.return_value = False
        isdir_mock.return_value = True
        expanduser_mock.return_value = '/home/user'
        
        archive_path = 'source_dir'
        label = 'custom-label'
        expected_zip_path = os.path.join(
            '/home/user',
            '.ebartifacts',
            'archives',
            'custom-label.zip'
        )
        
        # Execute
        result = deploy.get_or_create_source_bundle(archive=archive_path, label=label)
        
        # Verify
        is_zipfile_mock.assert_called_once_with(archive_path)
        isdir_mock.assert_called_once_with(archive_path)
        makedirs_mock.assert_called_once_with(
            os.path.join('/home/user', '.ebartifacts', 'archives'),
            exist_ok=True
        )
        zip_up_folder_mock.assert_called_once_with(archive_path, expected_zip_path)
        self.assertEqual(expected_zip_path, result)

    @mock.patch('ebcli.controllers.deploy.zipfile.is_zipfile')
    @mock.patch('ebcli.controllers.deploy.path.isdir')
    @mock.patch('ebcli.controllers.deploy.datetime')
    @mock.patch('ebcli.controllers.deploy.fileoperations.zip_up_folder')
    @mock.patch('ebcli.controllers.deploy.makedirs')
    def test_get_source_bundle_from_archive_creates_directories(
            self,
            makedirs_mock,
            zip_up_folder_mock,
            datetime_mock,
            isdir_mock,
            is_zipfile_mock
    ):
        # Setup
        is_zipfile_mock.return_value = False
        isdir_mock.return_value = True
        
        # Mock datetime to return a fixed timestamp
        mock_datetime = mock.MagicMock()
        mock_datetime.now.return_value.timestamp.return_value = '1712175524.123456'
        datetime_mock.now.return_value = mock_datetime
        datetime_mock.UTC = mock.MagicMock()
        
        archive_path = 'source_dir'
        
        # Execute
        deploy.get_or_create_source_bundle(archive=archive_path)
        
        # Verify
        makedirs_mock.assert_called_once_with(
            os.path.join(os.path.expanduser('~'), '.ebartifacts', 'archives'),
            exist_ok=True
        )

    @mock.patch('ebcli.controllers.deploy.io.log_error')
    def test_multiple_modules__none_of_the_specified_modules_actually_exists(
            self,
            log_error_mock
    ):
        app = EB(
            argv=[
                'deploy',
                '--modules', 'module-1', 'module-2',
            ]
        )
        app.setup()
        app.run()

        log_error_mock.assert_has_calls(
            [
                mock.call('The directory module-1 does not exist.'),
                mock.call('The directory module-2 does not exist.')
            ]
        )

    @mock.patch('ebcli.controllers.deploy.io.echo')
    def test_multiple_modules__one_or_more_of_the_specified_modules_lacks_an_env_yaml(
            self,
            echo_mock
    ):
        os.mkdir('module-1')
        os.mkdir('module-2')
        os.mkdir('module-3')
        open(os.path.join('module-1', 'env.yaml'), 'w').close()

        app = EB(
            argv=[
                'deploy',
                '--modules', 'module-1', 'module-2', 'module-3'
            ]
        )
        app.setup()
        app.run()

        echo_mock.assert_called_once_with(
            'All specified modules require an env.yaml file.\n'
            'The following modules are missing this file: module-2, module-3'
        )

    def create_config_file_in(self, path):
        original_dir = os.getcwd()
        os.chdir(path)
        fileoperations.create_config_file(
            'my-application',
            'us-west-2',
            self.platform.name
        )
        os.chdir(original_dir)

    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.io.echo')
    @mock.patch('ebcli.controllers.deploy.commonops.create_app_version')
    @mock.patch('ebcli.controllers.deploy.composeops.compose_no_events')
    @mock.patch('ebcli.controllers.deploy.commonops.wait_for_compose_events')
    def test_multiple_modules(
            self,
            wait_for_compose_events_mock,
            compose_no_events_mock,
            create_app_version_mock,
            echo_mock,
            get_app_name_mock
    ):
        get_app_name_mock.return_value = 'my-application'
        create_app_version_mock.side_effect = [
            'app-version-1',
            'app-version-2',
            'app-version-3'
        ]
        compose_no_events_mock.return_value = 'request-id'

        os.mkdir('module-1')
        os.mkdir('module-2')
        os.mkdir('module-3')
        with open(os.path.join('module-1', 'env.yaml'), 'w') as file:
            file.write("""AWSConfigurationTemplateVersion: 1.1.0.0
EnvironmentName: front+
""")

        with open(os.path.join('module-2', 'env.yaml'), 'w') as file:
            file.write("""AWSConfigurationTemplateVersion: 1.1.0.0
EnvironmentName: back+
""")

        with open(os.path.join('module-3', 'env.yaml'), 'w') as file:
            file.write("""AWSConfigurationTemplateVersion: 1.1.0.0
""")

        self.create_config_file_in('module-1')
        self.create_config_file_in('module-2')
        self.create_config_file_in('module-3')

        app = EB(
            argv=[
                'deploy',
                '--modules', 'module-1', 'module-2', 'module-3',
                '--env-group-suffix', 'group-name'
            ]
        )
        app.setup()
        app.run()

        echo_mock.assert_has_calls(
            [
                mock.call('--- Creating application version for module: module-1 ---'),
                mock.call('--- Creating application version for module: module-2 ---'),
                mock.call('--- Creating application version for module: module-3 ---'),
                mock.call('No environment name was specified in env.yaml for module module-3. Unable to deploy.')
            ]

        )

        compose_no_events_mock.assert_called_once_with(
            'my-application',
            [
                'app-version-1',
                'app-version-2'
            ],
            group_name='group-name'
        )
        wait_for_compose_events_mock.assert_called_once_with(
            'request-id',
            'my-application',
            [
                'front-group-name',
                'back-group-name'
            ],
            None
        )
