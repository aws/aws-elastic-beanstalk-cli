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
import mock
import unittest

from ebcli.core.ebcore import EB


class TestTerminate(unittest.TestCase):
    @mock.patch('ebcli.controllers.terminate.terminateops.terminate')
    @mock.patch('ebcli.controllers.terminate.io.echo')
    @mock.patch('ebcli.controllers.terminate.io.validate_action')
    @mock.patch('ebcli.controllers.terminate.AbstractBaseController.get_env_name')
    @mock.patch('ebcli.controllers.terminate.AbstractBaseController.get_app_name')
    @mock.patch('ebcli.controllers.terminate.terminateops.is_shared_load_balancer')
    @mock.patch('ebcli.controllers.terminate.io.log_alert')
    def test_terminate__single_environemnt__without_force_argument(
            self,
            log_alert_mock,
            is_shared_load_balancer_mock,
            get_app_name_mock,
            get_env_name_mock,
            validate_action_mock,
            echo_mock,
            terminate_mock
    ):
        get_env_name_mock.return_value = 'my-environment'
        get_app_name_mock.return_value = 'my-application'

        self.app = EB(argv=['terminate'])
        self.app.setup()
        self.app.run()

        echo_mock.assert_called_once_with(
            'The environment "my-environment" and all associated instances will be terminated.'
        )
        validate_action_mock.assert_called_once_with(
            'To confirm, type the environment name', 'my-environment'
        )
        is_shared_load_balancer_mock.assert_called_once_with('my-application', 'my-environment')

        terminate_mock.assert_called_once_with(
            'my-environment',
            force_terminate=False,
            nohang=False,
            timeout=None
        )

    @mock.patch('ebcli.controllers.terminate.terminateops.terminate')
    @mock.patch('ebcli.controllers.terminate.io.echo')
    @mock.patch('ebcli.controllers.terminate.io.validate_action')
    @mock.patch('ebcli.controllers.terminate.AbstractBaseController.get_env_name')
    @mock.patch('ebcli.controllers.terminate.AbstractBaseController.get_app_name')
    @mock.patch('ebcli.controllers.terminate.terminateops.is_shared_load_balancer')
    @mock.patch('ebcli.controllers.terminate.io.log_alert')
    def test_terminate__single_environemnt__with_force_argument(
            self,
            log_alert_mock,
            is_shared_load_balancer_mock,
            get_app_name_mock,
            get_env_name_mock,
            validate_action_mock,
            echo_mock,
            terminate_mock
    ):
        get_env_name_mock.return_value = 'my-environment'
        get_app_name_mock.return_value = 'my-application'

        self.app = EB(argv=['terminate', '--force'])
        self.app.setup()
        self.app.run()

        echo_mock.assert_not_called()
        validate_action_mock.assert_not_called()
        is_shared_load_balancer_mock.assert_called_once_with('my-application', 'my-environment')

        terminate_mock.assert_called_once_with(
            'my-environment',
            force_terminate=False,
            nohang=False,
            timeout=None
        )

    @mock.patch('ebcli.controllers.terminate.terminateops.delete_app')
    @mock.patch('ebcli.controllers.terminate.AbstractBaseController.get_app_name')
    def test_terminate__complete_application(
            self,
            get_app_name_mock,
            delete_app_mock
    ):
        get_app_name_mock.return_value = 'my-application'

        self.app = EB(argv=['terminate', '--all'])
        self.app.setup()
        self.app.run()

        delete_app_mock.assert_called_once_with(
            'my-application',
            False,
            cleanup=True,
            nohang=False,
            timeout=None
        )

    @mock.patch('ebcli.controllers.terminate.terminateops.delete_app')
    @mock.patch('ebcli.controllers.terminate.AbstractBaseController.get_app_name')
    def test_terminate__complete_application__with_force_region_timeout_and_nohang_arguments(
            self,
            get_app_name_mock,
            delete_app_mock
    ):
        get_app_name_mock.return_value = 'my-application'

        self.app = EB(
            argv=[
                'terminate',
                '--all',
                '--force',
                '--nohang',
                '--region', 'us-east-1',
                '--timeout', '25'
            ]
        )
        self.app.setup()
        self.app.run()

        delete_app_mock.assert_called_once_with(
            'my-application',
            True,
            cleanup=False,
            nohang=True,
            timeout=25
        )
