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

from ebcli.controllers import deploy
from ebcli.core.ebcore import EB
from ebcli.core import fileoperations
from ebcli.objects.platform import PlatformVersion


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


class TestErrorConditions(TestDeploy):
    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    def test_deploy__version_and_message_specified_together(
            self,
            get_env_name_mock,
            get_app_name_mock
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

    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    def test_deploy__version_and_label_specified_together(
            self,
            get_env_name_mock,
            get_app_name_mock
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
    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(argv=['deploy'])
        app.setup()
        app.run()

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
            timeout=None
        )

    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy__nohang_sets_timeout_to_zero(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(argv=['deploy', '--nohang', '--timeout', '5'])
        app.setup()
        app.run()

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
            timeout=0
        )

    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy__with_version_label(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(argv=['deploy', '--version', 'my-version'])
        app.setup()
        app.run()

        deploy_mock.assert_called_with(
            'my-application',
            'environment-1',
            'my-version',
            None,
            None,
            group_name=None,
            process_app_versions=False,
            source=None,
            staged=False,
            timeout=None
        )

    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy__with_label_and_message(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock
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

        deploy_mock.assert_called_with(
            'my-application',
            'environment-1',
            None,
            'my-label',
            'This is my message',
            group_name=None,
            process_app_versions=False,
            source=None,
            staged=False,
            timeout=None
        )

    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy__process_app_version_because_env_yaml_exists(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock
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
            timeout=None
        )

    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy__process_app_version_because_process_flag_is_specified(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock
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
            timeout=None
        )

    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy__pass_group_name(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock
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
            timeout=None
        )

    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy__specify_codecommit_source(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock
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

        deploy_mock.assert_called_with(
            'my-application',
            'environment-1',
            None,
            None,
            None,
            group_name=None,
            process_app_versions=False,
            source='codecommit/my-repository/my-branch',
            staged=False,
            timeout=None
        )

    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy__specify_codecommit_source_with_forward_slash_in_branch_name(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock
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

        deploy_mock.assert_called_with(
            'my-application',
            'environment-1',
            None,
            None,
            None,
            group_name=None,
            process_app_versions=False,
            source='codecommit/my-repository/my-branch/feature',
            staged=False,
            timeout=None
        )

    @mock.patch('ebcli.controllers.deploy.DeployController.get_app_name')
    @mock.patch('ebcli.controllers.deploy.DeployController.get_env_name')
    @mock.patch('ebcli.controllers.deploy.deployops.deploy')
    def test_deploy__indicate_staged_changes_must_be_used(
            self,
            deploy_mock,
            get_env_name_mock,
            get_app_name_mock
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
            timeout=None
        )


class TestMultipleAppDeploy(unittest.TestCase):
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
