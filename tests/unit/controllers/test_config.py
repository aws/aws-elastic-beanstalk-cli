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

from ebcli.controllers import config
from ebcli.core import fileoperations
from ebcli.core.ebcore import EB
from ebcli.objects.platform import PlatformVersion


class TestConfig(unittest.TestCase):
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


class TestConfigWithoutSubcommands(TestConfig):
    @mock.patch('ebcli.controllers.config.sys.stdin.isatty')
    @mock.patch('ebcli.controllers.config.configops.update_environment_configuration')
    @mock.patch('ebcli.controllers.config.ConfigController.get_app_name')
    @mock.patch('ebcli.controllers.config.ConfigController.get_env_name')
    def test_config__cfg_not_passed__in_non_interactive_mode(
            self,
            get_env_name_mock,
            get_app_name_mock,
            update_environment_configuration_mock,
            isatty_mock
    ):
        isatty_mock.return_value = True
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(argv=['config'])
        app.setup()
        app.run()

        update_environment_configuration_mock.assert_called_once_with(
            'my-application',
            'environment-1',
            False,
            timeout=None
        )

    @mock.patch('ebcli.controllers.config.saved_configs.resolve_config_name')
    @mock.patch('ebcli.controllers.config.saved_configs.update_environment_with_config_file')
    @mock.patch('ebcli.controllers.config.sys.stdin.isatty')
    @mock.patch('ebcli.controllers.config.ConfigController.get_app_name')
    @mock.patch('ebcli.controllers.config.ConfigController.get_env_name')
    def test_config__cfg_template_passed__in_non_interactive_mode(
            self,
            get_env_name_mock,
            get_app_name_mock,
            isatty_mock,
            update_environment_with_config_file_mock,
            resolve_config_name_mock,
    ):
        isatty_mock.return_value = True
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'
        resolve_config_name_mock.return_value = 'my-cfg-name'

        app = EB(argv=['config', '--cfg', 'my-cfg-name'])
        app.setup()
        app.run()

        update_environment_with_config_file_mock.assert_called_once_with(
            'environment-1',
            'my-cfg-name',
            False,
            timeout=None
        )

    @mock.patch('ebcli.controllers.config.saved_configs.update_environment_with_config_data')
    @mock.patch('ebcli.controllers.config.sys.stdin.isatty')
    @mock.patch('ebcli.controllers.config.sys.stdin.read')
    @mock.patch('ebcli.controllers.config.ConfigController.get_app_name')
    @mock.patch('ebcli.controllers.config.ConfigController.get_env_name')
    def test_config__cfg_not_passed__in_interactive_mode(
            self,
            get_env_name_mock,
            get_app_name_mock,
            read_mock,
            isatty_mock,
            update_environment_with_config_data_mock,
    ):
        isatty_mock.return_value = False
        read_mock.return_value = 'dome configurational detail'
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(argv=['config'])
        app.setup()
        app.run()

        update_environment_with_config_data_mock.assert_called_once_with(
            'environment-1',
            'dome configurational detail',
            False,
            timeout=None
        )

    @mock.patch('ebcli.controllers.config.io.prompt_for_unique_name')
    @mock.patch('ebcli.controllers.config.saved_configs.get_configurations')
    def test_choose_cfg_name(
            self,
            get_configurations_mock,
            prompt_for_unique_name_mock
    ):
        get_configurations_mock.return_value = [
            'configuration-template-1',
            'configuration-template-2',
        ]

        prompt_for_unique_name_mock.return_value = 'configuration-template-2'

        self.assertEqual(
            'configuration-template-2',
            config.ConfigController._choose_cfg_name(
                'my-application',
                'environment-1'
            )
        )

        prompt_for_unique_name_mock.assert_called_once_with(
            'environment-1-sc',
            [
                'configuration-template-1',
                'configuration-template-2'
            ]
        )


class TestConfigSave(TestConfig):
    @mock.patch('ebcli.controllers.config.ConfigController._choose_cfg_name')
    @mock.patch('ebcli.controllers.config.saved_configs.create_config')
    @mock.patch('ebcli.controllers.config.ConfigController.get_app_name')
    @mock.patch('ebcli.controllers.config.ConfigController.get_env_name')
    def test_save_config__customer_prompted_for_config_name(
            self,
            get_env_name_mock,
            get_app_name_mock,
            create_config_mock,
            _choose_cfg_name_mock
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'
        _choose_cfg_name_mock.return_value = 'my-cfg-name'

        app = EB(argv=['config', 'save'])
        app.setup()
        app.run()

        create_config_mock.assert_called_once_with(
            'my-application',
            'environment-1',
            'my-cfg-name',
            []
        )

    @mock.patch('ebcli.controllers.config.saved_configs.create_config')
    @mock.patch('ebcli.controllers.config.ConfigController.get_app_name')
    @mock.patch('ebcli.controllers.config.ConfigController.get_env_name')
    def test_save_config__customer_specified_config_name(
            self,
            get_env_name_mock,
            get_app_name_mock,
            create_config_mock,
    ):
        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'

        app = EB(argv=['config', 'save', '--cfg', 'my-cfg-name'])
        app.setup()
        app.run()

        create_config_mock.assert_called_once_with(
            'my-application',
            'environment-1',
            'my-cfg-name',
            []
        )

    @mock.patch('ebcli.controllers.config.ConfigController._choose_cfg_name')
    @mock.patch('ebcli.controllers.config.saved_configs.create_config')
    @mock.patch('ebcli.controllers.config.io.echo')
    @mock.patch('ebcli.controllers.config.ConfigController.get_app_name')
    @mock.patch('ebcli.controllers.config.ConfigController.get_env_name')
    def test_save_config__warn_if_env_yaml_exists(
            self,
            get_env_name_mock,
            get_app_name_mock,
            echo_mock,
            create_config_mock,
            _choose_cfg_name_mock
    ):
        open('env.yaml', 'w').close()

        get_app_name_mock.return_value = 'my-application'
        get_env_name_mock.return_value = 'environment-1'
        _choose_cfg_name_mock.return_value = 'my-cfg-name'

        app = EB(argv=['config', 'save'])
        app.setup()
        app.run()

        create_config_mock.assert_called_once_with(
            'my-application',
            'environment-1',
            'my-cfg-name',
            []
        )

        echo_mock.assert_called_once_with(
            'It appears your environment is using an env.yaml file. '
            'Be aware that a saved configuration will take precedence '
            'over the contents of your env.yaml file when both are present.'
        )


class TestConfigPut(TestConfig):
    @mock.patch('ebcli.controllers.config.io.echo')
    @mock.patch('ebcli.controllers.config.ConfigController.get_app_name')
    def test_positional_argument_name_not_specified__exception_raised(
            self,
            get_app_name_mock,
            echo_mock
    ):
        get_app_name_mock.return_value = 'my-application'
        echo_mock.return_value = 'my-cfg-name'

        app = EB(argv=['config', 'put'])
        app.setup()

        with self.assertRaises(config.InvalidSyntaxError) as context_manager:
            app.run()

        echo_mock.assert_called_once_with(
            'usage: eb config',
            'put',
            '[configuration_name]'
        )
        self.assertEqual(
            'too few arguments',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.controllers.config.solution_stack_ops.get_default_solution_stack')
    @mock.patch('ebcli.controllers.config.platformops.get_platform_for_platform_string')
    @mock.patch('ebcli.controllers.config.saved_configs.update_config')
    @mock.patch('ebcli.controllers.config.saved_configs.validate_config_file')
    @mock.patch('ebcli.controllers.config.ConfigController.get_app_name')
    def test_platform_is_solution_stack(
            self,
            get_app_name_mock,
            validate_config_file_mock,
            update_config_mock,
            get_platform_for_platform_string_mock,
            get_default_solution_stack_mock
    ):
        get_default_solution_stack_mock.return_value = '64bit Amazon Linux 2018.03 v2.8.0 running Go 1.10'
        get_app_name_mock.return_value = 'my-application'
        get_platform_for_platform_string_mock.return_value = self.platform

        app = EB(argv=['config', 'put', 'my-cfg-name.config'])
        app.setup()
        app.run()

        update_config_mock.assert_called_once_with(
            'my-application',
            'my-cfg-name.config'
        )
        validate_config_file_mock.assert_called_once_with(
            'my-application',
            'my-cfg-name',
            'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5'
        )

    @mock.patch('ebcli.controllers.config.solution_stack_ops.get_default_solution_stack')
    @mock.patch('ebcli.controllers.config.saved_configs.update_config')
    @mock.patch('ebcli.controllers.config.saved_configs.validate_config_file')
    @mock.patch('ebcli.controllers.config.ConfigController.get_app_name')
    def test_platform_is_an_arn(
            self,
            get_app_name_mock,
            validate_config_file_mock,
            update_config_mock,
            get_default_solution_stack_mock
    ):
        get_default_solution_stack_mock.return_value = 'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5'
        get_app_name_mock.return_value = 'my-application'

        app = EB(argv=['config', 'put', 'my-cfg-name.config'])
        app.setup()
        app.run()

        update_config_mock.assert_called_once_with(
            'my-application',
            'my-cfg-name.config'
        )
        validate_config_file_mock.assert_called_once_with(
            'my-application',
            'my-cfg-name',
            'arn:aws:elasticbeanstalk:us-west-2::platform/PHP 7.1 running on 64bit Amazon Linux/2.6.5'
        )


class TestConfigGet(TestConfig):
    @mock.patch('ebcli.controllers.config.io.echo')
    @mock.patch('ebcli.controllers.config.ConfigController.get_app_name')
    def test_positional_argument_name_not_specified__exception_raised(
            self,
            get_app_name_mock,
            echo_mock
    ):
        get_app_name_mock.return_value = 'my-application'
        echo_mock.return_value = 'my-cfg-name'

        app = EB(argv=['config', 'get'])
        app.setup()

        with self.assertRaises(config.InvalidSyntaxError) as context_manager:
            app.run()

        echo_mock.assert_called_once_with(
            'usage: eb config',
            'get',
            '[configuration_name]'
        )
        self.assertEqual(
            'too few arguments',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.controllers.config.ConfigController.get_app_name')
    @mock.patch('ebcli.controllers.config.saved_configs.download_config_from_s3')
    @mock.patch('ebcli.controllers.config.io.log_error')
    def test_failure_to_download_config_from_s3(
            self,
            log_error_mock,
            download_config_from_s3_mock,
            get_app_name_mock
    ):
        download_config_from_s3_mock.side_effect = config.NotFoundError
        get_app_name_mock.return_value = 'my-application'

        app = EB(argv=['config', 'get', 'my-cfg-name.config'])
        app.setup()
        app.run()

        log_error_mock.assert_called_once_with(
            'Elastic Beanstalk could not find any saved configuration with the name "my-cfg-name.config".'
        )

    @mock.patch('ebcli.controllers.config.ConfigController.get_app_name')
    @mock.patch('ebcli.controllers.config.saved_configs.download_config_from_s3')
    @mock.patch('ebcli.controllers.config.io.log_error')
    def test_download_config_from_s3(
            self,
            log_error_mock,
            download_config_from_s3_mock,
            get_app_name_mock
    ):
        download_config_from_s3_mock.side_effect = None
        get_app_name_mock.return_value = 'my-application'

        app = EB(argv=['config', 'get', 'my-cfg-name.config'])
        app.setup()
        app.run()

        log_error_mock.assert_not_called()


class TestConfigDelete(TestConfig):
    @mock.patch('ebcli.controllers.config.io.echo')
    @mock.patch('ebcli.controllers.config.ConfigController.get_app_name')
    def test_positional_argument_name_not_specified__exception_raised(
            self,
            get_app_name_mock,
            echo_mock
    ):
        get_app_name_mock.return_value = 'my-application'
        echo_mock.return_value = 'my-cfg-name'

        app = EB(argv=['config', 'delete'])
        app.setup()

        with self.assertRaises(config.InvalidSyntaxError) as context_manager:
            app.run()

        echo_mock.assert_called_once_with(
            'usage: eb config',
            'delete',
            '[configuration_name]'
        )
        self.assertEqual(
            'too few arguments',
            str(context_manager.exception)
        )

    @mock.patch('ebcli.controllers.config.ConfigController.get_app_name')
    @mock.patch('ebcli.controllers.config.saved_configs.delete_config')
    def test_failure_to_download_config_from_s3(
            self,
            delete_config_mock,
            get_app_name_mock
    ):
        delete_config_mock.side_effect = None
        get_app_name_mock.return_value = 'my-application'

        app = EB(argv=['config', 'delete', 'my-cfg-name.config'])
        app.setup()
        app.run()


class TestConfigList(TestConfig):
    @mock.patch('ebcli.controllers.config.io.echo')
    @mock.patch('ebcli.controllers.config.ConfigController.get_app_name')
    @mock.patch('ebcli.controllers.config.saved_configs.get_configurations')
    def test_list_all_configurations(
            self,
            get_configurations_mock,
            get_app_name_mock,
            echo_mock
    ):
        get_configurations_mock.return_value = [
            'configuration-template-1',
            'configuration-template-2',
        ]
        get_app_name_mock.return_value = 'my-application'

        app = EB(argv=['config', 'list'])
        app.setup()
        app.run()

        echo_mock.assert_has_calls(
            [
                mock.call('configuration-template-1'),
                mock.call('configuration-template-2')
            ]
        )
